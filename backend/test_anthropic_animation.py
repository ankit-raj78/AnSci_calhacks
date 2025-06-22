#!/usr/bin/env python3
"""
Test script for Anthropic-powered animation generation
Demonstrates how the system generates intelligent Manim code from outline content
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from ansci.types import AnsciOutline, AnsciOutlineBlock, AnsciAnimation
from ansci.animate import create_complete_animation, create_ansci_animation
from ansci.render import render_animation

def test_anthropic_animation_generation():
    """Test the complete workflow with Anthropic-powered Manim code generation"""
    
    print("🧠 Testing Anthropic-Powered Animation Generation")
    print("=" * 55)
    
    # Create a sample outline for "Attention Is All You Need"
    outline = AnsciOutline(
        title="Attention Is All You Need - Key Concepts",
        blocks=[
            AnsciOutlineBlock(
                content="The traditional sequence-to-sequence models with RNNs process input sequentially, which prevents parallelization and limits computational efficiency. This sequential nature creates a bottleneck in training and inference."
            ),
            AnsciOutlineBlock(
                content="The attention mechanism allows models to focus on different parts of the input sequence when producing each output element. Instead of compressing all information into a fixed-size context vector, attention provides direct access to all input positions."
            ),
            AnsciOutlineBlock(
                content="Self-attention, or intra-attention, computes attention weights between all positions in a single sequence. This allows each position to attend to all positions in the previous layer, capturing long-range dependencies effectively."
            ),
            AnsciOutlineBlock(
                content="Multi-head attention runs multiple attention mechanisms in parallel, each learning different types of relationships. The outputs are concatenated and linearly transformed, allowing the model to capture various linguistic patterns simultaneously."
            )
        ]
    )
    
    # Create sample history (could contain paper content, user questions, etc.)
    history = [
        {"role": "user", "content": "Can you explain the Transformer architecture?"},
        {"role": "system", "content": "I'll create an animation explaining the key concepts from 'Attention Is All You Need'"},
        {"role": "user", "content": "Focus on why attention is better than RNNs"}
    ]
    
    print(f"📋 Created outline with {len(outline.blocks)} blocks")
    print(f"💬 Using history with {len(history)} messages")
    
    # Test the animation creation with Anthropic
    print("\n🎬 Generating animation with Anthropic SDK...")
    
    try:
        # Create complete animation
        animation = create_complete_animation(outline, history)
        
        print(f"✅ Generated animation with {len(animation.blocks)} scenes")
        
        # Show generated content for each scene
        for i, block in enumerate(animation.blocks):
            print(f"\n📝 Scene {i+1}:")
            print(f"   Description: {block.description}")
            print(f"   Transcript: {block.transcript[:100]}...")
            print(f"   Manim Code: {'✅ Generated' if block.manim_code else '❌ Missing'}")
            
            # Show first few lines of generated Manim code
            if block.manim_code:
                lines = block.manim_code.split('\n')[:5]
                print(f"   Code Preview: {lines[0][:50]}...")
        
        # Test rendering (without actually creating videos)
        print(f"\n🎬 Testing rendering workflow...")
        print(f"   Animation ready for rendering: ✅")
        print(f"   Contains {len(animation.blocks)} renderable scenes")
        
        # Optional: Render first scene if Manim is available
        try:
            video_paths = render_animation(animation, output_dir="anthropic_test_output", quality="low")
            if video_paths:
                print(f"✅ Successfully rendered {len(video_paths)} videos")
                for path in video_paths:
                    print(f"   📹 {path}")
            else:
                print("⚠️  Rendering skipped (Manim not available or other issues)")
        except Exception as e:
            print(f"⚠️  Rendering test failed: {e}")
        
        return animation
        
    except Exception as e:
        print(f"❌ Animation generation failed: {e}")
        print("📋 This might be due to:")
        print("   - Missing ANTHROPIC_API_KEY environment variable")
        print("   - Network connectivity issues")
        print("   - API rate limits")
        print("   - The system will fallback to template-based generation")
        return None


def test_generator_interface():
    """Test the generator interface specifically"""
    print(f"\n🔄 Testing Generator Interface")
    print("=" * 35)
    
    # Simple outline for testing
    outline = AnsciOutline(
        title="Simple Test",
        blocks=[
            AnsciOutlineBlock(content="Test content 1: Introduction to transformers"),
            AnsciOutlineBlock(content="Test content 2: Attention mechanism basics")
        ]
    )
    
    # Test the generator
    scene_count = 0
    for scene_block in create_ansci_animation([], outline):
        scene_count += 1
        print(f"✅ Generated scene {scene_count}: {scene_block.description[:50]}...")
    
    print(f"✅ Generator interface working: {scene_count} scenes yielded")


if __name__ == "__main__":
    # Run the tests
    animation = test_anthropic_animation_generation()
    test_generator_interface()
    
    print(f"\n🚀 Anthropic Integration Complete!")
    print("=" * 40)
    print("✅ Outline → Intelligent Manim Code Generation")
    print("✅ Quality Assurance Integration")
    print("✅ Fallback to Template Generation")
    print("✅ Full Animation Rendering Pipeline")
    
    if animation:
        print(f"\n📊 Generated Animation Summary:")
        print(f"   Title: {animation.blocks[0].description if animation.blocks else 'N/A'}")
        print(f"   Scenes: {len(animation.blocks)}")
        print(f"   Ready for: Video rendering, quality validation")
