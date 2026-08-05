"""
Generate exact HiddenYatra Orange Pin Logo matching the user's uploaded icon image:
- Orange Location Pin (#FF7A18)
- Inner White Circle with Teal/Cyan Center Dot (#00BFA6)
- Bottom-left Teal Trail Line (#00BFA6)
- Wordmark "HiddenYatra" ("Hidden" in #0F172A navy, "Yatra" in #FF7A18 orange)
"""
import os
import sys
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')

static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../static'))

# 1. Exact SVG Logo Icon (Orange Map Pin with Teal Dot & Trail Line)
logo_icon_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
  <!-- Bottom-left Teal Trail Line -->
  <path d="M10 82 Q 18 78 24 82 Q 30 86 36 72" fill="none" stroke="#00BFA6" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
  
  <!-- Orange Location Pin Body -->
  <path d="M50 8 C 30 8 18 24 18 42 C 18 64 50 92 50 92 C 50 92 82 64 82 42 C 82 24 70 8 50 8 Z" fill="#FF7A18"/>
  
  <!-- Inner White Circle -->
  <circle cx="50" cy="40" r="14" fill="#FFFFFF"/>
  
  <!-- Center Teal Dot -->
  <circle cx="50" cy="40" r="6.5" fill="#00BFA6"/>
</svg>
"""

with open(os.path.join(static_dir, 'logo-icon.svg'), 'w', encoding='utf-8') as f:
    f.write(logo_icon_svg)

print("Generated static/logo-icon.svg (Orange Map Pin Icon)")

# 2. Exact Full Logo SVG (Orange Pin Icon + "HiddenYatra" Wordmark)
full_logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 70" width="340" height="70">
  <g transform="translate(5, -8)">
    """ + logo_icon_svg.replace('width="100" height="100"', 'width="75" height="75"') + """
  </g>
  <text x="85" y="52" font-family="'Poppins', 'Inter', -apple-system, sans-serif" font-weight="800" font-size="36" fill="#0F172A">Hidden<tspan fill="#FF7A18">Yatra</tspan></text>
</svg>
"""

with open(os.path.join(static_dir, 'logo.svg'), 'w', encoding='utf-8') as f:
    f.write(full_logo_svg)

print("Generated static/logo.svg (Full Brand Logo)")

# 3. Generate High-Res PNG Icons (192x192 & 512x512)
def make_png_icon(size):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    s = size / 100.0
    
    # Bottom-left teal trail
    trail_points = [(10*s, 82*s), (18*s, 78*s), (24*s, 82*s), (30*s, 86*s), (36*s, 72*s)]
    draw.line(trail_points, fill="#00BFA6", width=int(6*s), joint="curve")
    
    # Pin body
    cx, cy, r = 50*s, 42*s, 32*s
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#FF7A18")
    draw.polygon([(cx - 22*s, cy + 18*s), (cx + 22*s, cy + 18*s), (cx, 92*s)], fill="#FF7A18")
    
    # Inner white circle
    draw.ellipse([cx - 14*s, cy - 14*s, cx + 14*s, cy + 14*s], fill="#FFFFFF")
    
    # Center teal dot
    draw.ellipse([cx - 6.5*s, cy - 6.5*s, cx + 6.5*s, cy + 6.5*s], fill="#00BFA6")
    
    return img

icon192 = make_png_icon(192)
icon192.save(os.path.join(static_dir, 'icon-192.png'))
print("Generated static/icon-192.png")

icon512 = make_png_icon(512)
icon512.save(os.path.join(static_dir, 'icon-512.png'))
print("Generated static/icon-512.png")
