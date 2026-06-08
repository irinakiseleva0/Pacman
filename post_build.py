#!/usr/bin/env python3
"""Patch build/web/index.html after pygbag build."""
import re
from pathlib import Path

html_path = Path("build/web/index.html")
if not html_path.exists():
    print("ERROR: build/web/index.html not found. Run pygbag --build first.")
    exit(1)

html = html_path.read_text(encoding="utf-8")

# 1. Restore exact canvas size
html = re.sub(r'fb_width\s*:\s*"[^"]*"', 'fb_width : "800"', html)
html = re.sub(r'fb_height\s*:\s*"[^"]*"', 'fb_height : "600"', html)

# 2. Fix aspect ratio
html = re.sub(r'fb_ar\s*:\s*[\d.]+', 'fb_ar   :  1.333', html)

# 3. Black background, no grey
html = re.sub(r'background-color\s*:\s*powderblue',
              'background-color: #000000', html)

# 4. Body fullscreen
html = re.sub(
    r'(body\s*\{[^}]*font-family[^}]*\})',
    '''body {
            font-family: arial;
            margin: 0;
            padding: 0;
            background-color: #000000;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
        }''',
    html, flags=re.DOTALL
)

# 5. Center canvas with letterbox
html = re.sub(
    r'canvas\.emscripten\s*\{[^}]*\}',
    '''canvas.emscripten {
            border: 0px none !important;
            background-color: transparent !important;
            z-index: 5 !important;
            padding: 0 !important;
            margin: 0 !important;
            position: fixed !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            max-width: 100vw !important;
            max-height: 100vh !important;
            width: min(100vw, calc(100vh * 1.3333333333)) !important;
            height: auto !important;
        }''',
    html, flags=re.DOTALL
)

html_path.write_text(html, encoding="utf-8")
print("post_build.py: patched build/web/index.html successfully")
