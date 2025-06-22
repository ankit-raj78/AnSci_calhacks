"""
Pydantic type definitions for AcademIA system.
Based on the architecture diagrams and section-by-section processing pipeline.
"""

from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class ExplanationLevel(str, Enum):
    """User explanation level preference"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ProcessingStatus(str, Enum):
    """Processing status for various components"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATING = "validating"
    CORRECTING = "correcting"


class SyncConfidenceLevel(str, Enum):
    """Audio-visual synchronization confidence levels"""
    LOW = "low"          # < 0.8
    MEDIUM = "medium"    # 0.8 - 0.95
    HIGH = "high"        # > 0.95


# ============================================================================
# Core Document Types
# ============================================================================

class DocumentMetadata(BaseModel):
    """Document metadata after initial upload"""
    title: str
    file_path: str
    file_size: int
    mime_type: str = "application/pdf"
    upload_timestamp: datetime
    user_id: str
    explanation_level: ExplanationLevel


class ConceptDependency(BaseModel):
    """Represents dependency relationships between concepts"""
    concept_id: str
    depends_on: List[str] = Field(default_factory=list)
    dependency_type: Literal["prerequisite", "builds_on", "references"] = "prerequisite"
    strength: float = Field(ge=0.0, le=1.0, description="Dependency strength 0-1")


class ExtractedConcept(BaseModel):
    """Individual concept extracted from a section"""
    concept_id: str
    name: str
    description: str
    complexity_level: int = Field(ge=1, le=10)
    mathematical_content: bool = False
    visual_elements: List[str] = Field(default_factory=list)
    dependencies: List[ConceptDependency] = Field(default_factory=list)


class DocumentSection(BaseModel):
    """Represents a parsed section of the document"""
    section_id: str
    section_number: int
    title: str
    content_text: str
    explanation_level: ExplanationLevel
    complexity_level: int = Field(ge=1, le=10)
    concepts: List[ExtractedConcept] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list, description="Section IDs this depends on")
    prerequisite_sections: List[str] = Field(default_factory=list)
    requires_context: bool = True
    estimated_duration: Optional[float] = Field(None, description="Estimated duration in seconds")
    context_requirements: Dict[str, Any] = Field(default_factory=dict)


class ParsedDocument(BaseModel):
    """Complete parsed document with all sections"""
    document_id: str
    metadata: DocumentMetadata
    sections: List[DocumentSection]
    section_order: List[str]
    total_complexity: float
    dependency_graph: Dict[str, List[str]] = Field(default_factory=dict)
    parsing_status: ProcessingStatus = ProcessingStatus.COMPLETED


# ============================================================================
# Context Management Types
# ============================================================================

class KnowledgeGap(BaseModel):
    """Represents a gap in user knowledge"""
    concept_name: str
    gap_type: Literal["missing_prerequisite", "incomplete_understanding", "complexity_mismatch"]
    severity: float = Field(ge=0.0, le=1.0)
    suggested_action: str


class AccumulatedContext(BaseModel):
    """Context accumulated from previous sections"""
    covered_concepts: List[str] = Field(default_factory=list)
    established_knowledge: Dict[str, Any] = Field(default_factory=dict)
    complexity_progression: List[int] = Field(default_factory=list)
    timing_context: Dict[str, float] = Field(default_factory=dict)
    cumulative_duration: float = 0.0


class SectionContext(BaseModel):
    """Context for processing a specific section"""
    section_id: str
    document_id: str
    section_order: int
    accumulated_context: AccumulatedContext
    knowledge_gaps: List[KnowledgeGap] = Field(default_factory=list)
    next_requirements: List[str] = Field(default_factory=list)
    context_confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    created_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# Scene Planning Types
# ============================================================================

class VisualElement(BaseModel):
    """Visual element in a scene"""
    element_type: Literal["text", "equation", "diagram", "graph", "animation", "transition"]
    content: str
    position: Dict[str, float] = Field(default_factory=dict)
    timing: Dict[str, float] = Field(default_factory=dict)
    style_properties: Dict[str, Any] = Field(default_factory=dict)


class SceneTransition(BaseModel):
    """Transition between scenes"""
    transition_type: Literal["fade", "slide", "zoom", "morph", "cut"]
    duration: float = Field(gt=0.0)
    properties: Dict[str, Any] = Field(default_factory=dict)


class PlannedScene(BaseModel):
    """Planned scene with visual elements and timing"""
    scene_id: str
    scene_number: int
    title: str
    description: str
    visual_elements: List[VisualElement]
    timing_estimate: float = Field(gt=0.0, description="Estimated duration in seconds")
    transitions: List[SceneTransition] = Field(default_factory=list)
    concepts_covered: List[str] = Field(default_factory=list)
    context_integration: Dict[str, Any] = Field(default_factory=dict)


class ScenePlan(BaseModel):
    """Complete scene plan for a section"""
    section_id: str
    scenes: List[PlannedScene]
    total_estimated_duration: float
    context_dependencies: List[str] = Field(default_factory=list)
    planning_status: ProcessingStatus = ProcessingStatus.COMPLETED
    created_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# Audio & Transcript Types
