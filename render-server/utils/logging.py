"""
Logging utilities for AcademIA render server.
Provides structured logging for section-by-section processing pipeline.
"""

import logging
import logging.handlers
import json
import time
import traceback
from typing import Any, Dict, Optional, Union
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

from .config import LOG_LEVEL, LOG_FORMAT, LOG_FILE_MAX_SIZE, LOG_BACKUP_COUNT, LOGS_DIR


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured logs for processing pipeline."""
    
    def format(self, record: logging.LogRecord) -> str:
        # Create base log structure
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, 'job_id'):
            log_data["job_id"] = record.job_id
        if hasattr(record, 'section_id'):
            log_data["section_id"] = record.section_id
        if hasattr(record, 'agent_name'):
            log_data["agent_name"] = record.agent_name
        if hasattr(record, 'processing_stage'):
            log_data["processing_stage"] = record.processing_stage
        if hasattr(record, 'sync_confidence'):
            log_data["sync_confidence"] = record.sync_confidence
        if hasattr(record, 'duration'):
            log_data["duration"] = record.duration
        if hasattr(record, 'error_type'):
            log_data["error_type"] = record.error_type
        if hasattr(record, 'retry_count'):
            log_data["retry_count"] = record.retry_count
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_data, default=str, ensure_ascii=False)


class SectionLogger:
    """Logger specifically for section-by-section processing."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(f"academaia.{name}")
        self._setup_logger()
    
    def _setup_logger(self):
        """Set up logger with appropriate handlers."""
        if self.logger.handlers:
            return  # Already configured
        
        self.logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
        
        # Console handler with readable format for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(LOG_FORMAT)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with structured format for production
        log_file = LOGS_DIR / f"{self.logger.name.replace('.', '_')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=LOG_FILE_MAX_SIZE,
            backupCount=LOG_BACKUP_COUNT
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context."""
        self.logger.info(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context."""
        self.logger.debug(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception."""
        if error:
            kwargs['error_type'] = type(error).__name__
            self.logger.error(message, exc_info=error, extra=kwargs)
        else:
            self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log critical message with optional exception."""
        if error:
            kwargs['error_type'] = type(error).__name__
            self.logger.critical(message, exc_info=error, extra=kwargs)
        else:
            self.logger.critical(message, extra=kwargs)


class ProcessingLogger(SectionLogger):
    """Specialized logger for processing pipeline stages."""
    
    def __init__(self, job_id: str, agent_name: str = "unknown"):
        super().__init__("processing")
        self.job_id = job_id
        self.agent_name = agent_name
    
    def _add_context(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Add processing context to log data."""
        kwargs.setdefault('job_id', self.job_id)
        kwargs.setdefault('agent_name', self.agent_name)
        return kwargs
    
    def start_section(self, section_id: str, section_title: str):
        """Log start of section processing."""
        self.info(
            f"Starting processing of section: {section_title}",
            **self._add_context({
                'section_id': section_id,
                'processing_stage': 'section_start'
            })
        )
    
    def complete_section(self, section_id: str, duration: float, sync_confidence: float):
        """Log completion of section processing."""
        self.info(
            f"Completed section processing",
            **self._add_context({
                'section_id': section_id,
                'processing_stage': 'section_complete',
                'duration': duration,
                'sync_confidence': sync_confidence
            })
        )
    
    def context_update(self, section_id: str, context_confidence: float, gaps_found: int):
        """Log context management updates."""
        self.info(
            f"Updated context for section",
            **self._add_context({
                'section_id': section_id,
                'processing_stage': 'context_update',
                'context_confidence': context_confidence,
                'knowledge_gaps': gaps_found
            })
        )
    
    def sync_validation(self, section_id: str, confidence: float, passed: bool, issues: list):
        """Log synchronization validation results."""
        level = "info" if passed else "warning"
        message = f"Sync validation {'passed' if passed else 'failed'}"
        
        getattr(self, level)(
            message,
            **self._add_context({
                'section_id': section_id,
                'processing_stage': 'sync_validation',
                'sync_confidence': confidence,
                'validation_passed': passed,
                'issues_count': len(issues)
            })
        )
    
    def render_progress(self, section_id: str, progress_percent: float, estimated_remaining: float):
        """Log rendering progress."""
        self.debug(
            f"Rendering progress: {progress_percent:.1f}%",
            **self._add_context({
                'section_id': section_id,
                'processing_stage': 'rendering',
                'progress_percent': progress_percent,
                'estimated_remaining': estimated_remaining
            })
        )
    
    def retry_attempt(self, section_id: str, error_type: str, retry_count: int, max_retries: int):
        """Log retry attempts."""
        self.warning(
            f"Retrying after {error_type} (attempt {retry_count}/{max_retries})",
            **self._add_context({
                'section_id': section_id,
                'processing_stage': 'retry',
                'error_type': error_type,
                'retry_count': retry_count,
                'max_retries': max_retries
            })
        )


class APILogger(SectionLogger):
    """Logger for API interactions."""
    
    def __init__(self):
        super().__init__("api")
    
    def request_start(self, service: str, endpoint: str, request_id: str):
        """Log start of API request."""
        self.debug(
            f"Starting {service} API request",
            service=service,
            endpoint=endpoint,
            request_id=request_id,
            stage="request_start"
        )
    
    def request_complete(self, service: str, request_id: str, duration: float, status_code: int):
        """Log completion of API request."""
        self.info(
            f"Completed {service} API request",
            service=service,
            request_id=request_id,
            duration=duration,
            status_code=status_code,
            stage="request_complete"
        )
    
    def rate_limit_hit(self, service: str, retry_after: int):
        """Log rate limit encounters."""
        self.warning(
            f"Rate limit hit for {service}",
            service=service,
            retry_after=retry_after,
            stage="rate_limit"
        )
    
    def api_error(self, service: str, error: Exception, request_id: str):
        """Log API errors."""
        self.error(
            f"API error for {service}",
            error=error,
            service=service,
            request_id=request_id,
            stage="api_error"
        )


@contextmanager
def log_processing_time(logger: Union[SectionLogger, ProcessingLogger], operation: str, **kwargs):
    """Context manager to log operation timing."""
    start_time = time.time()
    logger.debug(f"Starting {operation}", **kwargs)
    
    try:
        yield
        duration = time.time() - start_time
        logger.info(f"Completed {operation}", duration=duration, **kwargs)
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Failed {operation}", error=e, duration=duration, **kwargs)
        raise


@contextmanager
def log_section_processing(logger: ProcessingLogger, section_id: str, section_title: str):
    """Context manager for complete section processing."""
    start_time = time.time()
    logger.start_section(section_id, section_title)
    
    try:
        yield logger
        duration = time.time() - start_time
        # Sync confidence will be set by the caller
        logger.complete_section(section_id, duration, sync_confidence=0.0)
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"Section processing failed: {section_title}",
            error=e,
            section_id=section_id,
            duration=duration,
            processing_stage='section_failed'
        )
        raise


def get_logger(name: str) -> SectionLogger:
    """Get a section logger by name."""
    return SectionLogger(name)


def get_processing_logger(job_id: str, agent_name: str = "unknown") -> ProcessingLogger:
    """Get a processing logger for a specific job."""
    return ProcessingLogger(job_id, agent_name)


def get_api_logger() -> APILogger:
    """Get an API logger."""
    return APILogger()


# Utility functions for common logging patterns
def log_agent_message(logger: SectionLogger, sender: str, receiver: str, message_type: str, success: bool):
    """Log agent-to-agent communication."""
    level = "info" if success else "warning"
    getattr(logger, level)(
        f"Agent message: {sender} -> {receiver}",
        sender_agent=sender,
        receiver_agent=receiver,
        message_type=message_type,
        success=success,
        stage="agent_communication"
    )


def log_quality_metrics(logger: ProcessingLogger, section_id: str, metrics: Dict[str, float]):
    """Log quality metrics for a section."""
    logger.info(
        "Quality metrics recorded",
        section_id=section_id,
        processing_stage='quality_metrics',
        **{f"quality_{k}": v for k, v in metrics.items()}
    )


def log_sync_correction(logger: ProcessingLogger, section_id: str, correction_type: str, 
                       original_confidence: float, new_confidence: float):
    """Log synchronization corrections."""
    logger.info(
        f"Applied sync correction: {correction_type}",
        section_id=section_id,
        processing_stage='sync_correction',
        correction_type=correction_type,
        original_confidence=original_confidence,
        new_confidence=new_confidence,
        improvement=new_confidence - original_confidence
    )


# Create default loggers for common use
system_logger = get_logger("system")
agent_logger = get_logger("agents")
sync_logger = get_logger("synchronization")
render_logger = get_logger("rendering")
api_logger = get_api_logger()

# Export commonly used loggers and functions
__all__ = [
    'SectionLogger', 'ProcessingLogger', 'APILogger',
    'get_logger', 'get_processing_logger', 'get_api_logger',
    'log_processing_time', 'log_section_processing',
    'log_agent_message', 'log_quality_metrics', 'log_sync_correction',
    'system_logger', 'agent_logger', 'sync_logger', 'render_logger', 'api_logger'
]
