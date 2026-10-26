import json, sys, math
src, out, title, subtitle = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
d = json.load(open(src)); R = d['rooms']; Wi, Di = d['W'], d['D']
T = 0.4; S = 54.0
EW, EH = Wi + 2*T, Di + 2*T
X0, Y0 = 130.0, 150.0
def X(x): return X0 + (x+T)*S      # internal metres -> px
def Y(y): return Y0 + (y+T)*S
NAMES = {'hall':'Хол','kit':'Кухня-їдальня','liv':'Вітальня','kitliv':'Кухня-вітальня','bed1':'Спальня 1 (двоспальна)','bed2':'Спальня 2 (односпальна)',
         'bath':'Ванна','toilet':'Туалет','tech':'Котельня','store':'Комора','corr':'Коридор'}
FILL = {'hall':'#f3f3f3','kit':'#fdf0d5','liv':'#fbe3c8','kitliv':'#fbe9cf','bed1':'#e8d5f0','bed2':'#e8d5f0','bath':'#d6eaf8',
        'toilet':'#d6eaf8','tech':'#e6e6e6','store':'#ececec','corr':'#f6f6f6'}
kit = 'kitliv' if 'kitliv' in R else 'kit'
combined = ('toilet' not in R)
if combined: NAMES['bath'] = 'Ванна з туалетом'
def share(a, b, tol=0.06):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    if abs((ax+aw)-bx) < tol or abs((bx+bw)-ax) < tol:
        lo, hi = max(ay, by), min(ay+ah, by+bh)
        return (hi-lo, 'v', (ax+aw if abs((ax+aw)-bx) < tol else ax), (lo, hi))
    if abs((ay+ah)-by) < tol or abs((by+bh)-ay) < tol:
        lo, hi = max(ax, bx), min(ax+aw, bx+bw)
        return (hi-lo, 'h', (ay+ah if abs((ay+ah)-by) < tol else ay), (lo, hi))
    return (0, None, None, None)
o = []; a = o.append
VW, VH = 820, 1340
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {VH}" width="{VW}" height="{VH}" font-family="Arial, sans-serif">')
a(f'<rect width="{VW}" height="{VH}" fill="#ffffff"/>')
a(f'<text x="{VW/2}" y="34" text-anchor="middle" font-size="18" font-weight="bold">{title}</text>')
a(f'<text x="{VW/2}" y="56" text-anchor="middle" font-size="12" fill="#444">{subtitle}</text>')
a(f'<text x="{VW/2}" y="74" text-anchor="middle" font-size="11" fill="#777">Умовний масштаб: 1 м = {S:.0f} px. Розміри в метрах. Стіни: зовнішня 0,40, перегородки 0,10.</text>')
# exterior wall
a(f'<rect x="{X(-T):.1f}" y="{Y(-T):.1f}" width="{EW*S:.1f}" height="{EH*S:.1f}" fill="#4a4a4a"/>')
a(f'<rect x="{X(0):.1f}" y="{Y(0):.1f}" width="{Wi*S:.1f}" height="{Di*S:.1f}" fill="#ffffff"/>')
# vestibule carved from hall on west edge: 1.5 (x) x 2.2 (y)
h = R['hall']
SIDE = 'w' if abs(h[0]) < 0.06 else 'n'
if SIDE == 'w':
    vw, vh = 1.5, 2.2
    VEST = (0.0, round(h[1] + (h[3]-vh)/2.0, 1), vw, vh)
else:
    vw, vh = 2.2, 1.5
    VEST = (round(h[0] + (h[2]-vw)/2.0, 1), 0.0, vw, vh)
rooms = dict(R)
# draw rooms
rows = []
for n, (x, y, w, hh) in rooms.items():
    a(f'<rect x="{X(x):.1f}" y="{Y(y):.1f}" width="{w*S:.1f}" height="{hh*S:.1f}" fill="{FILL[n]}" stroke="#555" stroke-width="3"/>')
