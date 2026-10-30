#!/usr/bin/env python3
"""Original native SVG plates. No external assets or runtime dependencies."""
from pathlib import Path
from math import sin, cos, pi
import random

ROOT = Path(__file__).resolve().parent.parent / 'web/assets/art'
BONE, MOSS, GOLD, BG = '#eee9dc', '#b7c398', '#c5a467', '#111613'

def tag(name, **a):
    return '<'+name+' '+ ' '.join(f'{k.replace("_", "-")}="{v}"' for k,v in a.items())+'/>'
def path(d, **a): return tag('path', d=d, **a)
def line(x1,y1,x2,y2,**a): return tag('line',x1=x1,y1=y1,x2=x2,y2=y2,**a)
def circle(x,y,r,**a): return tag('circle',cx=x,cy=y,r=r,**a)
def poly(points, **a): return tag('polygon',points=' '.join(f'{x:.2f},{y:.2f}' for x,y in points),**a)
def ellipse(x,y,rx,ry,**a): return tag('ellipse',cx=x,cy=y,rx=rx,ry=ry,**a)
def text(x,y,s,**a):
    attrs=' '.join(f'{k.replace("_","-")}="{v}"' for k,v in a.items())
    return f'<text x="{x}" y="{y}" {attrs}>{s}</text>'

