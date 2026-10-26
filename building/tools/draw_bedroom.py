import json, sys
src, idx, out, title, sub, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]  # mode: in | out
L = json.load(open(src))[idx]
W, H = 3.6, 2.8
S = 160.0; X0, Y0 = 200.0, 130.0
def X(x): return X0 + x*S
def Y(y): return Y0 + y*S
def f1(v): return f"{v:.2f}".replace('.', ',')
o = []; a = o.append
VW, VH = 960, 1080
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {VH}" width="{VW}" height="{VH}" font-family="Arial, sans-serif">')
a(f'<rect width="{VW}" height="{VH}" fill="#fff"/>')
a(f'<text x="{VW/2}" y="34" text-anchor="middle" font-size="18" font-weight="bold">{title}</text>')
a(f'<text x="{VW/2}" y="56" text-anchor="middle" font-size="12" fill="#444">{sub}</text>')
a(f'<text x="{VW/2}" y="76" text-anchor="middle" font-size="11" fill="#777">Масштаб: 1 м = {S:.0f} px. Внутрішні розміри кімнати 3,6 × 2,8 м (10,1 м²). Схід — зовнішня стіна з вікном.</text>')
# walls: east wall 0.4 thick (exterior), others 0.1 (partitions) drawn as outer ring
a(f'<rect x="{X(-0.1):.1f}" y="{Y(-0.1):.1f}" width="{(W+0.1+0.4)*S:.1f}" height="{(H+0.2)*S:.1f}" fill="#4a4a4a"/>')
a(f'<rect x="{X(0):.1f}" y="{Y(0):.1f}" width="{W*S:.1f}" height="{H*S:.1f}" fill="#fbf8f2"/>')
# window east y 0.8..2.0
a(f'<rect x="{X(W):.1f}" y="{Y(0.8):.1f}" width="{0.4*S:.1f}" height="{1.2*S:.1f}" fill="#fff"/>')
a(f'<rect x="{X(W)+0.4*S*0.35:.1f}" y="{Y(0.8):.1f}" width="{0.4*S*0.3:.1f}" height="{1.2*S:.1f}" fill="#9fd0ff" stroke="#2874a6" stroke-width="0.8"/>')
a(f'<text x="{X(W)+0.4*S+8:.1f}" y="{Y(1.4)+4:.1f}" font-size="11">вікно 1,2 м</text>')
# door west y 0.1..1.0
a(f'<rect x="{X(-0.1)-1:.1f}" y="{Y(0.1):.1f}" width="{0.1*S+2:.1f}" height="{0.9*S:.1f}" fill="#fff"/>')
if mode == 'in':
    # swing zone shaded + arc inside
    a(f'<rect x="{X(0):.1f}" y="{Y(0.1):.1f}" width="{0.9*S:.1f}" height="{0.9*S:.1f}" fill="#fde2e2" opacity="0.7"/>')
    a(f'<path d="M {X(0.9):.1f} {Y(0.1):.1f} A {0.9*S:.1f} {0.9*S:.1f} 0 0 1 {X(0):.1f} {Y(1.0):.1f}" fill="none" stroke="#c0392b" stroke-dasharray="4 3"/>')
    a(f'<line x1="{X(0):.1f}" y1="{Y(0.1):.1f}" x2="{X(0.9):.1f}" y2="{Y(0.1):.1f}" stroke="#c0392b"/>')
    a(f'<text x="{X(0.45):.1f}" y="{Y(0.62):.1f}" text-anchor="middle" font-size="9" fill="#c0392b">зона</text>')
    a(f'<text x="{X(0.45):.1f}" y="{Y(0.62)+11:.1f}" text-anchor="middle" font-size="9" fill="#c0392b">дверей</text>')
else:
    a(f'<rect x="{X(0):.1f}" y="{Y(0.1):.1f}" width="{0.6*S:.1f}" height="{0.9*S:.1f}" fill="#e9f5ea" opacity="0.8"/>')
    a(f'<text x="{X(0.3):.1f}" y="{Y(0.55):.1f}" text-anchor="middle" font-size="9" fill="#2e7d32">вхідна</text>')
    a(f'<text x="{X(0.3):.1f}" y="{Y(0.55)+11:.1f}" text-anchor="middle" font-size="9" fill="#2e7d32">зона</text>')
    a(f'<path d="M {X(-0.1):.1f} {Y(0.1):.1f} A {0.9*S:.1f} {0.9*S:.1f} 0 0 0 {X(-0.1)-0.9*S:.1f} {Y(1.0):.1f}" fill="none" stroke="#777" stroke-dasharray="4 3"/>')
    a(f'<text x="{X(-0.1)-8:.1f}" y="{Y(1.55):.1f}" text-anchor="end" font-size="10" fill="#555">двері назовні</text>')
    a(f'<text x="{X(-0.1)-8:.1f}" y="{Y(1.55)+11:.1f}" text-anchor="end" font-size="10" fill="#555">або розсувні</text>')
