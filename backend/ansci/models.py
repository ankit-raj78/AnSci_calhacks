from pydantic import BaseModel, Field


class AnsciOutlineBlock(BaseModel):
    """Single outline block - a piece of coherent information that should be animated together"""

    block_title: str = Field(description="The title of the outline block")
    text: str = Field(description="The content of the outline block")


class AnsciOutline(BaseModel):
    """Outline for the animation - divides the paper into coherent sections"""

    title: str = Field(description="The title of the animation")
    blocks: list[AnsciOutlineBlock] = Field(description="The blocks of the outline")


class AnsciSceneBlock(BaseModel):
    """Scene block - everything needed to animate a single scene"""

    transcript: str = Field(description="Transcript for the scene block")
    description: str = Field(description="Textual description of the animated scene")
    manim_code: str = Field(
        description="The Python code for the animation scene using the manim library"
    )


class AnsciAnimation(BaseModel):
    """Animation - a list of scene blocks forming the animation"""

    blocks: list[AnsciSceneBlock] = Field(description="The blocks of the scene")


class SceneDescription(BaseModel):
    """Composite scene description containing both transcript and visual description"""

    #     transcript: list[str] = Field(
    #         description="""
    # 30-60 seconds of narration (about 75-150 words), educational but accessible tone.
    # Return a list of strings, each string being a sentence or phrase of the transcript.
    # """
    #     )

    transcript: str = Field(
        description="30-60 seconds of narration (about 75-150 words), educational but accessible tone."
    )

    description: str = Field(
        description="Visual description of animations, 20-40 words maximum, specific about what viewers will see"
    )


class TranscriptChunk(BaseModel):
    """Chunk of transcript with start and end times"""

    text: str = Field(description="The text of the chunk")
    duration: float = Field(description="Durations of the chunk")
