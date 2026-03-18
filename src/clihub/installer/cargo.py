from __future__ import annotations

import shutil

from clihub.installer.base import BaseInstaller


class CargoInstaller(BaseInstaller):
    name = "cargo"

    def is_available(self) -> bool:
        return shutil.which("cargo") is not None

    def install(self, package: str) -> bool:
        return self._run(["cargo", "install", package])
