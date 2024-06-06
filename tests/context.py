import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from pathlib import Path
def resolve_path(relative):
    current_dir = Path(__file__).parent
    return current_dir / relative