<p align="center">
  <br>
  <a href="https://clihub.net">
    <img src="assets/readme-banner-transparent.svg" alt="clihub" width="500">
  </a>
  <br>
  <br>
  <strong>The App Store for AI Agents</strong>
  <br>
  <sub>Discover, install, and manage CLI tools. Add yours in 30 seconds.</sub>
  <br>
  <br>
  <a href="https://pypi.org/project/clihub"><img alt="PyPI" src="https://img.shields.io/pypi/v/clihub?style=flat-square&color=00ff88&labelColor=1a1a2e"></a>
  <a href="https://github.com/clihub-ai/clihub/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue?style=flat-square&labelColor=1a1a2e"></a>
  <a href="https://www.python.org/downloads/"><img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&labelColor=1a1a2e"></a>
  <a href="https://github.com/clihub-ai/clihub/actions"><img alt="Tests" src="https://img.shields.io/github/actions/workflow/status/clihub-ai/clihub/ci.yml?style=flat-square&labelColor=1a1a2e&label=tests"></a>
</p>

<p align="center">
  <a href="https://clihub.net">Website</a> &middot;
  <a href="#quick-start">Quick Start</a> &middot;
  <a href="#for-ai-agents">For AI Agents</a> &middot;
  <a href="#add-your-tool">Add Your Tool</a> &middot;
  <a href="#roadmap">Roadmap</a>
</p>

---

> Every CLI tool is a superpower your agent can wield. MCP dumps full schemas into every prompt — one server with 20 tools adds **8,000+ tokens**. CLI tools load **nothing** until the agent runs `--help`.

<br>

```
$ clihub search "resize images"

 #   Name          Description                           Rating   Category
 1   imagemagick   Create, edit, compose, or convert…    ★ 4.7    media, image
 2   ffmpeg        The Swiss Army knife of multimedi…    ★ 4.8    media, video

$ clihub install imagemagick
 ✓ Installed imagemagick@7.1.1 via brew

 Try it:
  $ magick input.png -resize 800x600 output.png
  $ magick convert input.jpg -quality 80 output.webp
```

<br>

## Highlights

| | Feature | Description |
|---|---|---|
| **0** | **Zero ambient cost** | No schemas injected into context. Tools are discovered on demand via `--help`. |
| **35+** | **Curated tools** | jq, ripgrep, ffmpeg, pandoc, httpie, and more — each with agent-ready hints. |
| **4** | **Package managers** | Auto-detects pip, npm, brew, or cargo. One command to install anything. |
| **`--json`** | **Agent-native** | Every command outputs structured JSON. Exit codes 0/1/2 for success/error/not-found. |
| **`convert`** | **Add your tool** | Auto-detect metadata and generate a manifest in 30 seconds. |

<br>

## Quick Start

```bash
pip install clihub          # or: pipx install clihub
```

> [!NOTE]
> Requires Python 3.10+

```bash
clihub search "json processing"    # find tools
clihub install jq                  # install with auto-detected package manager
clihub info ripgrep                # view metadata + help text
clihub list                        # browse the full registry
clihub doctor                      # check system readiness
```

<br>

## Commands

### `search` — Find tools with natural language

```bash
clihub search "json processing"
clihub search "pdf" --category documents
clihub search "video" --limit 5
```

### `install` — One command, auto-detected package manager

```bash
clihub install jq            # → brew install jq
clihub install httpie         # → pip install httpie
clihub install ripgrep --via cargo   # force a specific installer
```

### `info` — Full metadata + help text

```bash
clihub info jq
```

```
╭─────────────────────────────── jq ───────────────────────────────╮
│                                                                  │
│  jq v1.7.1                                                       │
│  Lightweight command-line JSON processor.                        │
│                                                                  │
│  Author:  Stephen Dolan                                          │
│  Home:    https://jqlang.github.io/jq/                           │
│  License: MIT                                                    │
│                                                                  │
│  Install: brew install jq                                        │
│                                                                  │
│  When to use: Parse, filter, or transform JSON data              │
│  Examples:                                                       │
│    $ cat data.json | jq '.users[] | select(.age > 30)'           │
│    $ jq -r '.items[].name' inventory.json                        │
│                                                                  │
╰──────────────────────────────────────────────────────────────────╯
```

### `list` — Browse the registry

```bash
clihub list                    # show all categories
clihub list --category data    # tools in a category
clihub list --installed        # what's on your PATH
```

### `doctor` — System readiness check

```bash
clihub doctor
```

```
              System Check
┏━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃      ┃ Check          ┃ Detail        ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ ✓    │ Python >= 3.10 │ Python 3.11.4 │
│ ✓    │ pip            │ pip           │
│ ✓    │ npm            │ npm           │
│ ✓    │ brew           │ brew          │
│ ✓    │ cargo          │ cargo         │
└──────┴────────────────┴───────────────┘
```

