#!/usr/bin/env python3
"""Patch build/web/index.html after pygbag build."""
import re
from pathlib import Path

from utils.logger import get_logger, setup_logging


setup_logging()
log = get_logger(__name__)

html_path = Path("build/web/index.html")
if not html_path.exists():
    log.error("build/web/index.html not found. Run pygbag --build first.")
    exit(1)

build_dir = html_path.parent


def _normalize_artifact(pattern: str, target_name: str) -> str:
    target = build_dir / target_name
    candidates = sorted(
        path
        for path in build_dir.glob(pattern)
        if path.name != target_name and path.is_file()
    )
    if candidates:
        if target.exists():
            target.unlink()
        candidates[0].replace(target)
    if not target.exists():
        log.error("build/web/%s not found after pygbag build.", target_name)
        exit(1)
    return target_name


apk_name = _normalize_artifact("*.apk", "pacman.apk")
archive_name = _normalize_artifact("*.tar.gz", "pacman.tar.gz")
(build_dir / ".nojekyll").write_text("", encoding="utf-8")

html = html_path.read_text(encoding="utf-8")
html = re.sub(r'platform\.fopen\("[^"]+\.apk"', f'platform.fopen("{apk_name}"', html)
html = re.sub(r'platform\.fopen\("[^"]+\.tar\.gz"', f'platform.fopen("{archive_name}"', html)
html = re.sub(r'Loading [^<\n]+ from [^<\n]+', f'Loading pacman from {apk_name}', html)

# 1. Restore exact canvas size
html = re.sub(r'fb_width\s*:\s*"[^"]*"', 'fb_width : "800"', html)
html = re.sub(r'fb_height\s*:\s*"[^"]*"', 'fb_height : "600"', html)

# 2. Fix aspect ratio
html = re.sub(r'fb_ar\s*:\s*[\d.]+', 'fb_ar   :  1.333', html)

# 3. Autorun — no click required
html = re.sub(r'autorun\s*:\s*\d+', 'autorun : 1', html)

# 4. Black background, no grey
html = re.sub(r'background-color\s*:\s*powderblue',
              'background-color: #000000', html)

# 5. Body fullscreen
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

# 6. Center canvas with letterbox
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
resource_hints = f'''    <link rel="preconnect" href="https://pygame-web.github.io" crossorigin>
    <link rel="dns-prefetch" href="//pygame-web.github.io">
    <link rel="preload" href="{archive_name}" as="fetch">
'''
html = re.sub(r'\s*<meta name="viewport" content="width=device-width, initial-scale=1\.0,\s*maximum-scale=1\.0,\s*user-scalable=no">\s*',
              '\n', html, flags=re.DOTALL)
html = re.sub(r'\s*<link rel="preconnect" href="https://pygame-web\.github\.io" crossorigin>\s*', '\n', html)
html = re.sub(r'\s*<link rel="dns-prefetch" href="//pygame-web\.github\.io">\s*', '\n', html)
html = re.sub(r'\s*<link rel="preload" href="[^"]+\.tar\.gz" as="fetch"(?: crossorigin(?:="[^"]*")?)?>\s*', '\n', html)
html = html.replace("</head>", f"    {viewport_meta}\n{resource_hints}</head>", 1)

canvas_rendering_style = '''        canvas {
            image-rendering: pixelated;
            image-rendering: crisp-edges;
        }

'''

html = re.sub(r'\s*canvas\s*\{\s*image-rendering:\s*pixelated;\s*image-rendering:\s*crisp-edges;\s*\}\s*',
              '\n', html, flags=re.DOTALL)

loader_style = '''        #transfer {
            position: fixed;
            inset: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 14px;
            background:
                linear-gradient(rgba(0, 238, 255, 0.08) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 238, 255, 0.08) 1px, transparent 1px),
                #02030b;
            background-size: 28px 28px;
            color: #f7fbff;
            z-index: 20;
        }

        #transfer::before {
            content: "PACMAN";
            color: #ffe66d;
            font: bold 42px arial, sans-serif;
            letter-spacing: 0;
            text-shadow: 0 0 14px rgba(255, 230, 109, 0.55);
        }

        #status {
            display: block;
            margin: 0;
            color: #7df9ff;
            font: bold 16px arial, sans-serif;
            text-transform: uppercase;
        }

        #progress {
            width: min(72vw, 420px);
            height: 18px;
            border: 2px solid #1cf7ff;
            border-radius: 0;
            background: #080b18;
            box-shadow: 0 0 18px rgba(28, 247, 255, 0.28);
        }

        #progress::-webkit-progress-bar {
            background: #080b18;
        }

        #progress::-webkit-progress-value {
            background: linear-gradient(90deg, #ffe66d, #ff4d8d);
        }

        #progress::-moz-progress-bar {
            background: linear-gradient(90deg, #ffe66d, #ff4d8d);
        }

        #infobox {
            background: #050817;
            border: 2px solid #1cf7ff;
            color: #ffe66d;
            box-shadow: 0 0 24px rgba(28, 247, 255, 0.35);
            text-transform: uppercase;
        }

'''

html = re.sub(r'\s*#transfer\s*\{.*?\}\s*#transfer::before\s*\{.*?\}\s*#status\s*\{.*?\}\s*#progress\s*\{.*?\}\s*#progress::-webkit-progress-bar\s*\{.*?\}\s*#progress::-webkit-progress-value\s*\{.*?\}\s*#progress::-moz-progress-bar\s*\{.*?\}\s*#infobox\s*\{.*?\}\s*',
              '\n', html, flags=re.DOTALL)
html = html.replace("</style>", f"{canvas_rendering_style}{loader_style}    </style>", 1)

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
log.info("patched build/web/index.html successfully")