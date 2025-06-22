# AnSci - Animation Science

Production-ready animation generation system for creating high-quality educational videos using Manim.

## Overview

AnSci is a robust system for generating animations that explain complex concepts, specifically designed for educational content like "Attention Is All You Need" and other AI/ML papers.

## Architecture

```
backend/ansci/
├── types.py                    # Pydantic models (AnsciSceneBlock, AnsciAnimation)
├── animation_service.py        # Main service (AnimationGenerationService)
├── quality_assurance.py       # Quality system (LayoutManager, validation)
├── production_example.py       # Usage example
└── PRODUCTION_ARCHITECTURE.py # Documentation
```

## Core Components

### 1. Type System (`types.py`)
- **AnsciSceneBlock**: Contains transcript, description, and manim_code
- **AnsciAnimation**: Collection of scene blocks
- Full Pydantic validation and type safety

### 2. Animation Service (`animation_service.py`)
- **AnimationGenerationService**: Main service class
- **render_animation()**: Renders AnsciAnimation to videos
- **create_complete_video()**: Combines videos
- Production utility functions

### 3. Quality Assurance (`quality_assurance.py`)
- **LayoutManager**: Safe positioning system
- Quality validation decorators
- Bounds checking and readability validation

## Usage

### Basic Usage
```python
from backend.ansci.types import AnsciSceneBlock, AnsciAnimation
from backend.ansci.animation_service import AnimationGenerationService

# 1. Create scene blocks
scene = AnsciSceneBlock(
    transcript="Narration text",
    description="Visual description", 
    manim_code="Manim Python code"
)

# 2. Combine into animation
animation = AnsciAnimation(blocks=[scene])

# 3. Render to videos
service = AnimationGenerationService()
video_paths = service.render_animation(animation)
```

### Command Line Interface

Generate educational animations from PDF papers:

```bash
# Basic usage - creates a single combined video
python main.py --paper research.pdf --output ./videos

# Create multiple video splits
python main.py --paper paper.pdf --output ./videos --splits 3

# Create one video per scene
python main.py --paper paper.pdf --output ./videos --splits 1

# With custom prompt
python main.py --paper attention.pdf --output ./videos --prompt "Focus on the attention mechanism"
```

#### CLI Options
- `--paper`: Path to the PDF paper to animate (required)
- `--output`: Output directory for generated videos (required)
- `--prompt`: Custom prompt to guide animation generation (optional)
- `--splits`: Number of video splits to create (optional)
  - If not specified: Creates a single combined video from all scenes
  - If `--splits 1`: Creates one video file per scene
  - If `--splits N` (N > 1): Creates N video files by grouping scenes

## Dependencies

- **pydantic**: Type validation
- **manim**: Animation rendering
- **ffmpeg**: Video combination (optional)

## Installation

```bash
cd backend
pip install -e .
```

## Running Examples

```bash
cd backend
python -m ansci.production_example
```

## Features

✅ **Clean Architecture**: All components in ansci/ module
✅ **Type Safety**: Full Pydantic validation
✅ **Modular Design**: Single responsibility components
✅ **Quality Assurance**: Built-in validation and bounds checking
✅ **Error Handling**: Graceful failure and cleanup
✅ **Self-contained**: No external file dependencies
✅ **Flexible**: Handles any manim_code content
✅ **Production Ready**: Tested and robust
✅ **Video Splitting**: Flexible output options (single video, per-scene videos, or custom splits)
✅ **Audio Integration**: Embedded audio with synchronized narration

## License

MIT License