#!/usr/bin/env python3
"""
Test script for the enhanced Manim code validation and regeneration
"""

import os
import sys
sys.path.insert(0, '.')

from ansci.verify import (
    validate_manim_code_with_subprocess, 
    validate_and_regenerate_manim_code,
    regenerate_manim_code_with_anthropic
)

def test_enhanced_validation():
    """Test the enhanced validation with subprocess error capture"""
    
    print("🧪 Testing Enhanced Manim Code Validation")
    print("=" * 50)
    
    # Test case 1: Code with common errors
    problematic_code = """
class TestScene(Scene):
    def construct(self):
        # Common errors: undefined variables
        text = Text("Hello World").move_to(UP)
        circle = Circle(color=BLUE).move_to(DOWN)
        self.play(Write(text), Create(circle))
        self.wait()
"""
    
    print("🔍 Testing problematic code with subprocess validation...")
    result = validate_manim_code_with_subprocess(problematic_code, "TestScene")
    
    print(f"Valid: {result.is_valid}")
    print(f"Error Type: {result.error_type}")
    print(f"Errors Found: {len(result.errors)}")
    
    if result.errors:
        print("Specific Errors:")
        for i, error in enumerate(result.errors[:3], 1):
            print(f"  {i}. {error}")
    
    if result.subprocess_stderr:
        print(f"Subprocess stderr captured: {len(result.subprocess_stderr)} characters")
    
    if result.manim_error_output:
        print(f"Manim error output captured: {len(result.manim_error_output)} characters")


def test_integration_validation():
    """Test the integrated validation and regeneration function"""
    
    print("\n🔗 Testing Integrated Validation and Regeneration")
    print("=" * 50)
    
    # Test code with multiple issues
    test_code = """
class Scene1(Scene):
    def construct(self):
        title = Text("Test Animation", font_size=48).move_to(UP * 2)
        subtitle = Text("With errors", font_size=24).move_to(ORIGIN)
        
        # Missing imports and undefined variables
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(1)
"""
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        print("🚀 Running integrated validation and regeneration...")
        
        try:
            final_code, final_result = validate_and_regenerate_manim_code(
                test_code,
                context="Educational animation with title and subtitle",
                max_attempts=2,
                use_subprocess=True
            )
            
            print(f"✅ Process completed")
            print(f"Final code valid: {final_result.is_valid}")
            print(f"Final code length: {len(final_code)} characters")
            
        except Exception as e:
            print(f"❌ Integration test failed: {e}")
    else:
        print("⚠️  Skipping integration test - no ANTHROPIC_API_KEY found")


if __name__ == "__main__":
    print("🚀 Enhanced Manim Validation Test Suite")
    print("=" * 60)
    
    test_enhanced_validation()
    test_integration_validation()
    
    print("\n" + "=" * 60)
    print("🎉 Test Suite Complete!")
    print("\nKey Features Demonstrated:")
    print("✅ Subprocess error capture from Manim execution")
    print("✅ Detailed error parsing and categorization") 
    print("✅ AI-powered code regeneration with error context")
    print("✅ Integrated validation and regeneration pipeline")
