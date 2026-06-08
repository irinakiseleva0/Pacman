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
            max-width: 100vw;
            max-height: 100vh;
            width: min(100vw, calc(100vh * 1.3333333333));
            height: auto;
        }''',
    html, flags=re.DOTALL
)

viewport_meta = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">'
html = re.sub(r'\s*<meta name="viewport" content="width=device-width, initial-scale=1\.0,\s*maximum-scale=1\.0,\s*user-scalable=no">\s*',
              '\n', html, flags=re.DOTALL)
html = html.replace("</head>", f"    {viewport_meta}\n</head>", 1)

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
    var sw = window.innerWidth;
    var sh = window.innerHeight;
    var scale = Math.min(sw / 800, sh / 600);
    var cw = Math.round(800 * scale);
    var ch = Math.round(600 * scale);
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
