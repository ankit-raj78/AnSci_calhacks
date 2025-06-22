#!/usr/bin/env python3
"""
Test script to demonstrate the validation system
Shows how verify.py catches invalid Python code during animation generation
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ansci.verify import (
    validate_generated_manim_code,
    ValidationResult,
    verify_animation_code,
)
from ansci.models import AnsciOutline, AnsciSceneBlock


def test_validation_system():
    """Test the validation system with sample data"""

    print("🧪 Testing Python Code Validation System")
    print("=" * 50)

    # Test 1: Valid Manim code
    print("\n1️⃣ Testing VALID Manim code:")
    valid_code = """
from manim import *
import numpy as np
from functools import wraps

class Scene1(Scene):
    def construct(self):
        title = Text("Hello World", font_size=36, color=BLUE)
        self.play(Write(title))
        self.wait(2)
"""

    result = validate_generated_manim_code(valid_code)
    print(f"✅ Valid code result: {result.is_valid}")
    if result.errors:
        print(f"❌ Errors: {result.errors}")
    if result.warnings:
        print(f"⚠️  Warnings: {result.warnings}")

    # Test 2: Invalid Manim code (syntax error)
    print("\n2️⃣ Testing INVALID Manim code (syntax error):")
    invalid_code = """
from manim import *
import numpy as np
from functools import wraps

class Scene1(Scene):
    def construct(self):
        title = Text("Hello World", font_size=36, color=BLUE
        self.play(Write(title))
        self.wait(2)
"""

    result = validate_generated_manim_code(invalid_code)
    print(f"✅ Invalid code result: {result.is_valid}")
    if result.errors:
        print(f"❌ Errors: {result.errors}")
    if result.warnings:
        print(f"⚠️  Warnings: {result.warnings}")

    # Test 3: Invalid Manim code (missing Scene class)
    print("\n3️⃣ Testing INVALID Manim code (missing Scene class):")
    invalid_code2 = """
from manim import *
import numpy as np
from functools import wraps

def construct(self):
    title = Text("Hello World", font_size=36, color=BLUE)
    self.play(Write(title))
    self.wait(2)
"""

    result = validate_generated_manim_code(invalid_code2)
    print(f"✅ Invalid code result: {result.is_valid}")
    if result.errors:
        print(f"❌ Errors: {result.errors}")
    if result.warnings:
        print(f"⚠️  Warnings: {result.warnings}")

    # Test 4: Invalid Manim code (missing construct method)
    print("\n4️⃣ Testing INVALID Manim code (missing construct method):")
    invalid_code3 = """
from manim import *
import numpy as np
from functools import wraps

class Scene1(Scene):
    def setup(self):
        title = Text("Hello World", font_size=36, color=BLUE)
        self.play(Write(title))
        self.wait(2)
"""

    result = validate_generated_manim_code(invalid_code3)
    print(f"✅ Invalid code result: {result.is_valid}")
    if result.errors:
        print(f"❌ Errors: {result.errors}")
    if result.warnings:
        print(f"⚠️  Warnings: {result.warnings}")

    print("\n" + "=" * 50)
    print("✅ Validation system test completed!")


def test_batch_validation():
    """Test batch validation of multiple scene blocks"""

    print("\n🔗 Testing Batch Validation")
    print("=" * 50)

    # Create sample scene blocks with different validation states
    scene_blocks = [
        AnsciSceneBlock(
            transcript="Valid scene",
            description="A valid Manim scene",
            manim_code="""
from manim import *
class Scene1(Scene):
    def construct(self):
        title = Text("Valid Scene", font_size=36, color=BLUE)
        self.play(Write(title))
        self.wait(2)
""",
        ),
        AnsciSceneBlock(
            transcript="Invalid scene",
            description="An invalid Manim scene",
            manim_code="""
from manim import *
class Scene2(Scene):
    def construct(self):
        title = Text("Invalid Scene", font_size=36, color=BLUE
        self.play(Write(title))
        self.wait(2)
""",
        ),
        AnsciSceneBlock(
            transcript="Missing construct scene",
            description="Scene missing construct method",
            manim_code="""
from manim import *
class Scene3(Scene):
    def setup(self):
        title = Text("Missing Construct", font_size=36, color=BLUE)
        self.play(Write(title))
        self.wait(2)
""",
        ),
    ]

    print("🎬 Testing batch validation of scene blocks...")

    try:
        # This will validate all scene blocks and provide a summary
        is_valid = verify_animation_code(scene_blocks)
        print(
            f"✅ Batch validation completed. Overall result: {'PASS' if is_valid else 'FAIL'}"
        )

    except Exception as e:
        print(f"❌ Error during batch validation test: {e}")


if __name__ == "__main__":
    test_validation_system()
    test_batch_validation()
