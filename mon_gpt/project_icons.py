"""Pictogrammes au trait partagés par arbre, fiche et galeries."""
import math
from PIL import Image, ImageDraw, ImageTk
from .identity import DEFAULTS, PALETTE


def icon_picture(key,color,size=28):
    scale=4
    image=Image.new("RGBA",(24*scale,24*scale))
    draw=ImageDraw.Draw(image)
    def line(points): draw.line([(round(x*scale),round(y*scale)) for x,y in points],fill=color,width=scale,joint="curve")
    def oval(box): draw.ellipse(tuple(round(v*scale) for v in box),outline=color,width=scale)
    def arc(box,start,end): draw.arc(tuple(round(v*scale) for v in box),start,end,fill=color,width=scale)
    def box(bounds):
        x,y,r,b=bounds;line([(x,y),(r,y),(r,b),(x,b),(x,y)])
    if key=="folder": line([(3,19),(3,6),(9,6),(12,9),(21,9),(21,19),(3,19)])
    elif key=="book": line([(12,6),(7,4),(3,5),(3,19),(7,18),(12,20),(17,18),(21,19),(21,5),(17,4),(12,6),(12,20)])
    elif key=="leaf":
        line([(5,20),(12,12),(20,4)]);arc((4,4,21,21),0,180);arc((4,3,21,20),180,360)
    elif key=="compass":
        oval((3,3,21,21));line([(16,7),(14,14),(7,17),(10,10),(16,7)]);line([(10,10),(14,14)])
    elif key=="mountain":
        line([(2,20),(10,5),(15,13),(18,9),(23,20),(2,20)]);line([(7,10),(10,12),(12,9)])
    elif key=="flask":
        line([(8,3),(16,3),(14,3),(14,10),(21,20),(3,20),(10,10),(10,3)]);line([(7,15),(17,15)])
    elif key=="palette":
        oval((3,3,21,21));oval((7,7,9,9));oval((13,6,15,8));oval((16,11,18,13));oval((7,13,9,15));line([(14,20),(12,17),(15,15),(18,17)])
    elif key=="circuit":
        box((7,7,17,17))
        for n in (9,12,15):
            line([(n,3),(n,7)]);line([(n,17),(n,21)]);line([(3,n),(7,n)]);line([(17,n),(21,n)])
    elif key=="pen":
        line([(4,20),(5,15),(17,3),(21,7),(9,19),(4,20)]);line([(14,6),(18,10)]);line([(5,15),(9,19)])
    elif key=="feather":
        line([(4,21),(17,6)]);line([(7,17),(7,10),(12,4),(21,3),(19,12),(13,17),(7,17)]);line([(12,9),(12,12),(17,12)])
    elif key in ("chat","conversation"):
        if key=="conversation": line([(8,5),(21,5),(21,15),(18,15),(18,19),(14,15)]);line([(3,9),(3,3),(16,3)])
        line([(3,7),(16,7),(16,16),(9,16),(5,20),(5,16),(3,16),(3,7)])
    elif key=="lamp":
        line([(4,21),(16,21),(13,18),(9,13),(14,7)]);line([(11,5),(15,3),(21,9),(17,12),(11,5)]);line([(17,12),(20,15)])
    elif key=="bulb":
        arc((6,3,18,15),155,385);line([(7,12),(9,16),(9,18),(15,18),(15,16),(17,12)]);line([(10,21),(14,21)])
    elif key=="planet":
        oval((5,5,19,19));arc((1,8,23,16),-25,155);arc((1,8,23,16),155,335)
    elif key=="star":
        points=[(12+10*math.sin(n*math.pi/5)*(1 if n%2==0 else .43),12-10*math.cos(n*math.pi/5)*(1 if n%2==0 else .43)) for n in range(10)]
        line(points+[points[0]])
    elif key=="map":
        line([(3,6),(9,3),(15,6),(21,3),(21,18),(15,21),(9,18),(3,21),(3,6)]);line([(9,3),(9,18)]);line([(15,6),(15,21)])
    elif key=="globe":
        oval((3,3,21,21));oval((8,3,16,21));line([(3,12),(21,12)]);arc((4,4,20,16),0,180)
    elif key=="tree":
        line([(12,2),(5,10),(8,10),(3,17),(10,17),(10,21),(14,21),(14,17),(21,17),(16,10),(19,10),(12,2)])
    elif key=="flower":
        for dx,dy in [(0,-5),(5,0),(0,5),(-5,0)]: oval((9+dx,7+dy,15+dx,13+dy))
        oval((10,8,14,12));line([(12,15),(12,22)]);line([(12,20),(7,17)])
    elif key=="sun":
        oval((7,7,17,17))
        for n in range(8):
            t=n*math.pi/4;line([(12+8*math.cos(t),12+8*math.sin(t)),(12+11*math.cos(t),12+11*math.sin(t))])
    elif key=="moon":
        arc((3,3,21,21),55,305);arc((10,0,25,19),75,250);line([(18,3),(20,6),(22,3)])
    elif key=="search": oval((3,3,16,16));line([(15,15),(22,22)])
    elif key=="code":
        line([(8,6),(2,12),(8,18)]);line([(16,6),(22,12),(16,18)]);line([(14,3),(10,21)])
    elif key=="terminal":
        box((3,4,21,20));line([(6,8),(10,12),(6,16)]);line([(13,16),(18,16)])
    elif key=="database":
        oval((4,3,20,9));line([(4,6),(4,18)]);line([(20,6),(20,18)]);arc((4,14,20,21),0,180);arc((4,8,20,15),0,180)
    elif key=="tools":
        line([(3,3),(7,7),(5,9),(2,5),(3,11),(7,12),(17,22),(21,18),(11,8),(10,4),(6,2)]);line([(15,10),(20,4),(22,6),(18,12)]);line([(9,16),(4,21),(2,19),(7,14)])
    elif key=="gear":
        points=[]
        for n in range(32):
            r=10 if n%4 in (0,1) else 8;t=n*math.pi/16
            points.append((12+r*math.cos(t),12+r*math.sin(t)))
        line(points+[points[0]]);oval((8,8,16,16))
    elif key=="microscope":
        line([(4,21),(21,21)]);line([(6,17),(17,17)]);line([(14,3),(18,5),(13,14),(9,12),(14,3)]);line([(11,3),(15,5)]);arc((6,6,22,21),-70,90);line([(15,17),(13,21)])
    elif key=="music":
        line([(9,18),(9,5),(21,2),(21,16)]);line([(9,8),(21,5)]);oval((3,16,9,21));oval((15,14,21,19))
    elif key=="camera":
        line([(3,7),(7,7),(9,4),(15,4),(17,7),(21,7),(21,20),(3,20),(3,7)]);oval((8,9,16,17));line([(18,9),(19,9)])
    elif key=="brush":
        line([(10,15),(18,2),(22,5),(13,18),(10,15)]);line([(10,15),(6,15),(3,20),(2,22),(8,21),(13,18)])
    elif key=="calendar":
        box((3,5,21,21));line([(3,10),(21,10)]);line([(7,2),(7,7)]);line([(17,2),(17,7)])
        for x in (7,12,17): line([(x,14),(x,15)]);line([(x,18),(x,19)])
    elif key=="clock": oval((3,3,21,21));line([(12,6),(12,12),(17,15)])
    elif key=="home":
        line([(2,11),(12,2),(22,11)]);line([(5,9),(5,21),(19,21),(19,9)]);line([(10,21),(10,14),(14,14),(14,21)])
    elif key=="heart":
        points=[(12+9*math.sin(t)**3,11-(7*math.cos(t)-3*math.cos(2*t)-1.5*math.cos(3*t)-.5*math.cos(4*t))) for t in [n*math.pi/40 for n in range(81)]]
        line(points)
    else: raise ValueError("Icône inconnue.")
    return image.resize((size,size),Image.Resampling.LANCZOS)


class ProjectIconCache:
    def __init__(self,master):
        self.master,self.photos=master,{}

    def get(self,icon=None,color=None,size=20):
        key=(icon or DEFAULTS["icon"],color or DEFAULTS["color"],size)
        if key not in self.photos:
            self.photos[key]=ImageTk.PhotoImage(icon_picture(key[0],PALETTE[key[1]][1],size),master=self.master)
        return self.photos[key]

    def for_project(self,record,size=20):
        return self.get(record.visual.get("icon"),record.visual.get("color"),size)