# ============================================================================

class TimingMarker(BaseModel):
    """Precise timing marker for audio-visual sync"""
    marker_id: str
    timestamp: float = Field(ge=0.0, description="Time in seconds")
    marker_type: Literal["scene_start", "concept_intro", "equation", "transition", "emphasis"]
    content_reference: str
    sync_priority: Literal["critical", "important", "normal"] = "normal"


class SyncPoint(BaseModel):
    """Synchronization point between audio and visual"""
    sync_id: str
    audio_timestamp: float = Field(ge=0.0)
    visual_frame: int = Field(ge=0)
    confidence: float = Field(ge=0.0, le=1.0)
    sync_type: Literal["hard", "soft", "flexible"] = "hard"
    tolerance: float = Field(ge=0.0, default=0.1, description="Acceptable timing tolerance in seconds")


class NarrationScript(BaseModel):
    """Generated narration script with timing"""
    section_id: str
    script_text: str
    explanation_level: ExplanationLevel
    timing_markers: List[TimingMarker] = Field(default_factory=list)
    sync_points: List[SyncPoint] = Field(default_factory=list)
    estimated_duration: float = Field(gt=0.0)
    speech_rate: float = Field(gt=0.0, default=150.0, description="Words per minute")
    pause_locations: List[float] = Field(default_factory=list)


class AudioMetadata(BaseModel):
    """Generated audio file metadata"""
    audio_file_path: str
    duration: float = Field(gt=0.0)
    sample_rate: int = 44100
    format: str = "mp3"
    quality_metrics: Dict[str, float] = Field(default_factory=dict)
    generation_timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# Animation & Manim Types
# ============================================================================

class ManimSyncMarker(BaseModel):
    """Synchronization marker in Manim code"""
    frame_number: int = Field(ge=0)
    timestamp: float = Field(ge=0.0)
    scene_method: str
    sync_point_id: str
    marker_code: str


class ManimScript(BaseModel):
    """Generated Manim animation script"""
    section_id: str
    script_content: str
    class_name: str
    sync_markers: List[ManimSyncMarker] = Field(default_factory=list)
    frame_rate: int = 60
    resolution: str = "1080p"
    estimated_frames: int = Field(ge=0)
    estimated_render_time: float = Field(ge=0.0)


class RenderMetadata(BaseModel):
    """Rendering process metadata"""
    render_job_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    render_duration: Optional[float] = None
    resource_usage: Dict[str, Any] = Field(default_factory=dict)
    quality_settings: Dict[str, Any] = Field(default_factory=dict)
    error_details: Optional[str] = None


# ============================================================================
# Synchronization & Quality Types
# ============================================================================

class SyncValidationResult(BaseModel):
    """Result of synchronization validation"""
    sync_confidence: float = Field(ge=0.0, le=1.0)
    confidence_level: SyncConfidenceLevel
    validation_passed: bool
    issues_found: List[str] = Field(default_factory=list)
    correction_suggestions: List[str] = Field(default_factory=list)
    frame_accuracy: float = Field(ge=0.0, le=1.0)
    timing_drift: float = Field(ge=0.0, description="Maximum timing drift in seconds")


class QualityMetrics(BaseModel):
    """Quality metrics for generated content"""
    visual_quality: float = Field(ge=0.0, le=1.0)
    audio_quality: float = Field(ge=0.0, le=1.0)
    sync_quality: float = Field(ge=0.0, le=1.0)
    educational_effectiveness: float = Field(ge=0.0, le=1.0)
    context_coherence: float = Field(ge=0.0, le=1.0)
    overall_score: float = Field(ge=0.0, le=1.0)


class SyncCorrection(BaseModel):
    """Correction data for synchronization issues"""
    correction_id: str
    issue_description: str
    correction_type: Literal["timing_adjustment", "frame_recomputation", "audio_stretching", "content_modification"]
    adjustment_value: float
    target_confidence: float = Field(ge=0.95, le=1.0)
    applied: bool = False


# ============================================================================
# Assembly & Final Output Types
# ============================================================================

class SectionAnimation(BaseModel):
    """Completed animation for a single section"""
    section_id: str
    animation_id: str
    video_file_path: str
    audio_file_path: str
    duration: float = Field(gt=0.0)
    sync_validation: SyncValidationResult
    quality_metrics: QualityMetrics
    render_metadata: RenderMetadata
    status: ProcessingStatus = ProcessingStatus.COMPLETED


class TransitionData(BaseModel):
    """Data for transitions between sections"""
    from_section: str
    to_section: str
    transition_type: Literal["contextual_bridge", "summary_preview", "smooth_fade", "concept_continuation"]
    duration: float = Field(gt=0.0)
    bridging_content: str
    visual_elements: List[VisualElement] = Field(default_factory=list)


class FinalAnimation(BaseModel):
    """Complete assembled animation"""
    document_id: str
    animation_id: str
    final_video_path: str
    total_duration: float = Field(gt=0.0)
    section_animations: List[SectionAnimation]
    transitions: List[TransitionData] = Field(default_factory=list)
    overall_quality: QualityMetrics
    assembly_timestamp: datetime = Field(default_factory=datetime.now)
    manifest: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Request/Response Types