def opening(title,desc):
    return [f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="700" viewBox="0 0 900 700" role="img" aria-labelledby="title desc">
<title id="title">{title}</title><desc id="desc">{desc}</desc>
<defs>
  <pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(-28)"><path d="M0 0V7" stroke="{MOSS}" stroke-width=".55" opacity=".35"/></pattern>
  <pattern id="fine" width="4" height="4" patternUnits="userSpaceOnUse"><path d="M0 0V4" stroke="{BONE}" stroke-width=".45" opacity=".2"/></pattern>
  <radialGradient id="light"><stop stop-color="{MOSS}" stop-opacity=".13"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
</defs>
<g fill="none" stroke="{MOSS}" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">''']

def stars(parts, seed=7, n=65):
    rng=random.Random(seed)
    for i in range(n):
        x,y=rng.uniform(85,815),rng.uniform(45,620)
        if rng.random()<.12:
            parts += [path(f'M{x-3} {y}h6M{x} {y-3}v6',stroke=GOLD,opacity='.55')]
        else: parts += [circle(round(x,2),round(y,2),'.7',fill=MOSS,stroke='none',opacity='.4')]

def compass(parts,cx,cy,r, ticks=72):
    parts += [circle(cx,cy,r,opacity='.24'),circle(cx,cy,r+8,opacity='.12')]
    for i in range(ticks):
        a=i*2*pi/ticks; l=8 if i%6==0 else 3
        parts += [line(cx+(r-l)*cos(a),cy+(r-l)*sin(a),cx+r*cos(a),cy+r*sin(a),opacity='.5' if i%6==0 else '.25')]

def finish(name,parts):
    parts += ['</g></svg>']
    (ROOT/name).write_text('\n'.join(parts),encoding='utf-8')

def iso(x,y,z,origin=(450,490),scale=1): return (origin[0]+(x-y)*.866*scale,origin[1]+(x+y)*.5*scale-z*scale)

def box(parts,x,y,z,w,d,h,origin=(450,490),tone=BG,opacity=1):
    p=lambda a,b,c:iso(a,b,c,origin)
    faces=[([p(x,y,z+h),p(x+w,y,z+h),p(x+w,y+d,z+h),p(x,y+d,z+h)],tone),
           ([p(x,y+d,z),p(x+w,y+d,z),p(x+w,y+d,z+h),p(x,y+d,z+h)],BG),
           ([p(x+w,y,z),p(x+w,y+d,z),p(x+w,y+d,z+h),p(x+w,y,z+h)],'#1c241c')]
    for points,fill in faces: parts += [poly(points,fill=fill,opacity=opacity)]

def aperture():
    a=opening('La puerta de lo posible','Una puerta abierta dentro de una esfera armilar, suspendida sobre una escalera. Grabado imaginario: una invitación a explorar, no un modelo físico.')
    stars(a,3,82)
    a += [circle(463,308,290,fill='url(#light)',stroke='none')]
    compass(a,463,310,251,96)
    a += [line(463,31,463,610,opacity='.16',stroke_dasharray='2 8'),line(158,310,770,310,opacity='.1',stroke_dasharray='2 8')]
    # Dim rear armillary rings.
    for ang in [-42,42]:
        a += [ellipse(463,310,220,82,transform=f'rotate({ang} 463 310)',stroke=GOLD,opacity='.58')]
    a += [ellipse(463,310,153,225,transform='rotate(21 463 310)',opacity='.6'),ellipse(463,310,160,227,transform='rotate(21 463 310)',opacity='.2')]
    # Foundation, cut stone, and a staircase rising to the portal.
    for i in reversed(range(7)):
        x=354-i*8; y=513+i*11; w=202+i*16
        a += [path(f'M{x} {y}l{w} -22 44 20 -{w} 22Z',fill=BG,stroke=MOSS,opacity='.8'),path(f'M{x} {y}v8l44 20 {w} -22v-8',fill=BG,opacity='.65')]
        for j in range(13):
            q=x+48+j*(w-10)/13
            a += [line(q,y+18,q+4,y+23,opacity='.22')]
    # Portal block in pseudo-perspective.
    a += [path('M350 477V256C350 123 541 123 541 256V477L573 457V246C573 104 374 93 329 225V459Z',fill='#182019',stroke=MOSS,stroke_width='1.2')]
    a += [path('M350 477V256C350 123 541 123 541 256V477L514 483V259C514 163 378 163 378 259V483Z',fill=BG,stroke=BONE,stroke_width='1.6')]
    a += [path('M350 477V256C350 123 541 123 541 256V477L514 483V259C514 163 378 163 378 259V483Z',fill='url(#hatch)',stroke='none')]
    a += [path('M360 473V256C360 140 531 140 531 256V476M369 476V256C369 152 522 152 522 256V478',stroke=MOSS,opacity='.5')]
    for i in range(11):
        t=pi+i*pi/10; cx,cy=446,255
        a += [line(cx+96*cos(t),cy+96*sin(t),cx+71*cos(t),cy+71*sin(t),opacity='.6')]
    for y in range(276,476,25):
        a += [line(351,y,377,y+2,opacity='.4'),line(515,y+4,541,y,opacity='.4')]
    # Door ajar to the right, its engraved panel visible.
    a += [path('M513 484V258L463 232V450Z',fill='#202a20',stroke=BONE),path('M506 469V267L471 248V444Z',stroke=MOSS,opacity='.7'),circle(478,359,2,fill=GOLD,stroke='none')]
    for y in range(275,439,9): a += [line(477,y,501,y+13,opacity='.16')]
    # Light beyond: an incomplete circle, unclosed question.
    a += [path('M461 324A36 36 0 1 0 445 369',stroke=BONE,stroke_width='1.3'),circle(433,334,3,fill=GOLD,stroke='none'),path('M433 289V279M433 389V379M388 334H378',stroke=GOLD,opacity='.8')]
    # Foreground sweeping orbit is deliberately broken around the opening.
    a += [path('M263 370C303 423 479 451 616 393S716 282 646 259',stroke=MOSS,stroke_width='1.6'),path('M267 378C330 439 501 452 627 393',stroke=MOSS,opacity='.35')]
    a += [circle(626,389,7,fill=BG,stroke=GOLD),circle(626,389,2,fill=GOLD,stroke='none'),circle(288,179,4,fill=GOLD,stroke='none')]
    a += [path('M183 544h43m-21-21v43M713 132h24m-12-12v24',stroke=GOLD,opacity='.55')]
    a += [text(182,584,'I M A G I N A R',fill=MOSS,stroke='none',font_family='serif',font_size='9',opacity='.5'),text(660,570,'∴',fill=GOLD,stroke='none',font_family='serif',font_size='23',opacity='.8')]
    finish('apertura.svg',a)

def universals():
    a=opening('Cuatro puntos para orientarse','Cuatro construcciones geométricas sobre un mismo plano: realidad, persona, responsabilidad y reciprocidad. Ilustración simbólica de principios filosóficos.')
    stars(a,19,58)
    a += [ellipse(450,458,315,146,opacity='.3'),ellipse(450,458,327,153,opacity='.12')]
    o=(450,471)
    box(a,-176,-176,-24,352,352,24,o)
    for t in range(-176,177,22):
        a += [line(*iso(t,-176,1,o),*iso(t,176,1,o),opacity='.14'),line(*iso(-176,t,1,o),*iso(176,t,1,o),opacity='.14')]
    # Far plinth and ring.
    box(a,-47,-150,0,94,94,31,o)
    p=iso(0,-103,31,o)
    a += [ellipse(p[0],p[1]-93,54,89,fill=BG,stroke=MOSS,stroke_width='1.5'),ellipse(p[0]+9,p[1]-93,54,89,stroke=GOLD,opacity='.5')]
    for i in range(15):
        t=2*pi*i/15
        a += [line(p[0]+46*cos(t),p[1]-93+78*sin(t),p[0]+53*cos(t),p[1]-93+88*sin(t),opacity='.5')]
    a += [circle(p[0],p[1]-93,8,fill=BG,stroke=BONE),line(p[0]-35,p[1]-93,p[0]+35,p[1]-93,opacity='.4')]
    # Left: a tetrahedron, grounded geometry.
    box(a,-150,-47,0,94,94,31,o)
    p=iso(-103,0,31,o)
    a += [poly([(p[0]-59,p[1]+2),(p[0]+1,p[1]-176),(p[0]+63,p[1]+5),(p[0],p[1]+35)],fill=BG,stroke=BONE),path(f'M{p[0]} {p[1]+35}V{p[1]-176}',stroke=MOSS)]
    for i in range(1,12):
        k=i/12
        a += [line(p[0]-59*(1-k),p[1]+2-178*k,p[0],p[1]+35-211*k,opacity='.33')]
    # Right: balanced stacked cubes.
    box(a,-47,56,0,94,94,31,o)
    for z,w,shift in [(31,66,0),(97,48,7),(145,33,-1)]:
        box(a,-w/2,103-w/2+shift,z,w,w,w,o)
    # Near: an open arch, shared obligations.
    box(a,56,-47,0,94,94,31,o)
    box(a,67,-31,31,24,62,118,o)
    box(a,117,-31,31,24,62,118,o)
    box(a,67,-31,149,74,62,24,o)
    # Four compass emblems outside the field.
    for x,y,s in [(450,82,'I'),(753,370,'II'),(450,646,'III'),(150,370,'IV')]:
        a += [circle(x,y,19,opacity='.45'),text(x,y+4,s,text_anchor='middle',fill=MOSS,stroke='none',font_family='serif',font_size='11')]
    a += [line(450,107,450,130,opacity='.4'),line(720,370,694,370,opacity='.4'),line(450,613,450,591,opacity='.4'),line(185,370,211,370,opacity='.4')]
    finish('universales.svg',a)

def practice():
    a=opening('La práctica de comprobar','Un compás abierto sobre una mesa de medición y una escalera con peldaños. El instrumento representa decisiones revisables, no un mecanismo de adivinación.')
    stars(a,23,46)
    compass(a,450,343,251,96)
    a += [ellipse(450,455,266,108,stroke=GOLD,opacity='.4'),ellipse(450,455,248,100,opacity='.25')]
    # Measurement plane.
    o=(450,478)
    box(a,-159,-159,-12,318,318,12,o)
    for i in range(-154,155,22):
        a += [line(*iso(i,-154,1,o),*iso(i,154,1,o),opacity='.13'),line(*iso(-154,i,1,o),*iso(154,i,1,o),opacity='.13')]
    # Six rising steps.
    for i in range(6):
        box(a,4+i*23,-132,0,23,83,18+i*18,o)
    # Open compass legs, machined edges and hinge.
    a += [path('M434 187L296 482 319 487 450 222 566 480 587 474 466 186Z',fill=BG,stroke=BONE,stroke_width='1.8')]
    a += [path('M439 204L309 474M460 206L575 470',stroke=MOSS,opacity='.65')]
    a += [path('M296 482L294 514 319 487M566 480L590 503 587 474',fill=MOSS,stroke=BONE)]
    a += [path('M361 345Q447 390 531 344L525 332Q447 374 369 332Z',fill=BG,stroke=GOLD)]
    for i in range(23):
        t=pi*.28+pi*.44*i/22
        a += [line(447+154*cos(t),230+146*sin(t),447+154*cos(t),235+146*sin(t),stroke=GOLD,opacity='.6')]
    a += [circle(450,198,31,fill=BG,stroke=BONE),circle(450,198,22,stroke=MOSS),circle(450,198,7,fill=GOLD,stroke='none')]
    a += [path('M443 168V137Q450 126 457 137V168',fill=BG,stroke=BONE)]
    a += [path('M447 147h6M447 153h6M447 159h6',opacity='.55')]
    # Drawn incomplete arc below the tips.
    a += [path('M294 514C345 551 520 558 590 503',stroke=BONE,stroke_width='1.3'),path('M307 517C372 549 520 543 572 506',opacity='.35',stroke_dasharray='2 6')]
    a += [circle(450,482,3,fill=GOLD,stroke='none'),line(437,482,463,482,stroke=GOLD),line(450,469,450,495,stroke=GOLD)]
    # Calibration decoration.
    a += [line(197,598,703,598,opacity='.35')]
    for i in range(51):
        x=197+i*10.12
        a += [line(x,598,x,590-(7 if i%5==0 else 0),opacity='.5')]
    a += [text(450,635,'P R E G U N T A R   ·   C O M P R O B A R   ·   C O R R E G I R',text_anchor='middle',fill=MOSS,stroke='none',font_family='serif',font_size='9',opacity='.65')]
    finish('practica.svg',a)

def city():
    a=opening('Áncora: el archivo abierto','Una ciudad imaginaria de torres y un archivo abierto en su centro. Escena del relato Los Últimos Universales, una ficción sobre el poder y la memoria.')
    stars(a,51,92)
    a += [circle(449,214,106,stroke=GOLD,opacity='.35'),circle(449,214,116,opacity='.14'),path('M449 74V104M449 324V345M309 214H339M559 214H589',stroke=GOLD,opacity='.4')]
    # Contour/horizon architecture, back to front.
    o=(450,459)
    box(a,-182,-182,-25,364,364,25,o)
    for i in range(-168,169,24):
        a += [line(*iso(i,-182,0,o),*iso(i,182,0,o),opacity='.14'),line(*iso(-182,i,0,o),*iso(182,i,0,o),opacity='.14')]
    buildings=[(-145,-130,47,50,158),(-75,-150,43,40,204),(5,-150,43,40,126),(83,-144,54,47,162),(-157,-38,42,43,111),(-95,-62,43,41,151),(70,-60,49,43,130),(125,20,30,38,88),(-150,65,37,47,97),(-88,102,38,41,77)]
    for x,y,w,d,h in buildings:
        box(a,x,y,0,w,d,h,o)
        for z in range(18,h-8,16):
            for j in range(2):
                p=iso(x+w,y+10+j*16,z,o)
                a += [line(p[0],p[1],p[0],p[1]-6,stroke=GOLD,opacity='.45')]
        if h>150:
            box(a,x+8,y+8,h,w-16,d-16,13,o)
            p=iso(x+w/2,y+d/2,h+13,o)
            a += [line(*p,p[0],p[1]-26,opacity='.65'),circle(p[0],p[1]-28,2,fill=GOLD,stroke='none')]
    # Open archival book, resting on a plinth in the foreground.
    box(a,-19,18,0,135,117,27,o)
    a += [path('M438 506C398 471 344 468 306 480V373C346 358 401 364 438 393C476 365 528 358 570 373V480C526 467 477 473 438 506Z',fill='#1b241b',stroke=BONE,stroke_width='1.4')]
    a += [path('M438 494C398 460 350 457 316 467V367C356 355 402 363 438 392C476 363 523 355 560 367V467C523 457 476 462 438 494Z',fill=BG,stroke=BONE,stroke_width='1.3')]
    a += [path('M438 393V494',stroke=GOLD),path('M316 473C356 464 402 471 438 500C474 471 525 464 560 473',opacity='.7')]
    for y in range(388,458,10):
        a += [path(f'M329 {y}Q376 {y-6} 422 {y+22}',stroke=MOSS,opacity='.38'),path(f'M453 {y+22}Q499 {y-6} 547 {y}',stroke=MOSS,opacity='.38')]
    # The open mark, a gap in a circle at the top of the archive.
    a += [path('M463 316A30 30 0 1 0 449 334',stroke=BONE,stroke_width='1.4'),line(438,273,438,258,stroke=GOLD),circle(438,305,3,fill=GOLD,stroke='none')]
    # Path to archive, person for a readable sense of scale.
    for i in range(6):
        a += [line(401-i*6,555+i*10,472+i*6,555+i*10,opacity='.35')]
    a += [circle(585,539,4,fill=MOSS,stroke='none'),path('M585 545v20m0-16-7 9m7-9 7 9m-7 7-5 12m5-12 5 12',stroke=MOSS,stroke_width='1.7')]
    a += [text(450,649,'L O S   Ú L T I M O S   U N I V E R S A L E S',text_anchor='middle',fill=MOSS,stroke='none',font_family='serif',font_size='10',opacity='.6')]
    finish('ancoro.svg',a)

if __name__ == '__main__':
    ROOT.mkdir(parents=True,exist_ok=True)
    aperture(); universals(); practice(); city()
    print('Created 4 original SVG plates in web/assets/art/')
