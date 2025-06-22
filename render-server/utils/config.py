"""
Configuration constants and settings for AcademIA render server.
Based on architecture requirements for section-by-section processing.
"""

import os
from typing import Dict, Any
from pathlib import Path

# ============================================================================
# File Paths & Storage
# ============================================================================

# Base directories
BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output" 
TEMP_DIR = BASE_DIR / "temp"
LOGS_DIR = BASE_DIR / "logs"

# File patterns
PDF_UPLOAD_PATH = UPLOAD_DIR / "pdfs"
AUDIO_OUTPUT_PATH = OUTPUT_DIR / "audio"
VIDEO_OUTPUT_PATH = OUTPUT_DIR / "videos"
MANIM_SCRIPTS_PATH = TEMP_DIR / "manim_scripts"

# Create directories if they don't exist
for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR, LOGS_DIR, 
                  PDF_UPLOAD_PATH, AUDIO_OUTPUT_PATH, VIDEO_OUTPUT_PATH, MANIM_SCRIPTS_PATH]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# API Configuration
# ============================================================================

# External API endpoints
CLAUDE_API_BASE = "https://api.anthropic.com/v1"
VAPI_API_BASE = "https://api.vapi.ai"
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# API Keys (from environment)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
VAPI_API_KEY = os.getenv("VAPI_API_KEY", "")

# Rate limiting
CLAUDE_RATE_LIMIT = 50  # requests per minute
VAPI_RATE_LIMIT = 100   # requests per minute

# ============================================================================
# Processing Configuration
# ============================================================================

# Section processing
MAX_SECTIONS_PER_DOCUMENT = 20
MAX_SECTION_LENGTH = 5000  # characters
MIN_SECTION_LENGTH = 100   # characters

# Context management
CONTEXT_WINDOW_SIZE = 3  # number of previous sections to consider
MAX_CONTEXT_TOKENS = 8000
CONTEXT_CONFIDENCE_THRESHOLD = 0.8

# Explanation levels
EXPLANATION_LEVELS = {
    "beginner": {
        "complexity_max": 3,
        "vocabulary_level": "simple",
        "pace": "slow",
        "examples": "many",
        "technical_depth": "minimal"
    },
    "intermediate": {
        "complexity_max": 6,
        "vocabulary_level": "moderate", 
        "pace": "normal",
        "examples": "some",
        "technical_depth": "moderate"
    },
    "advanced": {
        "complexity_max": 10,
        "vocabulary_level": "technical",
        "pace": "fast", 
        "examples": "few",
        "technical_depth": "detailed"
    }
}

# ============================================================================
# Audio & Video Configuration
# ============================================================================

# Audio settings
AUDIO_SAMPLE_RATE = 44100
AUDIO_FORMAT = "mp3"
AUDIO_QUALITY = 192  # kbps
DEFAULT_SPEECH_RATE = 150  # words per minute

# Speech rate by explanation level
SPEECH_RATES = {
    "beginner": 120,     # slower for beginners
    "intermediate": 150,  # normal pace
    "advanced": 180      # faster for advanced users
}

# Video settings
VIDEO_RESOLUTION = "1080p"
VIDEO_FRAME_RATE = 60
VIDEO_QUALITY = "high"
OUTPUT_FORMAT = "mp4"

# Manim specific settings
MANIM_QUALITY_FLAGS = {
    "preview": "-pql",      # preview quality, low resolution
    "low": "-ql",           # low quality
    "medium": "-qm",        # medium quality  
    "high": "-qh",          # high quality
    "4k": "-qk"             # 4K quality
}

DEFAULT_MANIM_QUALITY = "high"

# ============================================================================
# Synchronization Configuration  
# ============================================================================

# Sync validation thresholds
SYNC_CONFIDENCE_THRESHOLD = 0.95  # minimum confidence for acceptance
SYNC_TOLERANCE = 0.1              # seconds of acceptable timing drift
MAX_SYNC_ITERATIONS = 3           # max correction attempts

# Timing precision
FRAME_PRECISION = 1/60            # 60 FPS precision
AUDIO_SYNC_PRECISION = 0.01       # 10ms precision

