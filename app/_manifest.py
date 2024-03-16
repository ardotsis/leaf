import os
import json
from pathlib import Path

_MANIFEST_DIR = Path(__file__).parent / "data"

if not _MANIFEST_DIR.exists():
    os.mkdir(_MANIFEST_DIR)


class Manifest:
    def __init__(self) -> None:
        pass
    