# vestibule overlay
vx, vy_, vww, vhh = VEST
a(f'<rect x="{X(vx):.1f}" y="{Y(vy_):.1f}" width="{vww*S:.1f}" height="{vhh*S:.1f}" fill="#dff0e0" stroke="#555" stroke-width="3"/>')
# labels
num = 0; labels = {}
order = ['vest'] + [k for k in ('kit','liv','kitliv','bed1','bed2','bath','toilet','tech','store','corr','hall') if k in R]
def txt(cx, cy, lines, fs=11, bold_first=True):
    for i, s in enumerate(lines):
        a(f'<text x="{cx:.1f}" y="{cy+i*(fs+2):.1f}" text-anchor="middle" font-size="{fs if i else fs+1}" {"font-weight=\'bold\'" if (i==0 and bold_first) else ""}>{s}</text>')
for n, (x, y, w, hh) in rooms.items():
    area = w*hh
    if n == 'hall': area -= vww*vhh
    cx, cy = X(x+w/2), Y(y+hh/2)
    short = min(w, hh)*S
    big = short > 95
    nm = NAMES[n] if n != 'hall' else 'Передпокій'
    if n == 'hall':
        if SIDE == 'w': cx, cy = X(x+vw+(w-vw)/2), Y(y+hh/2)
        else: cx, cy = X(x+0.65+(w-0.65)/2), Y(y+vh+(hh-vh)/2)
    ar = f"{area:.1f}".replace('.', ',') + ' м²'
    if short > 62:
        words = nm.split(' ')
        lines = [nm, ar] if len(nm) <= 14 or ' ' not in nm else [words[0], ' '.join(words[1:]), ar]
        if n == 'hall' and ((SIDE == 'w' and (w-vw)*S < 90) or (SIDE == 'n' and (w-0.65)*S < 90)):
            lines = ['Перед-', 'покій', ar]
        txt(cx, cy-4*(len(lines)-1), lines, fs=11 if big else 9)
    else:
        short_nm = {'toilet':'Туалет','store':'Комора','tech':'Котельня','bath':'Ванна'}.get(n)
        txt(cx, cy+(0 if short_nm else 3), ([short_nm, ar] if short_nm else [ar]), fs=8, bold_first=False)
# vestibule label
a(f'<text x="{X(vx+vww/2):.1f}" y="{Y(vy_+vhh/2)-2:.1f}" text-anchor="middle" font-size="9" font-weight="bold">Тамбур</text>')
tm = f"{vww*vhh:.1f}".replace('.', ',') + ' м²'
a(f'<text x="{X(vx+vww/2):.1f}" y="{Y(vy_+vhh/2)+10:.1f}" text-anchor="middle" font-size="9">{tm}</text>')
# doors: connect rooms
def gap(x, y, w, hh, fill="#ffffff"):
    a(f'<rect x="{X(x):.1f}" y="{Y(y):.1f}" width="{w*S:.1f}" height="{hh*S:.1f}" fill="{fill}"/>')
def door(roomA, roomB, width=0.9, open_passage=False):
    ra, rb = rooms[roomA], rooms[roomB]
    L, kind, pos, (lo, hi) = share(ra, rb)
    if L < width + 0.2: return
    c = (lo + hi)/2.0
    if kind == 'v':
        gap(pos-0.07, c-width/2, 0.14, width)
        if not open_passage:
            a(f'<line x1="{X(pos):.1f}" y1="{Y(c-width/2):.1f}" x2="{X(pos)+width*S:.1f}" y2="{Y(c-width/2):.1f}" stroke="#777"/>')
            a(f'<path d="M {X(pos)+width*S:.1f} {Y(c-width/2):.1f} A {width*S:.1f} {width*S:.1f} 0 0 0 {X(pos):.1f} {Y(c+width/2):.1f}" fill="none" stroke="#999" stroke-width="0.8"/>')
    else:
        gap(c-width/2, pos-0.07, width, 0.14)
        if not open_passage:
            a(f'<line x1="{X(c-width/2):.1f}" y1="{Y(pos):.1f}" x2="{X(c-width/2):.1f}" y2="{Y(pos)+width*S:.1f}" stroke="#777"/>')
            a(f'<path d="M {X(c-width/2):.1f} {Y(pos)+width*S:.1f} A {width*S:.1f} {width*S:.1f} 0 0 0 {X(c+width/2):.1f} {Y(pos):.1f}" fill="none" stroke="#999" stroke-width="0.8"/>')
