import json
import os
from pathlib import Path

STORAGE_DIR = Path(__file__).parent / "data"

if not STORAGE_DIR.exists():
    os.mkdir(STORAGE_DIR)


class JsonStorage:
    def __init__(self, filepath: str) -> None:
        self._filepath = filepath

    def save(self, data: dict) -> None:
        self._write(self._filepath, data)

    def load(self) -> dict:
        return self._load(self._filepath)

    @staticmethod
    def _load(filepath: str) -> dict:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _write(filepath: str, data: dict) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
