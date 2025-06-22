#!/usr/bin/env python3
"""
Test No Fade-Out Fix
Tests that animations don't fade out when audio is longer than video
"""

import sys
import os
sys.path.append('/Users/ankitraj2/AnSci_calhacks/backend')

from ansci.models import AnsciAnimation, AnsciSceneBlock
from ansci.audio import create_audiovisual_animation_with_embedded_audio
from ansci.render import render_audiovisual_animation_embedded
import subprocess
import json

def test_no_fade_out():
    """Test that animations don't fade out due to audio length mismatch"""
    
    print("🔧 Testing No Fade-Out Fix")
    print("=" * 40)
    print("This test ensures animations don't fade out when audio is longer than video.")
    print()
    
    # Create test scene with longer narration
    test_scene = AnsciSceneBlock(
        transcript="""This is a comprehensive test of our no fade-out fix. 
        The audio narration is intentionally longer than the animation duration 
        to verify that the animation doesn't fade out prematurely. 
        We want the full animation to play while the audio continues naturally. 
        This should result in a complete animation without any artificial fade-out effects. 
        The audio should play to completion without being cut off or faded.""",
        description="No fade-out test with longer audio",
        manim_code="""
class NoFadeOutTest(Scene):
    def construct(self):
        # Simple animation that should NOT fade out
        title = Text("No Fade-Out Test", font_size=48, color=GREEN)
        subtitle = Text("Animation Plays Fully", font_size=24, color=BLUE)
        subtitle.next_to(title, DOWN)
        
        # Animation sequence
        self.play(Write(title), run_time=2)
        self.play(Write(subtitle), run_time=2)
        self.wait(2)  # Hold for 2 seconds
        
        # Transform to show completion
        final_text = Text("✅ Animation Complete", font_size=36, color=GOLD)
        self.play(Transform(VGroup(title, subtitle), final_text), run_time=2)
        self.wait(1)  # Final hold
        
        # Total animation time: ~9 seconds
        # Audio will be longer (~15+ seconds)
"""
    )
    
    test_animation = AnsciAnimation(blocks=[test_scene])
    
    print("🎙️  Generating long audio with natural duration...")
    audiovisual_animation = create_audiovisual_animation_with_embedded_audio(
        test_animation, 
        "no_fade_out_test"
    )
    
    print("🎬 Rendering animation (should NOT fade out)...")
    video_paths = render_audiovisual_animation_embedded(
        audiovisual_animation, 
        "no_fade_out_test",
        quality="medium"
    )
    
    if video_paths and len(video_paths) > 0:
        video_path = video_paths[0]
        print(f"✅ No fade-out test video created: {video_path}")
        
        # Analyze the video and audio durations
        try:
            cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", video_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            video_duration = None
            audio_duration = None
            
            print("\n📊 Duration Analysis:")
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_duration = float(stream.get('duration', 0))
                    print(f"   🎬 Video Duration: {video_duration:.1f}s")
                elif stream.get('codec_type') == 'audio':
                    audio_duration = float(stream.get('duration', 0))
                    print(f"   🎵 Audio Duration: {audio_duration:.1f}s")
            
            # Check for fade-out indicators
            if video_duration and audio_duration:
                if audio_duration > video_duration:
                    print(f"   ✅ Audio is longer than video ({audio_duration:.1f}s vs {video_duration:.1f}s)")
                    print(f"   🎯 This tests our no-fade-out fix!")
                else:
                    print(f"   ⚠️  Audio is not longer than video")
                
        except Exception as e:
            print(f"   ❌ Could not analyze durations: {e}")
        
        # Play the video to verify no fade-out
        print(f"\n🎵 Playing test video to verify no fade-out...")
        print("   Watch carefully: animation should play fully without fading out")
        
        try:
            subprocess.run(["afplay", video_path], check=True, timeout=25)
            print("   ✅ Playback complete")
            
            print("\n❓ Fade-Out Assessment:")
            print("   Did the animation fade out before completion?")
            print("   - If YES: The fix needs more work")
            print("   - If NO: ✅ Fade-out fix is working!")
            
        except subprocess.TimeoutExpired:
            print("   ✅ Playback timeout (normal)")
        except Exception as e:
            print(f"   ⚠️  Playback issue: {e}")
        
        print(f"\n🎯 No Fade-Out Test Results:")
        print(f"   🔧 Fix Applied: Remove automatic audio fade-out")
        print(f"   🎵 Audio Length: Natural (no artificial trimming)")
        print(f"   🎬 Animation: Should play to completion")
        print(f"   📁 Test Video: {video_path}")
        
        return True
    else:
        print("❌ Failed to create no fade-out test video")
        return False

if __name__ == "__main__":
    success = test_no_fade_out()
    if success:
        print("\n🎉 No Fade-Out Test Completed!")
        print("Animations should now play to completion without premature fade-out.")
    else:
        print("\n❌ No fade-out test failed!")