circ = ['hall'] + (['corr'] if 'corr' in R else [])
if 'corr' in R: door('hall', 'corr', 1.2, open_passage=True)
for n in R:
    if n in ('hall', 'corr'): continue
    if n == 'liv':
        if share(R['liv'], R['hall'])[0] >= 1.0: door('liv', 'hall')
        else: door('liv', kit)
        continue
    best = max(circ, key=lambda c: share(R[n], R[c])[0])
    if share(R[n], R[best])[0] >= 1.0:
        door(n, best, 0.8 if n in ('bath', 'toilet', 'tech', 'store') else 0.9)
# vestibule inner door and outer entrance door
if SIDE == 'w':
    gap(vx+vww-0.07, vy_+0.65, 0.14, 0.9)
    a(f'<line x1="{X(vx+vww):.1f}" y1="{Y(vy_+0.65):.1f}" x2="{X(vx+vww):.1f}" y2="{Y(vy_+0.65)+0.9*S:.1f}" stroke="#777"/>')
    ey = vy_ + (vhh-1.0)/2
    a(f'<rect x="{X(-T)-1:.1f}" y="{Y(ey):.1f}" width="{T*S+2:.1f}" height="{1.0*S:.1f}" fill="#ffffff"/>')
    a(f'<path d="M {X(0):.1f} {Y(ey):.1f} A {1.0*S:.1f} {1.0*S:.1f} 0 0 0 {X(0)-1.0*S:.1f} {Y(ey)+1.0*S:.1f}" fill="none" stroke="#777" stroke-width="0.8"/>')
    a(f'<line x1="{X(0):.1f}" y1="{Y(ey):.1f}" x2="{X(0)-1.0*S:.1f}" y2="{Y(ey):.1f}" stroke="#777"/>')
    a(f'<text x="{X(-T)-8:.1f}" y="{Y(ey+1.0)+14:.1f}" text-anchor="end" font-size="11" font-weight="bold">вхід</text>')
else:
    gap(vx_door := vx+(vww-0.9)/2, vy_+vhh-0.07, 0.9, 0.14)
    a(f'<line x1="{X(vx_door):.1f}" y1="{Y(vy_+vhh):.1f}" x2="{X(vx_door):.1f}" y2="{Y(vy_+vhh)+0.9*S:.1f}" stroke="#777"/>')
    ex = vx + (vww-1.0)/2
    a(f'<rect x="{X(ex):.1f}" y="{Y(-T)-1:.1f}" width="{1.0*S:.1f}" height="{T*S+2:.1f}" fill="#ffffff"/>')
    a(f'<path d="M {X(ex):.1f} {Y(0):.1f} A {1.0*S:.1f} {1.0*S:.1f} 0 0 1 {X(ex)+1.0*S:.1f} {Y(0)-1.0*S:.1f}" fill="none" stroke="#777" stroke-width="0.8"/>')
    a(f'<line x1="{X(ex):.1f}" y1="{Y(0):.1f}" x2="{X(ex):.1f}" y2="{Y(0)-1.0*S:.1f}" stroke="#777"/>')
    a(f'<text x="{X(ex+0.5):.1f}" y="{Y(-T)-14:.1f}" text-anchor="middle" font-size="11" font-weight="bold">вхід</text>')
# wardrobe in hall
if SIDE == 'w':
    wx = h[0] + vw + 0.1; ww = min(2.0, h[2]-vw-0.2); wy = h[1] + h[3] - 0.6; whh = 0.6
else:
    wx = h[0] + 0.05; ww = 0.6; wy = h[1] + vh + 0.1; whh = min(1.8, h[3]-vh-0.2)
