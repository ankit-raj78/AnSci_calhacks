from .types import AnsciOutline


def generate_outline(history: list[dict]) -> AnsciOutline | None:
    """
    Generate an outline for the animation from message history. We make sure
    that the history contains the paper as a file, and user messages.
    """
    raise NotImplementedError("Not implemented")
