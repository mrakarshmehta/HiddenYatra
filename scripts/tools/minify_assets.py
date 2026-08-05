"""
HiddenYatra — Static Asset Minifier Script
Minifies all CSS and JS files in static/ to .min.css and .min.js
Usage: python scripts/tools/minify_assets.py
"""
import os
import re


def minify_css(css):
    """Minify CSS by removing comments and unnecessary whitespace."""
    css = re.sub(r'/\*[\s\S]*?\*/', '', css)
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([\{\}:;,])\s*', r'\1', css)
    return css.strip()


def minify_js(js):
    """Minify JS by removing single/multi-line comments and extra blank lines."""
    js = re.sub(r'//.*', '', js)
    js = re.sub(r'/\*[\s\S]*?\*/', '', js)
    js = re.sub(r'^\s+|\s+$', '', js, flags=re.MULTILINE)
    js = re.sub(r'\n+', '\n', js)
    return js


def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'static'))
    count = 0
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith('.css') and not f.endswith('.min.css'):
                path = os.path.join(dirpath, f)
                with open(path, 'r', encoding='utf-8') as src:
                    content = src.read()
                out_path = os.path.join(dirpath, f.replace('.css', '.min.css'))
                minified = minify_css(content)
                with open(out_path, 'w', encoding='utf-8') as dst:
                    dst.write(minified)
                print(f"[+] Minified CSS: {f} ({len(content)} -> {len(minified)} bytes)")
                count += 1
            elif f.endswith('.js') and not f.endswith('.min.js'):
                path = os.path.join(dirpath, f)
                with open(path, 'r', encoding='utf-8') as src:
                    content = src.read()
                out_path = os.path.join(dirpath, f.replace('.js', '.min.js'))
                minified = minify_js(content)
                with open(out_path, 'w', encoding='utf-8') as dst:
                    dst.write(minified)
                print(f"[+] Minified JS: {f} ({len(content)} -> {len(minified)} bytes)")
                count += 1
    print(f"\nFinished: Minified {count} static assets.")


if __name__ == '__main__':
    main()
