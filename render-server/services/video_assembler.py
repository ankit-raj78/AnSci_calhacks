"""
Video Assembler Service
Handles video rendering, audio synchronization, and final assembly
"""

import os
import logging
import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class VideoAssembler:
    def __init__(self):
        self.output_dir = os.getenv('OUTPUT_DIR', './output')
        self.temp_dir = os.getenv('TEMP_DIR', './temp')
        self.video_codec = os.getenv('VIDEO_CODEC', 'libx264')
        self.video_bitrate = os.getenv('VIDEO_BITRATE', '2M')
        self.audio_bitrate = os.getenv('AUDIO_BITRATE', '128k')
        
        # Create directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        logger.info("Video assembler initialized")

    def is_available(self) -> bool:
        """Test if FFmpeg is available"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"FFmpeg availability test failed: {e}")
            return False

    def sync_audio_video(self, video_path: str, audio_path: str, 
                        timing_data: Dict[str, Any]) -> str:
        """
        Synchronize audio with video using timing data
        
        Args:
            video_path: Path to the video file (from Manim)
            audio_path: Path to the audio file (from Vapi)
            timing_data: Synchronization timing information
        
        Returns:
            Path to the synchronized video file
        """
        try:
            # Generate output filename
            output_filename = f"synced_{os.path.basename(video_path)}"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Get video and audio durations
            video_duration = self._get_duration(video_path)
            audio_duration = self._get_duration(audio_path)
            
            logger.info(f"Syncing video ({video_duration:.2f}s) with audio ({audio_duration:.2f}s)")
            
            # Build FFmpeg command for synchronization
            cmd = [
                'ffmpeg',
                '-i', video_path,  # Video input
                '-i', audio_path,  # Audio input
                '-c:v', 'copy',    # Copy video codec (no re-encoding)
                '-c:a', 'aac',     # Audio codec
                '-b:a', self.audio_bitrate,
                '-map', '0:v:0',   # Map video from first input
                '-map', '1:a:0',   # Map audio from second input
                '-shortest',       # End when shortest stream ends
                '-y',              # Overwrite output file
                output_path
            ]
            
            # Apply timing adjustments if needed
            if timing_data.get('video_offset'):
                offset = timing_data['video_offset']
                cmd.insert(-1, '-itsoffset')
                cmd.insert(-1, str(offset))
            
            # Run FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg sync failed: {result.stderr}")
                raise RuntimeError(f"Audio-video sync failed: {result.stderr}")
            
            # Verify output file exists and has reasonable size
            if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
                raise RuntimeError("Synchronized video file is invalid or too small")
            
            logger.info(f"Audio-video sync complete: {output_path}")
            return output_path
            
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg sync timeout")
            raise RuntimeError("Audio-video synchronization timeout")
        except Exception as e:
            logger.error(f"Error in audio-video sync: {e}")
            raise

    def assemble_sections(self, section_videos: List[Dict[str, Any]], job_id: str) -> str:
        """
        Assemble multiple section videos into a final video
        
        Args:
            section_videos: List of section video data
            job_id: Job identifier for naming
        
        Returns:
            Path to the final assembled video
        """
        try:
            if not section_videos:
                raise ValueError("No section videos to assemble")
            
            if len(section_videos) == 1:
                # Single section - just return the path
                return section_videos[0]['video_path']
            
            # Create temporary file list for FFmpeg concat
            concat_file = os.path.join(self.temp_dir, f"concat_{job_id}.txt")
            output_path = os.path.join(self.output_dir, f"final_{job_id}.mp4")
            
            # Write concat file
            with open(concat_file, 'w') as f:
                for section in section_videos:
                    video_path = section['video_path']
                    # Ensure path is absolute and escape special characters
                    abs_path = os.path.abspath(video_path)
                    f.write(f"file '{abs_path}'\n")
            
            # Create transitions if needed
            if self._should_add_transitions(section_videos):
                return self._assemble_with_transitions(section_videos, job_id)
            
            # Simple concatenation without transitions
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',  # Copy streams without re-encoding
                '-y',
                output_path
            ]
            
            logger.info(f"Assembling {len(section_videos)} sections into final video")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                logger.error(f"Video assembly failed: {result.stderr}")
                # Fallback to re-encoding if copy fails
                return self._assemble_with_reencoding(concat_file, output_path)
            
            # Clean up temporary file
            os.remove(concat_file)
            
            # Verify output
            if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
                raise RuntimeError("Assembled video file is invalid")
            
            logger.info(f"Video assembly complete: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error assembling sections: {e}")
            raise

    def _should_add_transitions(self, section_videos: List[Dict[str, Any]]) -> bool:
        """Determine if transitions should be added between sections"""
        # Add transitions if we have multiple sections and they're short enough
        return len(section_videos) > 1 and len(section_videos) <= 5

    def _assemble_with_transitions(self, section_videos: List[Dict[str, Any]], job_id: str) -> str:
        """Assemble videos with smooth transitions between sections"""
        try:
            output_path = os.path.join(self.output_dir, f"final_transitions_{job_id}.mp4")
            temp_dir = os.path.join(self.temp_dir, f"transitions_{job_id}")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Create transition effects between videos
            filter_complex = []
            input_files = []
            
            for i, section in enumerate(section_videos):
                input_files.extend(['-i', section['video_path']])
                
                if i > 0:
                    # Add fade transition between sections
                    filter_complex.append(
                        f"[{i-1}:v]fade=out:st={section_videos[i-1].get('duration', 5)-0.5}:d=0.5[v{i-1}out]; "
                        f"[{i}:v]fade=in:st=0:d=0.5[v{i}in]; "
                        f"[v{i-1}out][v{i}in]concat=n=2:v=1[v{i}]"
                    )
            
            # Build FFmpeg command with transitions
            cmd = [
                'ffmpeg',
                *input_files,
                '-filter_complex', '; '.join(filter_complex),
                '-map', f'[v{len(section_videos)-1}]',
                '-c:v', self.video_codec,
                '-b:v', self.video_bitrate,
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            
            if result.returncode != 0:
                logger.warning("Transition assembly failed, falling back to simple concat")
                return self._assemble_simple_concat(section_videos, job_id)
            
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error in transition assembly: {e}")
            return self._assemble_simple_concat(section_videos, job_id)

    def _assemble_simple_concat(self, section_videos: List[Dict[str, Any]], job_id: str) -> str:
        """Simple concatenation fallback"""
        concat_file = os.path.join(self.temp_dir, f"simple_concat_{job_id}.txt")
        output_path = os.path.join(self.output_dir, f"final_simple_{job_id}.mp4")
        
        with open(concat_file, 'w') as f:
            for section in section_videos:
                f.write(f"file '{os.path.abspath(section['video_path'])}'\n")
        
        return self._assemble_with_reencoding(concat_file, output_path)

    def _assemble_with_reencoding(self, concat_file: str, output_path: str) -> str:
        """Assemble with re-encoding (slower but more reliable)"""
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c:v', self.video_codec,
            '-b:v', self.video_bitrate,
            '-c:a', 'aac',
            '-b:a', self.audio_bitrate,
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        
        if result.returncode != 0:
            raise RuntimeError(f"Video re-encoding failed: {result.stderr}")
        
        return output_path

    def _get_duration(self, video_path: str) -> float:
        """Get duration of video/audio file"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'csv=p=0',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                logger.warning(f"Could not get duration for {video_path}")
                return 0.0
                
        except Exception as e:
            logger.error(f"Error getting duration: {e}")
            return 0.0

    def create_title_card(self, title: str, duration: float = 3.0) -> str:
        """Create a title card video"""
        try:
            output_path = os.path.join(self.output_dir, f"title_{hash(title)}.mp4")
            
            cmd = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', f'color=c=black:size=1280x720:duration={duration}',
                '-vf', f'drawtext=text="{title}":fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2',
                '-c:v', self.video_codec,
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return output_path
            else:
                logger.error(f"Title card creation failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating title card: {e}")
            return None

    def cleanup_job(self, job_id: str):
        """Clean up temporary files for a job"""
        try:
            # Remove temporary files related to this job
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    if job_id in file:
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                            logger.debug(f"Cleaned up temp file: {file_path}")
                        except:
                            pass
            
            # Remove temporary directories
            for item in os.listdir(self.temp_dir):
                if job_id in item:
                    item_path = os.path.join(self.temp_dir, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path, ignore_errors=True)
                        
        except Exception as e:
            logger.error(f"Error cleaning up job {job_id}: {e}")

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get detailed information about a video file"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                
                format_info = info.get('format', {})
                video_stream = next((s for s in info.get('streams', []) if s.get('codec_type') == 'video'), {})
                audio_stream = next((s for s in info.get('streams', []) if s.get('codec_type') == 'audio'), {})
                
                return {
                    'duration': float(format_info.get('duration', 0)),
                    'size': int(format_info.get('size', 0)),
                    'bit_rate': int(format_info.get('bit_rate', 0)),
                    'video_codec': video_stream.get('codec_name'),
                    'video_width': int(video_stream.get('width', 0)),
                    'video_height': int(video_stream.get('height', 0)),
                    'frame_rate': eval(video_stream.get('r_frame_rate', '0/1')),
                    'audio_codec': audio_stream.get('codec_name'),
                    'audio_sample_rate': int(audio_stream.get('sample_rate', 0)),
                    'audio_channels': int(audio_stream.get('channels', 0))
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {}
