
from pathlib import Path


def resolve_path(relative):
    current_dir = Path(__file__).parent
    return current_dir / relative