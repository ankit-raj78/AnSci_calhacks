#!/usr/bin/env python3
"""
Test script for enhanced validation system
Tests various types of Python errors and validation feedback
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "ansci"))

from ansci.verify import (
    validate_generated_manim_code,
    generate_regeneration_feedback,
    ValidationResult,
)


def test_syntax_error():
    """Test validation with syntax errors"""
    print("🔍 Testing syntax error detection...")

    code_with_syntax_error = """
from manim import *
import numpy as np

class Scene1(Scene):
    def construct(self):
        # Missing closing parenthesis
        text = Text("Hello World"
        self.play(Write(text))
    """

    result = validate_generated_manim_code(code_with_syntax_error)
    print(f"✅ Syntax error detected: {result.is_valid}")
    print(f"   Error type: {result.error_type}")
    print(f"   Errors: {result.errors}")

    if not result.is_valid:
        feedback = generate_regeneration_feedback(result)
        print(f"   Feedback preview: {feedback[:200]}...")

    return result


def test_undefined_variables():
    """Test validation with undefined variables"""
    print("\n🔍 Testing undefined variable detection...")

    code_with_undefined_vars = """
from manim import *
import numpy as np

class Scene1(Scene):
    def construct(self):
        # Using undefined variables
        text = Text("Hello World", color=BLUE)
        self.play(Write(text))
        
        # Undefined variable
        undefined_var = some_undefined_function()
        self.play(Create(undefined_var))
    """

    result = validate_generated_manim_code(code_with_undefined_vars)
    print(f"✅ Undefined variables detected: {result.is_valid}")
    print(f"   Error type: {result.error_type}")
    print(f"   Errors: {result.errors}")

    if not result.is_valid:
        feedback = generate_regeneration_feedback(result)
        print(f"   Feedback preview: {feedback[:200]}...")

    return result


def test_type_errors():
    """Test validation with type errors"""
    print("\n🔍 Testing type error detection...")

    code_with_type_errors = """
from manim import *
import numpy as np

class Scene1(Scene):
    def construct(self):
        # Type error: Text without arguments
        text = Text()
        self.play(Write(text))
        
        # Type error: Write without arguments
        self.play(Write())
    """

    result = validate_generated_manim_code(code_with_type_errors)
    print(f"✅ Type errors detected: {result.is_valid}")
    print(f"   Error type: {result.error_type}")
    print(f"   Errors: {result.errors}")

    if not result.is_valid:
        feedback = generate_regeneration_feedback(result)
        print(f"   Feedback preview: {feedback[:200]}...")

    return result


def test_valid_code():
    """Test validation with valid code"""
    print("\n🔍 Testing valid code...")

    valid_code = """
from manim import *
import numpy as np
from functools import wraps

class LayoutManager:
    SAFE_MARGIN = 0.5
    SCREEN_WIDTH = 14.22
    SCREEN_HEIGHT = 8.0
    
    @classmethod
    def safe_position(cls, mobject, target_position):
        x, y, z = target_position
        return np.array([x, y, z])

def validate_scene(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        return result
    return wrapper

class AnimationPresets:
    FAST = 0.5
    NORMAL = 1.0
    SLOW = 1.5
    TITLE_SIZE = 28

class Scene1(Scene):
    @validate_scene
    def construct(self):
        title = Text("Hello World", font_size=AnimationPresets.TITLE_SIZE, color=BLUE)
        title_pos = LayoutManager.safe_position(title, [0, 0, 0])
        title.move_to(title_pos)
        self.play(Write(title))
        self.wait(AnimationPresets.NORMAL)
    """

    result = validate_generated_manim_code(valid_code)
    print(f"✅ Valid code validation: {result.is_valid}")
    print(f"   Error type: {result.error_type}")
    print(f"   Warnings: {result.warnings}")

    return result


def test_runtime_errors():
    """Test validation with potential runtime errors"""
    print("\n🔍 Testing runtime error detection...")

    code_with_runtime_errors = """
from manim import *
import numpy as np

class Scene1(Scene):
    def construct(self):
        # Potential runtime error: division by zero
        x = 1 / 0
        
        # Potential runtime error: accessing non-existent attribute
        text = Text("Hello")
        width = text.non_existent_attribute
        
        self.play(Write(text))
    """

    result = validate_generated_manim_code(code_with_runtime_errors)
    print(f"✅ Runtime errors detected: {result.is_valid}")
    print(f"   Error type: {result.error_type}")
    print(f"   Errors: {result.errors}")

    if not result.is_valid:
        feedback = generate_regeneration_feedback(result)
        print(f"   Feedback preview: {feedback[:200]}...")

    return result


def main():
    """Run all validation tests"""
    print("🧪 Enhanced Validation System Test")
    print("=" * 50)

    # Run all tests
    results = []
    results.append(test_syntax_error())
    results.append(test_undefined_variables())
    results.append(test_type_errors())
    results.append(test_runtime_errors())
    results.append(test_valid_code())

    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    valid_count = sum(1 for r in results if r.is_valid)
    total_count = len(results)

    print(f"Total tests: {total_count}")
    print(f"Valid results: {valid_count}")
    print(f"Invalid results: {total_count - valid_count}")
    print(f"Success rate: {(valid_count/total_count)*100:.1f}%")

    # Show error types detected
    error_types = [r.error_type for r in results if not r.is_valid and r.error_type]
    if error_types:
        print(f"Error types detected: {list(set(error_types))}")

    print("\n✅ Enhanced validation system test complete!")


if __name__ == "__main__":
    main()
