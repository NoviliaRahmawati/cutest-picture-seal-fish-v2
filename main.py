#!/usr/bin/env python3
"""Draw a cozy baby seal hugging its tiny fish plushie."""
import math
import os
import struct
import zlib

W = H = 640
S = 2
CW = CH = W * S


class Canvas:
    def __init__(self):
        self.p = bytearray(CW * CH * 3)
        # Warm cream-to-peach paper sky, softly lit behind the characters.
        for y in range(CH):
            t = y / (CH - 1)
            row = bytearray(CW * 3)
            for x in range(CW):
                nx = (x / (CW - 1) - .49) / .78
                ny = (y / (CH - 1) - .43) / .88
                glow = max(0.0, 1.0 - math.sqrt(nx * nx + ny * ny)) ** 2
                row[x*3:x*3+3] = bytes((
                    int(250 - 15*t + 4*glow),
                    int(224 - 17*t + 10*glow),
                    int(207 - 8*t + 12*glow)))
            self.p[y*CW*3:(y+1)*CW*3] = row

    def ellipse(self, cx, cy, rx, ry, color, angle=0.0):
        cx, cy, rx, ry = cx*S, cy*S, rx*S, ry*S
        ca, sa = math.cos(angle), math.sin(angle)
        ex = int(math.sqrt((rx*ca)**2 + (ry*sa)**2)) + 2
        ey = int(math.sqrt((rx*sa)**2 + (ry*ca)**2)) + 2
        x0, x1 = max(0, int(cx-ex)), min(CW-1, int(cx+ex))
        y0, y1 = max(0, int(cy-ey)), min(CH-1, int(cy+ey))
        cr, cg, cb = color
        for y in range(y0, y1+1):
            dy = y-cy
            for x in range(x0, x1+1):
                dx = x-cx
                u = (dx*ca + dy*sa)/rx
                v = (-dx*sa + dy*ca)/ry
                if u*u + v*v <= 1:
                    i = (y*CW+x)*3
                    self.p[i:i+3] = bytes((cr, cg, cb))

    def circle(self, x, y, r, color):
        self.ellipse(x, y, r, r, color)

    def line(self, x1, y1, x2, y2, width, color):
        x1*=S; y1*=S; x2*=S; y2*=S; rad=width*S/2
        dx=x2-x1; dy=y2-y1; den=dx*dx+dy*dy
        xa=max(0,int(min(x1,x2)-rad-1)); xb=min(CW-1,int(max(x1,x2)+rad+1))
        ya=max(0,int(min(y1,y2)-rad-1)); yb=min(CH-1,int(max(y1,y2)+rad+1))
        cr,cg,cb=color
        for y in range(ya,yb+1):
            for x in range(xa,xb+1):
                t=max(0,min(1,((x-x1)*dx+(y-y1)*dy)/den)) if den else 0
                if (x-(x1+t*dx))**2+(y-(y1+t*dy))**2 <= rad*rad:
                    i=(y*CW+x)*3
                    self.p[i:i+3]=bytes((cr,cg,cb))

    def polygon(self, points, color):
        """Filled polygon by scanline intersections; coordinates are design pixels."""
        pts=[(x*S,y*S) for x,y in points]
        ymin=max(0,int(min(y for _,y in pts))); ymax=min(CH-1,int(max(y for _,y in pts)))
        cr,cg,cb=color
        for y in range(ymin,ymax+1):
            scan=y+.5; hits=[]
            for (x1,y1),(x2,y2) in zip(pts,pts[1:]+pts[:1]):
                if (y1<=scan<y2) or (y2<=scan<y1):
                    hits.append(x1+(scan-y1)*(x2-x1)/(y2-y1))
            hits.sort()
            for left,right in zip(hits[::2],hits[1::2]):
                x0=max(0,int(left)); x1=min(CW-1,int(right))
                if x1>=x0:
                    self.p[(y*CW+x0)*3:(y*CW+x1+1)*3]=bytes((cr,cg,cb))*(x1-x0+1)

    def star(self,x,y,r,color):
        self.line(x-r,y,x+r,y,2,color); self.line(x,y-r,x,y+r,2,color)
        self.line(x-r*.55,y-r*.55,x+r*.55,y+r*.55,1.2,color)
        self.line(x-r*.55,y+r*.55,x+r*.55,y-r*.55,1.2,color)

    def downsample(self):
        out=bytearray(W*H*3)
        for y in range(H):
            for x in range(W):
                a=((2*y)*CW+2*x)*3; b=a+3; c=a+CW*3; d=c+3
                j=(y*W+x)*3
                for k in range(3): out[j+k]=(self.p[a+k]+self.p[b+k]+self.p[c+k]+self.p[d+k])//4
        return bytes(out)


def png(rgb):
    def chunk(kind,data):
        body=kind+data
        return struct.pack('!I',len(data))+body+struct.pack('!I',zlib.crc32(body)&0xffffffff)
    scan=b''.join(b'\0'+rgb[y*W*3:(y+1)*W*3] for y in range(H))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',W,H,8,2,0,0,0))+
            chunk(b'IDAT',zlib.compress(scan,9))+chunk(b'IEND',b''))


