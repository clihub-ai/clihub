<p align="center">
  <br>
  <a href="https://clihub.net">
    <img src="assets/readme-banner-transparent.svg" alt="clihub" width="500">
  </a>
  <br>
  <br>
  <strong>The package manager for CLI tools — built for AI agents.</strong>
  <br>
  <br>
  <a href="https://pypi.org/project/clihub-ai"><img alt="PyPI" src="https://img.shields.io/pypi/v/clihub-ai?style=flat-square&color=00ff88&labelColor=1a1a2e"></a>
  <a href="https://github.com/clihub-ai/clihub/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue?style=flat-square&labelColor=1a1a2e"></a>
  <a href="https://www.python.org/downloads/"><img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&labelColor=1a1a2e"></a>
  <a href="https://github.com/clihub-ai/clihub/actions"><img alt="Tests" src="https://img.shields.io/github/actions/workflow/status/clihub-ai/clihub/ci.yml?style=flat-square&labelColor=1a1a2e&label=tests"></a>
</p>

<p align="center">
  <a href="#get-started">Get Started</a> &middot;
  <a href="#how-agents-use-it">How Agents Use It</a> &middot;
  <a href="#all-commands">All Commands</a> &middot;
  <a href="#add-your-tool">Add Your Tool</a>
</p>

---

Your AI agent needs to resize an image. Or parse JSON. Or deploy to S3.

It knows *how* — it's seen millions of shell examples in training. But it doesn't know *what's installed* on this machine, or *what tools exist* for the job.

**CliHub solves this.** 100+ curated CLI tools, each with agent-readable metadata. Two commands and your agent goes from "I need to process JSON" to running `jq`.

```
Agent: "I need to parse and filter JSON data"
  ↓
$ clihub list --json          → agent reads 100+ tool descriptions, picks jq
$ clihub install jq           → installed via brew in 3 seconds
$ jq '.users[] | .name' data.json
  ↓
Done. No MCP server. No schema. No tokens wasted.
```

<br>

## Why Not MCP?

MCP tools inject **thousands of tokens into every prompt** — even when the agent doesn't use them. A single MCP server with 20 tools adds 8,000–15,000 tokens of schema to every request.

CLI tools cost **zero tokens** until the agent actually runs one.

|  | MCP Server | CLI via CliHub |
|---|---|---|
| **Idle cost** | 8,000+ tokens per prompt | 0 tokens |
| **Discovery** | Schemas dumped into context | `clihub list --json` on demand |
| **LLM familiarity** | Must learn custom schemas | Trained on billions of shell examples |
| **Composability** | One tool per call | Unix pipes: `curl \| jq \| grep` |
| **Ecosystem** | Hundreds of MCP servers | Thousands of CLI tools, built over 50 years |

> [!TIP]
> LLMs are *already* trained on CLI tools. Your agent knows how to use `jq`, `ffmpeg`, `curl`, and `grep` — it just needs to discover and install them. That's what CliHub does.

<br>

## Get Started

```bash
pip install clihub-ai
```

That's it. Now your agent (or you) can discover, install, and use 100+ tools:

```bash
clihub list --json              # browse everything (the agent's primary workflow)
clihub search "resize images"   # fuzzy search for humans
clihub install imagemagick      # auto-detects brew/pip/npm/cargo
clihub info jq --json           # full metadata + help text
clihub doctor                   # check which package managers are available
```

> [!NOTE]
> Requires Python 3.10+. The CLI entry point is `clihub`.

<br>

## How Agents Use It

The design philosophy is simple: **CliHub is a dumb pipe. The agent is the brain.**

An agent doesn't need a smart search algorithm — it *is* a search algorithm. It just needs the data. CliHub gives it a structured catalog with descriptions, categories, tags, and usage hints. The agent decides what fits.

### The Two-Step Workflow

```bash
# Step 1: Agent reads the catalog
$ clihub list --json
[
  {
    "name": "jq",
    "description": "Lightweight command-line JSON processor.",
    "categories": ["data", "json"],
    "agent_hints": {
      "when_to_use": "Parse, filter, or transform JSON data",
      "example_usage": ["jq '.users[] | select(.age > 30)' data.json"]
    },
    "install": {"method": "brew", "package": "jq"}
  },
  ... 103 more tools
]

# Step 2: Agent installs what it needs
$ clihub install jq --json
{"status": "success", "message": "Installed jq@1.7.1 via brew"}
```

That's the entire integration. Two calls. The full catalog is ~87KB — fits in any context window with room to spare.

### Every Output is Machine-Readable

Pass `--json` to any command. Every response is valid JSON. Every error goes to stderr. Exit codes are predictable: `0` success, `1` error, `2` not found.

```bash
# All of these return clean, parseable JSON:
clihub list --json                      # full catalog
clihub list --category database --json  # slice by category
clihub list --installed --json          # what's on PATH
clihub info ruff --json                 # single tool detail
clihub search "kubernetes" --json       # fuzzy search results
clihub doctor --json                    # system readiness
```

### Composable with Any Tool

