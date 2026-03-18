<p align="center">
  <br>
  <code>&nbsp;$ clihub&nbsp;</code>
  <br>
  <br>
  <strong>The App Store for AI Agents</strong>
  <br>
  Discover, install, and manage CLI tools.
  <br>
  The protocol is <code>--help</code>. That's it.
  <br>
  <br>
  <a href="https://clihub.net">Website</a> &middot; <a href="https://github.com/clihub-ai/clihub/issues">Issues</a> &middot; <a href="#roadmap">Roadmap</a>
  <br>
  <br>
  <a href="https://pypi.org/project/clihub"><img alt="PyPI" src="https://img.shields.io/pypi/v/clihub?style=flat-square&color=00ff88&labelColor=1a1a2e"></a>
  <a href="https://github.com/clihub-ai/clihub/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue?style=flat-square&labelColor=1a1a2e"></a>
  <a href="https://www.python.org/downloads/"><img alt="Python" src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&labelColor=1a1a2e"></a>
</p>

---

Every CLI tool is a superpower your agent can wield. MCP dumps full schemas into every prompt — one server with 20 tools adds 8,000+ tokens. CLI tools load **nothing** until the agent runs `--help`.

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

## Highlights

- **Zero ambient cost** — No schemas injected into context. Tools are discovered on demand via `--help`.
- **35+ curated tools** — jq, ripgrep, ffmpeg, pandoc, httpie, and more. Each with agent-ready hints.
- **Auto-detect installer** — Picks the right package manager (pip, npm, brew, cargo) automatically.
- **Agent-native** — Every command supports `--json` for structured output. Exit code 0/1/2 for success/error/not-found.
- **Offline-first** — Bundled registry works without internet. No backend required.

## Install

```bash
pip install clihub
```

or with [pipx](https://pipx.pypa.io/):

```bash
pipx install clihub
```

Requires Python 3.10+.

## Usage

### Search

Find tools with natural language. Fuzzy matches against name, description, tags, and categories.

```bash
clihub search "json processing"
clihub search "pdf" --category documents
clihub search "video" --limit 5
```

### Install

One command. Auto-detects the right package manager.

```bash
clihub install jq            # → brew install jq
clihub install httpie         # → pip install httpie
clihub install ripgrep --via cargo   # force a specific installer
```

### Info

View full metadata. If the tool is installed, shows its `--help` output too.

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

### List

Browse the registry by category. See what's already on your system.

```bash
clihub list                    # show all categories
clihub list --category data    # tools in a category
clihub list --installed        # what's on your PATH
```

### Doctor

Check system readiness — which package managers are available.

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
│ ✓    │ docker         │ docker        │
│ ✓    │ git            │ git           │
│ ✗    │ ~/.clihub/     │ config dir    │
└──────┴────────────────┴───────────────┘
```

## For AI Agents

CliHub is built for agents to use directly. Pass `--json` to any command for structured output:

```bash
# Agent discovers tools
clihub --json search "convert pdf to markdown"

# Agent installs what it needs
clihub install pandoc

# Agent learns the tool
pandoc --help
```

**Why CLI over MCP?**

| | MCP | CLI (CliHub) |
|---|---|---|
| Context cost | 8,000–15,000 tokens per server | 0 tokens until `--help` |
| Discovery | Schema dumped into every prompt | On-demand via `search` |
| LLM familiarity | Needs schema learning | Trained on billions of shell examples |
| Composability | Single-tool calls | Unix pipes: `curl | jq | csv` |
| Error handling | Custom error formats | Exit codes + stderr |

## The Protocol

Every tool in CliHub follows one simple protocol:

```yaml
# tool.yaml
name: "image-resize"
version: "2.1.0"
description: "Resize, crop & convert images"
install:
  method: "pip"
  package: "image-resize-cli"
agent_hints:
  when_to_use: "resize or convert images"
  example: "image-resize in.png -w 800"
```

The tool self-documents via `--help`. That's the entire protocol. No JSON-RPC, no schema injection, no server to maintain.

## Registry

CliHub ships with a curated registry of 35+ battle-tested CLI tools:

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

## Roadmap

CliHub is in active development. Here's what's coming:

- [x] **Phase 1** — CLI core: search, install, info, list, doctor
- [ ] **Phase 2** — Registry API: remote search, `clihub publish`, `clihub update`
- [ ] **Phase 3** — Web marketplace at [clihub.net](https://clihub.net)
- [ ] **Phase 4** — AI-assisted tool creation: `clihub create "extract tables from PDFs"`

## Development

```bash
git clone https://github.com/clihub-ai/clihub.git
cd clihub
pip install -e ".[dev]"
pytest
```

## Contributing

Contributions are welcome. Here's how:

1. **Add tools to the registry** — Edit `src/clihub/data/registry.json`
2. **Improve search** — Better fuzzy matching in `src/clihub/registry/search.py`
3. **Add installers** — New package manager support in `src/clihub/installer/`
4. **Fix bugs** — Check [issues](https://github.com/clihub-ai/clihub/issues)

```bash
git checkout -b feature/your-feature
# make changes
pytest
git commit -m "feat: your feature"
git push origin feature/your-feature
```

## License

MIT &copy; [CliHub](https://clihub.net)
