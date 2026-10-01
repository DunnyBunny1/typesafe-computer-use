# Jev Computer Use

A computer-use engine and installable Codex skill: an LLM plans the task, **Jev selects actions and targets**, and the browser executes them with screenshots and result verification.

This is Donovan Murray's fork of [Aaron Levin's TypeSafe Computer Use](https://github.com/awlevin/typesafe-computer-use), retaining its MIT license and history. It adds adaptive browser planning, provider fallback, control handling repairs, completion verification, and a portable `$computer-use` skill. It does not train a new model.

**Measured:** 94/104 successes (90.4%) on an adapted MiniWoB++ subset, 5.7 seconds median, about $1.32 estimated inference for all 104 cases. These are short browser tasks, not a general desktop success rate or a SOTA claim. [Protocol, failures, costs and reproduction](docs/benchmark.md).

## Install the Codex skill

Requirements: Python 3.12+, [uv](https://docs.astral.sh/uv/getting-started/installation/), Google Chrome or Chromium, a [TypeSafe](https://typesafe.ai/) API key, and at least one supported LLM API key. The measured configuration used OpenAI models, with provider fallback. macOS is the locally tested platform; Linux browser support is included. Native Windows code is inherited and has not been accepted in this fork.

```sh
git clone https://github.com/DunnyBunny1/typesafe-computer-use.git
cd typesafe-computer-use
uv sync --frozen
uv run --frozen python scripts/install_skill.py
```

Configure keys in the ignored checkout `.env`:

```sh
cp .env.example .env
chmod 600 .env
# Edit .env: set TYPESAFE_API_KEY and OPENAI_API_KEY.
uv run --frozen computer-use doctor
```

Keep this checkout and its `.venv` in place: the skill points to that runtime. Installation defaults to `~/.codex/skills/computer-use`, honors `CODEX_HOME`, and accepts `--destination PATH`. Use `--replace` to update an existing skill; its previous files are backed up outside the active skills directory. Start a new Codex conversation if discovery is cached. No separate TypeSafe skill is needed.

### Try it

Ask Codex:

> Use $computer-use to find a round-trip flight from JFK to SFO, November 12–16, 2026, for one adult in economy. Apply nonstop only. Report one matching fare, airline, departure time and source link. Verify the dates and filter; do not book anything.

For a shorter task:

> Use $computer-use to open Python's official documentation, navigate to pathlib.Path.mkdir, and explain what parents=True and exist_ok=True do. Include the documentation URL.

Dates, fares and websites change; these are examples, not guaranteed outcomes. [Skill instructions](skills/computer-use/SKILL.md).

## Standalone CLI

```sh
uv tool install 'git+https://github.com/DunnyBunny1/typesafe-computer-use.git@v0.2.0.post1'
computer-use doctor
computer-use browser --url 'https://docs.python.org/3/library/pathlib.html'   --goal 'Find Path.mkdir and explain parents=True and exist_ok=True with the source URL.'
```

For a wheel/tool installation, put keys in `~/.config/jev-computer-use/.env`, export them, or set `COMPUTER_USE_ENV_FILE` to a private file. Process environment takes precedence, followed by that config file and checkout `.env`. Legacy `~/.env` contributes only `TYPESAFE_API_KEY`. Keys are not included in this repository.

The CLI prints a run folder containing `task.json`, `final-page.json`, `final.png` and per-step evidence. Default limits are 60 actions, 24 planning rounds and 180 seconds; an in-flight model request can exceed the time limit. Change them with `--steps`, `--rounds`, and `--seconds`. `--resume task.json` restores the goal and notes, not a lost browser login/session.

### Packaging

- Python package / CLI: `typesafe_computer_use`, `computer-use`.
- Portable skill: `skills/computer-use/`, installed by `scripts/install_skill.py`.
- Optional Codex plugin manifest: `.codex-plugin/plugin.json`, exposing the same skill. Plugin installation alone does **not** install the Python engine: install the standalone CLI first and put it on the host's PATH. This repository is not listed in a curated marketplace. Avoid installing both copies of the skill.
- Tagged source and wheel: [releases](https://github.com/DunnyBunny1/typesafe-computer-use/releases). The inherited PyPI package is not this fork; install from this GitHub URL or its release assets.

## How it works

```text
User goal → LLM subtask plan → Jev action/target → browser input
                    ↑                              ↓
              progress + verification ← DOM + screenshot
```

Easy tasks use a bounded Jev fast path. GPT-5.4 mini at low reasoning handles planning; dense visual tasks or stalls selectively use GPT-5.4. Exact form values bypass extra text generation; free text defaults to GPT-4.1 nano. Fallback tries configured providers only, records the actual model/usage, and disables unavailable endpoints for that run. The final benchmark used OpenRouter's OpenAI models and Fireworks fallback; provider availability affects reproducibility.

Controls include text fields, checkboxes, dropdowns, dates, nested scrolling, sliders, sortable-item dragging, CSS image buttons and SVG shapes. Fixes also cover stale targets, field labels, repeated-action stalls and verification popups.

## Boundaries

Browser mode uses isolated headless Chrome by default. For login, use `--headed --profile /path/to/dedicated-profile` and sign in yourself. Do not point it at your everyday browser profile. `--attach-port` is for an explicitly selected, dedicated single-tab CDP browser.

Native Mac control is available through `computer-use desktop --app TextEdit --goal 'Read the front document.'`. The named app must already be foreground, and the host needs macOS Accessibility and Screen Recording permissions. It moves the real mouse and keyboard. TextEdit has smoke coverage; no OSWorld desktop score is established. The original `clicker` command remains available; see the upstream documentation for its workflow.

Small visual references, iframe/shadow-root traversal, automatic tab switching and arbitrary canvas dragging remain weak or unsupported. CAPTCHA and missing login require user help. Verify consequential results: a model saying “done” is not ground truth. The agent does not provide a complete prompt-injection security boundary.

Page text and screenshots may go to the configured model providers; restrict `CLICKER_PLANNER_PROVIDERS` and `CLICKER_WRITER_PROVIDERS` to control that choice. Run artifacts remain on disk and may contain private page content. Do not publish your `.env`, profiles or run folders.

## Develop and evaluate

```sh
uv sync --frozen
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv build
```

Offline tests refuse real desktop input, browser connections and external network access. Live evaluations run separately. See [benchmark reproduction](docs/benchmark.md), [writer configuration](docs/writer-endpoints.md), [browser backend](docs/browser-backend.md), and [upstream OSWorld integration](docs/osworld.md). OSWorld integration is included but was not run for this release.

## Attribution

Original engine by [Aaron Levin](https://github.com/awlevin), powered by [TypeSafe/Jev](https://typesafe.ai/). MiniWoB++ is maintained by the [Farama Foundation](https://github.com/Farama-Foundation/miniwob-plusplus). Benchmark pages are downloaded separately; this fork publishes manifests and results. [MIT license](LICENSE).
