#!/usr/bin/env python3
"""
AcademIA Render Server
Flask application for processing PDF research papers into synchronized animations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import traceback
from datetime import datetime

# Import our modules
from services.pdf_processor import PDFProcessor
from services.claude_service import ClaudeService
from services.vapi_service import VapiService
from services.manim_generator import ManimGenerator
from services.video_assembler import VideoAssembler
from services.supabase_client import SupabaseClient
from utils.sync_validator import SyncValidator
from utils.progress_tracker import ProgressTracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize services
supabase_client = SupabaseClient()
pdf_processor = PDFProcessor()
claude_service = ClaudeService()
vapi_service = VapiService()
manim_generator = ManimGenerator()
video_assembler = VideoAssembler()
sync_validator = SyncValidator()
progress_tracker = ProgressTracker(supabase_client)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'manim': manim_generator.is_available(),
            'ffmpeg': video_assembler.is_available(),
            'claude': claude_service.is_available(),
            'vapi': vapi_service.is_available(),
            'supabase': supabase_client.is_connected()
        }
    })

@app.route('/process', methods=['POST'])
def process_document():
    """
    Main endpoint for processing a PDF document into synchronized animations
    Expected payload: {
        "job_id": "uuid",
        "pdf_url": "path/to/pdf",
        "level": "beginner|intermediate|advanced",
        "user_id": "uuid"
    }
    """
    try:
        data = request.json
        job_id = data['job_id']
        pdf_url = data['pdf_url']
        level = data['level']
        user_id = data.get('user_id')
        
        logger.info(f"Starting processing job {job_id} for level {level}")
        
        # Update job status to processing
        progress_tracker.update_job_status(job_id, 'processing', 'Starting document analysis...')
        
        # Step 1: Download and parse PDF
        progress_tracker.update_progress(job_id, 10, 'Downloading and parsing PDF...')
        pdf_content = pdf_processor.download_pdf(pdf_url)
        sections = pdf_processor.parse_into_sections(pdf_content, level)
        
        # Step 2: Process each section sequentially
        section_videos = []
        accumulated_context = {}
        
        for i, section in enumerate(sections):
            section_progress = 20 + (i * 60 / len(sections))
            progress_tracker.update_progress(
                job_id, 
                section_progress, 
                f'Processing section {i+1}/{len(sections)}: {section["title"]}'
            )
            
            # Process single section with context
            section_video = process_section(
                section, 
                accumulated_context, 
                level, 
                job_id, 
                i
            )
            
            section_videos.append(section_video)
            accumulated_context.update(section.get('concepts', {}))
        
        # Step 3: Assemble final video
        progress_tracker.update_progress(job_id, 85, 'Assembling final video...')
        final_video_url = video_assembler.assemble_sections(
            section_videos, 
            job_id
        )
        
        # Step 4: Upload to Supabase and update job
        progress_tracker.update_progress(job_id, 95, 'Uploading final video...')
        final_url = supabase_client.upload_video(final_video_url, job_id)
        
        # Update job as completed
        supabase_client.update_job(job_id, {
            'status': 'completed',
            'final_video_url': final_url,
            'sections': sections,
            'completed_at': datetime.utcnow().isoformat()
        })
        
        progress_tracker.update_progress(job_id, 100, 'Animation complete!')
        
        logger.info(f"Job {job_id} completed successfully")
        return jsonify({
            'success': True,
            'job_id': job_id,
            'final_video_url': final_url,
            'sections': len(sections)
        })
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Update job status to failed
        progress_tracker.update_job_status(
            job_id, 
            'failed', 
            f'Processing failed: {str(e)}'
        )
        
        return jsonify({
            'success': False,
            'error': str(e),
            'job_id': job_id
        }), 500

def process_section(section, context, level, job_id, section_index):
    """Process a single section with context awareness"""
    
    # Step 1: Generate scene plan with Claude
    scene_plan = claude_service.generate_scene_plan(
        section, 
        context, 
        level
    )
    
    # Step 2: Generate transcript with timing
    transcript_data = claude_service.generate_transcript(
        scene_plan, 
        level,
        context
    )
    
    # Step 3: Generate audio with Vapi
    audio_file = vapi_service.generate_audio(
        transcript_data['text'],
        transcript_data['timing_markers']
    )
    
    # Step 4: Generate Manim code
    manim_code = claude_service.generate_manim_code(
        scene_plan,
        transcript_data,
        audio_file['duration']
    )
    
    # Step 5: Validate synchronization
    sync_result = sync_validator.validate_sync(
        manim_code,
        audio_file,
        transcript_data['sync_points']
    )
    
    if sync_result['confidence'] < 0.95:
        # Apply corrections
        manim_code = sync_validator.apply_corrections(
            manim_code,
            sync_result['corrections']
        )
    
    # Step 6: Render animation
    video_file = manim_generator.render_scene(
        manim_code, 
        f"{job_id}_section_{section_index}"
    )
    
    # Step 7: Sync audio and video
    synced_video = video_assembler.sync_audio_video(
        video_file,
        audio_file['file_path'],
        sync_result['timing_data']
    )
    
    return {
        'video_path': synced_video,
        'section_data': section,
        'timing': sync_result['timing_data'],
        'confidence': sync_result['confidence']
    }

@app.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get current status of a processing job"""
    try:
        job_data = supabase_client.get_job_status(job_id)
        return jsonify(job_data)
    except Exception as e:
        logger.error(f"Error getting job status {job_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/cancel/<job_id>', methods=['POST'])
def cancel_job(job_id):
    """Cancel a processing job"""
    try:
        # Update job status to cancelled
        supabase_client.update_job(job_id, {
            'status': 'cancelled',
            'cancelled_at': datetime.utcnow().isoformat()
        })
        
        # Clean up any temporary files
        manim_generator.cleanup_job(job_id)
        video_assembler.cleanup_job(job_id)
        
        return jsonify({'success': True, 'job_id': job_id})
    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('temp', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Start the server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting AcademIA Render Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
