"""
Claude API Service
Handles all interactions with Anthropic's Claude API for content processing
"""

import os
import logging
from typing import Dict, List, Optional, Any
import json
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class ClaudeService:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-sonnet-20240229"
        logger.info("Claude service initialized")

    def is_available(self) -> bool:
        """Test Claude API availability"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Test"}]
            )
            return True
        except Exception as e:
            logger.error(f"Claude availability test failed: {e}")
            return False

    def parse_pdf_sections(self, pdf_text: str, level: str) -> List[Dict[str, Any]]:
        """Parse PDF content into logical sections"""
        prompt = f"""
        You are an educational content analyzer. Parse this research paper into logical sections that can be explained at a {level} level.

        For each section, provide:
        1. Title (clear and descriptive)
        2. Content summary (key concepts explained at {level} level)
        3. Dependencies (what concepts from previous sections are needed)
        4. Complexity score (1-10, where 1 is very basic)
        5. Key visual elements that should be animated
        6. Estimated explanation time in seconds

        Return as JSON array with this structure:
        [{{
            "title": "Section Title",
            "content": "Content summary adapted for {level} level",
            "dependencies": ["concept1", "concept2"],
            "complexity": 5,
            "visual_elements": ["diagram type", "animation type"],
            "estimated_time": 120,
            "concepts": ["new_concept1", "new_concept2"]
        }}]

        PDF Content:
        {pdf_text[:4000]}  # Limit content for API
        """

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse JSON response
            sections_text = response.content[0].text
            sections = json.loads(sections_text)
            
            logger.info(f"Parsed {len(sections)} sections from PDF")
            return sections
            
        except Exception as e:
            logger.error(f"Error parsing PDF sections: {e}")
            raise

    def generate_scene_plan(self, section: Dict[str, Any], context: Dict[str, Any], level: str) -> Dict[str, Any]:
        """Generate detailed scene plan for a section"""
        prompt = f"""
        You are an educational animation director. Create a detailed scene plan for this section.

        Section: {section['title']}
        Content: {section['content']}
        Level: {level}
        Dependencies satisfied: {list(context.keys())}

        Create a scene plan with:
        1. Scene breakdown (3-7 scenes)
        2. Visual elements for each scene
        3. Timing for each scene
        4. Transitions between scenes
        5. Key concepts to highlight
        6. Mathematical formulas (if any) in LaTeX

        Return as JSON:
        {{
            "title": "{section['title']}",
            "total_duration": 120,
            "scenes": [{{
                "scene_id": 1,
                "title": "Introduction",
                "duration": 20,
                "visual_type": "text_intro",
                "content": "Scene description",
                "concepts": ["concept1"],
                "formulas": ["\\\\frac{{a}}{{b}}"],
                "transitions": "fade_in"
            }}],
            "key_concepts": ["concept1", "concept2"],
            "difficulty_adaptations": {{
                "beginner": "Use simple analogies",
                "advanced": "Include mathematical proofs"
            }}
        }}
        """

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            scene_plan = json.loads(response.content[0].text)
            logger.info(f"Generated scene plan with {len(scene_plan['scenes'])} scenes")
            return scene_plan
            
        except Exception as e:
            logger.error(f"Error generating scene plan: {e}")
            raise

    def generate_transcript(self, scene_plan: Dict[str, Any], level: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate narration transcript with timing markers"""
        prompt = f"""
        You are an educational narrator. Create a detailed transcript for this animation.

        Scene Plan: {json.dumps(scene_plan, indent=2)}
        Explanation Level: {level}
        Previous Context: {list(context.keys())}

        Create a transcript with:
        1. Natural, engaging narration text
        2. Precise timing markers (sync points)
        3. Pause indicators for visual emphasis
        4. Level-appropriate language
        5. Smooth transitions between concepts

        Return as JSON:
        {{
            "text": "Full narration text...",
            "timing_markers": [{{
                "time": 5.0,
                "text": "Text at this moment",
                "sync_point": "scene_1_intro",
                "emphasis": "normal"
            }}],
            "sync_points": [{{
                "name": "scene_1_intro",
                "time": 5.0,
                "visual_cue": "Title appears"
            }}],
            "estimated_duration": 120,
            "word_count": 200,
            "speaking_rate": 160
        }}
        """

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            transcript = json.loads(response.content[0].text)
            logger.info(f"Generated transcript with {len(transcript['timing_markers'])} timing markers")
            return transcript
            
        except Exception as e:
            logger.error(f"Error generating transcript: {e}")
            raise

    def generate_manim_code(self, scene_plan: Dict[str, Any], transcript: Dict[str, Any], audio_duration: float) -> str:
        """Generate Manim Python code for the animation"""
        prompt = f"""
        You are a Manim animation programmer. Generate complete Python code for this educational animation.

        Scene Plan: {json.dumps(scene_plan, indent=2)}
        Transcript Timing: {json.dumps(transcript['timing_markers'], indent=2)}
        Audio Duration: {audio_duration} seconds

        Requirements:
        1. Use Manim Community Edition syntax
        2. Create smooth, educational animations
        3. Sync with audio timing markers
        4. Include mathematical formulas if present
        5. Use appropriate colors and layouts
        6. Add scene transitions

        Generate complete Python code starting with imports and including a MainScene class.
        Ensure timing matches the audio duration exactly: {audio_duration} seconds.

        Example structure:
        ```python
        from manim import *

        class MainScene(Scene):
            def construct(self):
                # Scene 1: Introduction
                title = Text("Section Title")
                self.play(Write(title))
                self.wait(2)  # Sync with audio
                
                # More scenes...
        ```
        """

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract Python code from response
            code_text = response.content[0].text
            
            # Clean up the code (remove markdown formatting if present)
            if "```python" in code_text:
                code_text = code_text.split("```python")[1].split("```")[0]
            elif "```" in code_text:
                code_text = code_text.split("```")[1].split("```")[0]
            
            logger.info("Generated Manim code successfully")
            return code_text.strip()
            
        except Exception as e:
            logger.error(f"Error generating Manim code: {e}")
            raise

    def correct_sync_timing(self, manim_code: str, corrections: List[Dict[str, Any]]) -> str:
        """Apply timing corrections to Manim code"""
        prompt = f"""
        You are a Manim timing expert. Apply these timing corrections to the Manim code:

        Original Code:
        {manim_code}

        Corrections to apply:
        {json.dumps(corrections, indent=2)}

        Modify the code to fix timing issues while maintaining visual quality.
        Focus on adjusting wait() times and animation durations.
        
        Return only the corrected Python code.
        """

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            corrected_code = response.content[0].text
            
            # Clean up the code
            if "```python" in corrected_code:
                corrected_code = corrected_code.split("```python")[1].split("```")[0]
            elif "```" in corrected_code:
                corrected_code = corrected_code.split("```")[1].split("```")[0]
            
            logger.info("Applied timing corrections to Manim code")
            return corrected_code.strip()
            
        except Exception as e:
            logger.error(f"Error correcting sync timing: {e}")
            return manim_code  # Return original if correction fails
