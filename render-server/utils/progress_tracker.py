"""
Progress Tracker Utility
Handles real-time progress updates for processing jobs
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ProgressTracker:
    def __init__(self, supabase_client):
        self.supabase_client = supabase_client
        logger.info("Progress tracker initialized")

    def update_job_status(self, job_id: str, status: str, message: str = "") -> bool:
        """Update job status with optional message"""
        try:
            updates = {
                'status': status,
                'status_message': message,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Add timestamp for specific statuses
            if status == 'processing':
                updates['started_at'] = datetime.utcnow().isoformat()
            elif status == 'completed':
                updates['completed_at'] = datetime.utcnow().isoformat()
            elif status == 'failed':
                updates['failed_at'] = datetime.utcnow().isoformat()
            
            return self.supabase_client.update_job(job_id, updates)
            
        except Exception as e:
            logger.error(f"Error updating job status for {job_id}: {e}")
            return False

    def update_progress(self, job_id: str, progress: int, message: str = "") -> bool:
        """Update job progress percentage (0-100)"""
        try:
            # Ensure progress is within valid range
            progress = max(0, min(100, progress))
            
            updates = {
                'progress': progress,
                'status_message': message,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Auto-update status based on progress
            if progress == 0:
                updates['status'] = 'pending'
            elif progress == 100:
                updates['status'] = 'completed'
                updates['completed_at'] = datetime.utcnow().isoformat()
            else:
                updates['status'] = 'processing'
            
            success = self.supabase_client.update_job(job_id, updates)
            
            if success:
                logger.info(f"Job {job_id} progress: {progress}% - {message}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating progress for {job_id}: {e}")
            return False

    def log_step(self, job_id: str, step_name: str, details: Dict[str, Any]) -> bool:
        """Log a processing step with details"""
        try:
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'step': step_name,
                'details': details
            }
            
            return self.supabase_client.log_processing_step(job_id, step_name, log_data)
            
        except Exception as e:
            logger.error(f"Error logging step {step_name} for {job_id}: {e}")
            return False

    def track_section_progress(self, job_id: str, section_index: int, total_sections: int, 
                             section_step: str, section_progress: float = 0) -> bool:
        """Track progress within a specific section"""
        try:
            # Calculate overall progress
            # Each section gets equal weight in overall progress
            section_weight = 70 / total_sections  # 70% for section processing
            base_progress = 20 + (section_index * section_weight)  # 20% for initial parsing
            current_progress = base_progress + (section_progress * section_weight)
            
            message = f"Section {section_index + 1}/{total_sections}: {section_step}"
            
            return self.update_progress(job_id, int(current_progress), message)
            
        except Exception as e:
            logger.error(f"Error tracking section progress for {job_id}: {e}")
            return False

    def start_section(self, job_id: str, section_index: int, section_title: str) -> bool:
        """Mark the start of processing a specific section"""
        try:
            details = {
                'section_index': section_index,
                'section_title': section_title,
                'started_at': datetime.utcnow().isoformat()
            }
            
            return self.log_step(job_id, f"section_{section_index}_start", details)
            
        except Exception as e:
            logger.error(f"Error starting section tracking for {job_id}: {e}")
            return False

    def complete_section(self, job_id: str, section_index: int, results: Dict[str, Any]) -> bool:
        """Mark the completion of processing a specific section"""
        try:
            details = {
                'section_index': section_index,
                'completed_at': datetime.utcnow().isoformat(),
                'results': results
            }
            
            return self.log_step(job_id, f"section_{section_index}_complete", details)
            
        except Exception as e:
            logger.error(f"Error completing section tracking for {job_id}: {e}")
            return False

    def get_current_progress(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current progress information for a job"""
        try:
            job_data = self.supabase_client.get_job_status(job_id)
            
            if job_data:
                return {
                    'progress': job_data.get('progress', 0),
                    'status': job_data.get('status', 'unknown'),
                    'message': job_data.get('status_message', ''),
                    'started_at': job_data.get('started_at'),
                    'updated_at': job_data.get('updated_at')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current progress for {job_id}: {e}")
            return None
