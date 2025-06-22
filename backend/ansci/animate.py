from typing import Generator
from .types import AnsciOutline, AnsciSceneBlock


def create_ansci_animation(
    history: list[dict],
    outline: AnsciOutline,
) -> Generator[AnsciSceneBlock]:
    raise NotImplementedError("Not implemented")
