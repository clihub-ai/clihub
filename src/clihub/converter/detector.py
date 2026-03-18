"""Auto-detect CLI tool metadata from the system."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass, fields


@dataclass
class DetectedMetadata:
    name: str | None = None
    version: str | None = None
    description: str | None = None
    author: str | None = None
    homepage: str | None = None
    repository: str | None = None
    license: str | None = None
    install_method: str | None = None
    install_package: str | None = None
    binary_name: str | None = None
    help_text: str | None = None


def _merge(base: DetectedMetadata, patch: DetectedMetadata) -> None:
    """Merge patch into base — only fills None fields."""
    for f in fields(base):
        if getattr(base, f.name) is None and getattr(patch, f.name) is not None:
            setattr(base, f.name, getattr(patch, f.name))


def _run_cmd(cmd: list[str], timeout: int = 5) -> str | None:
    """Run a command and return stdout, or None on failure."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or r.stderr or "").strip() or None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


_SEMVER_RE = re.compile(r"(\d+\.\d+(?:\.\d+)?(?:[-+][a-zA-Z0-9_.]+)?)")


def detect_binary(tool: str) -> DetectedMetadata:
    """Check if tool binary exists on PATH."""
    meta = DetectedMetadata()
    path = shutil.which(tool)
    if path:
        meta.name = tool
        meta.binary_name = tool
    return meta


def detect_version(tool: str) -> DetectedMetadata:
    """Try to extract version from the tool."""
    meta = DetectedMetadata()
    for flag in ["--version", "-V", "version"]:
        out = _run_cmd([tool, flag])
        if out:
            m = _SEMVER_RE.search(out)
            if m:
                meta.version = m.group(1)
                return meta
    return meta


def detect_help(tool: str) -> DetectedMetadata:
    """Run --help and extract description from the first meaningful line."""
    meta = DetectedMetadata()
    out = _run_cmd([tool, "--help"])
    if not out:
        return meta
    meta.help_text = out
    # Try to extract a short description from the first non-empty, non-usage line
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        # Skip usage lines and the tool name alone
        if line.lower().startswith(("usage:", "usage :", tool.lower())):
            continue
        # Skip lines that look like option flags
        if line.startswith("-"):
            continue
        # Take the first descriptive line
        if len(line) >= 10:
            meta.description = line[:200]
            break
    return meta


def detect_brew(package: str) -> DetectedMetadata:
    """Try to get metadata from Homebrew."""
    meta = DetectedMetadata()
    if not shutil.which("brew"):
        return meta
    out = _run_cmd(["brew", "info", "--json=v2", package], timeout=15)
    if not out:
        return meta
    try:
        data = json.loads(out)
        formulae = data.get("formulae", [])
        if not formulae:
            return meta
        f = formulae[0]
        meta.description = f.get("desc")
        meta.homepage = f.get("homepage")
        meta.license = f.get("license")
        versions = f.get("versions", {})
        if versions.get("stable"):
            meta.version = versions["stable"]
        meta.install_method = "brew"
        meta.install_package = package
    except (json.JSONDecodeError, KeyError, IndexError):
        pass
    return meta


def detect_pip(package: str) -> DetectedMetadata:
    """Try to get metadata from pip."""
    meta = DetectedMetadata()
    if not shutil.which("pip") and not shutil.which("pip3"):
        return meta
    pip_cmd = "pip3" if shutil.which("pip3") else "pip"
    out = _run_cmd([pip_cmd, "show", package], timeout=10)
    if not out:
        return meta
    info: dict[str, str] = {}
    for line in out.splitlines():
        if ": " in line:
            key, _, val = line.partition(": ")
            info[key.strip()] = val.strip()
    if info.get("Name"):
        meta.install_method = "pip"
        meta.install_package = info["Name"]
        meta.description = info.get("Summary")
        meta.author = info.get("Author")
        meta.version = info.get("Version")
        meta.homepage = info.get("Home-page") or info.get("Homepage")
        meta.license = info.get("License")
    return meta


def detect_npm(package: str) -> DetectedMetadata:
    """Try to get metadata from npm."""
    meta = DetectedMetadata()
    if not shutil.which("npm"):
        return meta
    out = _run_cmd(["npm", "info", package, "--json"], timeout=15)
    if not out:
        return meta
    try:
        data = json.loads(out)
        if "error" in data:
            return meta
        meta.install_method = "npm"
        meta.install_package = package
        meta.description = data.get("description")
        meta.homepage = data.get("homepage")
        meta.license = data.get("license")
        meta.version = data.get("version")
        repo = data.get("repository", {})
        if isinstance(repo, dict):
            meta.repository = repo.get("url", "").replace("git+", "").replace(".git", "")
        elif isinstance(repo, str):
            meta.repository = repo
        author = data.get("author")
        if isinstance(author, dict):
            meta.author = author.get("name")
        elif isinstance(author, str):
            meta.author = author
    except (json.JSONDecodeError, KeyError):
        pass
    return meta


def detect_cargo(package: str) -> DetectedMetadata:
    """Try to detect a cargo-installed package."""
    meta = DetectedMetadata()
    if not shutil.which("cargo"):
        return meta
    out = _run_cmd(["cargo", "install", "--list"], timeout=10)
    if not out:
        return meta
    for line in out.splitlines():
        # Lines look like: "ripgrep v14.1.0:"
        if line.startswith(package + " ") or line.startswith(package + " v"):
            m = _SEMVER_RE.search(line)
            if m:
                meta.version = m.group(1)
            meta.install_method = "cargo"
            meta.install_package = package
            break
    return meta


def guess_package_manager(tool: str) -> DetectedMetadata:
    """Try each package manager in order to find where the tool comes from."""
    for detect_fn in [detect_brew, detect_pip, detect_npm, detect_cargo]:
        meta = detect_fn(tool)
        if meta.install_method:
            return meta
    return DetectedMetadata()


def run_detection(
    tool: str, package: str | None = None, via: str | None = None
) -> DetectedMetadata:
    """Run the full detection pipeline and return merged metadata."""
    result = DetectedMetadata()
    pkg = package or tool

    # Always detect binary, version, help
    _merge(result, detect_binary(tool))
    _merge(result, detect_version(tool))
    _merge(result, detect_help(tool))

    # Package manager detection
    if via:
        detector_map = {
            "brew": detect_brew,
            "pip": detect_pip,
            "npm": detect_npm,
            "cargo": detect_cargo,
        }
        fn = detector_map.get(via)
        if fn:
            _merge(result, fn(pkg))
    else:
        # Try the specified package name across all managers
        _merge(result, guess_package_manager(pkg))

    # Ensure name is set
    if not result.name:
        result.name = tool

    return result
