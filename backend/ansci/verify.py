"""
Python Code Validation Module
Validates that generated Manim code from animate.py is syntactically correct and executable
"""

import ast
import sys
import traceback
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import tempfile
import subprocess
import importlib.util
from dataclasses import dataclass

from .models import AnsciOutline, AnsciSceneBlock, AnsciAnimation


@dataclass
class ValidationResult:
    """Result of code validation"""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    scene_name: Optional[str] = None
    line_number: Optional[int] = None


class PythonCodeValidator:
    """Validates Python code for syntax and basic execution"""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_syntax(self, code: str) -> ValidationResult:
        """
        Validate Python syntax using ast.parse

        Args:
            code: Python code string to validate

        Returns:
            ValidationResult with validation status and any errors
        """
        try:
            # Parse the code to check syntax
            ast.parse(code)
            return ValidationResult(is_valid=True, errors=[], warnings=[])
        except SyntaxError as e:
            error_msg = f"Syntax Error: {e.msg} at line {e.lineno}"
            return ValidationResult(
                is_valid=False, errors=[error_msg], warnings=[], line_number=e.lineno
            )
        except Exception as e:
            error_msg = f"Unexpected error during syntax validation: {str(e)}"
            return ValidationResult(is_valid=False, errors=[error_msg], warnings=[])

    def validate_imports(self, code: str) -> ValidationResult:
        """
        Validate that imports are valid and accessible

        Args:
            code: Python code string to validate

        Returns:
            ValidationResult with import validation status
        """
        errors = []
        warnings = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        try:
                            importlib.import_module(alias.name)
                        except ImportError:
                            errors.append(f"Import error: Cannot import '{alias.name}'")
                        except Exception as e:
                            warnings.append(
                                f"Warning importing '{alias.name}': {str(e)}"
                            )

                elif isinstance(node, ast.ImportFrom):
                    try:
                        if node.module:
                            importlib.import_module(node.module)
                    except ImportError:
                        errors.append(
                            f"Import error: Cannot import from '{node.module}'"
                        )
                    except Exception as e:
                        warnings.append(
                            f"Warning importing from '{node.module}': {str(e)}"
                        )

            return ValidationResult(
                is_valid=len(errors) == 0, errors=errors, warnings=warnings
            )

        except SyntaxError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Syntax error prevents import validation: {e.msg}"],
                warnings=[],
            )

    def validate_manim_specific(self, code: str) -> ValidationResult:
        """
        Validate Manim-specific requirements

        Args:
            code: Python code string to validate

        Returns:
            ValidationResult with Manim validation status
        """
        errors = []
        warnings = []

        try:
            tree = ast.parse(code)

            # Check for required Manim components
            has_scene_class = False
            has_construct_method = False
            scene_name = None

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's a Scene class
                    if any(
                        base.id == "Scene" for base in node.bases if hasattr(base, "id")
                    ):
                        has_scene_class = True
                        scene_name = node.name

                        # Check for construct method
                        for item in node.body:
                            if (
                                isinstance(item, ast.FunctionDef)
                                and item.name == "construct"
                            ):
                                has_construct_method = True
                                break

            if not has_scene_class:
                errors.append(
                    "Missing Scene class - code must define a class that inherits from Scene"
                )

            if not has_construct_method:
                errors.append(
                    "Missing construct() method - Scene class must have a construct method"
                )

            if not has_scene_class or not has_construct_method:
                return ValidationResult(
                    is_valid=False,
                    errors=errors,
                    warnings=warnings,
                    scene_name=scene_name,
                )

            # Check for common Manim issues
            code_lower = code.lower()
            if "manim" not in code_lower and "scene" not in code_lower:
                warnings.append(
                    "Code may not be Manim-specific - missing Manim imports or Scene class"
                )

            return ValidationResult(
                is_valid=True, errors=errors, warnings=warnings, scene_name=scene_name
            )

        except SyntaxError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Syntax error prevents Manim validation: {e.msg}"],
                warnings=[],
            )

    def validate_execution_safety(self, code: str) -> ValidationResult:
        """
        Validate code for safe execution (no dangerous operations)

        Args:
            code: Python code string to validate

        Returns:
            ValidationResult with safety validation status
        """
        errors = []
        warnings = []

        # Check for potentially dangerous operations
        dangerous_patterns = [
            "exec(",
            "eval(",
            "os.system(",
            "subprocess.call(",
            "subprocess.run(",
            "__import__(",
            "open(",
            "file(",
        ]

        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                warnings.append(f"Potentially unsafe operation detected: {pattern}")

        # Check for infinite loops or long-running operations
        if "while True:" in code or "while 1:" in code:
            warnings.append("Infinite loop detected - may cause execution to hang")

        return ValidationResult(is_valid=True, errors=errors, warnings=warnings)