a(f'<rect x="{X(wx):.1f}" y="{Y(wy):.1f}" width="{ww*S:.1f}" height="{whh*S:.1f}" fill="#cfd8dc" stroke="#607d8b" stroke-dasharray="3 2"/>')
a(f'<text x="{X(wx+ww/2):.1f}" y="{Y(wy)+whh*S/2+3:.1f}" text-anchor="middle" font-size="8">шафа</text>')
# windows on exterior walls
def window(n, width):
    x, y, w, hh = R[n]
    sides = []
    if abs(x) < 0.06: sides.append(('w', y, hh))
    if abs(y) < 0.06: sides.append(('n', x, w))
    if abs(x+w-Wi) < 0.06: sides.append(('e', y, hh))
    if abs(y+hh-Di) < 0.06: sides.append(('s', x, w))
    for side, start, length in sides[:2]:
        if length < width + 0.5: continue
        c = start + length/2
        if side == 'n': wx0, wy0, ww0, wh0 = X(c-width/2), Y(-T), width*S, T*S
        elif side == 's': wx0, wy0, ww0, wh0 = X(c-width/2), Y(Di), width*S, T*S
        elif side == 'w': wx0, wy0, ww0, wh0 = X(-T), Y(c-width/2), T*S, width*S
        else: wx0, wy0, ww0, wh0 = X(Wi), Y(c-width/2), T*S, width*S
        a(f'<rect x="{wx0:.1f}" y="{wy0:.1f}" width="{ww0:.1f}" height="{wh0:.1f}" fill="#ffffff"/>')
        if side in ('n', 's'):
            a(f'<rect x="{wx0:.1f}" y="{wy0+wh0*0.35:.1f}" width="{ww0:.1f}" height="{wh0*0.3:.1f}" fill="#9fd0ff" stroke="#2874a6" stroke-width="0.8"/>')
        else:
            a(f'<rect x="{wx0+ww0*0.35:.1f}" y="{wy0:.1f}" width="{ww0*0.3:.1f}" height="{wh0:.1f}" fill="#9fd0ff" stroke="#2874a6" stroke-width="0.8"/>')
for n, wd in (('kit',1.5),('kitliv',2.0),('liv',1.8),('bed1',1.2),('bed2',1.2),('bath',0.6),('toilet',0.5)):
    if n in R: window(n, wd)
