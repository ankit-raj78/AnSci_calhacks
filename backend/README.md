# AnSci Backend

Core animation generation service for creating educational videos.

## Quick Start

```bash
# Install dependencies
pip install -e .

# Run production example
python -m ansci.production_example
```

## Components

- `ansci/types.py` - Type definitions
- `ansci/animation_service.py` - Main service
- `ansci/quality_assurance.py` - Quality system
- `ansci/production_example.py` - Usage example

## Architecture

The system follows a clean workflow:
1. Create `AnsciSceneBlock` objects with manim code
2. Combine into `AnsciAnimation`
3. Render with `AnimationGenerationService`
4. Get high-quality MP4 videos

Production-ready and tested! 🚀
