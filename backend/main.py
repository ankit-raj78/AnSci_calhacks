from io import BytesIO
import argparse
import sys
from pathlib import Path
from ansci.workflow import create_animation


def main(paper_path: str, output_path: str, prompt: str | None = None):
    """
    Main entry point for PDF to Animation workflow
    
    Args:
        paper_path: Path to PDF file
        output_path: Output directory for generated videos
        prompt: Optional custom prompt for animation generation
    """
    print("🎬🎙️ AnSci Animation Generator")
    print("=" * 40)
    print(f"📄 Input PDF: {paper_path}")
    print(f"📁 Output: {output_path}")
    if prompt:
        print(f"💭 Custom prompt: {prompt[:50]}...")
    print()
    
    # Validate input file
    if not Path(paper_path).exists():
        print(f"❌ Error: PDF file not found: {paper_path}")
        sys.exit(1)
    
    if not paper_path.lower().endswith('.pdf'):
        print(f"❌ Error: File must be a PDF: {paper_path}")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Run the complete workflow
        with open(paper_path, "rb") as paper_file:
            paper_bytes = BytesIO(paper_file.read())
            video_paths = create_animation(paper_bytes, output_path, prompt)
        
        if video_paths:
            print(f"\n🎉 SUCCESS! Generated {len(video_paths)} animation videos:")
            for i, path in enumerate(video_paths):
                print(f"   {i+1}. {Path(path).name}")
            print(f"\n📂 All files saved to: {output_path}")
            print("✅ Animation generation complete!")
        else:
            print("❌ Failed to generate animations")
            sys.exit(1)
            
    except FileNotFoundError:
        print(f"❌ Error: Could not read PDF file: {paper_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during animation generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate educational animations from PDF papers with AI-powered narration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --paper paper.pdf --output ./animations
  python main.py --paper research.pdf --output ./videos --prompt "Focus on the mathematical concepts"
  python main.py --paper attention.pdf --output ./transformer_videos --prompt "Explain the attention mechanism visually"
        """
    )
    parser.add_argument("--paper", type=str, required=True, 
                       help="Path to the PDF paper to animate")
    parser.add_argument("--output", type=str, required=True,
                       help="Output directory for generated animation videos")
    parser.add_argument("--prompt", type=str,
                       help="Custom prompt to guide animation generation (optional)")
    
    args = parser.parse_args()
    main(args.paper, args.output, args.prompt)