### `convert` — Auto-generate a tool manifest

```bash
clihub convert jq                     # detect metadata → clihub.yaml
clihub convert rg --package ripgrep   # binary differs from package name
clihub convert myapp --via pip        # specify the package manager
```

### `submit` — Validate and prepare for submission

```bash
clihub submit clihub.yaml             # validate + print PR-ready JSON
clihub submit --validate-only         # just check, don't output
```

<br>

## For AI Agents

CliHub is built for agents to use directly. Pass `--json` to any command for structured output:

```bash
# Agent discovers tools (the primary workflow)
clihub list --json                              # full catalog with agent_hints
clihub list --category data --json              # slice by category

# Agent installs what it needs
clihub install jq

# Agent learns the tool
jq --help
```

> [!TIP]
> **Best practice for agents:** Use `clihub list --json` (not `search`) as the discovery command. The agent's LLM is better at matching tasks to tools than any search algorithm.

### Why CLI over MCP?

| | MCP | CLI (CliHub) |
|---|---|---|
| **Context cost** | 8,000–15,000 tokens per server | 0 tokens until `--help` |
| **Discovery** | Schema dumped into every prompt | On-demand via `list --json` |
| **LLM familiarity** | Needs schema learning | Trained on billions of shell examples |
| **Composability** | Single-tool calls | Unix pipes: `curl \| jq \| csv` |
| **Error handling** | Custom error formats | Exit codes + stderr |

<br>

## Add Your Tool

> [!IMPORTANT]
> **Got a CLI tool? Add it to CliHub in 30 seconds.**

```bash
clihub convert mytool                 # auto-detects name, version, description, license, install method
# → generates clihub.yaml with detected fields + TODO placeholders

# Edit clihub.yaml — fill in categories, tags, agent_hints
vim clihub.yaml

clihub submit clihub.yaml             # validates and prints PR-ready JSON
# → paste into registry.json, open a PR
```

**What `convert` auto-detects:**
- Binary location and version (`--version`, `-V`)
- Description from `--help` output
- Package metadata from brew, pip, npm, or cargo
- Homepage, license, author

**What you fill in:**
- `categories` and `tags`
- `agent_hints.when_to_use` — when should an AI agent reach for this tool?
- `agent_hints.example_usage` — 2-3 example commands

The generated manifest:

```yaml
name: jq
version: "1.7.1"
description: "Lightweight command-line JSON processor"
homepage: "https://jqlang.github.io/jq/"
license: "MIT"
categories: [data, json]           # ← you add these
tags: [json, filter, transform]    # ← you add these
install:
  method: brew
  package: jq
agent_hints:
  when_to_use: "Parse, filter, or transform JSON data"    # ← you add this
  example_usage:
    - "jq '.key' file.json"        # ← you add these
```

<br>

## Registry

CliHub ships with **35+ curated, battle-tested CLI tools:**

| Category | Tools |
|---|---|
| **Data** | jq, yq, csvkit, xsv, dasel, gron |
| **Search & Files** | ripgrep, fd, fzf, bat, eza, tree, ncdu, dust |
| **Network** | httpie, curl, wget, aria2, dog |
| **Dev Tools** | gh, lazygit, delta, tokei, hyperfine |
| **Media** | ffmpeg, imagemagick, yt-dlp |
| **Documents** | pandoc |
| **Productivity** | tmux, tldr, zoxide, starship |
| **System** | htop, btop, procs, bandwhich |

<br>

## Roadmap

- [x] **Phase 1** — CLI core: search, install, info, list, doctor
- [x] **Phase 1.5** — `convert` + `submit`: add any tool in 30 seconds
- [ ] **Phase 2** — Registry API: remote search, `clihub publish`, semantic discovery
- [ ] **Phase 3** — Web marketplace at [clihub.net](https://clihub.net)
- [ ] **Phase 4** — AI-assisted tool creation: `clihub create "extract tables from PDFs"`

<br>

## Development

```bash
git clone https://github.com/clihub-ai/clihub.git
cd clihub
pip install -e ".[dev]"
pytest                      # unit tests
ruff check src/ tests/      # lint
```

## Contributing

> [!TIP]
> The easiest way to contribute is to add a tool: `clihub convert <tool>`, fill in the TODOs, and open a PR.

Other ways to help:

1. **Improve search** — Better fuzzy matching in `src/clihub/registry/search.py`
2. **Add installers** — New package manager support in `src/clihub/installer/`
3. **Fix bugs** — Check [issues](https://github.com/clihub-ai/clihub/issues)

```bash
git checkout -b feature/your-feature
# make changes
pytest
git commit -m "feat: your feature"
git push origin feature/your-feature
```

## License

MIT &copy; [CliHub](https://clihub.net)
