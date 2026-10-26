import json, sys
cfgf, resf, idx, out, title, sub = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6]
cfg = json.load(open(cfgf)); L = json.load(open(resf))[idx]
W, H = cfg['W'], cfg['H']; EXT = set(cfg.get('exterior', []))
notes = cfg.get('wall_notes', {})
S = 150.0; X0, Y0 = 210.0, 140.0
def X(x): return X0 + x*S
def Y(y): return Y0 + y*S
o = []; a = o.append
VW, VH = 980, 1180
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {VH}" width="{VW}" height="{VH}" font-family="Arial, sans-serif">')
a(f'<rect width="{VW}" height="{VH}" fill="#fff"/>')
a(f'<text x="{VW/2}" y="34" text-anchor="middle" font-size="18" font-weight="bold">{title}</text>')
a(f'<text x="{VW/2}" y="56" text-anchor="middle" font-size="12" fill="#444">{sub}</text>')
a(f'<text x="{VW/2}" y="76" text-anchor="middle" font-size="11" fill="#777">Масштаб: 1 м = {S:.0f} px. Внутрішні розміри кімнати {str(W).replace(".", ",")} × {str(H).replace(".", ",")} м ({str(round(W*H,1)).replace(".", ",")} м²).</text>')
def th(w): return 0.4 if w in EXT else 0.1
# walls as dark bands
a(f'<rect x="{X(-th("W")):.1f}" y="{Y(-th("N")):.1f}" width="{(W+th("W")+th("E"))*S:.1f}" height="{(H+th("N")+th("S"))*S:.1f}" fill="#4a4a4a"/>')
a(f'<rect x="{X(0):.1f}" y="{Y(0):.1f}" width="{W*S:.1f}" height="{H*S:.1f}" fill="#fbf8f2"/>')
def band(wall, a0, a1, depth):
    if wall == 'W': return (0, a0, depth, a1)
    if wall == 'E': return (W-depth, a0, W, a1)
    if wall == 'N': return (a0, 0, a1, depth)
    return (a0, H-depth, a1, H)
def wall_rect(wall, a0, a1):         # opening in the wall band itself (outside the room)
    t = th(wall)
    if wall == 'W': return (-t, a0, 0, a1)
    if wall == 'E': return (W, a0, W+t, a1)
    if wall == 'N': return (a0, -t, a1, 0)
    return (a0, H, a1, H+t)
