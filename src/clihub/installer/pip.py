from __future__ import annotations

import shutil
import sys

from clihub.installer.base import BaseInstaller


class PipInstaller(BaseInstaller):
    name = "pip"

    def is_available(self) -> bool:
        return shutil.which("pip") is not None or shutil.which("pip3") is not None

    def install(self, package: str) -> bool:
        return self._run([sys.executable, "-m", "pip", "install", package])
