import subprocess
import sys
import os
import tempfile
import json
import traceback
from contextlib import contextmanager
import time

class CodeExecutor:
    def __init__(self, workspace_dir, timeout=300):
        self.workspace_dir = workspace_dir
        self.timeout = timeout  # 5 minutes default timeout
        
    @contextmanager
    def temporary_script(self, code):
        """Create a temporary Python script file"""
        fd, path = tempfile.mkstemp(suffix='.py', dir=self.workspace_dir)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(code)
            yield path
        finally:
            if os.path.exists(path):
                os.unlink(path)
    
    def prepare_code(self, code, data_files):
        """Prepare code by injecting proper file paths"""
        # Create a header that sets up the environment
        header = f"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# Set working directory
os.chdir(r'{self.workspace_dir}')

# Available data files
data_files = {json.dumps(data_files)}

# Helper function to load data
def load_data(filename):
    for file_info in data_files:
        if file_info['filename'] == filename:
            return pd.read_csv(file_info['path'])
    raise FileNotFoundError(f"Data file {{filename}} not found")

# Redirect plots to files
plot_counter = 0
def save_plot(name=None):
    global plot_counter
    if name is None:
        name = f'plot_{{plot_counter}}'
    plt.savefig(f'{{name}}.png', dpi=150, bbox_inches='tight')
    plot_counter += 1
    print(f"Plot saved as {{name}}.png")
    plt.close()

# Override plt.show() to save plots
plt.show = lambda: save_plot()

print("=== Starting Analysis ===")
"""
        
        # Append user code
        full_code = header + "\n\n" + code
        
        # Add footer to ensure all plots are saved
        footer = """
\n
# Save any remaining plots
import matplotlib.pyplot as plt
for fig_num in plt.get_fignums():
    plt.figure(fig_num)
    save_plot(f'figure_{fig_num}')

print("\\n=== Analysis Complete ===")
"""
        
        return full_code + footer
    
    def execute_code(self, code, data_files):
        """Execute the code in a sandboxed environment"""
        results = {
            'success': False,
            'output': '',
            'error': '',
            'files_created': [],
            'execution_time': 0
        }
        
        try:
            # Prepare the code with proper file paths
            prepared_code = self.prepare_code(code, data_files)
            
            # Create temporary script
            with self.temporary_script(prepared_code) as script_path:
                # Execute the script
                start_time = time.time()
                
                # Run in subprocess for safety
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=self.workspace_dir
                )
                
                try:
                    stdout, stderr = process.communicate(timeout=self.timeout)
                    execution_time = time.time() - start_time
                    
                    results['output'] = stdout
                    results['error'] = stderr
                    results['execution_time'] = execution_time
                    
                    if process.returncode == 0:
                        results['success'] = True
                        
                        # Check for created files (plots, CSVs, etc.)
                        for file in os.listdir(self.workspace_dir):
                            if file.endswith(('.png', '.jpg', '.csv', '.xlsx', '.json')):
                                file_path = os.path.join(self.workspace_dir, file)
                                if os.path.getctime(file_path) > start_time:
                                    results['files_created'].append(file)
                    else:
                        results['error'] = f"Process exited with code {process.returncode}\n{stderr}"
                        
                except subprocess.TimeoutExpired:
                    process.kill()
                    results['error'] = f"Code execution timed out after {self.timeout} seconds"
                    
        except Exception as e:
            results['error'] = f"Execution error: {str(e)}\n{traceback.format_exc()}"
            
        return results
    
    def validate_code(self, code):
        """Basic code validation before execution"""
        dangerous_imports = [
            'subprocess', 'os.system', 'eval', 'exec', '__import__',
            'compile', 'open', 'file', 'input', 'raw_input'
        ]
        
        dangerous_patterns = []
        
        for dangerous in dangerous_imports:
            if dangerous in code:
                dangerous_patterns.append(dangerous)
                
        if dangerous_patterns:
            return False, f"Code contains potentially dangerous operations: {', '.join(dangerous_patterns)}"
            
        # Try to compile the code
        try:
            compile(code, '<string>', 'exec')
            return True, "Code validation passed"
        except SyntaxError as e:
            return False, f"Syntax error in code: {str(e)}" 