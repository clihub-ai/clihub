# CliHub — Project Context

## What is CliHub?
The App Store for AI Agents. A Python CLI tool (`pip install clihub`) that lets AI agents and humans discover, install, and manage CLI tools. The core insight: `--help` is the universal protocol — no MCP schemas, no JSON-RPC.

## Tech Stack
- **Language**: Python 3.10+
- **CLI Framework**: Click
- **Output**: Rich (tables, panels, colors)
- **Data Models**: Pydantic v2
- **Search**: rapidfuzz (fuzzy matching)
- **Packaging**: pyproject.toml, src-layout, PyPI distribution
- **Registry**: Bundled JSON file (local-first, offline-capable)

## Project Structure
```
src/clihub/
├── __init__.py          # __version__
├── __main__.py          # python -m clihub entry
├── cli.py               # Click root group (--json, --quiet flags)
├── commands/
│   ├── search.py        # clihub search <query>
│   ├── install.py       # clihub install <tool>
│   ├── info.py          # clihub info <tool>
│   ├── list_cmd.py      # clihub list
│   └── doctor.py        # clihub doctor
├── registry/
│   ├── models.py        # Tool, InstallMethod, AgentHints (Pydantic)
│   ├── local.py         # Load bundled registry.json
│   └── search.py        # Fuzzy + keyword search engine
├── installer/
│   ├── base.py          # Abstract BaseInstaller
│   ├── pip.py           # pip install
│   ├── npm.py           # npm install -g
│   ├── brew.py          # brew install
│   ├── cargo.py         # cargo install
│   └── resolver.py      # Auto-detect best installer
├── output.py            # Rich formatting + JSON mode helpers
└── data/
    └── registry.json    # Bundled seed registry (35 tools)
tests/
├── test_search.py
├── test_registry.py
├── test_models.py
└── test_installer.py
```

## Key Design Decisions
- **--json flag**: All commands support `--json` for structured agent output
- **--quiet flag**: Minimal output for piping
- **Exit codes**: 0 = success, 1 = error, 2 = not found
- **stderr for errors, stdout for data** (important for piping)
- **Local-first**: Works offline with bundled registry.json
- **No remote API in Phase 1**: Pure local CLI

## URLs
- Website: https://clihub.net
- GitHub (code): https://github.com/clihub-ai/clihub
- GitHub (landing page): https://github.com/clihub-ai/clihub-landing-page
- PyPI: clihub (not yet published)

## Phase Plan
- Phase 1 (current): CLI Core — search, install, info, list, doctor
- Phase 2: Registry API (FastAPI + Supabase)
- Phase 3: Web Marketplace (Next.js)
- Phase 4: AI-assisted tool creation
