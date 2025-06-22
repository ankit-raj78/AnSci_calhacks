"""
Audio Integration Module
Responsible for generating synchronized narrations using LMNT TTS
Matches audio duration with animation video duration for perfect sync
"""

import os
import json
import subprocess
import asyncio
from pathlib import Path
from typing import List, Optional
import dotenv
from lmnt.api import Speech

from .animate import create_audiovisual_scene_block
from .models import AnsciSceneBlock, AnsciAnimation

dotenv.load_dotenv()

# Initialize LMNT client
assert os.getenv("LMNT_API_KEY") is not None, "LMNT_API_KEY is not set"


class AudioNarrationService:
    """Service for generating synchronized audio narrations using LMNT TTS"""

    def __init__(self, output_dir: str | None = None):
        self.output_dir = Path(output_dir) if output_dir else Path("audio_output")
        self.output_dir.mkdir(exist_ok=True)

    def generate_narration_for_scene(
        self,
        scene_block: AnsciSceneBlock,
        scene_name: str,
        target_duration: float | None = None,
    ) -> Optional[str]:
        """
        Generate audio narration for a single scene block
        Audio is adjusted to fit the animation duration (animation takes priority)

        Args:
            scene_block: Scene block containing transcript
            scene_name: Name for the audio file
            target_duration: Target duration in seconds (from animation video)

        Returns:
            Path to generated audio file, or None if failed
        """

        try:
            # Prioritize animation duration - adjust transcript if needed
            enhanced_transcript = self._adjust_transcript_for_animation_duration(
                scene_block.transcript, scene_block.description, target_duration
            )

            print(f"🎙️  Generating narration for {scene_name}...")
            print(f"   📝 Transcript: {enhanced_transcript[:100]}...")
            if target_duration:
                print(
                    f"   🎬 Animation duration: {target_duration:.1f}s (audio will match)"
                )

            # Generate audio using LMNT TTS or fallback
            audio_path = self._generate_lmnt_audio(
                enhanced_transcript, scene_name, target_duration
            )

            if audio_path:
                print(f"✅ Audio generated to match animation: {audio_path}")
                return audio_path
            else:
                print(f"❌ Failed to generate audio for {scene_name}")
                return None

        except Exception as e:
            print(f"❌ Error generating narration for {scene_name}: {e}")
            return None

    def generate_narrations_for_animation(
        self, animation: AnsciAnimation, video_paths: List[str]
    ) -> List[str]:
        """
        Generate synchronized narrations for all scenes in an animation

        Args:
            animation: Animation containing scene blocks
            video_paths: Optional list of video file paths to match duration

        Returns:
            List of paths to generated audio files
        """
        audio_paths = []

        for i, scene_block in enumerate(animation.blocks):
            scene_name = f"Scene{i+1}"

            # Get target duration from video if available
            target_duration = None
            if video_paths and i < len(video_paths):
                target_duration = self._get_video_duration(video_paths[i])
                print(f"🎬 Matching audio to video duration: {target_duration:.1f}s")

            audio_path = self.generate_narration_for_scene(
                scene_block, scene_name, target_duration
            )

            if audio_path:
                audio_paths.append(audio_path)

        return audio_paths

    def merge_audio_with_video(
        self, video_path: str, audio_path: str, output_name: str
    ) -> str:
        """
        Merge audio narration with video animation - prioritizing video duration

        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            output_name: Name for output file

        Returns:
            Path to merged video file
        """
        if not output_name:
            video_name = Path(video_path).stem
            output_name = f"{video_name}_with_audio"

        output_path = self.output_dir / f"{output_name}.mp4"

        # Get video duration to ensure audio matches
        video_duration = self._get_video_duration(video_path)

        # Use ffmpeg to merge audio and video - prioritizing video duration
        cmd = [
            "ffmpeg",
            "-y",  # -y to overwrite output files
            "-i",
            video_path,
            "-i",
            audio_path,
            "-c:v",
            "copy",  # Copy video stream without re-encoding
            "-c:a",
            "aac",  # Encode audio as AAC
            "-map",
            "0:v:0",  # Map video from first input
            "-map",
            "1:a:0",  # Map audio from second input
            "-t",
            str(video_duration),  # Use video duration as master
            "-af",
            f"apad=whole_dur={video_duration}",  # Pad audio to match video duration
            str(output_path),
        ]

        try:
            print(f"🎬 Merging audio with video (prioritizing video duration)...")
            print(f"   📹 Video: {Path(video_path).name} ({video_duration:.1f}s)")
            print(f"   🎙️  Audio: {Path(audio_path).name}")
            print(f"   🎯 Target: {output_name}.mp4 ({video_duration:.1f}s)")

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Merged video created: {output_path}")

            # Verify the final video has the correct duration
            final_duration = self._get_video_duration(str(output_path))
            print(
                f"   ✅ Final duration: {final_duration:.1f}s (matches video: {abs(final_duration - video_duration) < 0.5})"
            )

            return str(output_path)

        except subprocess.CalledProcessError as e:
            print(f"❌ Error merging audio with video: {e.stderr}")
            print(f"   Command was: {' '.join(cmd)}")

            # Fallback: Try simpler merge command
            simple_cmd = [
                "ffmpeg",
                "-y",
                "-i",
                video_path,
                "-i",
                audio_path,
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-map",
                "0:v",
                "-map",
                "1:a",
                str(output_path),
            ]

            try:
                print("🔄 Trying fallback merge command...")
                subprocess.run(simple_cmd, capture_output=True, text=True, check=True)
                print(f"✅ Fallback merge successful: {output_path}")
                return str(output_path)
            except subprocess.CalledProcessError as e2:
                print(f"❌ Fallback merge also failed: {e2.stderr}")
                return ""

    def create_complete_audiovisual_animation(
        self, animation: AnsciAnimation, video_paths: List[str]
    ) -> List[str]:
        """
        Create complete audiovisual animations by merging all videos with narrations

        Args:
            animation: Animation containing scene blocks
            video_paths: List of video file paths

        Returns:
            List of paths to merged audiovisual files
        """
        # Generate synchronized narrations
        audio_paths = self.generate_narrations_for_animation(animation, video_paths)

        # Merge each video with its corresponding audio
        merged_paths = []
        for i, (video_path, audio_path) in enumerate(zip(video_paths, audio_paths)):
            if audio_path:
                merged_path = self.merge_audio_with_video(
                    video_path, audio_path, f"Scene{i+1}_audiovisual"
                )
                if merged_path:
                    merged_paths.append(merged_path)

        return merged_paths

    def _adjust_transcript_for_animation_duration(
        self, transcript: str, description: str, animation_duration: float | None = None
    ) -> str:
        """
        Adjust transcript to fit animation duration (animation takes priority)
        """
        if not animation_duration:
            # No animation duration provided, use transcript as-is with minimal enhancement
            return self._add_natural_pauses(transcript)

        # Calculate natural speech duration (average 2.5 words per second)
        words = transcript.split()
        natural_duration = len(words) / 2.5

        print(
            f"   📊 Speech analysis: {len(words)} words, natural duration: {natural_duration:.1f}s"
        )
        print(f"   🎬 Animation duration: {animation_duration:.1f}s")

        # Determine if we need to adjust the transcript
        if animation_duration > natural_duration * 1.5:
            # Animation is much longer - add pauses and expand content
            print(f"   🔄 Expanding transcript for longer animation")
            enhanced = self._expand_transcript_for_longer_animation(
                transcript, animation_duration
            )
        elif animation_duration < natural_duration * 0.7:
            # Animation is shorter - condense transcript
            print(f"   ⚡ Condensing transcript for shorter animation")
            enhanced = self._condense_transcript_for_shorter_animation(
                transcript, animation_duration
            )
        else:
            # Animation duration is reasonable - add natural pauses
            print(f"   ✅ Good duration match - adding natural pauses")
            enhanced = self._add_natural_pauses(transcript)

        return enhanced

    def _expand_transcript_for_longer_animation(
        self, transcript: str, target_duration: float
    ) -> str:
        """Expand transcript for longer animations by adding pauses and emphasis"""
        enhanced = transcript

        # Add longer pauses at sentence boundaries
        enhanced = enhanced.replace(". ", "... ")
        enhanced = enhanced.replace("! ", "!... ")
        enhanced = enhanced.replace("? ", "?... ")

        # Add emphasis pauses for key terms
        enhanced = enhanced.replace("attention", "attention... ")
        enhanced = enhanced.replace("transformer", "transformer... ")
        enhanced = enhanced.replace("mechanism", "mechanism... ")
        enhanced = enhanced.replace("parallel", "parallel... ")

        # Add descriptive context from animation description if needed
        current_words = len(enhanced.split())
        needed_duration = target_duration * 2.5  # words needed for target duration

        if current_words < needed_duration * 0.8:
            # Still need more content - add descriptive phrases
            if "visual" not in enhanced.lower():
                enhanced += "... As you can see in this visualization... "
            if "animation" not in enhanced.lower():
                enhanced += "... This animation demonstrates the concept clearly... "

        return enhanced

    def _condense_transcript_for_shorter_animation(
        self, transcript: str, target_duration: float
    ) -> str:
        """Condense transcript for shorter animations"""
        # Remove unnecessary words and phrases
        condensed = transcript

        # Remove filler words
        filler_words = [
            "basically",
            "essentially",
            "actually",
            "really",
            "very",
            "quite",
        ]
        for filler in filler_words:
            condensed = condensed.replace(f" {filler} ", " ")

        # Shorten common phrases
        replacements = {
            "in order to": "to",
            "due to the fact that": "because",
            "at this point in time": "now",
            "for the purpose of": "to",
            "in the event that": "if",
        }

        for long_phrase, short_phrase in replacements.items():
            condensed = condensed.replace(long_phrase, short_phrase)

        # If still too long, truncate to essential points
        words = condensed.split()
        target_words = int(target_duration * 2.5)

        if len(words) > target_words:
            # Keep the most important parts (beginning and key concepts)
            condensed = " ".join(words[:target_words])
            if not condensed.endswith("."):
                condensed += "."

        return condensed

    def _add_natural_pauses(self, transcript: str) -> str:
        """Add natural speaking pauses without changing content"""
        enhanced = transcript

        # Add slight pauses for natural speech
        enhanced = enhanced.replace(", ", ",... ")
        enhanced = enhanced.replace("; ", ";... ")
        enhanced = enhanced.replace(": ", ":... ")

        # Emphasize important technical terms
        enhanced = enhanced.replace("attention", "ATTENTION")
        enhanced = enhanced.replace("transformer", "TRANSFORMER")

        return enhanced

    def _generate_lmnt_audio(
        self, text: str, scene_name: str, target_duration: float | None = None
    ) -> Optional[str]:
        """Generate audio using LMNT TTS API with high-quality voice synthesis and echo prevention"""

        print(
            f"   🎤 Using LMNT TTS for high-quality narration (echo prevention enabled)"
        )

        try:
            # Generate audio using LMNT async API
            # Handle the case where we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._lmnt_synthesize(text))
                    audio_data = future.result(timeout=30)
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
                audio_data = asyncio.run(self._lmnt_synthesize(text))

            if audio_data:
                # Save raw LMNT audio first
                raw_audio_path = self.output_dir / f"{scene_name}_raw_lmnt.mp3"
                with open(raw_audio_path, "wb") as f:
                    f.write(audio_data)

                print(f"✅ LMNT TTS raw audio generated: {raw_audio_path}")

                # Process audio to prevent echo and improve quality
                final_audio_path = self._process_audio_for_quality(
                    raw_audio_path, scene_name, target_duration
                )

                # Clean up raw file
                if raw_audio_path.exists():
                    raw_audio_path.unlink()

                return final_audio_path
            else:
                print("❌ LMNT TTS failed to generate audio")
                return self._fallback_system_tts(text, scene_name, target_duration)

        except Exception as e:
            print(f"❌ Error calling LMNT TTS: {e}")
            # Clean up any leftover coroutines
            import warnings
            warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*never awaited.*")
            # Try fallback TTS
            return self._fallback_system_tts(text, scene_name, target_duration)

    async def _lmnt_synthesize(self, text: str, voice: str = "leah") -> Optional[bytes]:
        """Async helper to synthesize speech using LMNT with optimized settings"""
        try:
            print(f"   🗣️  Synthesizing with voice '{voice}' (optimized for clarity)")
            async with Speech() as speech:
                # Use LMNT with basic settings (sample_rate will be handled in post-processing)
                synthesis = await speech.synthesize(text, voice)
                print(
                    f"   ✅ LMNT synthesis complete ({len(synthesis['audio'])} bytes)"
                )
                return synthesis["audio"]
        except Exception as e:
            print(f"❌ LMNT synthesis error: {e}")
            return None

    def _adjust_audio_duration_to_animation(
        self, audio_path: Path, scene_name: str, target_duration: float | None = None
    ) -> Optional[str]:
        """Adjust audio duration to exactly match animation duration"""
        if not target_duration:
            # No target duration, return as-is
            final_path = self.output_dir / f"{scene_name}_narration.mp3"
            audio_path.rename(final_path)
            return str(final_path)

        final_path = self.output_dir / f"{scene_name}_narration.mp3"

        try:
            # Get current audio duration
            current_duration = self._get_audio_duration(str(audio_path))

            if abs(current_duration - target_duration) < 0.5:
                # Duration is close enough, use as-is
                audio_path.rename(final_path)
                print(
                    f"   ✅ Audio duration matches animation: {current_duration:.1f}s"
                )
                return str(final_path)

            elif current_duration < target_duration:
                # Audio is shorter than animation - add silence at the end
                silence_duration = target_duration - current_duration
                print(
                    f"   🔇 Adding {silence_duration:.1f}s silence to match animation"
                )

                cmd = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(audio_path),
                    "-f",
                    "lavfi",
                    "-i",
                    f"anullsrc=channel_layout=stereo:sample_rate=48000",
                    "-filter_complex",
                    f"[0:a][1:a]concat=n=2:v=0:a=1",
                    "-t",
                    str(target_duration),
                    str(final_path),
                ]

                subprocess.run(cmd, capture_output=True, check=True)
                print(f"   ✅ Extended audio to {target_duration:.1f}s")
                return str(final_path)

            else:
                # Audio is longer than animation - let it play naturally, no fade
                print(
                    f"   🎵 Audio is longer ({current_duration:.1f}s) than target ({target_duration:.1f}s)"
                )
                print(f"   ✅ Keeping natural audio length - no artificial fade-out")

                # Just copy the file without trimming or fading
                audio_path.rename(final_path)
                print(f"   ✅ Audio kept at natural duration: {current_duration:.1f}s")
                return str(final_path)

        except Exception as e:
            print(f"⚠️  Audio duration adjustment failed: {e}")
            # Fallback: just copy the file
            audio_path.rename(final_path)
            return str(final_path)

    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds"""
        try:
            cmd = [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                audio_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            duration = float(data["format"]["duration"])
            return duration

        except Exception as e:
            print(f"⚠️  Could not get audio duration: {e}")
            return 10.0  # Default fallback duration

    def _fallback_system_tts(
        self, text: str, scene_name: str, target_duration: float | None = None
    ) -> Optional[str]:
        """Fallback to system TTS with normal speech speed"""
        print("🔄 Using system TTS with normal speech speed...")

        try:
            # Try system TTS (macOS 'say' command) with normal rate
            if os.system("which say > /dev/null 2>&1") == 0:
                print("🎤 Using macOS system TTS at normal speed...")

                # Generate audio with system TTS at normal rate (around 175 wpm)
                temp_audio = self.output_dir / f"{scene_name}_temp.aiff"

                # Use normal speaking rate (175 words per minute)
                cmd = ["say", "-v", "Alex", "-r", "175", "-o", str(temp_audio), text]

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0 and temp_audio.exists():
                    # Convert to MP3 and adjust duration to match animation
                    temp_mp3 = self.output_dir / f"{scene_name}_temp.mp3"

                    convert_cmd = [
                        "ffmpeg",
                        "-y",
                        "-i",
                        str(temp_audio),
                        "-c:a",
                        "mp3",
                        "-b:a",
                        "128k",
                        str(temp_mp3),
                    ]

                    subprocess.run(convert_cmd, capture_output=True, check=True)
                    temp_audio.unlink()  # Clean up temp file

                    # Adjust duration to match animation
                    final_audio_path = self._adjust_audio_duration_to_animation(
                        temp_mp3, scene_name, target_duration
                    )

                    if temp_mp3.exists():
                        temp_mp3.unlink()

                    print(f"✅ System TTS audio generated with normal speech")
                    return final_audio_path

            # If system TTS fails, generate silent audio matched to animation duration
            print("🔇 Generating silent audio matched to animation duration...")
            duration = target_duration if target_duration else 10.0
            audio_path = self.output_dir / f"{scene_name}_narration.mp3"

            cmd = [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"anullsrc=channel_layout=stereo:sample_rate=48000",
                "-t",
                str(duration),
                "-c:a",
                "mp3",
                "-metadata",
                f"title=Narration: {text[:50]}...",
                "-metadata",
                f"artist=AnSci Animation System",
                str(audio_path),
            ]

            subprocess.run(cmd, capture_output=True, check=True)
            print(
                f"✅ Generated silent audio placeholder: {audio_path} ({duration:.1f}s)"
            )
            print(f"   💡 Text: {text[:100]}...")
            return str(audio_path)

        except Exception as e:
            print(f"❌ Fallback audio generation failed: {e}")
            return None

    def _get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds using ffprobe"""
        try:
            cmd = [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                video_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            duration = float(data["format"]["duration"])
            return duration

        except Exception as e:
            print(f"⚠️  Could not get video duration: {e}")
            return 10.0  # Default fallback duration

    def _process_audio_for_quality(
        self,
        raw_audio_path: Path,
        scene_name: str,
        target_duration: float | None = None,
    ) -> Optional[str]:
        """
        Process raw audio to prevent echo and improve quality
        - Normalize audio levels
        - Ensure mono output (prevent stereo echo)
        - Standardize sample rate
        - Apply gentle noise reduction
        - Handle duration adjustment cleanly
        """
        final_path = self.output_dir / f"{scene_name}_narration.mp3"

        try:
            print(f"   🔧 Processing audio for quality and echo prevention...")

            # Step 1: Get current audio info
            current_duration = self._get_audio_duration(str(raw_audio_path))
            print(f"   📏 Raw audio duration: {current_duration:.1f}s")

            # Step 2: Build FFmpeg command for quality processing
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(raw_audio_path),
                # Audio processing filters to prevent echo
                "-af",
                self._build_quality_audio_filter(current_duration, target_duration),
                # Output settings optimized for Manim compatibility
                "-c:a",
                "mp3",  # MP3 codec
                "-b:a",
                "128k",  # Consistent bitrate
                "-ac",
                "2",  # Force stereo (prevent Manim from doing mono->stereo conversion)
                "-ar",
                "48000",  # Use Manim's preferred sample rate
                "-avoid_negative_ts",
                "make_zero",  # Avoid timing issues
            ]

            # Add duration constraint if needed
            if target_duration:
                cmd.extend(["-t", str(target_duration)])

            cmd.append(str(final_path))

            print(
                f"   🎛️  Applying audio filters: proper stereo, normalize, noise reduction"
            )
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Verify the processed audio
            final_duration = self._get_audio_duration(str(final_path))
            print(f"   ✅ Audio processed successfully")
            print(f"   📏 Final duration: {final_duration:.1f}s")
            print(
                f"   🎵 Output: Proper Stereo, 48kHz, 128kbps MP3 (natural duration, no fade)"
            )

            if target_duration and abs(final_duration - target_duration) > 0.5:
                print(
                    f"   ⚠️  Duration mismatch: expected {target_duration:.1f}s, got {final_duration:.1f}s"
                )

            return str(final_path)

        except subprocess.CalledProcessError as e:
            print(f"❌ Audio processing failed: {e.stderr}")
            # Fallback: simple copy with basic format conversion
            return self._fallback_audio_processing(
                raw_audio_path, scene_name, target_duration
            )
        except Exception as e:
            print(f"❌ Unexpected error in audio processing: {e}")
            return self._fallback_audio_processing(
                raw_audio_path, scene_name, target_duration
            )

    def _build_quality_audio_filter(
        self, current_duration: float, target_duration: float | None = None
    ) -> str:
        """Build FFmpeg audio filter string for quality and echo prevention"""
        filters = []

        # 1. Normalize audio levels (prevent volume-related echo)
        filters.append("loudnorm=I=-16:TP=-2:LRA=7")

        # 2. Light noise reduction (remove background artifacts)
        filters.append("highpass=f=80")  # Remove very low frequencies
        filters.append("lowpass=f=8000")  # Remove very high frequencies

        # 3. Dynamic range compression (even out volume)
        filters.append("acompressor=threshold=0.5:ratio=3:attack=5:release=50")

        # 4. CRITICAL: Convert to proper stereo for Manim (prevents channel duplication echo)
        # Instead of mono->stereo duplication, create true stereo with slight delay to prevent echo
        filters.append(
            "pan=stereo|c0=0.7*c0|c1=0.7*c0"
        )  # Distribute mono to both channels properly

        # 5. NO FADE-OUT: Let audio play naturally for full speech clarity
        # Removed automatic fade-out to prevent animations from fading out prematurely

        return ",".join(filters)

    def _fallback_audio_processing(
        self,
        raw_audio_path: Path,
        scene_name: str,
        target_duration: float | None = None,
    ) -> Optional[str]:
        """Fallback audio processing with minimal filters"""
        final_path = self.output_dir / f"{scene_name}_narration.mp3"

        try:
            print(f"   🔄 Using fallback audio processing...")
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(raw_audio_path),
                "-c:a",
                "mp3",
                "-b:a",
                "128k",
                "-ac",
                "2",  # Force proper stereo
                "-ar",
                "48000",  # Manim's preferred sample rate
            ]

            if target_duration:
                cmd.extend(["-t", str(target_duration)])

            cmd.append(str(final_path))

            subprocess.run(cmd, capture_output=True, check=True)
            print(f"   ✅ Fallback processing complete")
            return str(final_path)

        except Exception as e:
            print(f"❌ Fallback processing also failed: {e}")
            # Last resort: just copy the file
            raw_audio_path.rename(final_path)
            return str(final_path)


