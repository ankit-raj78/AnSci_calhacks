"""
Manim Generator Service
Handles Manim animation rendering and scene generation
"""

import os
import subprocess
import logging
import tempfile
import shutil
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class ManimGenerator:
    def __init__(self):
        self.output_dir = os.getenv('OUTPUT_DIR', './output')
        self.temp_dir = os.getenv('TEMP_DIR', './temp')
        self.quality = os.getenv('MANIM_QUALITY', 'medium_quality')
        self.frame_rate = int(os.getenv('MANIM_FRAME_RATE', '30'))
        
        # Create directories if they don't exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        logger.info("Manim generator initialized")

    def is_available(self) -> bool:
        """Test if Manim is available"""
        try:
            result = subprocess.run(['manim', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Manim availability test failed: {e}")
            return False

    def render_scene(self, manim_code: str, scene_name: str) -> str:
        """
        Render a Manim scene and return the output video path
        
        Args:
            manim_code: Python code containing Manim scene
            scene_name: Unique name for this scene (used for file naming)
        
        Returns:
            Path to the rendered video file
        """
        try:
            # Create temporary directory for this scene
            scene_dir = os.path.join(self.temp_dir, scene_name)
            os.makedirs(scene_dir, exist_ok=True)
            
            # Write Manim code to file
            code_file = os.path.join(scene_dir, f"{scene_name}.py")
            with open(code_file, 'w') as f:
                f.write(manim_code)
            
            # Determine quality flags
            quality_flags = self._get_quality_flags()
            
            # Construct Manim command
            cmd = [
                'manim',
                *quality_flags,
                '--output_file', f"{scene_name}",
                code_file,
                'MainScene'  # Assuming the main scene class is named MainScene
            ]
            
            # Run Manim
            logger.info(f"Rendering scene {scene_name} with command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=scene_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Manim rendering failed: {result.stderr}")
                raise RuntimeError(f"Manim rendering failed: {result.stderr}")
            
            # Find the output video file
            output_video = self._find_output_video(scene_dir, scene_name)
            
            if not output_video:
                raise RuntimeError("Could not find rendered video file")
            
            # Move to final output location
            final_path = os.path.join(self.output_dir, f"{scene_name}.mp4")
            shutil.move(output_video, final_path)
            
            logger.info(f"Scene {scene_name} rendered successfully: {final_path}")
            return final_path
            
        except subprocess.TimeoutExpired:
            logger.error(f"Manim rendering timeout for scene {scene_name}")
            raise RuntimeError("Rendering timeout - scene too complex")
        except Exception as e:
            logger.error(f"Error rendering scene {scene_name}: {e}")
            raise

    def _get_quality_flags(self) -> List[str]:
        """Get Manim quality flags based on configuration"""
        quality_map = {
            'low_quality': ['-ql'],
            'medium_quality': ['-qm'],
            'high_quality': ['-qh'],
            'production_quality': ['-p']
        }
        
        return quality_map.get(self.quality, ['-qm'])

    def _find_output_video(self, scene_dir: str, scene_name: str) -> Optional[str]:
        """Find the rendered video file in Manim's output structure"""
        # Manim creates a complex directory structure
        # Look in media/videos/[scene_name]/[quality]/
        possible_paths = [
            os.path.join(scene_dir, 'media', 'videos', scene_name, '480p15', f'{scene_name}.mp4'),
            os.path.join(scene_dir, 'media', 'videos', scene_name, '720p30', f'{scene_name}.mp4'),
            os.path.join(scene_dir, 'media', 'videos', scene_name, '1080p60', f'{scene_name}.mp4'),
            os.path.join(scene_dir, 'media', 'videos', scene_name, '480p15', 'MainScene.mp4'),
            os.path.join(scene_dir, 'media', 'videos', scene_name, '720p30', 'MainScene.mp4'),
            os.path.join(scene_dir, 'media', 'videos', scene_name, '1080p60', 'MainScene.mp4'),
        ]
        
        # Also search recursively for any .mp4 files
        for root, dirs, files in os.walk(os.path.join(scene_dir, 'media')):
            for file in files:
                if file.endswith('.mp4'):
                    possible_paths.append(os.path.join(root, file))
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found output video: {path}")
                return path
        
        logger.error(f"Could not find output video for {scene_name}")
        logger.error(f"Checked paths: {possible_paths}")
        return None

    def create_simple_test_scene(self, text: str = "Test Animation") -> str:
        """Create a simple test scene for validation"""
        test_code = f'''
from manim import *

class MainScene(Scene):
    def construct(self):
        # Simple test animation
        title = Text("{text}", font_size=48)
        title.set_color(BLUE)
        
        self.play(Write(title))
        self.wait(1)
        
        # Add some movement
        self.play(title.animate.shift(UP))
        self.wait(0.5)
        
        # Fade out
        self.play(FadeOut(title))
        self.wait(0.5)
'''
        
        return self.render_scene(test_code, "test_scene")

    def validate_manim_code(self, code: str) -> Dict[str, Any]:
        """Validate Manim code without rendering"""
        try:
            # Basic syntax validation
            compile(code, '<string>', 'exec')
            
            # Check for required imports and class
            has_imports = 'from manim import' in code or 'import manim' in code
            has_main_scene = 'class MainScene' in code
            has_construct = 'def construct(self):' in code
            
            validation_result = {
                'valid': has_imports and has_main_scene and has_construct,
                'has_imports': has_imports,
                'has_main_scene': has_main_scene,
                'has_construct': has_construct,
                'syntax_valid': True
            }
            
            if not validation_result['valid']:
                issues = []
                if not has_imports: issues.append("Missing Manim imports")
                if not has_main_scene: issues.append("Missing MainScene class")
                if not has_construct: issues.append("Missing construct method")
                validation_result['issues'] = issues
            
            return validation_result
            
        except SyntaxError as e:
            return {
                'valid': False,
                'syntax_valid': False,
                'syntax_error': str(e),
                'line': e.lineno if hasattr(e, 'lineno') else None
            }

    def cleanup_job(self, job_id: str):
        """Clean up temporary files for a job"""
        try:
            # Remove temporary directories for this job
            job_temp_dir = os.path.join(self.temp_dir, f"*{job_id}*")
            for path in Path(self.temp_dir).glob(f"*{job_id}*"):
                if path.is_dir():
                    shutil.rmtree(path)
                    logger.info(f"Cleaned up temp directory: {path}")
        except Exception as e:
            logger.error(f"Error cleaning up job {job_id}: {e}")

    def get_render_info(self) -> Dict[str, Any]:
        """Get information about the render environment"""
        try:
            # Get Manim version
            result = subprocess.run(['manim', '--version'], capture_output=True, text=True)
            manim_version = result.stdout.strip() if result.returncode == 0 else "Unknown"
            
            return {
                'manim_available': self.is_available(),
                'manim_version': manim_version,
                'output_dir': self.output_dir,
                'temp_dir': self.temp_dir,
                'quality': self.quality,
                'frame_rate': self.frame_rate
            }
        except Exception as e:
            logger.error(f"Error getting render info: {e}")
            return {'error': str(e)}