# Quality thresholds
MIN_VISUAL_QUALITY = 0.8
MIN_AUDIO_QUALITY = 0.8  
MIN_SYNC_QUALITY = 0.95
MIN_EDUCATIONAL_EFFECTIVENESS = 0.7
MIN_OVERALL_QUALITY = 0.8

# ============================================================================
# Agent Configuration
# ============================================================================

# Agent timeouts (seconds)
AGENT_TIMEOUTS = {
    "pdf_parser": 120,
    "scene_planner": 180,
    "transcript_generator": 90,
    "animation_generator": 300,
    "context_manager": 60,
    "sync_validator": 120,
    "render_controller": 600,  # 10 minutes for rendering
    "assembly_agent": 240
}

# Agent retry configuration
MAX_AGENT_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2.0  # exponential backoff

# ============================================================================
# Database Configuration
# ============================================================================

# Table names
TABLES = {
    "documents": "documents",
    "sections": "document_sections", 
    "contexts": "section_contexts",
    "scene_plans": "scene_plans",
    "animations": "section_animations",
    "sync_data": "synchronization_data",
    "quality_metrics": "quality_metrics",
    "jobs": "processing_jobs",
    "agent_messages": "agent_messages"
}

# Connection pool settings
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_TIMEOUT = 30

# ============================================================================
# Rendering Configuration
# ============================================================================

# Resource limits
MAX_RENDER_MEMORY = "8GB"
MAX_RENDER_TIME = 600      # seconds per section
MAX_CONCURRENT_RENDERS = 2  # parallel render jobs

# File size limits
MAX_PDF_SIZE = 50 * 1024 * 1024    # 50MB
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB
MAX_AUDIO_SIZE = 50 * 1024 * 1024   # 50MB

# Cleanup settings
TEMP_FILE_RETENTION = 3600  # 1 hour
CLEANUP_INTERVAL = 1800     # 30 minutes

# ============================================================================
# Error Handling & Logging
# ============================================================================

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Error handling
MAX_ERROR_RETRIES = 3
ERROR_COOLDOWN = 60  # seconds

# Critical error types that should not retry
FATAL_ERROR_TYPES = [
    "invalid_pdf_format",
    "unsupported_content_type", 
    "api_key_invalid",
    "insufficient_permissions"
]

# ============================================================================
# Performance & Monitoring
# ============================================================================

# Performance targets (seconds)
TARGET_PROCESSING_TIMES = {
    "pdf_parsing": 30,
    "section_processing": 60,  # per section
    "scene_planning": 45,      # per section
    "transcript_generation": 30,  # per section
    "animation_generation": 120,  # per section
    "audio_generation": 20,    # per section
    "sync_validation": 15,     # per section
    "rendering": 180,          # per section
    "final_assembly": 60
}

# Monitoring intervals
HEALTH_CHECK_INTERVAL = 30      # seconds
METRICS_COLLECTION_INTERVAL = 60  # seconds
STATUS_UPDATE_INTERVAL = 5      # seconds

# ============================================================================
# Claude Model Configuration
# ============================================================================

CLAUDE_MODELS = {
    "parsing": "claude-3-sonnet-20240229",      # for PDF parsing
    "scene_planning": "claude-3-sonnet-20240229",  # for scene generation
    "code_generation": "claude-3-sonnet-20240229", # for Manim code
    "transcript": "claude-3-haiku-20240307"     # for transcript generation (faster)
}

# Claude prompt templates directory
PROMPT_TEMPLATES_DIR = BASE_DIR / "prompts"
PROMPT_TEMPLATES_DIR.mkdir(exist_ok=True)

# ============================================================================
# Vapi Configuration
# ============================================================================

# Voice settings
VAPI_VOICE_SETTINGS = {
    "beginner": {
        "voice_id": "rachel",  # clear, friendly voice
        "speed": 0.9,
        "stability": 0.8
    },
    "intermediate": {
        "voice_id": "adam",    # professional voice
        "speed": 1.0,
        "stability": 0.7
    },
    "advanced": {
        "voice_id": "brian",   # technical, efficient voice
        "speed": 1.1,
        "stability": 0.6
    }
}

