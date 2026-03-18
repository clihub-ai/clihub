from __future__ import annotations

import shutil

from clihub.installer.base import BaseInstaller


class NpmInstaller(BaseInstaller):
    name = "npm"

    def is_available(self) -> bool:
        return shutil.which("npm") is not None

    def install(self, package: str) -> bool:
        return self._run(["npm", "install", "-g", package])
