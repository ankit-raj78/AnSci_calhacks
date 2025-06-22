# Utils package
"""
AcademIA Render Server Utilities

This package contains core utilities, type definitions, and helper functions
for the AcademIA educational animation generation system.

Key components:
- types: Pydantic models for section-by-section processing
- config: Configuration constants and settings
- logging: Structured logging for processing pipeline
- validation: Comprehensive validation utilities
"""

__version__ = "1.0.0"

# Import core types for easy access
try:
    from .types import (
        # Enums
        ExplanationLevel, ProcessingStatus, SyncConfidenceLevel,
        
        # Core document types
        DocumentMetadata, DocumentSection, ParsedDocument,
        ConceptDependency, ExtractedConcept,
        
        # Context management
        SectionContext, AccumulatedContext, KnowledgeGap,
        
        # Scene planning
        PlannedScene, ScenePlan, VisualElement, SceneTransition,
        
        # Audio & synchronization
        NarrationScript, SyncPoint, TimingMarker, AudioMetadata,
        
        # Animation & rendering
        ManimScript, ManimSyncMarker, SectionAnimation, FinalAnimation,
        RenderMetadata, TransitionData,
        
        # Quality & validation
        SyncValidationResult, QualityMetrics, SyncCorrection,
        
        # Request/Response
        ProcessingRequest, ProcessingResponse, StatusResponse,
        
        # Agent communication
        AgentMessage, AgentResponse,
        
        # Error handling
        ProcessingError,
        
        # Helper functions
        get_confidence_level, calculate_overall_quality, validate_section_order
    )
    
    # Import configuration
    from .config import CONFIG, get_config, validate_config
    
    # Import logging utilities
    from .logging import (
        SectionLogger, ProcessingLogger, APILogger,
        get_logger, get_processing_logger, get_api_logger,
        log_processing_time, log_section_processing,
        system_logger, agent_logger, sync_logger, render_logger, api_logger
    )
    
    # Import validation utilities
    from .validation import (
        ValidationError, ValidationResult,
        validate_pdf_file, validate_explanation_level,
        validate_document_sections, validate_scene_plan,
        validate_narration_script, validate_sync_data,
        validate_manim_script, validate_processing_request,
        validate_and_raise
    )
    
    __all__ = [
        # Core types
        'ExplanationLevel', 'ProcessingStatus', 'SyncConfidenceLevel',
        'DocumentMetadata', 'DocumentSection', 'ParsedDocument',
        'ConceptDependency', 'ExtractedConcept',
        'SectionContext', 'AccumulatedContext', 'KnowledgeGap',
        'PlannedScene', 'ScenePlan', 'VisualElement', 'SceneTransition',
        'NarrationScript', 'SyncPoint', 'TimingMarker', 'AudioMetadata',
        'ManimScript', 'ManimSyncMarker', 'SectionAnimation', 'FinalAnimation',
        'RenderMetadata', 'TransitionData',
        'SyncValidationResult', 'QualityMetrics', 'SyncCorrection',
        'ProcessingRequest', 'ProcessingResponse', 'StatusResponse',
        'AgentMessage', 'AgentResponse', 'ProcessingError',
        
        # Configuration
        'CONFIG', 'get_config', 'validate_config',
        
        # Logging
        'SectionLogger', 'ProcessingLogger', 'APILogger',
        'get_logger', 'get_processing_logger', 'get_api_logger',
        'log_processing_time', 'log_section_processing',
        'system_logger', 'agent_logger', 'sync_logger', 'render_logger', 'api_logger',
        
        # Validation
        'ValidationError', 'ValidationResult',
        'validate_pdf_file', 'validate_explanation_level',
        'validate_document_sections', 'validate_scene_plan',
        'validate_narration_script', 'validate_sync_data',
        'validate_manim_script', 'validate_processing_request',
        'validate_and_raise',
        
        # Helper functions
        'get_confidence_level', 'calculate_overall_quality', 'validate_section_order'
    ]
    
    # Export commonly used constants
    EXPLANATION_LEVELS = ExplanationLevel
    PROCESSING_STATUSES = ProcessingStatus
    SYNC_CONFIDENCE_LEVELS = SyncConfidenceLevel
    
    def create_processing_context(job_id: str, agent_name: str = "system"):
        """Create a complete processing context with logger and validation."""
        logger = get_processing_logger(job_id, agent_name)
        
        return {
            'job_id': job_id,
            'agent_name': agent_name,
            'logger': logger,
            'validate': validate_and_raise,
            'config': CONFIG
        }
    
    def validate_pipeline_stage(stage_name: str, data: dict, context: dict = None):
        """Validate data for a specific pipeline stage."""
        validation_map = {
            'pdf_parsing': validate_processing_request,
            'document_sections': validate_document_sections,
            'scene_planning': validate_scene_plan,
            'transcript_generation': validate_narration_script,
            'manim_generation': validate_manim_script,
            'sync_validation': validate_sync_data
        }
        
        validator = validation_map.get(stage_name)
        if not validator:
            raise ValueError(f"Unknown pipeline stage: {stage_name}")
        
        result = validator(data)
        if context and context.get('logger'):
            if result.errors:
                context['logger'].error(f"Validation failed for {stage_name}", 
                                      errors=result.errors)
            if result.warnings:
                context['logger'].warning(f"Validation warnings for {stage_name}",
                                        warnings=result.warnings)
        
        return result
    
except ImportError as e:
    # Graceful degradation if dependencies are not installed
    import warnings
    warnings.warn(f"Could not import all utilities: {e}")
    
    __all__ = []
    
    # Define minimal types for development
    class ExplanationLevel:
        BEGINNER = "beginner"
        INTERMEDIATE = "intermediate" 
        ADVANCED = "advanced"
    
    class ProcessingStatus:
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"
    
    class SyncConfidenceLevel:
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
    
    # Minimal config
    CONFIG = {
        "explanation_levels": {
            "beginner": {"complexity_max": 3},
            "intermediate": {"complexity_max": 6},
            "advanced": {"complexity_max": 10}
        }
    }
    
    def get_config(key_path: str, default=None):
        """Fallback config getter."""
        return default
    
    def validate_config():
        """Fallback config validator."""
        return {}


# Utility function for quick type checking
def is_valid_explanation_level(level: str) -> bool:
    """Check if explanation level is valid."""
    try:
        return level in [ExplanationLevel.BEGINNER, ExplanationLevel.INTERMEDIATE, ExplanationLevel.ADVANCED]
    except:
        return level in ["beginner", "intermediate", "advanced"]


def get_processing_stages() -> list:
    """Get list of all processing pipeline stages."""
    return [
        "pdf_parsing",
        "section_extraction", 
        "context_analysis",
        "scene_planning",
        "transcript_generation",
        "manim_generation",
        "audio_generation",
        "sync_validation",
        "rendering",
        "quality_check",
        "final_assembly"
    ]


def get_agent_types() -> list:
    """Get list of all agent types in the system."""
    return [
        "pdf_agent",
        "scene_agent", 
        "transcript_agent",
        "animation_agent",
        "context_agent",
        "sync_agent",
        "render_agent",
        "assembly_agent"
    ]
