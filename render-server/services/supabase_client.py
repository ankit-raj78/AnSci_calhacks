"""
Supabase Client Service
Handles all database operations and file storage
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import json

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_SERVICE_KEY')
        self.bucket_name = os.getenv('SUPABASE_STORAGE_BUCKET', 'academaia-storage')
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and Service Key must be provided")
        
        self.client: Client = create_client(self.url, self.key)
        logger.info("Supabase client initialized")

    def is_connected(self) -> bool:
        """Test database connection"""
        try:
            # Simple query to test connection
            result = self.client.table('jobs').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get current job status and details"""
        try:
            result = self.client.table('jobs').select('*').eq('id', job_id).single().execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting job status for {job_id}: {e}")
            raise

    def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update job with new data"""
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            result = self.client.table('jobs').update(updates).eq('id', job_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating job {job_id}: {e}")
            raise

    def update_job_progress(self, job_id: str, progress: int, message: str) -> bool:
        """Update job progress and status message"""
        try:
            updates = {
                'progress': progress,
                'status_message': message,
                'updated_at': datetime.utcnow().isoformat()
            }
            result = self.client.table('jobs').update(updates).eq('id', job_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating job progress {job_id}: {e}")
            return False

    def store_section_data(self, job_id: str, section_index: int, section_data: Dict[str, Any]) -> bool:
        """Store processed section data"""
        try:
            data = {
                'job_id': job_id,
                'section_index': section_index,
                'section_data': json.dumps(section_data),
                'created_at': datetime.utcnow().isoformat()
            }
            result = self.client.table('sections').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Error storing section data for job {job_id}, section {section_index}: {e}")
            return False

    def get_sections_for_job(self, job_id: str) -> List[Dict[str, Any]]:
        """Get all sections for a job"""
        try:
            result = self.client.table('sections').select('*').eq('job_id', job_id).order('section_index').execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting sections for job {job_id}: {e}")
            return []

    def download_file(self, file_path: str) -> bytes:
        """Download file from Supabase storage"""
        try:
            result = self.client.storage.from_(self.bucket_name).download(file_path)
            return result
        except Exception as e:
            logger.error(f"Error downloading file {file_path}: {e}")
            raise

    def upload_video(self, local_path: str, job_id: str) -> str:
        """Upload video file to Supabase storage"""
        try:
            # Generate storage path
            storage_path = f"videos/{job_id}/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp4"
            
            # Upload file
            with open(local_path, 'rb') as file:
                result = self.client.storage.from_(self.bucket_name).upload(
                    storage_path, 
                    file,
                    file_options={"content-type": "video/mp4"}
                )
            
            # Return public URL
            url = self.client.storage.from_(self.bucket_name).get_public_url(storage_path)
            logger.info(f"Video uploaded successfully: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Error uploading video for job {job_id}: {e}")
            raise

    def upload_audio(self, local_path: str, job_id: str, section_index: int) -> str:
        """Upload audio file to Supabase storage"""
        try:
            # Generate storage path
            storage_path = f"audio/{job_id}/section_{section_index}.mp3"
            
            # Upload file
            with open(local_path, 'rb') as file:
                result = self.client.storage.from_(self.bucket_name).upload(
                    storage_path, 
                    file,
                    file_options={"content-type": "audio/mpeg"}
                )
            
            # Return public URL
            url = self.client.storage.from_(self.bucket_name).get_public_url(storage_path)
            return url
            
        except Exception as e:
            logger.error(f"Error uploading audio for job {job_id}, section {section_index}: {e}")
            raise

    def store_sync_data(self, job_id: str, section_index: int, sync_data: Dict[str, Any]) -> bool:
        """Store synchronization data for a section"""
        try:
            data = {
                'job_id': job_id,
                'section_index': section_index,
                'sync_confidence': sync_data.get('confidence', 0),
                'timing_data': json.dumps(sync_data.get('timing_data', {})),
                'corrections_applied': json.dumps(sync_data.get('corrections', [])),
                'created_at': datetime.utcnow().isoformat()
            }
            result = self.client.table('sync_data').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Error storing sync data for job {job_id}, section {section_index}: {e}")
            return False

    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user learning context and preferences"""
        try:
            result = self.client.table('user_memory').select('*').eq('user_id', user_id).execute()
            if result.data:
                return result.data[0]
            return {}
        except Exception as e:
            logger.error(f"Error getting user context for {user_id}: {e}")
            return {}

    def update_user_context(self, user_id: str, context_data: Dict[str, Any]) -> bool:
        """Update user learning context"""
        try:
            # Check if user context exists
            existing = self.client.table('user_memory').select('id').eq('user_id', user_id).execute()
            
            data = {
                'user_id': user_id,
                'memory_data': json.dumps(context_data),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if existing.data:
                # Update existing
                result = self.client.table('user_memory').update(data).eq('user_id', user_id).execute()
            else:
                # Create new
                data['created_at'] = datetime.utcnow().isoformat()
                result = self.client.table('user_memory').insert(data).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error updating user context for {user_id}: {e}")
            return False

    def log_processing_step(self, job_id: str, step: str, details: Dict[str, Any]) -> bool:
        """Log processing step for debugging and analytics"""
        try:
            data = {
                'job_id': job_id,
                'step_name': step,
                'step_details': json.dumps(details),
                'timestamp': datetime.utcnow().isoformat()
            }
            result = self.client.table('processing_logs').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Error logging processing step {step} for job {job_id}: {e}")
            return False