```bash
# Find all installed Python tools
clihub list --installed --json | jq '[.[] | select(.categories[] == "python")]'

# Get example commands for a tool
clihub info ffmpeg --json | jq '.agent_hints.example_usage'

# Check which package managers are missing
clihub doctor --json | jq '[.[] | select(.ok == false) | .check]'
```

<br>

## What's in the Registry

**104 tools** across 17 categories. Every tool has `agent_hints` with natural-language descriptions and example commands.

| Category | Tools | Example Use Case |
|---|---|---|
| **Data** | jq, yq, csvkit, xsv, dasel, gron, fx, jless | Parse JSON, transform YAML, query CSV |
| **Database** | mycli, pgcli, litecli, iredis, usql | Connect to MySQL, Postgres, Redis, SQLite |
| **Search & Files** | ripgrep, fd, fzf, bat, eza, lsd, broot, ranger, nnn | Find files, search code, browse directories |
| **Network** | httpie, curl, wget, aria2, ngrok, mosh, nmap | HTTP requests, downloads, tunneling, scanning |
| **Python** | ruff, black, mypy, uv, pipx, poetry | Lint, format, type-check, manage packages |
| **JavaScript** | prettier, eslint, tsx, npm-check-updates | Format, lint, run TypeScript, update deps |
| **Dev Tools** | gh, lazygit, gitui, tokei, hyperfine, just, grex, shellcheck | Git workflows, benchmarks, task running, linting |
| **Docker & Cloud** | lazydocker, k9s, dive, act, awscli, terraform | Containers, Kubernetes, CI, infrastructure |
| **Media** | ffmpeg, imagemagick, yt-dlp, svgo, gifsicle, asciinema | Video, images, downloads, GIFs, recordings |
| **Documents** | pandoc, glow | Convert Markdown/HTML/PDF, render in terminal |
| **Text** | sd, choose, sad | Find-and-replace, cut columns, batch edits |
| **Editors** | neovim, micro, helix | Terminal-based text editing |
| **Productivity** | tmux, tldr, zoxide, starship, taskwarrior, watson, nb | Sessions, docs, navigation, tasks, time tracking |
| **Release** | semantic-release, release-it, commitizen, cookiecutter | Versioning, changelogs, project scaffolding |
| **Security** | openssl, age, mkcert | TLS, encryption, local certificates |
| **System** | htop, btop, procs, bandwhich, pv, ncdu, dust | Processes, bandwidth, disk usage, pipelines |
| **Fun** | lolcat, fortune, cmatrix | Rainbow text, quotes, Matrix rain |

<br>

## All Commands

| Command | What it Does | Agent Flag |
|---|---|---|
| `clihub list` | Browse the full tool catalog | `--json` returns all 104 tools with metadata |
| `clihub search <query>` | Fuzzy-search by keyword | `--json` returns matching tools |
| `clihub install <tool>` | Install via auto-detected package manager | `--json` returns status |
| `clihub info <tool>` | Show metadata, hints, and `--help` output | `--json` returns full detail |
| `clihub doctor` | Check system readiness | `--json` returns check results |
| `clihub convert <tool>` | Auto-generate a manifest from installed tool | `--json` returns Tool object |
| `clihub submit <file>` | Validate manifest for registry submission | `--json` returns validation |

<br>

## Add Your Tool

Got a CLI tool? Add it to CliHub in 30 seconds:

```bash
clihub convert mytool           # auto-detects version, description, license, homepage
vim clihub.yaml                 # fill in categories, tags, agent_hints
clihub submit clihub.yaml       # validates and prints PR-ready JSON
```

`convert` detects metadata from `--help`, `--version`, and package managers (brew, pip, npm, cargo). You fill in what it can't detect: categories, tags, and `agent_hints.when_to_use` — the natural-language description that tells an AI agent *when to reach for your tool*.

```yaml
name: mytool
version: "2.1.0"
description: "Do something useful from the terminal"
categories: [utilities]
tags: [useful, fast]
install:
  method: brew
  package: mytool
agent_hints:
  when_to_use: "When you need to do something useful quickly"
  example_usage:
    - "mytool input.txt --output result.json"
    - "cat data.csv | mytool --format json"
```

Then [open a PR](https://github.com/clihub-ai/clihub) adding it to the registry.

<br>

## Roadmap

- [x] **Phase 1** — CLI core: search, install, info, list, doctor
- [x] **Phase 1.5** — 104 tools, `convert` + `submit`, PyPI release
- [ ] **Phase 2** — Registry API with semantic search (FastAPI + pgvector)
- [ ] **Phase 3** — Web marketplace at [clihub.net](https://clihub.net)
- [ ] **Phase 4** — AI-assisted tool creation: `clihub create "extract tables from PDFs"`

## Development

```bash
git clone https://github.com/clihub-ai/clihub.git
cd clihub
pip install -e ".[dev]"
pytest                      # unit tests
ruff check src/ tests/      # lint
```

## Contributing

The easiest way to contribute: `clihub convert <tool>`, fill in the TODOs, [open a PR](https://github.com/clihub-ai/clihub/issues).

## License

MIT &copy; [CliHub](https://clihub.net)
