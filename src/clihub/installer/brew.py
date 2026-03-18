from __future__ import annotations

import shutil

from clihub.installer.base import BaseInstaller


class BrewInstaller(BaseInstaller):
    name = "brew"

    def is_available(self) -> bool:
        return shutil.which("brew") is not None

    def install(self, package: str) -> bool:
        return self._run(["brew", "install", package])
