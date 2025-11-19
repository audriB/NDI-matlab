"""
Dataset directory management for cloud downloads.
"""

import os
from pathlib import Path
from typing import Optional


class DatasetDir:
    """Manages local dataset directory structure."""

    def __init__(self, path: str, create: bool = True):
        """
        Initialize dataset directory.

        Args:
            path: Path to dataset directory
            create: If True, create directory structure if it doesn't exist
        """
        self.path = Path(path)

        if create:
            self.path.mkdir(parents=True, exist_ok=True)
            self.docs_path.mkdir(exist_ok=True)
            self.files_path.mkdir(exist_ok=True)

    @property
    def docs_path(self) -> Path:
        """Path to documents directory."""
        return self.path / 'documents'

    @property
    def files_path(self) -> Path:
        """Path to files directory."""
        return self.path / 'files'

    def get_doc_path(self, doc_id: str) -> Path:
        """Get path for a specific document JSON file."""
        return self.docs_path / f'{doc_id}.json'

    def get_file_path(self, file_name: str) -> Path:
        """Get path for a specific data file."""
        return self.files_path / file_name

    def exists(self) -> bool:
        """Check if dataset directory exists."""
        return self.path.exists()

    def is_empty(self) -> bool:
        """Check if dataset directory is empty."""
        if not self.exists():
            return True
        return not any(self.path.iterdir())
