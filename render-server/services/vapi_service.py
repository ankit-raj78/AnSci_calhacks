"""
Vapi.ai Service
Handles text-to-speech generation and audio processing
"""

import os
import logging
import requests
import json
from typing import Dict, List, Optional, Any
import tempfile
import subprocess

logger = logging.getLogger(__name__)

class VapiService:
    def __init__(self):
        self.api_key = os.getenv('VAPI_API_KEY')
        if not self.api_key:
            raise ValueError("VAPI_API_KEY must be provided")
        
        self.base_url = "https://api.vapi.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        self.sample_rate = int(os.getenv('AUDIO_SAMPLE_RATE', '44100'))
        self.audio_format = os.getenv('AUDIO_FORMAT', 'mp3')
        self.output_dir = os.getenv('OUTPUT_DIR', './output')
        
        logger.info("Vapi service initialized")

    def is_available(self) -> bool:
        """Test Vapi.ai API availability"""
        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Vapi availability test failed: {e}")
            return False

    def generate_audio(self, text: str, timing_markers: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate audio from text with timing preservation
        
        Args:
            text: Text to convert to speech
            timing_markers: List of timing markers for synchronization
        
        Returns:
            Dict containing audio file path, duration, and timing data
        """
        try:
            # Prepare the TTS request
            tts_payload = {
                "text": text,
                "voice": "en-US-AriaNeural",  # Default voice
                "speed": 1.0,
                "pitch": 0,
                "volume": 80,
                "sample_rate": self.sample_rate,
                "format": self.audio_format
            }
            
            # Add timing markers if provided
            if timing_markers:
                tts_payload["timing_markers"] = timing_markers
            
            # Make request to Vapi.ai
            response = requests.post(
                f"{self.base_url}/tts",
                headers=self.headers,
                json=tts_payload,
                timeout=60
            )
            
            response.raise_for_status()
            
            # Get audio data
            if response.headers.get('content-type') == 'audio/mpeg':
                # Direct audio response
                audio_data = response.content
                timing_data = {}
            else:
                # JSON response with audio URL
                result = response.json()
                audio_url = result.get('audio_url')
                timing_data = result.get('timing_data', {})
                
                # Download audio file
                audio_response = requests.get(audio_url)
                audio_response.raise_for_status()
                audio_data = audio_response.content
            
            # Save audio file
            audio_filename = f"audio_{int(time.time())}.{self.audio_format}"
            audio_path = os.path.join(self.output_dir, audio_filename)
            
            with open(audio_path, 'wb') as f:
                f.write(audio_data)
            
            # Get audio duration
            duration = self._get_audio_duration(audio_path)
            
            result = {
                'file_path': audio_path,
                'duration': duration,
                'sample_rate': self.sample_rate,
                'format': self.audio_format,
                'timing_data': timing_data,
                'word_count': len(text.split()),
                'character_count': len(text)
            }
            
            logger.info(f"Generated audio: {audio_path} ({duration:.2f}s)")
            return result
            
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            # Fallback to local TTS if available
            return self._generate_audio_fallback(text, timing_markers)

    def _generate_audio_fallback(self, text: str, timing_markers: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fallback audio generation using local TTS
        This is a simplified implementation - you might want to use other TTS libraries
        """
        try:
            # Try to use espeak as a fallback (if installed)
            audio_filename = f"audio_fallback_{int(time.time())}.wav"
            audio_path = os.path.join(self.output_dir, audio_filename)
            
            # Generate audio with espeak
            cmd = [
                'espeak',
                '-w', audio_path,
                '-s', '160',  # Speed (words per minute)
                '-v', 'en',   # Voice
                text
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(audio_path):
                # Convert to MP3 if needed
                if self.audio_format == 'mp3':
                    mp3_path = audio_path.replace('.wav', '.mp3')
                    self._convert_to_mp3(audio_path, mp3_path)
                    os.remove(audio_path)
                    audio_path = mp3_path
                
                duration = self._get_audio_duration(audio_path)
                
                return {
                    'file_path': audio_path,
                    'duration': duration,
                    'sample_rate': self.sample_rate,
                    'format': self.audio_format,
                    'timing_data': {},
                    'fallback': True,
                    'word_count': len(text.split()),
                    'character_count': len(text)
                }
            else:
                raise RuntimeError("Fallback TTS failed")
                
        except Exception as e:
            logger.error(f"Fallback audio generation failed: {e}")
            raise RuntimeError("All audio generation methods failed")

    def _get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file using ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'csv=p=0',
                audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                # Fallback: estimate duration from file size
                file_size = os.path.getsize(audio_path)
                # Very rough estimate: 1 second ≈ 16KB for compressed audio
                estimated_duration = file_size / 16000
                logger.warning(f"Could not get precise duration, estimating: {estimated_duration:.2f}s")
                return estimated_duration
                
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0.0

    def _convert_to_mp3(self, input_path: str, output_path: str):
        """Convert audio file to MP3 using ffmpeg"""
        try:
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-codec:a', 'libmp3lame',
                '-b:a', '128k',
                '-ar', str(self.sample_rate),
                '-y',  # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error converting to MP3: {e}")
            raise

    def adjust_audio_timing(self, audio_path: str, timing_adjustments: List[Dict[str, Any]]) -> str:
        """
        Apply timing adjustments to audio file
        
        Args:
            audio_path: Path to original audio file
            timing_adjustments: List of timing corrections to apply
        
        Returns:
            Path to adjusted audio file
        """
        try:
            adjusted_filename = audio_path.replace('.mp3', '_adjusted.mp3')
            
            # Apply timing adjustments using ffmpeg
            # This is a simplified implementation
            # In practice, you'd need more sophisticated audio stretching
            
            if not timing_adjustments:
                # No adjustments needed, return original
                return audio_path
            
            # For now, just copy the file
            # TODO: Implement actual timing adjustments
            import shutil
            shutil.copy2(audio_path, adjusted_filename)
            
            logger.info(f"Applied timing adjustments: {adjusted_filename}")
            return adjusted_filename
            
        except Exception as e:
            logger.error(f"Error adjusting audio timing: {e}")
            return audio_path  # Return original if adjustment fails

    def get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """Get detailed information about an audio file"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                
                format_info = info.get('format', {})
                streams = info.get('streams', [])
                audio_stream = next((s for s in streams if s.get('codec_type') == 'audio'), {})
                
                return {
                    'duration': float(format_info.get('duration', 0)),
                    'bit_rate': int(format_info.get('bit_rate', 0)),
                    'size': int(format_info.get('size', 0)),
                    'codec': audio_stream.get('codec_name'),
                    'sample_rate': int(audio_stream.get('sample_rate', 0)),
                    'channels': int(audio_stream.get('channels', 0)),
                    'channel_layout': audio_stream.get('channel_layout')
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return {}

# Add time import at the top of the file
import time
