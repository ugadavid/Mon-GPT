"""Couverture originale prolongeant le paysage Canvas historique, sans maquette."""
from pathlib import Path
from PIL import Image, ImageDraw


def create(destination):
    image=Image.new("RGB",(1200,675),"#F7F3EA")
    draw=ImageDraw.Draw(image)
    def hill(start,segments,color):
        points=[start]
        for a,b,end in segments:
            p=points[-1]
            for n in range(1,81):
                t=n/80;u=1-t
                points.append((u**3*p[0]+3*u*u*t*a[0]+3*u*t*t*b[0]+t**3*end[0],u**3*p[1]+3*u*u*t*a[1]+3*u*t*t*b[1]+t**3*end[1]))
        draw.polygon(points+[(1200,675),(0,675)],fill=color)
    # Les mêmes repères que le bandeau : soleil miel, collines sauge, livre, arbres.
    draw.ellipse((772,58,1000,286),fill="#E9C58E")
    draw.ellipse((40,294,460,408),fill="#EEE8DA")
    hill((0,411),[((180,300),(220,410),(420,300)),((620,185),(810,426),(1200,280))],"#E5E6CF")
    hill((0,511),[((180,430),(300,381),(450,411)),((740,465),(787,316),(1200,361))],"#CAD5B9")
    hill((0,562),[((260,440),(330,580),(555,508)),((835,421),(916,533),(1200,423))],"#94AF91")
    draw.ellipse((175,561,1009,757),fill="#819C7B")
    for x,y,s in [(188,435,1),(1036,440,1.3),(940,353,.65)]:
        draw.line((x,y,x,y-144*s),fill="#315E4F",width=max(2,round(6*s)))
        for side,dy in [(-1,-117),(1,-84),(-1,-47)]:
            left=x if side>0 else x-47*s
            draw.ellipse((left,y+dy*s,left+47*s,y+(dy+35)*s),fill="#315E4F" if side>0 else "#6F9275")
    # Livre ouvert : pages intactes, volume et filet chaud, sans texte à lire.
    draw.polygon([(374,449),(611,478),(847,449),(864,591),(611,635),(358,591)],fill="#637E66")
    draw.polygon([(365,430),(610,462),(855,430),(855,581),(610,623),(365,581)],fill="#CEBA9C")
    draw.polygon([(374,420),(593,448),(610,462),(628,448),(847,420),(847,568),(610,608),(374,568)],fill="#FFFCF7")
    draw.line((610,462,610,608),fill="#CEBA9C",width=4)
    for n in range(5):
        y=463+n*19
        draw.line((409,y,564,y+21),fill="#C8CCB9",width=3)
        draw.line((655,y+21,810,y),fill="#C8CCB9",width=3)
    draw.polygon([(624,450),(639,447),(639,548),(630,540),(623,551)],fill="#C87A50")
    for x,y in [(110,564),(1053,584),(244,612),(923,535)]:
        draw.line((x,y,x+5,y-25),fill="#315E4F",width=3)
        draw.ellipse((x-6,y-29,x+9,y-14),fill="#E9C58E")
    destination=Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    image.save(destination,quality=95,optimize=True)


if __name__=="__main__":
    create(Path(__file__).resolve().parents[1]/"mon_gpt/assets/covers/soleil.jpg")