# ============================================================================

class ProcessingRequest(BaseModel):
    """Request to process a document"""
    document_id: str
    pdf_file_path: str
    explanation_level: ExplanationLevel
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    priority: Literal["low", "normal", "high"] = "normal"


class ProcessingResponse(BaseModel):
    """Response from processing request"""
    job_id: str
    status: ProcessingStatus
    message: str
    estimated_completion_time: Optional[datetime] = None
    progress_percentage: float = Field(ge=0.0, le=100.0, default=0.0)


class StatusResponse(BaseModel):
    """Status response for ongoing jobs"""
    job_id: str
    status: ProcessingStatus
    progress_percentage: float = Field(ge=0.0, le=100.0)
    current_section: Optional[str] = None
    sections_completed: int = 0
    total_sections: int = 0
    estimated_time_remaining: Optional[float] = None
    error_message: Optional[str] = None


# ============================================================================
# Agent Communication Types
# ============================================================================

class AgentMessage(BaseModel):
    """Message between agents"""
    message_id: str
    sender_agent: str
    receiver_agent: str
    message_type: Literal["section_data", "context_update", "scene_plan", "sync_validation", "render_request"]
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    priority: Literal["low", "normal", "high", "critical"] = "normal"


class AgentResponse(BaseModel):
    """Response from an agent"""
    response_id: str
    original_message_id: str
    agent_name: str
    success: bool
    response_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    processing_time: float = Field(ge=0.0)


# ============================================================================
# Error Types
# ============================================================================

class ProcessingError(BaseModel):
    """Error during processing"""
    error_id: str
    error_type: Literal["pdf_parse", "context_analysis", "scene_generation", "sync_validation", "render_failure"]
    error_message: str
    section_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    recoverable: bool = True
    retry_count: int = 0
    max_retries: int = 3


# ============================================================================
# Validators
# ============================================================================

@validator('sync_confidence', 'confidence', 'frame_accuracy')
def validate_confidence_score(cls, v):
    """Validate confidence scores are between 0 and 1"""
    if not 0.0 <= v <= 1.0:
        raise ValueError('Confidence scores must be between 0.0 and 1.0')
    return v


@validator('timing_estimate', 'duration', 'estimated_duration')
def validate_positive_duration(cls, v):
    """Validate durations are positive"""
    if v is not None and v <= 0:
        raise ValueError('Duration must be positive')
    return v


# ============================================================================
# Helper Functions
# ============================================================================

def get_confidence_level(score: float) -> SyncConfidenceLevel:
    """Convert confidence score to confidence level"""
    if score >= 0.95:
        return SyncConfidenceLevel.HIGH
    elif score >= 0.8:
        return SyncConfidenceLevel.MEDIUM
    else:
        return SyncConfidenceLevel.LOW


def calculate_overall_quality(metrics: QualityMetrics) -> float:
    """Calculate overall quality score"""
    weights = {
        'visual_quality': 0.2,
        'audio_quality': 0.2,
        'sync_quality': 0.3,  # Higher weight for sync
        'educational_effectiveness': 0.2,
        'context_coherence': 0.1
    }
    
    total = sum(
        getattr(metrics, field) * weight 
        for field, weight in weights.items()
    )
    return round(total, 3)


def validate_section_order(sections: List[DocumentSection]) -> bool:
    """Validate that sections can be processed in order based on dependencies"""
    processed = set()
    
    for section in sorted(sections, key=lambda s: s.section_number):
        # Check if all dependencies are already processed
        for dep in section.dependencies:
            if dep not in processed:
                return False
        processed.add(section.section_id)
    
    return True


# Export all types
__all__ = [
    # Enums
    'ExplanationLevel', 'ProcessingStatus', 'SyncConfidenceLevel',
    
    # Document types
    'DocumentMetadata', 'ConceptDependency', 'ExtractedConcept', 
    'DocumentSection', 'ParsedDocument',
    
    # Context types
    'KnowledgeGap', 'AccumulatedContext', 'SectionContext',
    
    # Scene types
    'VisualElement', 'SceneTransition', 'PlannedScene', 'ScenePlan',
    
    # Audio types
    'TimingMarker', 'SyncPoint', 'NarrationScript', 'AudioMetadata',
    
    # Animation types
    'ManimSyncMarker', 'ManimScript', 'RenderMetadata',
    
    # Quality types
    'SyncValidationResult', 'QualityMetrics', 'SyncCorrection',
    
    # Assembly types
    'SectionAnimation', 'TransitionData', 'FinalAnimation',
    
    # Request/Response types
    'ProcessingRequest', 'ProcessingResponse', 'StatusResponse',
    
    # Agent types
    'AgentMessage', 'AgentResponse',
    
    # Error types
    'ProcessingError',
    
    # Helper functions
    'get_confidence_level', 'calculate_overall_quality', 'validate_section_order'
]