def rect(r, fill, stroke="#444", sw=1.4, dash=None, op=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    a(f'<rect x="{X(r[0]):.1f}" y="{Y(r[1]):.1f}" width="{(r[2]-r[0])*S:.1f}" height="{(r[3]-r[1])*S:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d} opacity="{op}"/>')
def label(r, lines, fs=11):
    cx, cy = X((r[0]+r[2])/2), Y((r[1]+r[3])/2)
    for i, t in enumerate(lines):
        a(f'<text x="{cx:.1f}" y="{cy+(i-(len(lines)-1)/2)*(fs+2)+4:.1f}" text-anchor="middle" font-size="{fs}">{t}</text>')
# clearance zones (dashed)
for z in L['free_sides']: rect(z, '#e8f4fd', '#5dade2', 1, '5 3', 0.7)
if L['foot']: rect(L['foot'], '#e8f4fd', '#5dade2', 1, '5 3', 0.7)
rect(L['wd_front'], '#fff3e0', '#e67e22', 1, '5 3', 0.7)
rect(L['chair'], '#f3e5f5', '#9b59b6', 1, '5 3', 0.7)
# furniture
bd = L['bed']; rect(bd, '#d7ccc8', '#5d4037', 1.6)
# pillows at head (east): two pillows
for k in range(2):
    py0 = bd[1] + 0.12 + k*0.72; rect((bd[2]-0.40, py0, bd[2]-0.08, py0+0.62), '#ffffff', '#8d6e63', 1)
a(f'<text x="{X((bd[0]+bd[2])/2)-20:.1f}" y="{Y((bd[1]+bd[3])/2)+4:.1f}" text-anchor="middle" font-size="12" font-weight="bold">Ліжко 160×200</text>')
for ns in L['ns']:
    rect(ns, '#bcaaa4', '#5d4037', 1.4)
a(f'<text x="{X(L["ns"][0][0])-4:.1f}" y="{Y(L["ns"][0][1])-5:.1f}" text-anchor="end" font-size="9">тумба 40×35</text>')
a(f'<text x="{X(L["ns"][1][0])-4:.1f}" y="{Y(L["ns"][1][3])+11:.1f}" text-anchor="end" font-size="9">тумба 40×35</text>')
ds = L['desk']; rect(ds, '#cfd8dc', '#455a64', 1.6)
label(ds, ['Стіл', f"{round((ds[2]-ds[0])*100)}×{round((ds[3]-ds[1])*100)}"], 10)
ch = L['chair']; cx0 = (ch[0]+ch[2])/2; cy0 = (ch[1]+ch[3])/2
a(f'<circle cx="{X(cx0):.1f}" cy="{Y(cy0):.1f}" r="{0.22*S:.1f}" fill="#eceff1" stroke="#455a64"/>')
a(f'<text x="{X(cx0):.1f}" y="{Y(cy0)+3:.1f}" text-anchor="middle" font-size="8">стілець</text>')
wd = L['wd']; rect(wd, '#c5cae9', '#303f9f', 1.6)
# sliding doors lines (along the long axis)
if wd[3]-wd[1] > wd[2]-wd[0]:
    n = int(round((wd[3]-wd[1])/0.6)); 
    for i in range(1, n):
        yy = wd[1] + i*(wd[3]-wd[1])/n; a(f'<line x1="{X(wd[0]):.1f}" y1="{Y(yy):.1f}" x2="{X(wd[2]):.1f}" y2="{Y(yy):.1f}" stroke="#303f9f" stroke-width="0.8"/>')
a(f'<text x="{X((wd[0]+wd[2])/2):.1f}" y="{Y((wd[1]+wd[3])/2)-4:.1f}" text-anchor="middle" font-size="9" font-weight="bold">Шафа</text>')
a(f'<text x="{X((wd[0]+wd[2])/2):.1f}" y="{Y((wd[1]+wd[3])/2)+8:.1f}" text-anchor="middle" font-size="8">{round((wd[3]-wd[1])*100)}×60</text>')
# dimension helper
def dim(x1, y1, x2, y2, text, off=(0, -6)):
    a(f'<line x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" y2="{Y(y2):.1f}" stroke="#c0392b" stroke-width="1.2"/>')
    for (xx, yy) in ((x1, y1), (x2, y2)):
        if abs(x1-x2) < 1e-6: a(f'<line x1="{X(xx)-4:.1f}" y1="{Y(yy):.1f}" x2="{X(xx)+4:.1f}" y2="{Y(yy):.1f}" stroke="#c0392b"/>')
        else: a(f'<line x1="{X(xx):.1f}" y1="{Y(yy)-4:.1f}" x2="{X(xx):.1f}" y2="{Y(yy)+4:.1f}" stroke="#c0392b"/>')
    a(f'<text x="{(X(x1)+X(x2))/2+off[0]:.1f}" y="{(Y(y1)+Y(y2))/2+off[1]:.1f}" text-anchor="middle" font-size="10" font-weight="bold" fill="#c0392b">{text}</text>')
gaps = []
ymid = (bd[1]+bd[3])/2
# wardrobe front <-> bed foot (x direction), if overlap in y
if wd[2] <= bd[0] and min(wd[3], bd[3]) > max(wd[1], bd[1]):
    yy = (max(wd[1], bd[1]) + min(wd[3], bd[3]))/2; g = bd[0]-wd[2]; dim(wd[2], yy, bd[0], yy, f"{round(g*100)} см", (0, -6)); gaps.append(('Шафа (фасад) — ніжки ліжка', g))
# north and south side gaps of the bed
if bd[1] > 0.3:
    xx = bd[0]+0.5; dim(xx, 0, xx, bd[1], f"{round(bd[1]*100)} см", (22, 4)); gaps.append(('Прохід із півночі від ліжка до стіни', bd[1]))
if H-bd[3] > 0.3:
    xx = bd[0]+0.5
    top = bd[3]; bottom = ds[1] if (ds[1] > bd[3]-0.01 and ds[0] < xx < ds[2]) else H
    dim(xx, top, xx, bottom, f"{round((bottom-top)*100)} см", (22, 4)); gaps.append(('Прохід з півдня від ліжка до стіни/столу', bottom-top))
# overall dims
a(f'<line x1="{X(0):.1f}" y1="{Y(H)+34:.1f}" x2="{X(W):.1f}" y2="{Y(H)+34:.1f}" stroke="#222"/>')
a(f'<text x="{X(W/2):.1f}" y="{Y(H)+28:.1f}" text-anchor="middle" font-size="11">3,60 м</text>')
a(f'<line x1="{X(0)-92:.1f}" y1="{Y(0):.1f}" x2="{X(0)-92:.1f}" y2="{Y(H):.1f}" stroke="#222"/>')
a(f'<text x="{X(0)-98:.1f}" y="{Y(H/2)+4:.1f}" text-anchor="end" font-size="11">2,80 м</text>')
# legend
ly = Y(H) + 76
a(f'<text x="40" y="{ly:.1f}" font-size="14" font-weight="bold">Меблі і розміри (припущення, не норми)</text>')
items = [
 ("Ліжко 160 × 200 см, узголів'я до східної стіни, під вікном", "#d7ccc8"),
 ("Тумби 40 × 35 см з обох боків узголів'я", "#bcaaa4"),
 (f"Стіл {round((ds[2]-ds[0])*100)} × {round((ds[3]-ds[1])*100)} см, стілець, зона стільця 50 см", "#cfd8dc"),
 (f"Шафа {round((wd[3]-wd[1])*100)} × 60 см, розсувні двері, фронт 70 см", "#c5cae9"),
]
for i, (t, c) in enumerate(items):
    yy = ly + 20 + i*20
    a(f'<rect x="40" y="{yy-10:.1f}" width="18" height="12" fill="{c}" stroke="#555"/>'); a(f'<text x="66" y="{yy:.1f}" font-size="11">{t}</text>')
yy = ly + 20 + len(items)*20 + 6
a(f'<text x="40" y="{yy:.1f}" font-size="12" font-weight="bold">Зони:</text>')
zl = [("#e8f4fd", "проходи біля ліжка (60 см)"), ("#fff3e0", "фронт шафи (70 см)"), ("#f3e5f5", "зона стільця (50 см)")]
if mode == 'in': zl.append(("#fde2e2", "зона відкривання дверей (0,9 × 0,9 м)"))
else: zl.append(("#e9f5ea", "вхідна зона (0,6 × 0,9 м)"))
for i, (c, t) in enumerate(zl):
    xx = 40 + (i % 2)*380; y2 = yy + 18 + (i//2)*18
    a(f'<rect x="{xx}" y="{y2-10:.1f}" width="18" height="12" fill="{c}" stroke="#999" stroke-dasharray="3 2"/>'); a(f'<text x="{xx+26}" y="{y2:.1f}" font-size="11">{t}</text>')
yy = yy + 18 + ((len(zl)+1)//2)*18 + 14
a(f'<text x="40" y="{yy:.1f}" font-size="12" font-weight="bold">Проходи (виміряно за креслеником):</text>')
for i, (t, g) in enumerate(gaps):
    a(f'<text x="40" y="{yy+18+i*18:.1f}" font-size="11">{t}: {round(g*100)} см</text>')
yy += 18 + len(gaps)*18 + 18
notes = ["Розкладку знайдено автоматичним перебором: меблі біля стін, зони вільні, шлях від дверей до ліжка, столу і шафи шириною ≥ 0,6 м.",
         "Не враховано: розетки, вимикачі, батареї, фактичні розміри обраних меблів, відчинення вікна, сторону світу."]
for i, t in enumerate(notes):
    a(f'<text x="40" y="{yy+i*16:.1f}" font-size="10" fill="#777">{t}</text>')
a('</svg>')
open(out, 'w', encoding='utf-8').write('\n'.join(o))
print('ok', out, [(t, round(g, 2)) for t, g in gaps])