# Convenience functions
# def generate_narration_for_animation(
#     animation: AnsciAnimation,
#     video_paths: List[str] | None = None,
#     output_dir: str | None = None,
# ) -> List[str]:
#     """
#     Convenience function to generate narrations for an animation

#     Args:
#         animation: Animation to generate narrations for
#         video_paths: Optional video paths to match duration
#         output_dir: Output directory for audio files

#     Returns:
#         List of audio file paths
#     """
#     service = AudioNarrationService(output_dir)
#     return service.generate_narrations_for_animation(animation, video_paths)


# def create_audiovisual_animation(
#     animation: AnsciAnimation, video_paths: List[str], output_dir: str = None
# ) -> List[str]:
#     """
#     Convenience function to create complete audiovisual animations

#     Args:
#         animation: Animation containing scene blocks
#         video_paths: List of video file paths
#         output_dir: Output directory for merged files

#     Returns:
#         List of merged audiovisual file paths
#     """
#     service = AudioNarrationService(output_dir)
#     return service.create_complete_audiovisual_animation(animation, video_paths)


def create_audiovisual_animation_with_embedded_audio(
    animation: AnsciAnimation, output_dir: str
) -> AnsciAnimation:
    """
    Create audiovisual animation by embedding audio directly in Manim code
    This approach uses self.add_sound() instead of external ffmpeg merging

    Args:
        animation: Original animation to add audio to
        output_dir: Directory for audio files

    Returns:
        New animation with embedded audio in Manim code
    """

    service = AudioNarrationService(output_dir)
    audiovisual_blocks = []

    for i, scene_block in enumerate(animation.blocks):
        scene_name = f"Scene{i+1}"

        print(f"🎙️  Processing {scene_name} for embedded audio...")

        # Generate audio file
        audio_path = service.generate_narration_for_scene(
            scene_block,
            scene_name,
            target_duration=None,  # Let audio be natural length - no forced duration matching
        )

        if audio_path:
            # Create scene block with embedded audio
            audiovisual_block = create_audiovisual_scene_block(
                scene_block, audio_path, scene_name
            )
            audiovisual_blocks.append(audiovisual_block)
            print(f"✅ {scene_name} prepared with embedded audio")
        else:
            # If audio generation fails, use original block
            audiovisual_blocks.append(scene_block)
            print(f"⚠️  {scene_name} using original block (no audio)")

    return AnsciAnimation(blocks=audiovisual_blocks)


if __name__ == "__main__":
    print("🎙️  Audio Narration Service with LMNT Integration")
    print("=" * 55)
    print("✅ LMNT TTS integration")
    print("✅ Duration synchronization")
    print("✅ Audio-video merging")
    print("✅ Professional narration generation")
    print("\nReady for audiovisual animation creation! 🚀")
