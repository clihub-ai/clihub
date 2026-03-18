"""Abstract base installer."""

from __future__ import annotations

import shutil
import subprocess
from abc import ABC, abstractmethod


class BaseInstaller(ABC):
    name: str

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this package manager is on the system."""

    @abstractmethod
    def install(self, package: str) -> bool:
        """Install a package. Returns True on success."""

    def check_installed(self, binary_name: str) -> bool:
        """Check if a binary is on PATH."""
        return shutil.which(binary_name) is not None

    def _run(self, cmd: list[str]) -> bool:
        """Run a command and return True on success."""
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
