#!/usr/bin/env python3
"""Generate this site's Costa surface illustration, using only Python's stdlib.

Run from any directory with Python >= 3.10:
    python3 scripts/generate_costa.py

Mathematics: O. Michael Melko, Visualizing Minimal Surfaces (2010), (16)--(17):
https://content.wolfram.com/sites/19/2010/12/Melko.pdf
The Weierstrass data are f = wp(z), g = sqrt(8*pi*e1)/wp'(z) on the square
torus C/(Z+iZ), punctured at 0, 1/2, i/2.  We evaluate the explicit integrated
formula, not a look-alike implicit surface or a deformed torus.  The drawing
is a finite part of this noncompact surface: the three punctures are cut off
by small circles in the parameter domain.  Their images form the three rims.

The elliptic functions are computed from Jacobi theta series, q = exp(-pi),
reduced to the centered unit square. Eight terms suffice in double precision
on this compact domain. Coordinate curves and rims are projected to SVG;
a software depth buffer removes lines hidden by the surface. No downloaded
geometry, bitmap, graphics package, or runtime dependency is used.
"""

from __future__ import annotations

import cmath
import json
import math
from pathlib import Path

PI = math.pi
Q = math.exp(-PI)
TERMS = [(2*n+1, 2*(-1)**n * Q**((n+.5)**2)) for n in range(8)]
WIDTH, HEIGHT = 600, 400
AZIMUTH, ELEVATION = math.radians(36), math.radians(23)
CA, SA = math.cos(AZIMUTH), math.sin(AZIMUTH)
CE, SE = math.cos(ELEVATION), math.sin(ELEVATION)
# Different radii compensate for the different rates of divergence of the ends.
CUTS = [(0j, .115), (.5+0j, .026), (.5j, .026)]


def elliptic(z: complex) -> tuple[complex, complex]:
    """Return zeta(z), wp(z), for basic periods 1, i."""
    m, n = math.floor(z.real + .5), math.floor(z.imag + .5)
    w = z - complex(m, n)
    t = t1 = t2 = 0j
    for k, a in TERMS:
        s, c = cmath.sin(k*PI*w), cmath.cos(k*PI*w)
        t += a*s
        t1 += a*k*c
        t2 -= a*k*k*s
    ratio = t1/t
    return (PI*w + PI*ratio + PI*complex(m, -n),
            -PI - PI*PI*(t2/t - ratio*ratio))


E1 = elliptic(.5)[1].real


def costa(u: float, v: float) -> tuple[float, float, float]:
    """The explicit Weierstrass immersion; a constant translation is omitted."""
    z = complex(u, v)
    zeta, wp = elliptic(z)
    delta = elliptic(z-.5)[0] - elliptic(z-.5j)[0]
    x = (-.5*zeta + .5*PI*z + PI/(4*E1)*delta).real
    y = (-.5j*zeta - .5j*PI*z - 1j*PI/(4*E1)*delta).real
    h = math.sqrt(2*PI)/4 * math.log(abs((wp-E1)/(wp+E1)))
    # This translation places X((1+i)/2) at the origin.
    shift = PI*PI/(8*E1)
    return x+shift, y+shift, h


def domain(u: float, v: float) -> bool:
    """Keep points outside the three marked disks on the square torus."""
    for center, radius in CUTS:
        du = u - center.real
        dv = v - center.imag
        du -= round(du)
        dv -= round(dv)
        if du*du + dv*dv < radius*radius - 1e-14:
            return False
    return True


def camera(p):
    x, y, z = p
    horizontal = CA*x - SA*y
    along = SA*x + CA*y
    return horizontal, CE*z - SE*along, CE*along + SE*z