# overall dimensions
def dim_h(x1, x2, y, text, fs=11):
    a(f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="#222"/>')
    for xx in (x1, x2): a(f'<line x1="{xx:.1f}" y1="{y-5:.1f}" x2="{xx:.1f}" y2="{y+5:.1f}" stroke="#222"/>')
    a(f'<text x="{(x1+x2)/2:.1f}" y="{y-6:.1f}" text-anchor="middle" font-size="{fs}">{text}</text>')
def dim_v(y1, y2, x, text, fs=11):
    a(f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke="#222"/>')
    for yy in (y1, y2): a(f'<line x1="{x-5:.1f}" y1="{yy:.1f}" x2="{x+5:.1f}" y2="{yy:.1f}" stroke="#222"/>')
    a(f'<text x="{x-7:.1f}" y="{(y1+y2)/2+4:.1f}" text-anchor="end" font-size="{fs}">{text}</text>')
dim_h(X(-T), X(Wi+T), Y(-T)-26, f"{EW:.2f} м".replace('.', ','))
dim_v(Y(-T), Y(Di+T), X(-T)-70, f"{EH:.2f} м".replace('.', ','))
# explication
yb = Y(Di+T) + 48
a(f'<text x="40" y="{yb:.1f}" font-size="14" font-weight="bold">Експлікація (внутрішня площа, без стін)</text>')
hy = yb + 24
cols = [40, 78, 250, 360, 450]
a(f'<rect x="34" y="{hy-15:.1f}" width="752" height="21" fill="#eee" opacity="0.7"/>')
for cx, t in zip(cols, ["№", "Приміщення", "Розмір, м", "Площа, м²", "Норма (ДБН В.2.2-15) і статус"]):
    a(f'<text x="{cx}" y="{hy:.1f}" font-size="11" font-weight="bold">{t}</text>')
def chk(n, w, hh, area):
    if n == 'liv': return ('≥ 16 м² (п. 5.19)', area >= 16.0)
    if n == 'kit': return ('≥ 8 м², ширина ≥ 2,3 м (п. 5.19, 5.22)', area >= 8 and min(w, hh) >= 2.3)
    if n == 'kitliv': return ('об\'єднання допустиме з електроплитою і витяжкою (п. 5.19)', True)
    if n in ('bed1', 'bed2'): return ('≥ 9 м² (п. 5.19)', area >= 9.0)
    if n == 'bath': return (('суміщений санвузол ≥ 4,9 м² (п. 5.20)', area >= 4.9) if combined else ('ванна ≥ 3,3 м² (п. 5.20)', area >= 3.3))
    if n == 'toilet': return ('туалет ≥ 1,5 м² (п. 5.20)', area >= 1.5)
    if n == 'corr': return ('ширина ≥ 1,5 м (п. 5.22)', min(w, hh) >= 1.5)
    if n == 'hall': return ('передпокій ширина ≥ 1,6 м (п. 5.22)', min(w, hh) >= 1.6 and area >= 5.0)
    return ('норми немає', None)
rown = 0; all_ok = True
seq = [('vest', VEST[2], VEST[3])] + [(n, R[n][2], R[n][3]) for n in order if n != 'vest']
total = 0.0
for i, (n, w, hh) in enumerate(seq, start=1):
    yy = hy + 22 + (i-1)*20
    if n == 'vest':
        nm, ar = 'Тамбур', w*hh
        status = ('≥ 1,5 × 2,2 м (п. 5.9)', min(w, hh) >= 1.5 and max(w, hh) >= 2.2)
        size = f"{w:.1f} × {hh:.1f}"
    else:
        ar = w*hh
        if n == 'hall': ar -= VEST[2]*VEST[3]
        nm = NAMES[n] if n != 'hall' else 'Передпокій'
        status = chk(n, w, hh, ar)
        size = f"{w:.1f} × {hh:.1f}"
    total += ar
    ok = status[1]
    mark = '' if ok is None else (' — OK' if ok else ' — НЕ ВИКОНАНО')
    if ok is False: all_ok = False
    for cx, t in zip(cols, [str(i), nm, size.replace('.', ','), f"{ar:.2f}".replace('.', ','), status[0] + mark]):
        a(f'<text x="{cx}" y="{yy:.1f}" font-size="11" fill="{"#c0392b" if ok is False else "#000"}">{t}</text>')
yy = hy + 22 + len(seq)*20 + 4
a(f'<line x1="34" y1="{yy-14:.1f}" x2="786" y2="{yy-14:.1f}" stroke="#aaa"/>')
a(f'<text x="{cols[1]}" y="{yy:.1f}" font-size="11" font-weight="bold">Сума приміщень</text>')
t1 = f"{total:.2f}".replace('.', ',')
a(f'<text x="{cols[3]}" y="{yy:.1f}" font-size="11" font-weight="bold">{t1} м²</text>')
yy += 20
a(f'<text x="{cols[1]}" y="{yy:.1f}" font-size="11">Внутрішня площа ({str(round(Wi,1)).replace('.', ',')} × {str(round(Di,1)).replace('.', ',')} м)</text>')
t2 = f"{Wi*Di:.2f}".replace('.', ',')
a(f'<text x="{cols[3]}" y="{yy:.1f}" font-size="11">{t2} м² (з перегородками)</text>')
yy += 20
a(f'<text x="{cols[1]}" y="{yy:.1f}" font-size="11">Площа забудови ({str(round(EW,1)).replace('.', ',')} × {str(round(EH,1)).replace('.', ',')} м)</text>')
t3 = f"{EW*EH:.2f}".replace('.', ',')
a(f'<text x="{cols[3]}" y="{yy:.1f}" font-size="11">{t3} м²</text>')
yy += 34
a(f'<text x="40" y="{yy:.1f}" font-size="11" fill="#777">Плани згенеровано розв\'язувачем обмежень за мінімумами ДБН В.2.2-15. Двері, вікна, шафа розміщені автоматично й умовно.</text>')
a(f'<text x="40" y="{yy+16:.1f}" font-size="11" fill="#777">Не перевірено: освітленість, висота приміщень, товщина перегородок, протипожежні вимоги, газове обладнання. Схема — ескіз, не робоче креслення.</text>')
a('</svg>')
open(out, 'w', encoding='utf-8').write('\n'.join(o))
print(out, 'all norms ok' if all_ok else 'NORM VIOLATION', 'sum', round(total, 2))
