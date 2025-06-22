"""
Validation utilities for AcademIA render server.
Provides comprehensive validation for section-by-section processing pipeline.
"""

import re
import mimetypes
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime

try:
    from .types import (
        DocumentSection, ParsedDocument, SectionContext, 
        PlannedScene, NarrationScript, ManimScript,
        SyncValidationResult, QualityMetrics, ExplanationLevel,
        ProcessingStatus, SyncConfidenceLevel
    )
    from .config import (
        MAX_SECTIONS_PER_DOCUMENT, MAX_SECTION_LENGTH, MIN_SECTION_LENGTH,
        MAX_PDF_SIZE, SYNC_CONFIDENCE_THRESHOLD, MIN_SYNC_QUALITY,
        MIN_VISUAL_QUALITY, MIN_AUDIO_QUALITY, MIN_OVERALL_QUALITY
    )
except ImportError:
    # Fallback for when pydantic is not available
    pass


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(message)


class ValidationResult:
    """Result of validation with errors and warnings."""
    
    def __init__(self):
        self.is_valid = True
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
    
    def add_error(self, message: str, field: str = None, value: Any = None):
        """Add a validation error."""
        self.is_valid = False
        self.errors.append({
            "message": message,
            "field": field,
            "value": value,
            "type": "error"
        })
    
    def add_warning(self, message: str, field: str = None, value: Any = None):
        """Add a validation warning."""
        self.warnings.append({
            "message": message,
            "field": field,
            "value": value,
            "type": "warning"
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings
        }


# ============================================================================
# File Validation
# ============================================================================

def validate_pdf_file(file_path: Union[str, Path]) -> ValidationResult:
    """Validate PDF file for processing."""
    result = ValidationResult()
    file_path = Path(file_path)
    
    # Check file exists
    if not file_path.exists():
        result.add_error(f"File does not exist: {file_path}", "file_path")
        return result
    
    # Check file size
    file_size = file_path.stat().st_size
    if file_size > MAX_PDF_SIZE:
        result.add_error(
            f"File too large: {file_size} bytes (max: {MAX_PDF_SIZE})",
            "file_size",
            file_size
        )
    
    if file_size == 0:
        result.add_error("File is empty", "file_size", file_size)
        return result
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type != "application/pdf":
        result.add_error(
            f"Invalid file type: {mime_type} (expected: application/pdf)",
            "mime_type",
            mime_type
        )
    
    # Check file extension
    if file_path.suffix.lower() != ".pdf":
        result.add_warning(
            f"Unexpected file extension: {file_path.suffix}",
            "file_extension",
            file_path.suffix
        )
    
    return result


def validate_explanation_level(level: str) -> ValidationResult:
    """Validate explanation level."""
    result = ValidationResult()
    
    valid_levels = ["beginner", "intermediate", "advanced"]
    if level not in valid_levels:
        result.add_error(
            f"Invalid explanation level: {level} (valid: {valid_levels})",
            "explanation_level",
            level
        )
    
    return result


# ============================================================================
# Document Structure Validation
# ============================================================================

def validate_document_sections(sections: List[Dict[str, Any]]) -> ValidationResult:
    """Validate document sections structure."""
    result = ValidationResult()
    
    # Check number of sections
    if len(sections) > MAX_SECTIONS_PER_DOCUMENT:
        result.add_error(
            f"Too many sections: {len(sections)} (max: {MAX_SECTIONS_PER_DOCUMENT})",
            "section_count",
            len(sections)
        )
    
    if len(sections) == 0:
        result.add_error("No sections found in document", "section_count", 0)
        return result
    
    section_ids = set()
    for i, section in enumerate(sections):
        section_result = validate_single_section(section, i)
        result.errors.extend(section_result.errors)
        result.warnings.extend(section_result.warnings)
        if not section_result.is_valid:
            result.is_valid = False
        
        # Check for duplicate section IDs
        section_id = section.get("section_id")
        if section_id in section_ids:
            result.add_error(
                f"Duplicate section ID: {section_id}",
                "section_id",
                section_id
            )
        section_ids.add(section_id)
    
    return result


def validate_single_section(section: Dict[str, Any], index: int) -> ValidationResult:
    """Validate a single document section."""
    result = ValidationResult()
    
    # Required fields
    required_fields = ["section_id", "title", "content_text", "section_number"]
    for field in required_fields:
        if field not in section or not section[field]:
            result.add_error(
                f"Missing required field: {field}",
                f"section[{index}].{field}"
            )
    
    # Validate content length
    content = section.get("content_text", "")
    if len(content) < MIN_SECTION_LENGTH:
        result.add_warning(
            f"Section content too short: {len(content)} chars (min: {MIN_SECTION_LENGTH})",
            f"section[{index}].content_length",
            len(content)
        )
    
    if len(content) > MAX_SECTION_LENGTH:
        result.add_error(
            f"Section content too long: {len(content)} chars (max: {MAX_SECTION_LENGTH})",
            f"section[{index}].content_length",
            len(content)
        )
    
    # Validate section number
    section_num = section.get("section_number")
    if not isinstance(section_num, int) or section_num < 0:
        result.add_error(
            f"Invalid section number: {section_num}",
            f"section[{index}].section_number",
            section_num
        )
    
    # Validate complexity level
    complexity = section.get("complexity_level")
    if complexity is not None:
        if not isinstance(complexity, int) or complexity < 1 or complexity > 10:
            result.add_error(
                f"Invalid complexity level: {complexity} (must be 1-10)",
                f"section[{index}].complexity_level",
                complexity
            )
    
    return result


def validate_section_dependencies(sections: List[Dict[str, Any]]) -> ValidationResult:
    """Validate section dependency structure."""
    result = ValidationResult()
    
    section_ids = {s.get("section_id") for s in sections}
    section_numbers = {s.get("section_id"): s.get("section_number") for s in sections}
    
    for i, section in enumerate(sections):
        section_id = section.get("section_id")
        dependencies = section.get("dependencies", [])
        
        for dep_id in dependencies:
            # Check dependency exists
            if dep_id not in section_ids:
                result.add_error(
                    f"Unknown dependency: {dep_id}",
                    f"section[{i}].dependencies",
                    dep_id
                )
                continue
            
            # Check dependency order (dependency should come before current section)
            dep_number = section_numbers.get(dep_id)
            current_number = section_numbers.get(section_id)
            
            if dep_number and current_number and dep_number >= current_number:
                result.add_warning(
                    f"Dependency {dep_id} comes after or at same position as {section_id}",
                    f"section[{i}].dependencies",
                    {"dependency": dep_id, "order_issue": True}
                )
    
    return result


# ============================================================================
# Scene Plan Validation
# ============================================================================

def validate_scene_plan(scene_plan: Dict[str, Any]) -> ValidationResult:
    """Validate scene plan structure."""
    result = ValidationResult()
    
    # Required fields
    required_fields = ["section_id", "scenes", "total_estimated_duration"]
    for field in required_fields:
        if field not in scene_plan:
            result.add_error(f"Missing required field: {field}", field)
    
    # Validate scenes
    scenes = scene_plan.get("scenes", [])
    if not scenes:
        result.add_error("No scenes in scene plan", "scenes")
    else:
        total_duration = 0
        for i, scene in enumerate(scenes):
            scene_result = validate_single_scene(scene, i)
            result.errors.extend(scene_result.errors)
            result.warnings.extend(scene_result.warnings)
            if not scene_result.is_valid:
                result.is_valid = False
            
            total_duration += scene.get("timing_estimate", 0)
        
        # Check total duration consistency
        stated_duration = scene_plan.get("total_estimated_duration", 0)
        if abs(total_duration - stated_duration) > 1.0:  # 1 second tolerance
            result.add_warning(
                f"Duration mismatch: scenes={total_duration}s, stated={stated_duration}s",
                "total_estimated_duration"
            )
    
    return result


def validate_single_scene(scene: Dict[str, Any], index: int) -> ValidationResult:
    """Validate a single scene."""
    result = ValidationResult()
    
    # Required fields
    required_fields = ["scene_id", "title", "visual_elements", "timing_estimate"]
    for field in required_fields:
        if field not in scene:
            result.add_error(
                f"Missing required field: {field}",
                f"scene[{index}].{field}"
            )
    
    # Validate timing
    timing = scene.get("timing_estimate")
    if timing is not None:
        if not isinstance(timing, (int, float)) or timing <= 0:
            result.add_error(
                f"Invalid timing estimate: {timing}",
                f"scene[{index}].timing_estimate",
                timing
            )
        elif timing > 60:  # Warn for very long scenes
            result.add_warning(
                f"Very long scene: {timing}s",
                f"scene[{index}].timing_estimate",
                timing
            )
    
    # Validate visual elements
    visual_elements = scene.get("visual_elements", [])
    if not visual_elements:
        result.add_warning(
            "Scene has no visual elements",
            f"scene[{index}].visual_elements"
        )
    
    return result


# ============================================================================
# Audio & Transcript Validation
# ============================================================================

def validate_narration_script(script: Dict[str, Any]) -> ValidationResult:
    """Validate narration script."""
    result = ValidationResult()
    
    # Required fields
    required_fields = ["section_id", "script_text", "estimated_duration"]
    for field in required_fields:
        if field not in script:
            result.add_error(f"Missing required field: {field}", field)
    
    # Validate script content
    script_text = script.get("script_text", "")
    if not script_text.strip():
        result.add_error("Empty script text", "script_text")
    elif len(script_text) < 50:
        result.add_warning(
            f"Very short script: {len(script_text)} chars",
            "script_text",
            len(script_text)
        )
    
    # Validate timing markers
    timing_markers = script.get("timing_markers", [])
    if timing_markers:
        previous_timestamp = -1
        for i, marker in enumerate(timing_markers):
            if not isinstance(marker, dict):
                result.add_error(
                    f"Invalid timing marker format",
                    f"timing_markers[{i}]"
                )
                continue
            
            timestamp = marker.get("timestamp")
            if timestamp is None:
                result.add_error(
                    f"Missing timestamp in timing marker",
                    f"timing_markers[{i}].timestamp"
                )
            elif timestamp <= previous_timestamp:
                result.add_error(
                    f"Non-sequential timestamp: {timestamp} <= {previous_timestamp}",
                    f"timing_markers[{i}].timestamp"
                )
            
            previous_timestamp = timestamp
    
    return result


# ============================================================================
# Synchronization Validation
# ============================================================================

def validate_sync_data(sync_data: Dict[str, Any]) -> ValidationResult:
    """Validate synchronization data."""
    result = ValidationResult()
    
    # Required fields
    required_fields = ["sync_confidence", "validation_passed"]
    for field in required_fields:
        if field not in sync_data:
            result.add_error(f"Missing required field: {field}", field)
    
    # Validate confidence score
    confidence = sync_data.get("sync_confidence")
    if confidence is not None:
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            result.add_error(
                f"Invalid confidence score: {confidence} (must be 0-1)",
                "sync_confidence",
                confidence
            )
        elif confidence < SYNC_CONFIDENCE_THRESHOLD:
            result.add_warning(
                f"Low sync confidence: {confidence} (threshold: {SYNC_CONFIDENCE_THRESHOLD})",
                "sync_confidence",
                confidence
            )
    
    # Validate timing drift
    timing_drift = sync_data.get("timing_drift")
    if timing_drift is not None:
        if timing_drift < 0:
            result.add_error(
                f"Invalid timing drift: {timing_drift} (must be >= 0)",
                "timing_drift",
                timing_drift
            )
        elif timing_drift > 0.5:  # More than 500ms drift
            result.add_warning(
                f"High timing drift: {timing_drift}s",
                "timing_drift",
                timing_drift
            )
    
    return result


def validate_quality_metrics(metrics: Dict[str, Any]) -> ValidationResult:
    """Validate quality metrics."""
    result = ValidationResult()
    
    quality_fields = [
        "visual_quality", "audio_quality", "sync_quality", 
        "educational_effectiveness", "overall_score"
    ]
    
    for field in quality_fields:
        value = metrics.get(field)
        if value is not None:
            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                result.add_error(
                    f"Invalid {field}: {value} (must be 0-1)",
                    field,
                    value
                )
    
    # Check minimum quality thresholds
    thresholds = {
        "visual_quality": MIN_VISUAL_QUALITY,
        "audio_quality": MIN_AUDIO_QUALITY,
        "sync_quality": MIN_SYNC_QUALITY,
        "overall_score": MIN_OVERALL_QUALITY
    }
    
    for field, threshold in thresholds.items():
        value = metrics.get(field)
        if value is not None and value < threshold:
            result.add_warning(
                f"Quality below threshold: {field}={value} (min: {threshold})",
                field,
                value
            )
    
    return result


# ============================================================================
# Manim Script Validation
# ============================================================================

def validate_manim_script(script: Dict[str, Any]) -> ValidationResult:
    """Validate Manim script structure."""
    result = ValidationResult()
    
    # Required fields
    required_fields = ["section_id", "script_content", "class_name"]
    for field in required_fields:
        if field not in script:
            result.add_error(f"Missing required field: {field}", field)
    
    # Validate script content
    script_content = script.get("script_content", "")
    if not script_content.strip():
        result.add_error("Empty script content", "script_content")
    else:
        # Basic Python syntax checks
        if not _validate_python_syntax(script_content):
            result.add_error("Invalid Python syntax in script", "script_content")
        
        # Check for required Manim imports
        if "from manim import" not in script_content and "import manim" not in script_content:
            result.add_warning("No Manim imports found", "script_content")
        
        # Check for class definition
        class_name = script.get("class_name", "")
        if class_name and class_name not in script_content:
            result.add_error(
                f"Class {class_name} not found in script",
                "class_name",
                class_name
            )
    
    return result


def _validate_python_syntax(code: str) -> bool:
    """Check if Python code has valid syntax."""
    try:
        compile(code, "<string>", "exec")
        return True
    except SyntaxError:
        return False


# ============================================================================
# Context Validation
# ============================================================================

def validate_section_context(context: Dict[str, Any]) -> ValidationResult:
    """Validate section context data."""
    result = ValidationResult()
    
    # Required fields
    required_fields = ["section_id", "document_id", "section_order"]
    for field in required_fields:
        if field not in context:
            result.add_error(f"Missing required field: {field}", field)
    
    # Validate section order
    section_order = context.get("section_order")
    if section_order is not None:
        if not isinstance(section_order, int) or section_order < 0:
            result.add_error(
                f"Invalid section order: {section_order}",
                "section_order",
                section_order
            )
    
    # Validate accumulated context
    accumulated = context.get("accumulated_context", {})
    if accumulated:
        covered_concepts = accumulated.get("covered_concepts", [])
        if not isinstance(covered_concepts, list):
            result.add_error(
                "covered_concepts must be a list",
                "accumulated_context.covered_concepts"
            )
        
        cumulative_duration = accumulated.get("cumulative_duration", 0)
        if not isinstance(cumulative_duration, (int, float)) or cumulative_duration < 0:
            result.add_error(
                f"Invalid cumulative duration: {cumulative_duration}",
                "accumulated_context.cumulative_duration",
                cumulative_duration
            )
    
    return result


# ============================================================================
# Processing Pipeline Validation
# ============================================================================

def validate_processing_request(request: Dict[str, Any]) -> ValidationResult:
    """Validate processing request."""
    result = ValidationResult()
    
    # Required fields
    required_fields = ["document_id", "pdf_file_path", "explanation_level"]
    for field in required_fields:
        if field not in request:
            result.add_error(f"Missing required field: {field}", field)
    
    # Validate file path
    pdf_path = request.get("pdf_file_path")
    if pdf_path:
        file_result = validate_pdf_file(pdf_path)
        result.errors.extend(file_result.errors)
        result.warnings.extend(file_result.warnings)
        if not file_result.is_valid:
            result.is_valid = False
    
    # Validate explanation level
    level = request.get("explanation_level")
    if level:
        level_result = validate_explanation_level(level)
        result.errors.extend(level_result.errors)
        result.warnings.extend(level_result.warnings)
        if not level_result.is_valid:
            result.is_valid = False
    
    return result


def validate_complete_pipeline_output(output: Dict[str, Any]) -> ValidationResult:
    """Validate complete pipeline output."""
    result = ValidationResult()
    
    # Required fields
    required_fields = ["document_id", "final_video_path", "section_animations"]
    for field in required_fields:
        if field not in output:
            result.add_error(f"Missing required field: {field}", field)
    
    # Validate section animations
    section_animations = output.get("section_animations", [])
    if not section_animations:
        result.add_error("No section animations found", "section_animations")
    else:
        for i, animation in enumerate(section_animations):
            anim_result = validate_section_animation(animation, i)
            result.errors.extend(anim_result.errors)
            result.warnings.extend(anim_result.warnings)
            if not anim_result.is_valid:
                result.is_valid = False
    
    # Validate final video path
    final_video = output.get("final_video_path")
    if final_video and not Path(final_video).exists():
        result.add_error(
            f"Final video file does not exist: {final_video}",
            "final_video_path",
            final_video
        )
    
    return result


def validate_section_animation(animation: Dict[str, Any], index: int) -> ValidationResult:
    """Validate section animation output."""
    result = ValidationResult()
    
    # Required fields
    required_fields = ["section_id", "video_file_path", "duration"]
    for field in required_fields:
        if field not in animation:
            result.add_error(
                f"Missing required field: {field}",
                f"section_animations[{index}].{field}"
            )
    
    # Validate file paths
    video_path = animation.get("video_file_path")
    if video_path and not Path(video_path).exists():
        result.add_error(
            f"Video file does not exist: {video_path}",
            f"section_animations[{index}].video_file_path",
            video_path
        )
    
    # Validate duration
    duration = animation.get("duration")
    if duration is not None:
        if not isinstance(duration, (int, float)) or duration <= 0:
            result.add_error(
                f"Invalid duration: {duration}",
                f"section_animations[{index}].duration",
                duration
            )
    
    return result


# ============================================================================
# Utility Functions
# ============================================================================

def validate_and_raise(validation_result: ValidationResult, context: str = ""):
    """Raise ValidationError if validation failed."""
    if not validation_result.is_valid:
        error_messages = [error["message"] for error in validation_result.errors]
        message = f"Validation failed{f' for {context}' if context else ''}: {'; '.join(error_messages)}"
        raise ValidationError(message)


def get_validation_summary(results: List[ValidationResult]) -> Dict[str, Any]:
    """Get summary of multiple validation results."""
    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)
    all_valid = all(r.is_valid for r in results)
    
    return {
        "all_valid": all_valid,
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "validation_count": len(results),
        "success_rate": sum(1 for r in results if r.is_valid) / len(results) if results else 0
    }


# Export main functions
__all__ = [
    'ValidationError', 'ValidationResult',
    'validate_pdf_file', 'validate_explanation_level',
    'validate_document_sections', 'validate_section_dependencies',
    'validate_scene_plan', 'validate_narration_script',
    'validate_sync_data', 'validate_quality_metrics',
    'validate_manim_script', 'validate_section_context',
    'validate_processing_request', 'validate_complete_pipeline_output',
    'validate_and_raise', 'get_validation_summary'
]
