# Cyberpunk Pac-Man

[![Deploy](https://github.com/irinakiseleva0/Pacman/actions/workflows/deploy.yml/badge.svg)](https://irinakiseleva0.github.io/Pacman)
[![CI](https://github.com/irinakiseleva0/Pacman/actions/workflows/ci.yml/badge.svg)](https://github.com/irinakiseleva0/Pacman/actions)

A neon cyberpunk reimagining of Pac-Man, built in Python/pygame and ported to JavaScript.

## 🎮 Play

| Version | Tech | Link |
|---------|------|------|
| JS Version | Vanilla JavaScript + Canvas API | [Play](https://irinakiseleva0.github.io/Pacman/showcase/game.html) |
| Python Version | Python/pygame via WebAssembly (pygbag) | [Play](https://irinakiseleva0.github.io/Pacman/) |
| Showcase | React + Vite | [Open](https://irinakiseleva0.github.io/Pacman/showcase/) |

## ✨ Features

- Classic Pac-Man maze gameplay: pellets, power seeds, ghosts, teleports, level clears
- Multiple modes: Arcade, Endless, Challenge, Time Attack
- Persistent local profile: rank, achievements, unlocks, run history, high scores
- Cyberpunk UI: animated menus, neon panels, scanline effects, controller support
- Distinct ghost behavior and visual cues
- Leaderboard and Daily Challenge via Django REST API
- JS port: 60 FPS, no lag, instant load in any browser

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Game (original) | Python 3.12, pygame, raylib |
| Browser port | pygbag (WebAssembly) |
| JS version | Vanilla JavaScript, Canvas API |
| Showcase frontend | React, Vite, Tailwind CSS |
| Backend API | Django REST Framework |
| Deploy | GitHub Pages + Railway |
| CI/CD | GitHub Actions |

## 🚀 Run Locally

```bash
git clone https://github.com/irinakiseleva0/Pacman.git
cd Pacman
python -m venv .venv
.venv/Scripts/activate  # Windows
pip install -r requirements.txt
python main.py
```

## Requirements

- Python 3.12
- raylib 5.5.0.4
