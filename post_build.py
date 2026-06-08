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
            border: 0px none;
            background-color: transparent;
            z-index: 5;
            padding: 0;
            margin: 0;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }''',
    html, flags=re.DOTALL
)

html_path.write_text(html, encoding="utf-8")
print("post_build.py: patched build/web/index.html successfully")
