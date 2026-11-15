"""Starter package. Replace with the project's code."""


def describe_project(name: str) -> str:
    """Return a one-line description of the project.

    Args:
        name: The project's name.

    Returns:
        A sentence naming the project.

    Raises:
        ValueError: If name is empty.
    """
    if not name.strip():
        raise ValueError("name must not be empty")
    return f"{name} is a Second Order Strategy project."
