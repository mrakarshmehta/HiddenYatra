"""
Generate official HiddenYatra logo SVG & PNG assets matching user image:
- Golden circular compass casing with top loop ring
- Silver/white compass dial with star markings
- Red needle pointing North-West (top-left)
- Bold wordmark "HiddenYatra" ("Hidden" in white/dark, "Yatra" in Saffron #FF7A18)
"""
import os
import sys
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')

static_dir = os.path.join(os.path.dirname(__file__), '../../static')

# 1. Write SVG Icon (Golden Compass with Red Needle)
logo_icon_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
  <defs>
    <!-- Golden Casing Gradient -->
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FCD34D"/>
      <stop offset="50%" stop-color="#F59E0B"/>
      <stop offset="100%" stop-color="#B45309"/>
    </linearGradient>
    <!-- Dial Face Gradient -->
    <radialGradient id="dialGrad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="85%" stop-color="#F1F5F9"/>
      <stop offset="100%" stop-color="#E2E8F0"/>
    </radialGradient>
    <!-- Red Needle Gradient -->
    <linearGradient id="redNeedle" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#EF4444"/>
      <stop offset="100%" stop-color="#DC2626"/>
    </linearGradient>
    <!-- Silver Needle Gradient -->
    <linearGradient id="silverNeedle" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#94A3B8"/>
      <stop offset="100%" stop-color="#64748B"/>
    </linearGradient>
  </defs>

  <!-- Top Ring Handle -->
  <circle cx="50" cy="10" r="7" fill="none" stroke="url(#goldGrad)" stroke-width="4"/>

  <!-- Outer Golden Casing -->
  <circle cx="50" cy="55" r="42" fill="url(#goldGrad)"/>
  <circle cx="50" cy="55" r="37" fill="#B45309"/>
  
  <!-- Dial Face -->
  <circle cx="50" cy="55" r="35" fill="url(#dialGrad)" stroke="#CBD5E1" stroke-width="1.5"/>

  <!-- Compass Star Markings -->
  <!-- N, S, E, W Ticks -->
  <line x1="50" y1="23" x2="50" y2="28" stroke="#64748B" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="50" y1="82" x2="50" y2="87" stroke="#94A3B8" stroke-width="2" stroke-linecap="round"/>
  <line x1="18" y1="55" x2="23" y2="55" stroke="#94A3B8" stroke-width="2" stroke-linecap="round"/>
  <line x1="77" y1="55" x2="82" y2="55" stroke="#94A3B8" stroke-width="2" stroke-linecap="round"/>

  <!-- 8-Point Compass Star -->
  <polygon points="50,26 53,50 50,55 47,50" fill="#94A3B8" opacity="0.3"/>
  <polygon points="50,84 53,60 50,55 47,60" fill="#94A3B8" opacity="0.3"/>
  <polygon points="18,55 42,52 50,55 42,58" fill="#94A3B8" opacity="0.3"/>
  <polygon points="82,55 58,52 50,55 58,58" fill="#94A3B8" opacity="0.3"/>

  <!-- Red Pointer Needle (Pointing North-West) -->
  <g transform="rotate(-45 50 55)">
    <!-- Red North Needle -->
    <polygon points="50,22 45,55 50,53 55,55" fill="url(#redNeedle)"/>
    <!-- Silver South Needle -->
    <polygon points="50,88 45,55 50,57 55,55" fill="url(#silverNeedle)"/>
    <!-- Center Pivot Cap -->
    <circle cx="50" cy="55" r="4.5" fill="#F59E0B" stroke="#78350F" stroke-width="1"/>
    <circle cx="50" cy="55" r="2" fill="#FFFFFF"/>
  </g>
</svg>
"""

with open(os.path.join(static_dir, 'logo-icon.svg'), 'w', encoding='utf-8') as f:
    f.write(logo_icon_svg)

print("Generated static/logo-icon.svg")

# 2. Write SVG Full Logo (Icon + Text)
full_logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 70" width="340" height="70">
  <g transform="translate(5, -5)">
    """ + logo_icon_svg.replace('width="100" height="100"', 'width="65" height="65"') + """
  </g>
  <text x="75" y="48" font-family="'Poppins', 'Inter', sans-serif" font-weight="800" font-size="34" fill="#FFFFFF">Hidden<tspan fill="#FF7A18">Yatra</tspan></text>
</svg>
"""

with open(os.path.join(static_dir, 'logo.svg'), 'w', encoding='utf-8') as f:
    f.write(full_logo_svg)

print("Generated static/logo.svg")

# 3. Generate PNG Icons (192x192 & 512x512) matching golden compass
def make_png_icon(size):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Scale coordinates based on size
    s = size / 100.0
    
    # Top ring
    draw.ellipse([38*s, 3*s, 62*s, 23*s], outline="#F59E0B", width=int(5*s))
    
    # Outer gold casing
    draw.ellipse([8*s, 13*s, 92*s, 97*s], fill="#F59E0B", outline="#B45309", width=int(3*s))
    
    # Inner Dial
    draw.ellipse([14*s, 19*s, 86*s, 91*s], fill="#F8FAFC", outline="#CBD5E1", width=int(2*s))
    
    # Red needle (pointing NW)
    cx, cy = 50*s, 55*s
    needle_top = (27*s, 32*s)
    needle_bottom = (73*s, 78*s)
    draw.polygon([needle_top, (cx - 4*s, cy + 4*s), (cx + 4*s, cy - 4*s)], fill="#EF4444")
    draw.polygon([needle_bottom, (cx - 4*s, cy + 4*s), (cx + 4*s, cy - 4*s)], fill="#64748B")
    
    # Pivot center
    draw.ellipse([cx - 5*s, cy - 5*s, cx + 5*s, cy + 5*s], fill="#F59E0B", outline="#78350F")
    draw.ellipse([cx - 2*s, cy - 2*s, cx + 2*s, cy + 2*s], fill="#FFFFFF")
    
    return img

icon192 = make_png_icon(192)
icon192.save(os.path.join(static_dir, 'icon-192.png'))
print("Generated static/icon-192.png")

icon512 = make_png_icon(512)
icon512.save(os.path.join(static_dir, 'icon-512.png'))
print("Generated static/icon-512.png")
