#!/usr/bin/env python3
"""
Test script for improved validation system
Tests that the system has fewer false positives and better error detection
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "ansci"))

from ansci.verify import (
    validate_generated_manim_code,
    generate_regeneration_feedback,
    ValidationResult,
)


def test_valid_code():
    """Test validation with valid code - should pass"""
    print("🔍 Testing valid code...")

    valid_code = """
from manim import *
import numpy as np
from functools import wraps

class Scene1(Scene):
    def construct(self):
        title = Text("Hello World", font_size=36, color=BLUE)
        title.move_to([0, 0, 0])
        self.play(Write(title))
        self.wait(1)
        
        content = Text("This is a test", font_size=24, color=WHITE)
        content.move_to([0, -1, 0])
        self.play(Write(content))
        self.wait(1)
    """

    result = validate_generated_manim_code(valid_code)
    print(f"✅ Valid code result: {result.is_valid}")
    print(f"   Error type: {result.error_type}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Warnings: {len(result.warnings)}")

    return result


def test_syntax_error():
    """Test validation with syntax error - should fail"""
    print("\n🔍 Testing syntax error...")

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
    print(f"✅ Syntax error result: {result.is_valid}")
    print(f"   Error type: {result.error_type}")
    print(f"   Errors: {result.errors}")

    return result


def test_critical_undefined():
    """Test validation with critical undefined variable - should fail"""
    print("\n🔍 Testing critical undefined variable...")

    code_with_undefined = """
from manim import *
import numpy as np

class Scene1(Scene):
    def construct(self):
        # Critical undefined variable
        text = Text("Hello World", color=BLUE)
        self.play(Write(text))
        
        # This should be flagged
        undefined_var = some_undefined_function()
        self.play(Create(undefined_var))
    """

    result = validate_generated_manim_code(code_with_undefined)
    print(f"✅ Critical undefined result: {result.is_valid}")
    print(f"   Error type: {result.error_type}")
    print(f"   Errors: {result.errors}")

    return result


def test_common_patterns():
    """Test validation with common Manim patterns - should pass or warn only"""
    print("\n🔍 Testing common Manim patterns...")

    code_with_patterns = """
from manim import *
import numpy as np

class Scene1(Scene):
    def construct(self):
        # Common patterns that should be warnings, not errors
        mobject = Text("Hello", color=color)
        animation = Write(mobject)
        position = [0, 0, 0]
        duration = 2.0
        
        self.play(animation, run_time=duration)
        mobject.move_to(position)
    """

    result = validate_generated_manim_code(code_with_patterns)
    print(f"✅ Common patterns result: {result.is_valid}")
    print(f"   Error type: {result.error_type}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Warnings: {len(result.warnings)}")

    return result


def test_critical_type_error():
    """Test validation with critical type error - should fail"""
    print("\n🔍 Testing critical type error...")

    code_with_type_error = """
from manim import *
import numpy as np

class Scene1(Scene):
    def construct(self):
        # Critical type error - Text without arguments
        text = Text()
        self.play(Write(text))
        
        # Critical type error - Write without arguments
        self.play(Write())
    """

    result = validate_generated_manim_code(code_with_type_error)
    print(f"✅ Critical type error result: {result.is_valid}")
    print(f"   Error type: {result.error_type}")
    print(f"   Errors: {result.errors}")

    return result


def main():
    """Run all validation tests"""
    print("🧪 Improved Validation System Test")
    print("=" * 50)

    # Run all tests
    results = []
    results.append(test_valid_code())
    results.append(test_syntax_error())
    results.append(test_critical_undefined())
    results.append(test_common_patterns())
    results.append(test_critical_type_error())

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

    # Check if the system is working as expected
    expected_valid = [True, False, False, True, False]  # Expected results
    actual_valid = [r.is_valid for r in results]

    correct_predictions = sum(
        1
        for expected, actual in zip(expected_valid, actual_valid)
        if expected == actual
    )
    accuracy = (correct_predictions / total_count) * 100

    print(f"\n🎯 Validation Accuracy: {accuracy:.1f}%")
    print(f"   Expected valid: {expected_valid}")
    print(f"   Actual valid: {actual_valid}")

    if accuracy >= 80:
        print("✅ Validation system is working well!")
    else:
        print("⚠️  Validation system needs improvement")

    print("\n✅ Improved validation system test complete!")


if __name__ == "__main__":
    main()