def validate_generated_manim_code(manim_code: str) -> ValidationResult:
    """
    Comprehensive validation of generated Manim code

    Args:
        manim_code: The Manim code string to validate

    Returns:
        ValidationResult with comprehensive validation status
    """
    validator = PythonCodeValidator()

    # Step 1: Syntax validation
    syntax_result = validator.validate_syntax(manim_code)
    if not syntax_result.is_valid:
        return syntax_result

    # Step 2: Import validation
    import_result = validator.validate_imports(manim_code)

    # Step 3: Manim-specific validation
    manim_result = validator.validate_manim_specific(manim_code)

    # Step 4: Execution safety validation
    safety_result = validator.validate_execution_safety(manim_code)

    # Combine all results
    all_errors = (
        syntax_result.errors
        + import_result.errors
        + manim_result.errors
        + safety_result.errors
    )
    all_warnings = (
        syntax_result.warnings
        + import_result.warnings
        + manim_result.warnings
        + safety_result.warnings
    )

    return ValidationResult(
        is_valid=len(all_errors) == 0,
        errors=all_errors,
        warnings=all_warnings,
        scene_name=manim_result.scene_name,
    )


def validate_animation_from_outline(
    scene_blocks: List[AnsciSceneBlock],
) -> List[ValidationResult]:
    """
    Validate all generated animation code from scene blocks

    Args:
        scene_blocks: List of scene blocks to validate

    Returns:
        List of ValidationResult for each scene block
    """
    validation_results = []

    print(f"🔍 Validating {len(scene_blocks)} scene blocks")

    for i, scene_block in enumerate(scene_blocks):
        print(f"🔍 Validating Scene {i+1}/{len(scene_blocks)}...")

        # Validate the Manim code
        validation_result = validate_generated_manim_code(scene_block.manim_code)
        validation_result.scene_name = f"Scene{i+1}"

        # Add scene-specific information
        if validation_result.is_valid:
            print(f"✅ Scene {i+1} validation passed")
        else:
            print(f"❌ Scene {i+1} validation failed:")
            for error in validation_result.errors:
                print(f"   - {error}")

        validation_results.append(validation_result)

    return validation_results


def test_manim_code_execution(
    manim_code: str, scene_name: str = "TestScene"
) -> ValidationResult:
    """
    Test if Manim code can be executed (without actually rendering)

    Args:
        manim_code: The Manim code to test
        scene_name: Name of the scene to test

    Returns:
        ValidationResult with execution test results
    """
    try:
        # Create a temporary file with the code
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as temp_file:
            temp_file.write(manim_code)
            temp_file_path = temp_file.name

        # Try to import the module (this tests basic execution)
        spec = importlib.util.spec_from_file_location(scene_name, temp_file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check if the scene class exists
            scene_class = getattr(module, scene_name, None)
            if scene_class:
                return ValidationResult(
                    is_valid=True,
                    errors=[],
                    warnings=["Code executed successfully in test environment"],
                    scene_name=scene_name,
                )
            else:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Scene class '{scene_name}' not found in generated code"],
                    warnings=[],
                    scene_name=scene_name,
                )
        else:
            return ValidationResult(
                is_valid=False,
                errors=["Failed to create module spec for execution testing"],
                warnings=[],
                scene_name=scene_name,
            )

    except Exception as e:
        return ValidationResult(
            is_valid=False,
            errors=[f"Execution test failed: {str(e)}"],
            warnings=[],
            scene_name=scene_name,
        )

    finally:
        # Clean up temporary file
        try:
            Path(temp_file_path).unlink()
        except:
            pass


def print_validation_summary(validation_results: List[ValidationResult]) -> None:
    """
    Print a summary of validation results

    Args:
        validation_results: List of validation results to summarize
    """
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    total_scenes = len(validation_results)
    valid_scenes = sum(1 for result in validation_results if result.is_valid)
    invalid_scenes = total_scenes - valid_scenes

    print(f"Total scenes: {total_scenes}")
    print(f"Valid scenes: {valid_scenes}")
    print(f"Invalid scenes: {invalid_scenes}")
    print(
        f"Success rate: {(valid_scenes/total_scenes)*100:.1f}%"
        if total_scenes > 0
        else "N/A"
    )

    if invalid_scenes > 0:
        print("\n❌ VALIDATION ERRORS:")
        for i, result in enumerate(validation_results):
            if not result.is_valid:
                print(f"\nScene {i+1} ({result.scene_name or 'Unknown'}):")
                for error in result.errors:
                    print(f"  - {error}")

    # Print warnings
    all_warnings = []
    for result in validation_results:
        all_warnings.extend(result.warnings)

    if all_warnings:
        print(f"\n⚠️  WARNINGS ({len(all_warnings)} total):")
        for warning in all_warnings:
            print(f"  - {warning}")

    print("=" * 60)


# Main validation function for external use
def verify_animation_code(scene_blocks: List[AnsciSceneBlock]) -> bool:
    """
    Main verification function - validates all generated animation code

    Args:
        scene_blocks: List of scene blocks to validate

    Returns:
        True if all code is valid, False otherwise
    """
    print("🔍 Starting comprehensive animation code validation...")

    # Validate all generated code
    validation_results = validate_animation_from_outline(scene_blocks)

    # Print summary
    print_validation_summary(validation_results)

    # Return overall success status
    all_valid = all(result.is_valid for result in validation_results)

    if all_valid:
        print("✅ All animation code validation passed!")
    else:
        print("❌ Some animation code validation failed!")

    return all_valid


if __name__ == "__main__":
    print("🔍 Python Code Validation Module")
    print("=" * 40)
    print("✅ Syntax validation")
    print("✅ Import validation")
    print("✅ Manim-specific validation")
    print("✅ Execution safety validation")
    print("✅ Comprehensive testing framework")
    print("\nReady for animation code validation! 🚀")