def make_image():
    c=Canvas()
    ink=(91,76,91); cream=(255,248,232); blush=(245,151,157)
    # Airy sparkles framing the large, centered cuddle.
    for x,y,r,col in [(92,115,4,(255,255,239)),(174,175,3,(255,255,243)),
        (520,112,4,(255,255,239)),(553,222,3,(255,255,243)),(82,285,3,(255,255,243)),
        (505,333,3,(255,255,239)),(126,413,2.5,(255,255,243)),(472,445,3,(255,255,239))]:
        c.star(x,y,r,col)
    # Soft rosy halo and a simple cushion ground the portrait.
    c.ellipse(324,329,238,221,(248,202,190))
    c.ellipse(322,545,244,53,(223,164,164))
    c.ellipse(322,532,220,43,(250,218,196))
    # Seal's plump body and little back flippers sit behind the face and fish.
    c.ellipse(302,447,128,121,(175,197,207),-.04)
    c.ellipse(301,473,78,78,(244,235,216),-.03)
    c.ellipse(218,476,47,25,(141,171,187),-.45)
    c.ellipse(378,480,46,24,(141,171,187),.42)
    # Round head, pale face, tiny ears/tufts for a baby-like silhouette.
    c.ellipse(302,300,171,153,(124,158,178))
    c.ellipse(302,294,160,146,(218,231,223))
    c.ellipse(190,211,34,29,(124,158,178),-.48)
    c.ellipse(190,211,23,19,(239,195,183),-.48)
    c.ellipse(414,211,34,29,(124,158,178),.48)
    c.ellipse(414,211,23,19,(239,195,183),.48)
    # Forehead shine and large, glossy eyes with clear highlights.
    c.ellipse(249,219,55,16,(244,249,235),-.35)
    c.ellipse(251,292,13,18,ink); c.ellipse(354,292,13,18,ink)
    c.circle(255,285,5,(255,255,250)); c.circle(358,285,5,(255,255,250))
    c.circle(244,298,2.5,(174,135,135)); c.circle(365,298,2.5,(174,135,135))
    c.ellipse(218,328,20,10,blush); c.ellipse(386,328,20,10,blush)
    # Soft muzzle, heart-like nose and little smile.
    c.ellipse(279,328,35,24,(245,239,223)); c.ellipse(327,328,35,24,(245,239,223))
    c.ellipse(296,323,9,7,(112,92,105)); c.ellipse(308,323,9,7,(112,92,105))
    c.polygon([(296,323),(308,323),(302,331)],(112,92,105))
    c.line(302,331,302,340,2.5,ink)
    c.line(302,339,291,345,2.4,ink); c.line(302,339,313,345,2.4,ink)
    # Whiskers, short and delicate so the face stays clean at thumbnail size.
    for side in (-1,1):
        c.line(267 if side<0 else 337,333,235 if side<0 else 369,326,1.8,(147,164,164))
        c.line(267 if side<0 else 337,341,232 if side<0 else 372,343,1.8,(147,164,164))
    # Plush fish: tail first, then a chubby aqua body with a warm belly patch.
    c.polygon([(439,431),(482,402),(478,448)],(240,154,126))
    c.polygon([(442,429),(470,413),(467,439)],(255,195,151))
    c.ellipse(411,435,65,48,(104,183,187),-.22)
    c.ellipse(407,438,52,35,(131,207,199),-.22)
    c.ellipse(394,451,27,20,(250,218,169),-.24)
    c.polygon([(405,403),(424,378),(436,416)],(240,154,126))
    c.polygon([(402,462),(425,480),(435,447)],(240,154,126))
    # Fish eye, smile, cheek and visible plush seam.
    c.circle(371,421,8,(255,251,232)); c.circle(373,421,4.2,ink); c.circle(374,419,1.5,(255,255,250))
    c.ellipse(361,444,8,5,(246,151,153))
    c.line(354,435,346,439,1.8,ink); c.line(346,439,354,443,1.8,ink)
    for j in range(5): c.line(402+j*8,411+j*3,399+j*8,416+j*3,1.6,(221,244,218))
    # Front flippers wrap around both sides of the plush, making the cuddle obvious.
    c.ellipse(247,418,75,25,(124,158,178),-.40)
    c.ellipse(247,414,57,15,(195,215,209),-.40)
    c.ellipse(371,468,70,23,(124,158,178),.47)
    c.ellipse(371,464,52,13,(195,215,209),.47)
    # Tiny paw dots where the seal holds its treasured fish.
    for x,y in [(287,426),(298,430),(309,430),(319,426)]: c.circle(x,y,3,(239,173,165))
    # A daisy clip adds a specific, memorable character detail.
    for dx,dy in [(0,-11),(10,-4),(6,7),(-6,7),(-10,-4)]: c.circle(390+dx,187+dy,6,(255,248,222))
    c.circle(390,187,5,(244,190,101))
    # Tiny floating hearts reinforce the affectionate story without clutter.
    c.circle(164,382,7,(244,151,157)); c.circle(176,382,7,(244,151,157))
    c.polygon([(157,385),(183,385),(170,400)],(244,151,157))
    c.circle(462,301,6,(244,151,157)); c.circle(472,301,6,(244,151,157))
    c.polygon([(456,304),(478,304),(467,316)],(244,151,157))
    return png(c.downsample())


def main():
    data=make_image()
    if len(data)>1024*1024: raise SystemExit('PNG exceeds 1 MiB')
    output_dir=os.environ.get('OUTPUT_DIR','/output')
    os.makedirs(output_dir,exist_ok=True)
    with open(os.path.join(output_dir,'entry.png'),'wb') as f: f.write(data)

if __name__=='__main__': main()
