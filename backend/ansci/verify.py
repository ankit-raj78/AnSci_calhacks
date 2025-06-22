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
    error_type: Optional[str] = None  # Type of error (syntax, runtime, undefined, etc.)
    error_details: Optional[Dict] = None  # Additional error context
    suggestions: List[str] = None  # Suggestions for fixing the errors


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

    def validate_undefined_variables(self, code: str) -> ValidationResult:
        """
        Detect undefined variables and names in the code

        Args:
            code: Python code string to validate

        Returns:
            ValidationResult with undefined variable detection
        """
        errors = []
        warnings = []
        suggestions = []

        try:
            tree = ast.parse(code)

            # Track defined names
            defined_names = set()
            undefined_names = set()

            # Standard Manim imports and names
            manim_names = {
                "Scene",
                "Text",
                "MathTex",
                "Circle",
                "Square",
                "Rectangle",
                "Line",
                "Arrow",
                "Dot",
                "Write",
                "Create",
                "Transform",
                "FadeIn",
                "FadeOut",
                "ReplacementTransform",
                "MoveToTarget",
                "GrowFromCenter",
                "ShrinkToCenter",
                "Rotate",
                "Scale",
                "Shift",
                "BLUE",
                "RED",
                "GREEN",
                "YELLOW",
                "WHITE",
                "BLACK",
                "ORANGE",
                "PURPLE",
                "PINK",
                "GRAY",
                "BROWN",
                "self",
                "np",
                "LayoutManager",
                "AnimationPresets",
                "validate_scene",
                "wraps",
            }

            # Add common Python built-ins
            builtins = {
                "print",
                "len",
                "range",
                "list",
                "dict",
                "set",
                "tuple",
                "str",
                "int",
                "float",
                "bool",
                "True",
                "False",
                "None",
                "abs",
                "min",
                "max",
                "sum",
                "enumerate",
                "zip",
                "map",
                "filter",
                "sorted",
                "reversed",
            }

            defined_names.update(manim_names)
            defined_names.update(builtins)

            class NameVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.undefined = set()
                    self.defined = set()

                def visit_Import(self, node):
                    for alias in node.names:
                        self.defined.add(alias.name.split(".")[0])
                    self.generic_visit(node)

                def visit_ImportFrom(self, node):
                    if node.module:
                        self.defined.add(node.module.split(".")[0])
                    for alias in node.names:
                        self.defined.add(alias.name)
                    self.generic_visit(node)

                def visit_ClassDef(self, node):
                    self.defined.add(node.name)
                    self.generic_visit(node)

                def visit_FunctionDef(self, node):
                    self.defined.add(node.name)
                    # Add function parameters to defined names
                    for arg in node.args.args:
                        self.defined.add(arg.arg)
                    self.generic_visit(node)

                def visit_Assign(self, node):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.defined.add(target.id)
                        elif isinstance(target, ast.Tuple):
                            for elt in target.elts:
                                if isinstance(elt, ast.Name):
                                    self.defined.add(elt.id)
                    self.generic_visit(node)

                def visit_AnnAssign(self, node):
                    if isinstance(node.target, ast.Name):
                        self.defined.add(node.target.id)
                    self.generic_visit(node)

                def visit_Name(self, node):
                    if isinstance(node.ctx, ast.Load) and node.id not in self.defined:
                        self.undefined.add(node.id)
                    self.generic_visit(node)

            visitor = NameVisitor()
            visitor.visit(tree)

            # Check for undefined names, but be more lenient with common patterns
            for name in visitor.undefined:
                if name not in defined_names:
                    # Skip some common patterns that might be false positives
                    if name in ["self", "cls"] or name.startswith("_"):
                        continue
                    errors.append(f"Undefined variable: '{name}'")
                    suggestions.append(
                        f"Define '{name}' or import it if it's a module/class"
                    )

            # Check for common Manim-specific undefined names
            common_manim_errors = {
                "mobject": "Use specific Manim objects like Text, Circle, etc.",
                "animation": "Use specific animations like Write, Create, Transform, etc.",
                "color": "Use predefined colors like BLUE, RED, GREEN, etc.",
                "position": "Use specific positioning like move_to(), shift(), etc.",
                "duration": "Specify animation duration in seconds",
                "rate_func": "Use rate functions like linear, ease_in_out, etc.",
            }

            for name, suggestion in common_manim_errors.items():
                if name in visitor.undefined:
                    warnings.append(f"Common Manim pattern: '{name}' - {suggestion}")

            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                error_type="undefined_variables" if errors else None,
            )

        except SyntaxError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Syntax error prevents undefined variable detection: {e.msg}"],
                warnings=[],
                suggestions=[],
                error_type="syntax_error",
            )

    def validate_type_errors(self, code: str) -> ValidationResult:
        """
        Detect potential type errors and type-related issues

        Args:
            code: Python code string to validate

        Returns:
            ValidationResult with type error detection
        """
        errors = []
        warnings = []
        suggestions = []

        try:
            tree = ast.parse(code)

            class TypeVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.type_errors = []
                    self.type_warnings = []

                def visit_Call(self, node):
                    # Check for common type errors in function calls
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id

                        # Check for common Manim function signature issues
                        if func_name in ["Text", "MathTex"]:
                            if not node.args and not node.keywords:
                                self.type_errors.append(
                                    f"'{func_name}' requires at least one argument"
                                )
                                self.type_warnings.append(
                                    f"'{func_name}' typically needs text content as first argument"
                                )

                        elif func_name in ["Write", "Create", "FadeIn", "FadeOut"]:
                            if not node.args:
                                self.type_errors.append(
                                    f"'{func_name}' requires a mobject argument"
                                )
                                self.type_warnings.append(
                                    f"'{func_name}' needs a Manim object to animate"
                                )

                        elif func_name in ["move_to", "shift", "scale", "rotate"]:
                            if not node.args:
                                self.type_errors.append(
                                    f"'{func_name}' requires position/transformation argument"
                                )
                                self.type_warnings.append(
                                    f"'{func_name}' needs coordinates or transformation parameters"
                                )

                    self.generic_visit(node)

                def visit_BinOp(self, node):
                    # Check for type mismatches in binary operations
                    if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                        # Check if trying to add/subtract incompatible types
                        if isinstance(node.left, ast.Str) and isinstance(
                            node.right, ast.Num
                        ):
                            self.type_warnings.append(
                                "Mixing string and number in arithmetic operation"
                            )
                        elif isinstance(node.left, ast.Num) and isinstance(
                            node.right, ast.Str
                        ):
                            self.type_warnings.append(
                                "Mixing number and string in arithmetic operation"
                            )

                    self.generic_visit(node)

                def visit_Compare(self, node):
                    # Check for comparison type issues
                    for comparator in node.comparators:
                        if isinstance(node.left, ast.Str) and isinstance(
                            comparator, ast.Num
                        ):
                            self.type_warnings.append("Comparing string with number")
                        elif isinstance(node.left, ast.Num) and isinstance(
                            comparator, ast.Str
                        ):
                            self.type_warnings.append("Comparing number with string")

                    self.generic_visit(node)

            visitor = TypeVisitor()
            visitor.visit(tree)

            errors.extend(visitor.type_errors)
            warnings.extend(visitor.type_warnings)

            # Add suggestions for common type errors
            if errors:
                suggestions.extend(
                    [
                        "Check function argument types and order",
                        "Ensure all variables are properly initialized before use",
                        "Verify that objects have the expected methods and attributes",
                    ]
                )

            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                error_type="type_error" if errors else None,
            )

        except SyntaxError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Syntax error prevents type error detection: {e.msg}"],
                warnings=[],
                suggestions=[],
                error_type="syntax_error",
            )

    def validate_runtime_errors(self, code: str) -> ValidationResult:
        """
        Simulate runtime execution to detect potential runtime errors

        Args:
            code: Python code string to validate

        Returns:
            ValidationResult with runtime error detection
        """
        errors = []
        warnings = []
        suggestions = []

        try:
            # Create a safe execution environment
            safe_globals = {
                "__builtins__": {
                    "print": lambda *args: None,
                    "len": len,
                    "range": range,
                    "list": list,
                    "dict": dict,
                    "set": set,
                    "tuple": tuple,
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "True": True,
                    "False": False,
                    "None": None,
                    "abs": abs,
                    "min": min,
                    "max": max,
                    "sum": sum,
                    "enumerate": enumerate,
                    "zip": zip,
                    "map": map,
                    "filter": filter,
                    "sorted": sorted,
                    "reversed": reversed,
                }
            }

            safe_locals = {}

            # Mock Manim classes and functions for safe execution
            class MockScene:
                def __init__(self):
                    self.mobjects = []

                def play(self, *args, **kwargs):
                    pass

                def wait(self, duration=1):
                    pass

                def add(self, *args):
                    pass

                def remove(self, *args):
                    pass

                def clear(self):
                    pass

                def add_sound(self, *args, **kwargs):
                    pass

            class MockText:
                def __init__(self, text="", **kwargs):
                    self.text = text

                def move_to(self, *args):
                    return self

                def shift(self, *args):
                    return self

                def scale(self, *args):
                    return self

                def rotate(self, *args):
                    return self

                def get_width(self):
                    return 1.0

                def get_height(self):
                    return 0.5

            class MockCircle:
                def __init__(self, **kwargs):
                    pass

                def move_to(self, *args):
                    return self

                def get_width(self):
                    return 1.0

                def get_height(self):
                    return 1.0

            # Add mock objects to safe environment
            safe_globals.update(
                {
                    "Scene": MockScene,
                    "Text": MockText,
                    "Circle": MockCircle,
                    "BLUE": "blue",
                    "RED": "red",
                    "GREEN": "green",
                    "YELLOW": "yellow",
                    "WHITE": "white",
                    "BLACK": "black",
                    "Write": lambda obj: None,
                    "Create": lambda obj: None,
                    "FadeIn": lambda obj: None,
                    "FadeOut": lambda obj: None,
                    "Transform": lambda obj1, obj2: None,
                    "ReplacementTransform": lambda obj1, obj2: None,
                    "np": __import__("numpy"),
                    "LayoutManager": type(
                        "LayoutManager", (), {"safe_position": lambda obj, pos: pos}
                    ),
                    "AnimationPresets": type(
                        "AnimationPresets",
                        (),
                        {
                            "FAST": 0.5,
                            "NORMAL": 1.0,
                            "SLOW": 1.5,
                            "TITLE_SIZE": 28,
                            "SUBTITLE_SIZE": 22,
                            "BODY_SIZE": 14,
                        },
                    ),
                    "validate_scene": lambda func: func,
                    "wraps": lambda func: lambda f: f,
                }
            )

            # Try to compile and execute the code in safe environment
            compiled_code = compile(code, "<string>", "exec")

            # Execute in safe environment with timeout
            import signal
            import time
            import threading

            # Use threading-based timeout for Windows compatibility
            def timeout_handler():
                raise TimeoutError("Code execution timed out")

            # Create a timer thread
            timer = threading.Timer(5.0, timeout_handler)

            try:
                timer.start()
                exec(compiled_code, safe_globals, safe_locals)
                timer.cancel()
            except TimeoutError:
                errors.append("Code execution timed out - possible infinite loop")
                suggestions.append("Check for infinite loops or very long operations")
            except Exception as e:
                error_type = type(e).__name__
                errors.append(f"Runtime error: {error_type}: {str(e)}")

                # Provide specific suggestions based on error type
                if error_type == "AttributeError":
                    suggestions.append(
                        "Check that objects have the required methods/attributes"
                    )
                elif error_type == "TypeError":
                    suggestions.append("Check argument types and function signatures")
                elif error_type == "NameError":
                    suggestions.append(
                        "Check that all variables are defined before use"
                    )
                elif error_type == "IndexError":
                    suggestions.append("Check array/list indices are within bounds")
                elif error_type == "KeyError":
                    suggestions.append("Check dictionary keys exist before accessing")
                else:
                    suggestions.append("Review the code logic and error handling")
            finally:
                timer.cancel()

            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                error_type="runtime_error" if errors else None,
            )

        except SyntaxError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Syntax error prevents runtime validation: {e.msg}"],
                warnings=[],
                suggestions=[],
                error_type="syntax_error",
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Runtime validation failed: {str(e)}"],
                warnings=[],
                suggestions=[],
                error_type="validation_error",
            )


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

    # Step 5: Undefined variable detection
    undefined_result = validator.validate_undefined_variables(manim_code)

    # Step 6: Type error detection
    type_result = validator.validate_type_errors(manim_code)

    # Step 7: Runtime error detection
    runtime_result = validator.validate_runtime_errors(manim_code)

    # Combine all results
    all_errors = (
        syntax_result.errors
        + import_result.errors
        + manim_result.errors
        + safety_result.errors
        + undefined_result.errors
        + type_result.errors
        + runtime_result.errors
    )
    all_warnings = (
        syntax_result.warnings
        + import_result.warnings
        + manim_result.warnings
        + safety_result.warnings
        + undefined_result.warnings
        + type_result.warnings
        + runtime_result.warnings
    )

    # Combine all suggestions
    all_suggestions = []
    for result in [
        syntax_result,
        import_result,
        manim_result,
        safety_result,
        undefined_result,
        type_result,
        runtime_result,
    ]:
        if hasattr(result, "suggestions") and result.suggestions:
            all_suggestions.extend(result.suggestions)

    # Determine primary error type
    primary_error_type = None
    if syntax_result.errors:
        primary_error_type = "syntax_error"
    elif undefined_result.errors:
        primary_error_type = "undefined_variables"
    elif type_result.errors:
        primary_error_type = "type_error"
    elif runtime_result.errors:
        primary_error_type = "runtime_error"
    elif import_result.errors:
        primary_error_type = "import_error"
    elif manim_result.errors:
        primary_error_type = "manim_structure_error"

    return ValidationResult(
        is_valid=len(all_errors) == 0,
        errors=all_errors,
        warnings=all_warnings,
        suggestions=all_suggestions,
        scene_name=manim_result.scene_name,
        error_type=primary_error_type,
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
            mode="w", suffix=".py", delete=False, encoding="utf-8"
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


def generate_regeneration_feedback(validation_result: ValidationResult) -> str:
    """
    Generate detailed feedback for code regeneration based on validation errors

    Args:
        validation_result: Validation result with errors and suggestions

    Returns:
        Detailed feedback string for regeneration
    """
    if validation_result.is_valid:
        return "Code validation passed - no regeneration needed."

    feedback = f"Code validation failed with {len(validation_result.errors)} errors.\n"
    feedback += f"Primary error type: {validation_result.error_type or 'unknown'}\n\n"

    feedback += "DETAILED ERROR ANALYSIS:\n"
    feedback += "=" * 40 + "\n"

    for i, error in enumerate(validation_result.errors, 1):
        feedback += f"{i}. {error}\n"

    if validation_result.warnings:
        feedback += "\nWARNINGS:\n"
        feedback += "-" * 20 + "\n"
        for warning in validation_result.warnings:
            feedback += f"⚠️  {warning}\n"

    if validation_result.suggestions:
        feedback += "\nSUGGESTIONS FOR FIXES:\n"
        feedback += "-" * 25 + "\n"
        for suggestion in validation_result.suggestions:
            feedback += f"💡 {suggestion}\n"

    # Add specific guidance based on error type
    feedback += "\nSPECIFIC GUIDANCE:\n"
    feedback += "-" * 20 + "\n"

    if validation_result.error_type == "syntax_error":
        feedback += "🔧 SYNTAX ERRORS:\n"
        feedback += (
            "- Check all parentheses, brackets, and quotes are properly matched\n"
        )
        feedback += "- Verify proper indentation throughout the code\n"
        feedback += "- Ensure all statements end properly\n"
        feedback += "- Check for missing colons after function/class definitions\n"

    elif validation_result.error_type == "undefined_variables":
        feedback += "🔧 UNDEFINED VARIABLES:\n"
        feedback += "- Define all variables before using them\n"
        feedback += "- Import required modules and classes\n"
        feedback += "- Use proper Manim object names (Text, Circle, etc.)\n"
        feedback += "- Check spelling of variable and function names\n"

    elif validation_result.error_type == "type_error":
        feedback += "🔧 TYPE ERRORS:\n"
        feedback += "- Check function argument types and order\n"
        feedback += "- Ensure objects have required methods/attributes\n"
        feedback += "- Verify variable types before operations\n"
        feedback += "- Use proper Manim function signatures\n"

    elif validation_result.error_type == "runtime_error":
        feedback += "🔧 RUNTIME ERRORS:\n"
        feedback += "- Check for infinite loops or long operations\n"
        feedback += "- Verify object methods exist and are called correctly\n"
        feedback += "- Ensure proper error handling\n"
        feedback += "- Check for division by zero or invalid operations\n"

    elif validation_result.error_type == "import_error":
        feedback += "🔧 IMPORT ERRORS:\n"
        feedback += "- Use only basic Manim imports: 'from manim import *'\n"
        feedback += "- Avoid external libraries like librosa, scipy, etc.\n"
        feedback += "- Include: 'import numpy as np', 'from functools import wraps'\n"

    elif validation_result.error_type == "manim_structure_error":
        feedback += "🔧 MANIM STRUCTURE ERRORS:\n"
        feedback += "- Define a class that inherits from Scene\n"
        feedback += "- Include a construct(self) method\n"
        feedback += "- Use proper Manim animation syntax\n"
        feedback += "- Follow Manim best practices for scene structure\n"

    feedback += "\nREGENERATION INSTRUCTIONS:\n"
    feedback += "-" * 25 + "\n"
    feedback += "1. Fix the identified errors above\n"
    feedback += "2. Ensure proper Manim scene structure\n"
    feedback += "3. Use only basic Manim imports and functions\n"
    feedback += "4. Test the code logic before generating\n"
    feedback += "5. Follow the suggestions provided above\n"

    return feedback


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
                print(f"  Error type: {result.error_type or 'unknown'}")
                for error in result.errors:
                    print(f"  - {error}")

                # Print suggestions if available
                if hasattr(result, "suggestions") and result.suggestions:
                    print(f"  Suggestions:")
                    for suggestion in result.suggestions[
                        :3
                    ]:  # Limit to first 3 suggestions
                        print(f"    💡 {suggestion}")

    # Print warnings
    all_warnings = []
    for result in validation_results:
        all_warnings.extend(result.warnings)

    if all_warnings:
        print(f"\n⚠️  WARNINGS ({len(all_warnings)} total):")
        for warning in all_warnings[:5]:  # Limit to first 5 warnings
            print(f"  - {warning}")
        if len(all_warnings) > 5:
            print(f"  ... and {len(all_warnings) - 5} more warnings")

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
    print("✅ Undefined variable detection")
    print("✅ Type error detection")
    print("✅ Runtime error detection")
    print("✅ Comprehensive testing framework")
    print("\nReady for animation code validation! 🚀")
