from io import BytesIO
import base64
from pathlib import Path
from typing import List, Optional
from anthropic.types import MessageParam

from .outline import generate_outline
from .animate import create_ansci_animation
from .models import AnsciAnimation
from .service import llm


def create_animation(
    file: BytesIO, filename: str, prompt: str | None = None
) -> Optional[List[str]]:
    """
    Complete animation workflow: PDF → Outline → Animation → Audio → Video

    Args:
        file: PDF file as BytesIO
        filename: Output filename/path for the animation
        prompt: Optional custom prompt for animation generation

    Returns:
        List of paths to generated video files with embedded audio
    """
    if prompt is None:
        prompt = "Create an educational animation for this paper with clear explanations of key concepts."

    print("🚀 Starting Complete Animation Workflow")
    print("=" * 50)

    # Step 1: Process PDF and create history
    print("📄 Step 1: Processing PDF...")
    pdf_data = base64.b64encode(file.read()).decode("utf-8")

    history: list[MessageParam] = [
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data,
                    },
                },
                {
                    "type": "text",
                    "text": prompt,
                },
            ],
        },
    ]
    print(f"✅ PDF processed and prompt set: '{prompt[:50]}...'")

    # Step 2: Generate outline
    print("\n📋 Step 2: Generating outline with AI...")
    try:
        outline_text, outline = generate_outline(history)
        print(f"Assistant: {outline_text}")

        if outline is None:
            print("❌ Failed to generate outline")
            return None

        print(f"✅ Outline generated: '{outline.title}'")
        print(f"📊 Found {len(outline.blocks)} animation sections:")
        for i, block in enumerate(outline.blocks):
            print(f"   {i+1}. {block.block_title}")

    except Exception as e:
        print(f"❌ Error generating outline: {e}")
        return None

    # Step 3: Create animation scenes
    print("\n🎬 Step 3: Creating animation scenes with AI...")
    try:
        animation_generator = create_ansci_animation(history, outline)

        # Convert generator to list of scene blocks
        scene_blocks = []
        for i, scene in enumerate(animation_generator):
            scene_blocks.append(scene)
            print(f"✅ Scene {i+1}: {scene.description[:60]}...")

            # Limit scenes for testing (remove in production)
            if len(scene_blocks) >= 3:  # Process max 3 scenes
                print(f"⚡ Limited to {len(scene_blocks)} scenes for testing")
                break

        if not scene_blocks:
            print("❌ No animation scenes were generated")
            return None

        # Create complete animation
        animation = AnsciAnimation(blocks=scene_blocks)
        print(f"✅ Animation created with {len(animation.blocks)} scenes")

    except Exception as e:
        print(f"❌ Error creating animation: {e}")
        return None

    # Step 4: Render with embedded audio
    print("\n🎙️ Step 4: Rendering with LMNT audio integration...")
    try:
        from .render import render_audiovisual_animation_embedded

        # Create output directory
        output_path = Path(filename)
        output_dir = output_path.parent if output_path.suffix else output_path
        output_dir.mkdir(exist_ok=True)

        # Render animation with embedded audio
        video_paths = render_audiovisual_animation_embedded(
            animation,
            output_dir=str(output_dir),
            quality="high",
            enable_validation=True,
        )

        if video_paths:
            print(f"✅ Successfully rendered {len(video_paths)} videos with audio!")
            print(f"📁 Output directory: {output_dir}")

            for i, path in enumerate(video_paths):
                path_obj = Path(path)
                print(f"   🎬🎙️  Video {i+1}: {path_obj.name}")

                # Verify audio is embedded
                if _verify_audio_in_video(path):
                    print(f"   ✅ Audio verified in {path_obj.name}")
                else:
                    print(f"   ⚠️  Audio verification failed for {path_obj.name}")

            # Step 5: Success summary
            print("\n" + "=" * 50)
            print("🎉 ANIMATION WORKFLOW COMPLETED SUCCESSFULLY!")
            print("=" * 50)
            print(
                f"📄 Source: {Path(filename).name if hasattr(filename, 'name') else 'PDF'}"
            )
            print(f"📋 Outline: {len(outline.blocks)} sections")
            print(f"🎬 Scenes: {len(scene_blocks)} animated")
            print(f"🎙️  Audio: LMNT TTS embedded")
            print(f"📁 Output: {len(video_paths)} video files")
            print(f"📂 Location: {output_dir}")

            return video_paths
        else:
            print("❌ No videos were rendered")
            return None

    except Exception as e:
        print(f"❌ Error during rendering: {e}")
        import traceback

        traceback.print_exc()
        return None


def _verify_audio_in_video(video_path: str) -> bool:
    """Verify that a video file contains an audio stream"""
    try:
        import subprocess

        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-show_streams",
                "-select_streams",
                "a",
                "-of",
                "csv=p=0",
                video_path,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        return bool(result.stdout.strip())
    except Exception:
        return False


# Convenience function for direct usage
def create_animation_from_pdf_path(
    pdf_path: str, output_path: str, prompt: str | None = None
) -> Optional[List[str]]:
    """
    Create animation directly from PDF file path

    Args:
        pdf_path: Path to PDF file
        output_path: Path for output videos
        prompt: Optional custom prompt

    Returns:
        List of paths to generated video files
    """
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = BytesIO(f.read())
            return create_animation(pdf_bytes, output_path, prompt)
    except Exception as e:
        print(f"❌ Error reading PDF file: {e}")
        return None
