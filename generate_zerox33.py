#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║       ZEROX33 — 128 Animated Cube Generator          ║
║       OPTIMIZED + Z-RARE SPECIAL CUBES               ║
╠══════════════════════════════════════════════════════╣
║  pip install Pillow                                  ║
║  python generate_zerox33.py                          ║
║                                                      ║
║  OUTPUT: ./assets/0.gif → 127.gif + logo.png         ║
║                                                      ║
║  GIFs 0–111:   Normal cubes (14 traits × 8 vars)    ║
║  GIFs 112–127: Z-RARE (white bg, black/dark cubes)  ║
╚══════════════════════════════════════════════════════╝
"""

import math, os, random, time
from PIL import Image, ImageDraw, ImageFilter, ImageChops

OUTPUT_DIR = "./assets"
FRAMES = 20
IMG_SIZE = 400
DURATION = 85

TRAITS = [
    "KERNEL","DAEMON","THREAD","SOCKET","SIGNAL","PIPE","MUTEX",
    "BUFFER","STACK","HEAP","CACHE","FORK","EXEC","SWAP",
    "Z-RARE-I","Z-RARE-II",
]

TRAIT_PARAMS = [
    (0,   40), (25,  45), (45,  50), (75,  35),
    (130, 30), (170, 40), (200, 45), (225, 40),
    (255, 35), (280, 38), (315, 32), (345, 38),
    (15,  12), (190, 15),
    (0, 0), (0, 0),
]

def hsl_to_rgb(h, s, l):
    h = (h % 360) / 360.0
    if s == 0:
        v = int(l * 255)
        return (v, v, v)
    def h2r(p, q, t):
        if t < 0: t += 1
        if t > 1: t -= 1
        if t < 1/6: return p + (q-p)*6*t
        if t < 1/2: return q
        if t < 2/3: return p + (q-p)*(2/3-t)*6
        return p
    q = l*(1+s) if l < 0.5 else l+s-l*s
    p = 2*l - q
    return (int(h2r(p,q,h+1/3)*255), int(h2r(p,q,h)*255), int(h2r(p,q,h-1/3)*255))

def make_colors(bh, bs, v):
    c = []
    for i in range(6):
        h = (bh + v*7 + i*12) % 360
        s = max(0.08, min(0.85, bs/100 + (i-3)*0.04 + v*0.02))
        l = max(0.18, min(0.65, 0.28 + i*0.07 + (v%3)*0.03))
        c.append(hsl_to_rgb(h, s, l))
    return c

def make_rare_colors(v):
    c = []
    for i in range(6):
        b = max(5, min(60, 12 + i*7 + v*3))
        c.append((b, b, b + v%3))
    return c

def make_rare_inner(v):
    c = []
    for i in range(6):
        b = max(20, min(85, 28 + i*9 + v*4))
        c.append((b, b, b + v%2))
    return c

def make_rare_bg(v):
    rng = random.Random(v * 999)
    b = 205 + rng.randint(-12, 12)
    return (b, b - 2 + rng.randint(0,5), b - 6 + rng.randint(0,6))

def make_glow(h, s, v):
    return hsl_to_rgb((h+v*7)%360, min(0.7,s/100+0.1), 0.45)

def make_bg(h, s, v):
    return hsl_to_rgb((h+v*5)%360, min(0.15,s/200), 0.04+(v%4)*0.008)

def rotate_pt(x, y, z, ax, ay, az):
    ca,sa = math.cos(ax),math.sin(ax)
    y1,z1 = y*ca-z*sa, y*sa+z*ca
    cb,sb = math.cos(ay),math.sin(ay)
    x2,z2 = x*cb+z1*sb, -x*sb+z1*cb
    cc,sc = math.cos(az),math.sin(az)
    return (x2*cc-y1*sc, x2*sc+y1*cc, z2)

def proj(x, y, z, cx, cy):
    f = 300.0/(4.0+z/100.0)
    return (cx+x*f/100, cy+y*f/100)

def cube_v(s):
    return [(-s,-s,-s),(s,-s,-s),(s,s,-s),(-s,s,-s),(-s,-s,s),(s,-s,s),(s,s,s),(-s,s,s)]

FACES = [([0,1,2,3],0),([4,5,6,7],1),([0,4,7,3],2),([1,5,6,2],3),([0,1,5,4],4),([3,2,6,7],5)]

def draw_cube(draw, v2d, v3d, colors):
    fd = sorted([(sum(v3d[i][2] for i in idx)/4, idx, fi) for idx,fi in FACES], key=lambda x:-x[0])
    for _, idx, fi in fd:
        c = colors[fi % len(colors)]
        draw.polygon([v2d[i] for i in idx], fill=c, outline=tuple(min(255,v+20) for v in c))

def draw_z_shape(draw, cx, cy, sz, color):
    """Draw a Z letter shape as background watermark"""
    # Top bar
    draw.rectangle([cx-sz, cy-sz, cx+sz, cy-sz + sz*0.18], fill=color)
    # Bottom bar
    draw.rectangle([cx-sz, cy+sz - sz*0.18, cx+sz, cy+sz], fill=color)
    # Diagonal
    w = sz * 0.18
    pts = [
        (cx+sz, cy-sz + sz*0.18),
        (cx+sz - w*0.5, cy-sz + sz*0.18),
        (cx-sz, cy+sz - sz*0.18),
        (cx-sz + w*0.5, cy+sz - sz*0.18),
    ]
    draw.polygon(pts, fill=color)
    # Two dots under Z
    dot_r = sz * 0.07
    draw.ellipse([cx - sz*0.35 - dot_r, cy+sz+dot_r*2 - dot_r, cx - sz*0.35 + dot_r, cy+sz+dot_r*2 + dot_r], fill=color)
    draw.ellipse([cx - sz*0.05 - dot_r, cy+sz+dot_r*2 - dot_r, cx - sz*0.05 + dot_r, cy+sz+dot_r*2 + dot_r], fill=color)

def gen_gif(gi, ti, vi):
    is_rare = ti >= 14

    if is_rare:
        fc = make_rare_colors(vi)
        ic = make_rare_inner(vi)
        bg_c = make_rare_bg(vi)
        glow_c = (50+vi*4, 50+vi*4, 50+vi*4)
    else:
        bh,bs = TRAIT_PARAMS[ti]
        fc = make_colors(bh,bs,vi)
        ic = [tuple(min(255,c+35) for c in col) for col in fc]
        bg_c = make_bg(bh,bs,vi)
        glow_c = make_glow(bh,bs,vi)

    rng = random.Random(gi*7919+vi*31+ti*127)
    out_s = rng.randint(62,85)
    in_s = out_s*(0.30+rng.random()*0.18)
    rspd = 0.75+rng.random()*0.5
    wobx = 0.15+rng.random()*0.25
    wobz = 0.05+rng.random()*0.15
    tilt = rng.random()*0.4+0.3
    ispd = 1.1+rng.random()*0.6

    frames = []
    cx, cy = IMG_SIZE//2, IMG_SIZE//2-8

    for f in range(FRAMES):
        t = f/FRAMES
        ay = t*2*math.pi*rspd
        ax = math.sin(t*2*math.pi)*wobx+tilt
        az = math.cos(t*2*math.pi)*wobz

        img = Image.new('RGB', (IMG_SIZE, IMG_SIZE), bg_c)
        draw = ImageDraw.Draw(img)

        # Z-RARE: dirty texture + Z watermark
        if is_rare:
            # Dirty grain on white bg
            grng = random.Random(f*100+gi)
            for _ in range(400):
                gx,gy = grng.randint(0,IMG_SIZE-1), grng.randint(0,IMG_SIZE-1)
                sh = grng.randint(-25, 5)
                r,g,b = bg_c
                draw.point((gx,gy), fill=(max(0,r+sh),max(0,g+sh),max(0,b+sh)))

            # Z watermark behind cube (subtle)
            z_shade = tuple(max(0, c-18-vi*2) for c in bg_c)
            draw_z_shape(draw, cx, cy+5, 85+vi*2, z_shade)

        # Outer cube
        ov = cube_v(out_s)
        r3 = [rotate_pt(x,y,z,ax,ay,az) for x,y,z in ov]
        p2 = [proj(x,y,z,cx,cy) for x,y,z in r3]
        draw_cube(draw, p2, r3, fc)

        # Inner cube
        iv = cube_v(in_s)
        ir3 = [rotate_pt(x,y,z,ax*0.65+0.15,-ay*ispd,az*0.3) for x,y,z in iv]
        ip2 = [proj(x,y,z,cx,cy) for x,y,z in ir3]
        draw_cube(draw, ip2, ir3, ic)

        # Glow rings — FAST (no pixel loop, use ImageChops.add)
        glow = Image.new('RGB', (IMG_SIZE, IMG_SIZE), (0,0,0))
        gd = ImageDraw.Draw(glow)
        r1 = int(out_s*1.8+math.sin(t*4*math.pi)*6)
        r2 = int(out_s*2.15+math.cos(t*4*math.pi)*5)
        if is_rare:
            rc = (35+vi*3,35+vi*3,35+vi*3)
            rc2 = (20+vi*2,20+vi*2,20+vi*2)
        else:
            rc = glow_c
            rc2 = tuple(c//2 for c in glow_c)
        gd.ellipse([cx-r1,cy-r1,cx+r1,cy+r1], outline=rc, width=1)
        gd.ellipse([cx-r2,cy-r2,cx+r2,cy+r2], outline=rc2, width=1)
        glow = glow.filter(ImageFilter.GaussianBlur(2))

        # FAST composite (replaces slow pixel-by-pixel loop)
        img = ImageChops.add(img, glow, scale=3)

        frames.append(img)

    fp = os.path.join(OUTPUT_DIR, f"{gi}.gif")
    frames[0].save(fp, save_all=True, append_images=frames[1:], duration=DURATION, loop=0, optimize=True)
    return fp

def generate_logo():
    s = 200
    img = Image.new('RGBA',(s,s),(0,0,0,0))
    d = ImageDraw.Draw(img)
    d.ellipse([8,8,192,192],outline=(34,34,34),width=7)
    d.ellipse([20,20,180,180],fill=(240,240,240))
    d.rectangle([60,50,140,62],fill=(26,26,26))
    d.rectangle([60,138,140,150],fill=(26,26,26))
    d.polygon([(140,62),(84,138),(60,138),(116,62)],fill=(26,26,26))
    d.ellipse([72,154,88,170],fill=(26,26,26))
    d.ellipse([100,154,116,170],fill=(26,26,26))
    img.save(os.path.join(OUTPUT_DIR,"logo.png"))

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print()
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║   ZEROX33 — 128 Animated Cube Generator      ║")
    print("  ║   Now with Z-RARE special cubes! (112-127)   ║")
    print("  ╚══════════════════════════════════════════════╝")
    print()
    print(f"  Output:  {os.path.abspath(OUTPUT_DIR)}")
    print(f"  Size:    {IMG_SIZE}x{IMG_SIZE}px, {FRAMES} frames each")
    print(f"  Normal:  0-111  (14 traits x 8 color variations)")
    print(f"  Z-RARE:  112-127 (dirty white bg + black cubes + Z)")
    print()

    start = time.time()
    gi = 0
    for ti in range(16):
        for vi in range(8):
            gen_gif(gi,ti,vi)
            gi += 1
            pct = gi/128
            filled = int(30*pct)
            bar = "█"*filled + "░"*(30-filled)
            elapsed = time.time()-start
            eta = (elapsed/gi)*(128-gi) if gi>0 else 0
            tag = " ★ RARE" if ti>=14 else ""
            print(f"\r  [{bar}] {gi:>3}/128  {TRAITS[ti]} v{vi}{tag}  ETA:{int(eta)}s   ", end="", flush=True)

    elapsed = time.time()-start
    print()
    print()

    generate_logo()

    tb = sum(os.path.getsize(os.path.join(OUTPUT_DIR,f)) for f in os.listdir(OUTPUT_DIR))
    print(f"  Done in {int(elapsed)} seconds")
    print(f"  {gi} GIFs + logo.png = {tb//(1024*1024)} MB")
    print()
    print("  Trait Map:")
    for i,n in enumerate(TRAITS):
        tag = "  ★ RARE (white bg, black cubes, Z watermark)" if i>=14 else ""
        print(f"    {i*8:>3}-{i*8+7:<3}  {n}{tag}")
    print()
    print("  Place assets/ folder next to index.html and you're live!")
    print()
