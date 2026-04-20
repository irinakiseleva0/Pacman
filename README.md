# Cyberpunk Pac-Man

Arcade maze-chasing reimagined as a neon district survival run.

`Cyberpunk Pac-Man` is a stylized Pac-Man reinterpretation built with Python and raylib. It expands the classic maze loop into a small arcade package with multiple modes, progression, unlockables, challenge boards, and a cinematic cyberpunk UI shell.

## At A Glance

- `4 modes`: Arcade, Endless, Challenge, Time Attack
- `meta progression`: career rank, achievements, run history, unlock tracks
- `cosmetic rewards`: themes, HUD packs, title variants
- `systems depth`: district modifiers, directives, ghost personalities, pressure escalation
- `presentation`: neon menu shell, controller support, capture mode

## Media

Release screenshots and a short gameplay GIF are planned for the next public polish pass.

The contributor-facing media template lives in:

- [docs/README-media-template.md](docs/README-media-template.md)

## Overview

This is not meant to be a plain classroom Pac-Man clone.

The project aims to feel like a compact premium arcade game:

- classic route-based Pac-Man rules
- a moody cyberpunk neon presentation
- multiple playable modes
- persistent profile progression
- unlockable rewards and meta goals

The strongest intended identity is:

- `retro rules, modern shell`
- `arcade clarity, cyberpunk atmosphere`
- `small game, strong product framing`

## Key Features

### Gameplay

- classic pellets, power seeds, cherries, teleports, and ghost pressure
- stronger feedback for pickups, ghost-eats, near-miss moments, route chains, and late-board tension
- district traits and run directives that change pacing and reward priorities
- more distinct ghost personalities with path-based navigation

### Modes

- `Arcade`
  - a chapter-style three-district run
- `Endless`
  - survival escalation with tiered pressure
- `Challenge`
  - curated trial-board style runs with unlockable elite trials
- `Time Attack`
  - countdown-driven routing with time banking on board clears

### Progression

- persistent profile saved locally
- career rank and long-term goals
- mode mastery
- challenge rank, credits, streaks, and trophies
- achievements and run history

### Unlockables

- themes
- HUD packs
- title variants
- directive packs
- elite districts
- elite trials

### Presentation

- cyberpunk neon shell UI
- cinematic menu flow
- controller support
- capture mode with `F10` for cleaner screenshots and clips

## Controls

### Keyboard

- `WASD` / Arrow Keys: move
- `Enter` / `Space`: confirm
- `Esc`: back / leave current screen
- `P`: pause
- `F10`: toggle capture mode

### Controller

- D-pad / left stick: move and navigate
- south face button: confirm
- east face button / back: cancel
- start: pause

## Installation

Requirements:

- Python `3.12` is the target runtime for this repo
- Python `3.13` may work, but is not the primary tested target
- `raylib==5.5.0.4`

### Runtime Install

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
source .venv/bin/activate
```

Install runtime dependencies:

```bash
pip install -r requirements.txt
```

Run directly:

```bash
python main.py
```

Or run through the packaged console entrypoint:

```bash
pip install -e .
cyberpunk-pacman
```

### Development Install

Install runtime + local tooling:

```bash
pip install -r requirements-dev.txt
```

or:

```bash
pip install -e .[dev]
```

Run the repo checks in one command:

```bash
python -m checks
```

After `pip install -e .[dev]`, you can also use:

```bash
cyberpunk-pacman-check
```

### OS Notes

Windows:

- this is the primary tested environment
- `pip install -r requirements.txt` should be enough once Python `3.12` is installed

Linux:

- you may need system graphics/audio libraries for raylib-backed windows
- if the app fails to open a window, install the usual X11 / OpenGL / ALSA packages for your distro first

macOS:

- not the primary tested target for this repo
- expect to verify raylib/windowing support locally before relying on it

### Tested On

- Windows 11
- Python `3.12`
- `raylib==5.5.0.4`

## Project Structure

```text
assets/      textures and runtime-loaded art
core/        context, progression, scene base classes, raylib wrapper
data/config/ JSON-backed runtime, difficulty, and layout tuning
entities/    pacman, ghosts, pellets, cherry, walls, teleports
maps/        map definitions and board loading
scenes/      menu flow, gameplay scene, pause/result, meta screens
ui/          layout, HUD, navigation, controls, theme drawing
utils/       profile, score, audio, visual effects, sprites
main.py      app entry point and scene loop
pyproject.toml packaging metadata and console entrypoint
```

## Save Data

Generated runtime files:

- `%AppData%/Cyberpunk Pac-Man/saves/profile.json` on Windows
- `~/.local/share/Cyberpunk Pac-Man/saves/profile.json` on Linux
- `%AppData%/Cyberpunk Pac-Man/saves/scores.json` on Windows
- `~/.local/share/Cyberpunk Pac-Man/saves/scores.json` on Linux

Save files are stored in the user data directory, not in the repository. Writes use an atomic `tmp -> replace` flow, and older `data/saves/` files are migrated automatically when found.

## Repository Notes

Useful next GitHub-side improvements:

- repository description
- topic tags
- screenshots / GIF previews
- first release

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

Publishing helper docs:

- [docs/github-publishing-checklist.md](docs/github-publishing-checklist.md)
- [docs/README-media-template.md](docs/README-media-template.md)

## Roadmap

### Current Prototype

- multi-mode arcade shell with progression, unlocks, and cyberpunk presentation
- active refactors around scene systems, rendering, saves, and test coverage

### Next Gameplay Milestone

- richer district-specific enemy pressure
- more map-specific mechanics
- more readable mastery- and style-driven progression

### Next Polish Milestone

- stronger release-ready gameplay screenshots and GIFs
- more reward-track visualization
- additional elite trials and unlock paths
- cleaner release/changelog cadence tied to GitHub releases

## Status

Active prototype moving toward a stronger portfolio / release-quality presentation.
