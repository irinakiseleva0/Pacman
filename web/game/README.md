# Browser game build

This folder documents the experimental Python-to-WASM path for the raylib game.

## Build

From the repository root:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-wasm.txt
.venv\Scripts\python.exe -m pygbag --disable-sound-format-error --build main.py
```

Pygbag writes its build to `build/web/`. Copy the generated files into `web/public/game/` before building the Vite showcase:

```powershell
Copy-Item -Recurse -Force build\web\* web\public\game\
cd web
npm.cmd run build
```

From `web/`, the same Pygbag build can be started with:

```powershell
npm.cmd run build:game
```

## Current limitation

This project uses Python `raylib` bindings. Pygbag is the shortest experimental route to browser delivery, but browser runtime support depends on whether those bindings can resolve under the bundled Python/WebAssembly environment. If that blocks, the next production path is to port the core movement and collision loop to C or TypeScript and keep the surrounding UI in the React showcase.