def simplify(points, tolerance=.16):
    """Ramer--Douglas--Peucker in SVG coordinates, below 0.1 display pixels."""
    if len(points)<3:
        return points
    a,b = points[0],points[-1]
    dx,dy = b[0]-a[0],b[1]-a[1]
    length = dx*dx+dy*dy
    distances=[]
    for x,y in points[1:-1]:
        t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/length)) if length else 0
        distances.append((x-a[0]-t*dx)**2+(y-a[1]-t*dy)**2)
    farthest=max(distances)
    if farthest<=tolerance*tolerance:
        return [a,b]
    index=distances.index(farthest)+1
    return simplify(points[:index+1],tolerance)[:-1]+simplify(points[index:],tolerance)


def validate():
    """Check periods, conformality and mean curvature away from punctures."""
    max_period = max_conformal = max_mean = 0.
    samples = [(.17,.23),(.31,.41),(.63,.72),(.81,.28),(.38,.63)]
    step = 1e-4
    for u, v in samples:
        p = costa(u,v)
        for a,b in [(u+1,v),(u,v+1)]:
            max_period = max(max_period, math.dist(p,costa(a,b)))
        up, um = costa(u+step,v), costa(u-step,v)
        vp, vm = costa(u,v+step), costa(u,v-step)
        xu = [(a-b)/(2*step) for a,b in zip(up,um)]
        xv = [(a-b)/(2*step) for a,b in zip(vp,vm)]
        xuu = [(a-2*b+c)/(step*step) for a,b,c in zip(up,p,um)]
        xvv = [(a-2*b+c)/(step*step) for a,b,c in zip(vp,p,vm)]
        pp, pm = costa(u+step,v+step), costa(u+step,v-step)
        mp, mm = costa(u-step,v+step), costa(u-step,v-step)
        xuv = [(a-b-c+d)/(4*step*step) for a,b,c,d in zip(pp,pm,mp,mm)]
        dot = lambda a,b: sum(x*y for x,y in zip(a,b))
        e,f,g = dot(xu,xu),dot(xu,xv),dot(xv,xv)
        cross = [xu[1]*xv[2]-xu[2]*xv[1], xu[2]*xv[0]-xu[0]*xv[2], xu[0]*xv[1]-xu[1]*xv[0]]
        length = math.sqrt(dot(cross,cross))
        normal = [c/length for c in cross]
        h = (dot(xuu,normal)*g - 2*dot(xuv,normal)*f + dot(xvv,normal)*e)/(2*(e*g-f*f))
        max_mean = max(max_mean,abs(h))
        max_conformal = max(max_conformal,abs(e/g-1),abs(f)/math.sqrt(e*g))
    assert max_period < 1e-11
    assert max_conformal < 1e-4
    assert max_mean < 1e-4
    return dict(e1=E1,period_error=max_period,conformal_error=max_conformal,mean_curvature_error=max_mean)


