import openai
import os
from dotenv import load_dotenv
import json

load_dotenv()

class LLMIntegration:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        
    def generate_plan_and_code(self, user_query, documents_info):
        """
        Generate a plan and code based on user query and available documents
        """
        system_prompt = """You are an expert data analyst specialized in survey analysis. 
        Given a user query and information about available documents (survey designs and data files),
        generate:
        1. A step-by-step plan to analyze the data
        2. Python code that implements the plan
        
        The code should use pandas for data manipulation and matplotlib/seaborn for visualizations.
        Make sure the code is complete and executable.
        
        Return your response in JSON format with keys: 'plan' and 'code'
        """
        
        user_prompt = f"""
        User Query: {user_query}
        
        Available Documents:
        {json.dumps(documents_info, indent=2)}
        
        Generate a plan and Python code to address this query.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the response
            content = response.choices[0].message.content
            
            # Try to extract JSON from the response
            try:
                result = json.loads(content)
                return result.get('plan', ''), result.get('code', '')
            except:
                # If JSON parsing fails, extract plan and code manually
                plan = "Generated analysis plan:\n" + content.split('```')[0].strip()
                code = ""
                if '```python' in content:
                    code = content.split('```python')[1].split('```')[0].strip()
                elif '```' in content:
                    code = content.split('```')[1].split('```')[0].strip()
                
                return plan, code
                
        except Exception as e:
            # Return mock data if API fails
            plan = f"""1. Load the survey data files
2. Explore the data structure and summary statistics
3. Analyze key survey questions based on the query: {user_query}
4. Generate relevant visualizations
5. Provide insights and recommendations"""
            
            code = f"""import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
# TODO: Update with actual file paths
df = pd.read_csv('survey_data.csv')

# Basic exploration
print("Data shape:", df.shape)
print("\\nColumn names:")
print(df.columns.tolist())
print("\\nData summary:")
print(df.describe())

# Analysis based on query: {user_query}
# TODO: Add specific analysis code here

# Visualization
plt.figure(figsize=(10, 6))
# TODO: Add visualization code
plt.show()
"""
            
            return plan, code
    
    def refine_plan(self, original_query, original_plan, original_code, user_feedback):
        """
        Refine the plan and code based on user feedback
        """
        system_prompt = """You are an expert data analyst. 
        The user has rejected your initial plan and code. 
        Based on their feedback, provide a refined plan and code.
        
        Return your response in JSON format with keys: 'plan' and 'code'
        """
        
        user_prompt = f"""
        Original Query: {original_query}
        
        Original Plan:
        {original_plan}
        
        Original Code:
        {original_code}
        
        User Feedback: {user_feedback}
        
        Please provide a refined plan and code that addresses the user's concerns.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            try:
                result = json.loads(content)
                return result.get('plan', ''), result.get('code', '')
            except:
                # Extract manually if JSON parsing fails
                plan = "Refined plan:\n" + content.split('```')[0].strip()
                code = ""
                if '```python' in content:
                    code = content.split('```python')[1].split('```')[0].strip()
                elif '```' in content:
                    code = content.split('```')[1].split('```')[0].strip()
                
                return plan, code
                
        except Exception as e:
            # Return refined mock data if API fails
            refined_plan = f"""Refined plan based on feedback: {user_feedback}
            
1. Address the specific concerns raised
2. {original_plan}
3. Additional steps based on feedback"""
            
            refined_code = f"""# Refined code based on user feedback
{original_code}

# Additional code to address feedback: {user_feedback}
"""
            
            return refined_plan, refined_code 