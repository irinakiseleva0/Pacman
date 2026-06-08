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

canvas_rendering_style = '''        canvas {
            image-rendering: pixelated;
            image-rendering: crisp-edges;
        }

'''

html = re.sub(r'\s*canvas\s*\{\s*image-rendering:\s*pixelated;\s*image-rendering:\s*crisp-edges;\s*\}\s*',
              '\n', html, flags=re.DOTALL)
html = html.replace("</style>", f"{canvas_rendering_style}    </style>", 1)

resize_script = '''<script>
var _orig_window_resize = window._orig_window_resize ||
                          window.window_resize || function(){};
window._orig_window_resize = _orig_window_resize;
window.window_resize = function() {
    _orig_window_resize.apply(this, arguments);
    var c = document.getElementById('canvas');
    if (!c) return;
    var dpr = window.devicePixelRatio || 1;
    var sw = window.innerWidth, sh = window.innerHeight;
    var scale = Math.min(sw / 800, sh / 600);
    var cw = Math.round(800 * scale);
    var ch = Math.round(600 * scale);
    // Set actual pixel size for sharpness
    c.width  = Math.round(800 * scale * dpr);
    c.height = Math.round(600 * scale * dpr);
    c.style.cssText = [
        'position:fixed',
        'left:' + Math.round((sw - cw) / 2) + 'px',
        'top:' + Math.round((sh - ch) / 2) + 'px',
        'width:' + cw + 'px',
        'height:' + ch + 'px',
        'margin:0',
        'transform:none',
        'z-index:5',
        'border:0',
        'image-rendering:pixelated',
        'image-rendering:crisp-edges'
    ].join(';');
};
window.addEventListener('resize', window.window_resize);
setTimeout(window.window_resize, 500);
setTimeout(window.window_resize, 1500);
setTimeout(window.window_resize, 3000);
</script>'''

html = re.sub(r'\s*<script>\s*var _orig_window_resize = .*?</script>\s*',
              '\n', html, flags=re.DOTALL)
html = html.replace("</body>", f"{resize_script}\n</body>", 1)

html_path.write_text(html, encoding="utf-8")
print("post_build.py: patched build/web/index.html successfully")
