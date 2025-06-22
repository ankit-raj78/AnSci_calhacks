"""
Production Example: Using the AnsciAnimation System
==================================================

This demonstrates the proper production workflow:
1. Create AnsciSceneBlock objects with manim_code
2. Combine them into AnsciAnimation
3. Render the complete animation

This is how the system should be used in production.
"""

from .types import AnsciSceneBlock, AnsciAnimation
from .animation_service import AnimationGenerationService, render_complete_animation


def create_fibonacci_scene_example():
    """Example of creating a scene block with Fibonacci explanation"""
    
    # Scene 1: Sequential Processing Problem
    scene1_code = '''
from manim import *

class FibonacciSequential(Scene):
    def construct(self):
        # Title
        title = Text("Sequential Processing Problem", font_size=24, color=RED)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)
        
        # Show Fibonacci sequence
        fib_text = Text("Fibonacci: F(n) = F(n-1) + F(n-2)", font_size=18, color=WHITE)
        fib_text.move_to([0, 2, 0])
        self.play(Write(fib_text))
        
        # Show sequential dependency
        dependency_text = Text("Each step waits for previous calculations", 
                              font_size=16, color=YELLOW)
        dependency_text.move_to([0, 1, 0])
        self.play(Write(dependency_text))
        
        # Show the problem
        problem_text = Text("Cannot use parallel processing!", 
                           font_size=18, color=RED)
        problem_text.move_to([0, -1, 0])
        self.play(Write(problem_text))
        
        self.wait(3)
'''
    
    scene1 = AnsciSceneBlock(
        transcript="Traditional RNNs process sequences step by step, like computing Fibonacci numbers. Each calculation must wait for the previous ones, preventing parallel processing.",
        description="Visual demonstration of sequential Fibonacci computation showing dependency chain",
        manim_code=scene1_code
    )
    
    # Scene 2: Parallel Attention Solution
    scene2_code = '''
from manim import *

class AttentionParallel(Scene):
    def construct(self):
        # Title
        title = Text("Attention: Parallel Processing", font_size=24, color=GREEN)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)
        
        # Show attention formula
        formula = MathTex(
            r"\\text{Attention}(Q,K,V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V",
            font_size=16,
            color=YELLOW
        )
        formula.move_to([0, 1, 0])
        self.play(Write(formula))
        
        # Show parallel processing benefit
        parallel_text = Text("All positions processed simultaneously!", 
                            font_size=16, color=GREEN)
        parallel_text.move_to([0, 0, 0])
        self.play(Write(parallel_text))
        
        # Show impact
        impact_text = Text("Revolutionized AI: BERT, GPT, ChatGPT", 
                          font_size=14, color=BLUE)
        impact_text.move_to([0, -1, 0])
        self.play(Write(impact_text))
        
        self.wait(3)
'''
    
    scene2 = AnsciSceneBlock(
        transcript="Transformers use attention to process all positions simultaneously. This parallel approach revolutionized AI, enabling modern language models.",
        description="Attention mechanism visualization showing parallel processing advantage",
        manim_code=scene2_code
    )
    
    return [scene1, scene2]


def main():
    """Production workflow example"""
    
    print("🎬 Production Animation Workflow")
    print("=" * 40)
    
    # Step 1: Create scene blocks
    scene_blocks = create_fibonacci_scene_example()
    print(f"✅ Created {len(scene_blocks)} scene blocks")
    
    # Step 2: Create animation
    animation = AnsciAnimation(blocks=scene_blocks)
    print("✅ Created AnsciAnimation object")
    
    # Step 3: Render animation
    service = AnimationGenerationService(output_dir="production_output")
    video_paths = service.render_animation(animation, quality="high")
    
    if video_paths:
        print(f"✅ Rendered {len(video_paths)} videos:")
        for i, path in enumerate(video_paths):
            print(f"   Scene {i+1}: {path}")
        
        # Step 4: Combine into complete video
        complete_video = service.create_complete_video(video_paths, "fibonacci_explanation")
        if complete_video:
            print(f"✅ Complete animation: {complete_video}")
        else:
            print("⚠️  Video combination failed")
    else:
        print("❌ No videos were rendered")
    
    print("\n🚀 Production workflow complete!")
    
    return animation


if __name__ == "__main__":
    # Run production example
    animation = main()
    
    print(f"\n📊 Animation Summary:")
    print(f"   Scenes: {len(animation.blocks)}")
    for i, block in enumerate(animation.blocks):
        print(f"   Scene {i+1}: {block.description}")
    
    print(f"\n📁 Files Structure:")
    print(f"   Types: backend/ansci/types.py")
    print(f"   Service: backend/ansci/animation_service.py") 
    print(f"   Quality: backend/ansci/quality_assurance.py")
    print(f"   Example: backend/ansci/production_example.py")
    
    print(f"\n✅ PRODUCTION READY!")