# ============================================================================
# Development & Testing
# ============================================================================

# Development flags
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
TESTING_MODE = os.getenv("TESTING", "false").lower() == "true"
MOCK_APIS = os.getenv("MOCK_APIS", "false").lower() == "true"

# Test data
TEST_PDF_PATH = BASE_DIR / "test_data" / "sample_paper.pdf"
TEST_OUTPUT_DIR = BASE_DIR / "test_output"

if TESTING_MODE:
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# Export Configuration
# ============================================================================

# Configuration dictionary for easy access
CONFIG = {
    # Paths
    "paths": {
        "upload_dir": UPLOAD_DIR,
        "output_dir": OUTPUT_DIR,
        "temp_dir": TEMP_DIR,
        "logs_dir": LOGS_DIR,
    },
    
    # Processing
    "processing": {
        "max_sections": MAX_SECTIONS_PER_DOCUMENT,
        "context_window": CONTEXT_WINDOW_SIZE,
        "explanation_levels": EXPLANATION_LEVELS,
        "sync_threshold": SYNC_CONFIDENCE_THRESHOLD
    },
    
    # API
    "api": {
        "claude_models": CLAUDE_MODELS,
        "vapi_voices": VAPI_VOICE_SETTINGS,
        "rate_limits": {
            "claude": CLAUDE_RATE_LIMIT,
            "vapi": VAPI_RATE_LIMIT
        }
    },
    
    # Media
    "media": {
        "audio": {
            "sample_rate": AUDIO_SAMPLE_RATE,
            "format": AUDIO_FORMAT,
            "quality": AUDIO_QUALITY
        },
        "video": {
            "resolution": VIDEO_RESOLUTION, 
            "frame_rate": VIDEO_FRAME_RATE,
            "format": OUTPUT_FORMAT
        }
    },
    
    # Performance
    "performance": {
        "targets": TARGET_PROCESSING_TIMES,
        "timeouts": AGENT_TIMEOUTS,
        "quality_thresholds": {
            "sync": MIN_SYNC_QUALITY,
            "visual": MIN_VISUAL_QUALITY,
            "audio": MIN_AUDIO_QUALITY,
            "overall": MIN_OVERALL_QUALITY
        }
    }
}


def get_config(key_path: str, default: Any = None) -> Any:
    """
    Get configuration value using dot notation.
    
    Args:
        key_path: Dot-separated path to config value (e.g., "api.claude_models.parsing")
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    keys = key_path.split(".")
    value = CONFIG
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def validate_config() -> Dict[str, str]:
    """
    Validate that all required configuration values are set.
    
    Returns:
        Dictionary of validation errors (empty if all valid)
    """
    errors = {}
    
    # Check required API keys
    if not ANTHROPIC_API_KEY:
        errors["anthropic_api_key"] = "ANTHROPIC_API_KEY environment variable not set"
    
    if not VAPI_API_KEY:
        errors["vapi_api_key"] = "VAPI_API_KEY environment variable not set"
        
    if not SUPABASE_URL:
        errors["supabase_url"] = "SUPABASE_URL environment variable not set"
        
    if not SUPABASE_SERVICE_KEY:
        errors["supabase_service_key"] = "SUPABASE_SERVICE_KEY environment variable not set"
    
    # Check directory permissions
    for name, path in [("upload", UPLOAD_DIR), ("output", OUTPUT_DIR), ("temp", TEMP_DIR)]:
        if not path.exists():
            errors[f"{name}_dir"] = f"{name} directory does not exist: {path}"
        elif not os.access(path, os.W_OK):
            errors[f"{name}_dir_perms"] = f"No write permission for {name} directory: {path}"
    
    return errors


# Validate configuration on import (unless testing)
if not TESTING_MODE:
    _config_errors = validate_config()
    if _config_errors:
        import warnings
        warnings.warn(f"Configuration validation errors: {_config_errors}")
