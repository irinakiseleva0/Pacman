# Cyberpunk Pac-Man

[![Deploy](https://github.com/irinakiseleva0/Pacman/actions/workflows/deploy.yml/badge.svg)](https://irinakiseleva0.github.io/Pacman)
[![CI](https://github.com/irinakiseleva0/Pacman/actions/workflows/ci.yml/badge.svg)](https://github.com/irinakiseleva0/Pacman/actions)

A Python/raylib arcade game that reimagines Pac-Man as a neon cyberpunk district run.

The project keeps the classic Pac-Man loop: eat pellets, route through the maze, avoid ghosts, use power seeds, clear boards, and chase high scores. Around that core it adds a polished arcade shell with modes, progression, unlocks, animated UI, cyberpunk visual effects, and local save data.

## Features

- Classic Pac-Man-style maze gameplay with pellets, power seeds, cherries, ghosts, teleports, and level clears.
- Multiple modes: Arcade, Endless, Challenge, and Time Attack.
- Persistent local profile with rank, achievements, mastery, unlocks, run history, and high scores.
- Difficulty presets for Easy, Normal, and Hard.
- Cyberpunk UI shell with animated menus, neon panels, scanline effects, controller support, and capture mode.
- Distinct ghost behavior and visual intent cues.
- Local tests for game flow, storage, progression, HUD data, movement, and content mechanics.

## Requirements

- Python `3.12`
- `raylib==5.5.0.4`

Python `3.13` may work, but Python `3.12` is the primary target.

## Setup

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install runtime dependencies:

```powershell
pip install -r requirements.txt
```

Run the game:

```powershell
python main.py
```

For development checks:

```powershell
pip install -r requirements-dev.txt
python -m checks
```

## Web Frontend

A separate Vite/React/TypeScript showcase site lives in `web/`. It presents the game as a polished cyberpunk portfolio page with preview slots, feature cards, mock career stats, achievements, and score charts. The frontend is isolated from the Python/raylib game and does not change game logic.

Run it from the `web/` folder:

```powershell
npm install
npm run dev
npm run build
npm run preview
```

## Controls

- `WASD` or Arrow Keys: move
- `Enter` or `Space`: confirm
- `Esc`: back/menu
- `P`: pause
- `F10`: capture mode

Controller support:

- D-pad or left stick: move/menu navigation
- South face button: confirm
- East face button/back: cancel
- Start: pause

## Project Structure

```text
assets/       runtime-loaded textures and art helpers
core/         game context, config, progression, loop, scene base classes
data/config/  JSON tuning for runtime, layouts, and difficulties
entities/     Pac-Man, ghosts, pickups, walls, gates, barriers
maps/         board definitions and map loading
scenes/       menu, gameplay, pause, result, options, modes, progression screens
ui/           cyberpunk style tokens, components, layout helpers, HUD, controls
utils/        audio, storage, visual effects, sprites
tests/        unit tests for game systems
```

## UI Direction

The current UI direction is a dark cyberpunk arcade terminal:

- near-black backgrounds
- cyan, magenta, and gold signal colors
- sharp neon panel borders
- scanlines and subtle animated grids
- consistent button, panel, badge, and progress components
- polished HUD and result screens without changing core gameplay

## Save Data

Save files are stored in the user data directory, not in the repository.

Windows:

```text
%AppData%/Cyberpunk Pac-Man/saves/profile.json
%AppData%/Cyberpunk Pac-Man/saves/scores.json
```

Linux:

```text
~/.local/share/Cyberpunk Pac-Man/saves/profile.json
~/.local/share/Cyberpunk Pac-Man/saves/scores.json
```

## Roadmap

Near-term:

- Continue polishing menu, pause, result, and options screens.
- Add cleaner screen transitions and more consistent layout helpers.
- Improve score popups, pickup particles, and readable ghost feedback.
- Tune input feel, frame stability, and visual jitter.
- Add release screenshots and gameplay GIFs.

Later:

- Add a Django backend for accounts, leaderboard sync, run history, and cloud saves.
- Add a React dashboard for profile stats, run analytics, achievements, and admin/content tools.
- Keep the Python/raylib game client as the playable arcade experience.

## License

MIT. See [LICENSE](LICENSE).

---

## Browser version (pygbag)

The `pygbag` branch contains a WebAssembly port playable at
[irinakiseleva0.github.io/Pacman](https://irinakiseleva0.github.io/Pacman).

**Build locally:**

```powershell
git checkout pygbag
pip install pygame pygbag
python -m pygbag --build --width 800 --height 600 .
python post_build.py
```

**Run locally after building:**

```powershell
python -m http.server 8000 --directory build/web
```

Then open `http://localhost:8000` in a browser.
Do not open `index.html` directly via `file://` — pygbag requires an HTTP server.

**Auto-deploy:** pushing to the `pygbag` branch triggers GitHub Actions,
which builds and deploys to `gh-pages` automatically.

---

## Mobile layout

The game includes a mobile touch control overlay.
To enable it, set `layout_name = "mobile"` in `core/balance.py`
or let the pygbag version detect it automatically based on screen width (≤480px).

The D-pad renders in the bottom-left corner; pause button in the bottom-right.

---
