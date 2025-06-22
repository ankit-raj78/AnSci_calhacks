from pydantic import BaseModel, Field


class AnsciOutlineBlock(BaseModel):
    """Single outline block - a piece of coherent information that should be animated together"""

    content: str = Field(description="The content of the outline block")


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