def render():
    # A dense, internal mesh is used only for visibility; the visible wireframe
    # is much sparser so it remains legible at the website's display size.
    size = 220
    vertices = {}
    for j in range(size+1):
        for i in range(size+1):
            u,v = i/size,j/size
            if domain(u,v):
                vertices[i,j] = camera(costa(u,v))

    xs = [p[0] for p in vertices.values()]
    ys = [p[1] for p in vertices.values()]
    scale = min((WIDTH-44)/(max(xs)-min(xs)), (HEIGHT-52)/(max(ys)-min(ys)))
    cx,cy = (max(xs)+min(xs))/2,(max(ys)+min(ys))/2
    def project(p):
        x,y,depth = p
        return WIDTH/2 + scale*(x-cx), HEIGHT/2 - scale*(y-cy), depth
    vertices = {k:project(p) for k,p in vertices.items()}

    depth = [-math.inf]*(WIDTH*HEIGHT)
    triangles = []
    for j in range(size):
        for i in range(size):
            for keys in [((i,j),(i+1,j),(i+1,j+1)),((i,j),(i+1,j+1),(i,j+1))]:
                if all(k in vertices for k in keys):
                    triangles.append(tuple(vertices[k] for k in keys))
    for a,b,c in triangles:
        den = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
        if abs(den) < 1e-9:
            continue
        for y in range(max(0,math.floor(min(a[1],b[1],c[1]))), min(HEIGHT-1,math.ceil(max(a[1],b[1],c[1])))+1):
            for x in range(max(0,math.floor(min(a[0],b[0],c[0]))), min(WIDTH-1,math.ceil(max(a[0],b[0],c[0])))+1):
                px,py = x+.5,y+.5
                wa = ((b[1]-c[1])*(px-c[0]) + (c[0]-b[0])*(py-c[1]))/den
                wb = ((c[1]-a[1])*(px-c[0]) + (a[0]-c[0])*(py-c[1]))/den
                wc = 1-wa-wb
                if min(wa,wb,wc) >= -1e-5:
                    k = y*WIDTH+x
                    depth[k] = max(depth[k],wa*a[2]+wb*b[2]+wc*c[2])

    paths=[]
    def emit(points, rim=False):
        current=[]
        def flush():
            if len(current)>1 and sum(math.dist(a,b) for a,b in zip(current,current[1:]))>1.5:
                paths.append((simplify(list(current)),rim))
            current.clear()
        for uv in points:
            if uv is None or not domain(*uv):
                flush()
                continue
            x,y,z = project(camera(costa(*uv)))
            ix,iy = math.floor(x-.5),math.floor(y-.5)
            # The tolerance is in projected world units, allowing for the finite
            # depth mesh without drawing curves through the opposite sheet.
            nearby=[depth[yy*WIDTH+xx] for yy in (iy,iy+1) for xx in (ix,ix+1) if 0<=xx<WIDTH and 0<=yy<HEIGHT]
            visible = bool(nearby) and z >= min(nearby)-.018
            if not visible:
                flush()
            else:
                current.append((x,y))
        flush()

    divisions, samples = 34, 900
    for k in range(divisions):
        t=(k+.5)/divisions
        emit([(t,j/samples) for j in range(samples+1)])
        emit([(j/samples,t) for j in range(samples+1)])
    for center,radius in CUTS:
        # Evaluate the full loop; periodicity gives the same rim on the torus.
        emit([(center.real+radius*math.cos(2*PI*j/900),center.imag+radius*math.sin(2*PI*j/900)) for j in range(901)],rim=True)
        # Circles adapted to the punctures prevent the ends from being sparsely
        # sampled by the rectangular coordinate lines alone.
        for k in range(1,8):
            r=radius*(1.6 if center==0j else 6.0)**(k/8)
            emit([(center.real+r*math.cos(2*PI*j/600),center.imag+r*math.sin(2*PI*j/600)) for j in range(601)])

    path_tags=[]
    for points,rim in paths:
        d='M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in points)
        path_tags.append(f'<path d="{d}" class="{"rim" if rim else "mesh"}"/>')
    svg='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" role="img" aria-labelledby="title desc">
<title id="title">Costa minimal surface</title>
<desc id="desc">A mathematically generated finite portion of Costa's genus-one minimal surface, with one planar and two catenoidal ends.</desc>
<style>svg{color:#234d78}path{fill:none;stroke:currentColor;stroke-linejoin:round;stroke-linecap:round}.mesh{stroke-width:1.05;opacity:.62}.rim{stroke-width:1.4;opacity:.85}@media(prefers-color-scheme:dark){svg{color:#a4c8ee}}</style>
'''+ '\n'.join(path_tags)+'\n</svg>\n'
    output=Path(__file__).resolve().parents[1]/'assets/surfaces/costa.svg'
    output.write_text(svg,encoding='utf-8')
    return dict(output=str(output),bytes=output.stat().st_size,visible_paths=len(paths),visibility_triangles=len(triangles))


if __name__ == '__main__':
    print(json.dumps({'validation':validate(),'render':render()},indent=2))