def rr(r, fill, stroke="none", sw=0, dash=None, op=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    a(f'<rect x="{X(r[0]):.1f}" y="{Y(r[1]):.1f}" width="{(r[2]-r[0])*S:.1f}" height="{(r[3]-r[1])*S:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d} opacity="{op}"/>')
# windows
for w in cfg['windows']:
    s0, s1 = w['c']-w['w']/2, w['c']+w['w']/2
    r = wall_rect(w['wall'], s0, s1); rr(r, '#fff')
    if w['wall'] in 'WE':
        mid = (r[0]+r[2])/2; rr((mid-0.06, s0, mid+0.06, s1), '#9fd0ff', '#2874a6', 0.8)
    else:
        mid = (r[1]+r[3])/2; rr((s0, mid-0.06, s1, mid+0.06), '#9fd0ff', '#2874a6', 0.8)
# door
dw, dc, dd = cfg['door']['wall'], L['door_c'], cfg['door']['depth']
rr(wall_rect(dw, dc-0.45, dc+0.45), '#fff')
dz = band(dw, dc-0.45, dc+0.45, dd); rr(dz, '#fde2e2', '#c0392b', 0.8, '4 3', 0.8)
a(f'<text x="{X((dz[0]+dz[2])/2):.1f}" y="{Y((dz[1]+dz[3])/2)-2:.1f}" text-anchor="middle" font-size="9" fill="#c0392b">зона</text>')
a(f'<text x="{X((dz[0]+dz[2])/2):.1f}" y="{Y((dz[1]+dz[3])/2)+9:.1f}" text-anchor="middle" font-size="9" fill="#c0392b">дверей</text>')
# clearance zones
for z in L['free_sides']: rr(z, '#e8f4fd', '#5dade2', 1, '5 3', 0.7)
if L['foot']: rr(L['foot'], '#e8f4fd', '#5dade2', 1, '5 3', 0.7)
rr(L['wd_front'], '#fff3e0', '#e67e22', 1, '5 3', 0.7)
rr(L['chair'], '#f3e5f5', '#9b59b6', 1, '5 3', 0.7)
def txt(x, y, t, fs=11, anchor='middle', bold=False, fill='#000'):
    a(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{fs}" {"font-weight=\'bold\'" if bold else ""} fill="{fill}">{t}</text>')
bd = L['bed']; rr(bd, '#d7ccc8', '#5d4037', 1.6)
# pillows at the head
ww = L['bed_wall']
if ww in 'EW':
    hx0 = bd[2]-0.40 if ww == 'E' else bd[0]+0.08
    for k in range(2):
        py0 = bd[1]+0.12+k*0.72; rr((hx0, py0, hx0+0.32, py0+0.62), '#fff', '#8d6e63', 1)
else:
    hy0 = bd[1]+0.08 if ww == 'N' else bd[3]-0.40
    for k in range(2):
        px0 = bd[0]+0.12+k*0.72; rr((px0, hy0, px0+0.62, hy0+0.32), '#fff', '#8d6e63', 1)
txt(X((bd[0]+bd[2])/2), Y((bd[1]+bd[3])/2)+4, 'Ліжко 160×200', 12, bold=True)
for ns in L['ns']: rr(ns, '#bcaaa4', '#5d4037', 1.4)
ds = L['desk']; rr(ds, '#cfd8dc', '#455a64', 1.6)
txt(X((ds[0]+ds[2])/2), Y((ds[1]+ds[3])/2)+3, f"Стіл {round((ds[2]-ds[0])*100) if ds[2]-ds[0] > ds[3]-ds[1] else round((ds[3]-ds[1])*100)}×{round(min(ds[2]-ds[0], ds[3]-ds[1])*100)}", 9)
ch = L['chair']; cx0, cy0 = (ch[0]+ch[2])/2, (ch[1]+ch[3])/2
a(f'<circle cx="{X(cx0):.1f}" cy="{Y(cy0):.1f}" r="{0.22*S:.1f}" fill="#eceff1" stroke="#455a64"/>')
txt(X(cx0), Y(cy0)+3, 'стілець', 8)
wd = L['wd']; rr(wd, '#c5cae9', '#303f9f', 1.6)
long_h = (wd[2]-wd[0]) > (wd[3]-wd[1])
n = int(round(max(wd[2]-wd[0], wd[3]-wd[1])/0.5))
for i in range(1, n):
    if long_h: xx = wd[0]+i*(wd[2]-wd[0])/n; a(f'<line x1="{X(xx):.1f}" y1="{Y(wd[1]):.1f}" x2="{X(xx):.1f}" y2="{Y(wd[3]):.1f}" stroke="#303f9f" stroke-width="0.8"/>')
    else: yy = wd[1]+i*(wd[3]-wd[1])/n; a(f'<line x1="{X(wd[0]):.1f}" y1="{Y(yy):.1f}" x2="{X(wd[2]):.1f}" y2="{Y(yy):.1f}" stroke="#303f9f" stroke-width="0.8"/>')
txt(X((wd[0]+wd[2])/2), Y((wd[1]+wd[3])/2)+3, f"Шафа {round(max(wd[2]-wd[0], wd[3]-wd[1])*100)}×60", 10, bold=True)
# wall notes
for wall, t in notes.items():
    if wall == 'N': txt(X(W/2), Y(-th('N'))-8, t, 10, fill='#555')
    if wall == 'S': txt(X(W/2), Y(H+th('S'))+16, t, 10, fill='#555')
    if wall == 'E': a(f'<text x="{X(W+th("E"))+10:.1f}" y="{Y(H/2):.1f}" font-size="10" fill="#555">{t}</text>')
    if wall == 'W': a(f'<text x="{X(-th("W"))-10:.1f}" y="{Y(H/2):.1f}" text-anchor="end" font-size="10" fill="#555">{t}</text>')
# gap measurements (perpendicular lines through bed centre)
obst = [L['wd'], L['desk']] + L['ns']
def gap_dim(x1, y1, x2, y2, label):
    a(f'<line x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" y2="{Y(y2):.1f}" stroke="#c0392b" stroke-width="1.2"/>')
    for (xx, yy) in ((x1, y1), (x2, y2)):
        if abs(x1-x2) < 1e-6: a(f'<line x1="{X(xx)-4:.1f}" y1="{Y(yy):.1f}" x2="{X(xx)+4:.1f}" y2="{Y(yy):.1f}" stroke="#c0392b"/>')
        else: a(f'<line x1="{X(xx):.1f}" y1="{Y(yy)-4:.1f}" x2="{X(xx):.1f}" y2="{Y(yy)+4:.1f}" stroke="#c0392b"/>')
    a(f'<text x="{(X(x1)+X(x2))/2+10:.1f}" y="{(Y(y1)+Y(y2))/2+4:.1f}" font-size="10" font-weight="bold" fill="#c0392b">{label}</text>')
gaps = []
cx_b, cy_b = (bd[0]+bd[2])/2, (bd[1]+bd[3])/2
def nearest_x(from_x, direction, y):      # horizontal ray at y
    best = (0 if direction < 0 else W)
    for r in obst:
        if r[1] < y < r[3]:
            if direction < 0 and r[2] <= from_x + 1e-9: best = max(best, r[2])
            if direction > 0 and r[0] >= from_x - 1e-9: best = min(best, r[0])
    return best
def nearest_y(from_y, direction, x):
    best = (0 if direction < 0 else H)
    for r in obst:
        if r[0] < x < r[2]:
            if direction < 0 and r[3] <= from_y + 1e-9: best = max(best, r[3])
            if direction > 0 and r[1] >= from_y - 1e-9: best = min(best, r[1])
    return best
if ww in 'EW':
    # foot gap along x, side gaps along y at mid-length
    if ww == 'E': fx = nearest_x(bd[0], -1, cy_b); g = bd[0]-fx; gap_dim(fx, cy_b, bd[0], cy_b, f"{round(g*100)} см"); gaps.append(('Від ніжок ліжка до шафи/стіни', g))
    else: fx = nearest_x(bd[2], 1, cy_b); g = fx-bd[2]; gap_dim(bd[2], cy_b, fx, cy_b, f"{round(g*100)} см"); gaps.append(('Від ніжок ліжка до шафи/стіни', g))
    mx = (bd[0]+bd[2])/2
    n_ = nearest_y(bd[1], -1, mx); g = bd[1]-n_; gap_dim(mx, n_, mx, bd[1], f"{round(g*100)} см"); gaps.append(('Прохід із півночі від ліжка', g))
    s_ = nearest_y(bd[3], 1, mx); g = s_-bd[3]; gap_dim(mx, bd[3], mx, s_, f"{round(g*100)} см"); gaps.append(('Прохід з півдня від ліжка', g))
else:
    if ww == 'S': fy = nearest_y(bd[1], -1, cx_b); g = bd[1]-fy; gap_dim(cx_b, fy, cx_b, bd[1], f"{round(g*100)} см"); gaps.append(('Від ніжок ліжка до шафи/стіни', g))
    else: fy = nearest_y(bd[3], 1, cx_b); g = fy-bd[3]; gap_dim(cx_b, bd[3], cx_b, fy, f"{round(g*100)} см"); gaps.append(('Від ніжок ліжка до шафи/стіни', g))
    my = (bd[1]+bd[3])/2
    w_ = nearest_x(bd[0], -1, my); g = bd[0]-w_; gap_dim(w_, my, bd[0], my, f"{round(g*100)} см"); gaps.append(('Прохід із заходу від ліжка', g))
    e_ = nearest_x(bd[2], 1, my); g = e_-bd[2]; gap_dim(bd[2], my, e_, my, f"{round(g*100)} см"); gaps.append(('Прохід зі сходу від ліжка', g))
# legend below
ly = Y(H) + th('S')*S + 70
txt(40, ly, 'Меблі і зони', 14, 'start', True)
items = [("#d7ccc8", f"Ліжко 160×200, узголів'я до стіни {'(північної)' if ww=='N' else '(південної)' if ww=='S' else '(східної)' if ww=='E' else '(західної)'}" + (", під вікном" if L['head_under_window'] else ", не під вікном")),
         ("#bcaaa4", "Тумби 45×40 з обох боків"), ("#cfd8dc", "Стіл 120×55, стілець"), ("#c5cae9", f"Шафа {round(max(wd[2]-wd[0], wd[3]-wd[1])*100)}×60, фронт 80 см")]
for i, (c, t) in enumerate(items):
    yy = ly + 22 + i*20
    a(f'<rect x="40" y="{yy-10:.1f}" width="18" height="12" fill="{c}" stroke="#555"/>'); txt(66, yy, t, 11, 'start')
yy = ly + 22 + len(items)*20 + 6
zl = [("#e8f4fd", "проходи біля ліжка (60 см)"), ("#fff3e0", "фронт шафи (80 см)"), ("#f3e5f5", "зона стільця (60 см)"), ("#fde2e2", "зона відкривання дверей 0,9 × 0,9 м")]
for i, (c, t) in enumerate(zl):
    xx = 40 + (i % 2)*400; y2 = yy + (i//2)*18
    a(f'<rect x="{xx}" y="{y2-10:.1f}" width="18" height="12" fill="{c}" stroke="#999" stroke-dasharray="3 2"/>'); txt(xx+26, y2, t, 11, 'start')
yy += 2*18 + 14
txt(40, yy, 'Проходи (виміряно за кресленням):', 12, 'start', True)
for i, (t, g) in enumerate(gaps): txt(40, yy+18+i*18, f"{t}: {round(g*100)} см", 11, 'start')
yy += 18 + len(gaps)*18 + 14
for i, t in enumerate(cfg.get('footer', [])): txt(40, yy+i*15, t, 10, 'start', fill='#777')
a('</svg>')
open(out, 'w', encoding='utf-8').write('\n'.join(o))
print('ok', out, [(t, round(g, 2)) for t, g in gaps])
