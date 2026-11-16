"""Trois rendus, un seul widget et le contrat d'interactions de CatalogList.

Le mode Liste délègue intégralement au composant validé. Le mode Détaillée
change seulement dessin et géométrie ; Mosaïque délègue à son renderer.
Aucun accès au catalogue ou aux URL.
"""
from collections import OrderedDict
import tkinter as tk
from tkinter.font import Font
from PIL import ImageTk
from .atelier import CatalogList, rounded, shorten
from .identity import DEFAULTS
from .identity_ui import contained_picture
from .theme import COLORS as C
from .mosaic import MosaicRenderer


class ResultsView(MosaicRenderer,CatalogList):
    def __init__(self,parent,library,icons,view="list",mosaic_size="normal"):
        self.view,self.library,self.icons=view,library,icons
        self.mosaic_size=mosaic_size
        self.covers=OrderedDict()
        super().__init__(parent)
        self.detail_title_font=Font(self,font=("Segoe UI",11,"bold"))
        self.bind("<Left>",lambda e:self.mosaic_navigate(-1,0) if self.view=="mosaic" else self.focus_action(False))
        self.bind("<Right>",lambda e:self.mosaic_navigate(1,0) if self.view=="mosaic" else self.focus_action(True))
        self.bind("<Configure>",self.mosaic_resize,add="+")
        self.bind("<FocusOut>",lambda e:self.hide_tip() if self.view=="mosaic" else None,add="+")
        for key,dx,dy in (("Left",-1,0),("Right",1,0),("Up",0,-1),("Down",0,1)):
            self.bind(f"<Shift-{key}>",lambda e,x=dx,y=dy:self.mosaic_navigate(x,y,extend=True) if self.view=="mosaic" else self.navigate(y or x,extend=True))

    def set_view(self,view):
        if view not in ("list","detail","mosaic"): raise ValueError("Vue inconnue")
        if self.view==view: return
        self.hide_tip()
        self.view=view
        self.resize_column=None
        self.hovered=None
        self.top=0
        self.configure(cursor="")
        self.draw()
        if self.selected in self.rows: self.see(self.selected)

    def layout(self):
        if self.view=="mosaic":
            self.row_height,self.header_height=self.grid_layout().stride,0
            self.secondary_order=[]
            return {}
        if self.view=="list":
            self.row_height,self.header_height=42,34
            return super().layout()
        self.row_height,self.header_height=126,0
        self.secondary_order=[]
        width=self.winfo_width()
        image_width=112 if width>=470 else 80
        self.text_x=22+image_width+14
        return {"#0":(10,image_width),"title":(self.text_x,max(30,width-self.text_x-42)),"open":(width-36,36)}

    def bbox(self,identity,column=None):
        if self.view=="mosaic": return self.mosaic_bbox(identity,column)
        result=super().bbox(identity,column)
        if self.view=="detail" and result and column=="title":
            x,y,w,_=result
            return x+27,y+10,max(20,w-29),26
        return result

    def open_hit(self,identity,x,y):
        if self.view=="mosaic": return self.mosaic_open_hit(identity,x,y)
        if self.view=="list": return super().open_hit(identity,x,y)
        if identity not in self.rows or "project" in self.rows[identity].get("tags",()): return False
        if self.identify_row(y)!=identity: return False
        bx,by,bw,_=self.bbox(identity,"title")
        title=shorten(self.detail_title_font,self.rows[identity]["values"][0],bw-4)
        return (bx<=x<=bx+self.detail_title_font.measure(title) and by<=y<by+26) or (self.winfo_width()-36<=x<self.winfo_width() and by<=y<by+28)

    def select_click(self,event):
        if self.view=="mosaic":
            self.hide_tip();self.focus_set()
            identity=self.identify_at(event.x,event.y)
            if identity:
                self.gesture_select(identity,event)
            return
        if self.view=="list": return super().select_click(event)
        self.hide_tip();self.focus_set()
        identity=self.identify_row(event.y)
        if identity:
            self.gesture_select(identity,event)

    def resize_motion(self,event):
        if self.view=="list": return super().resize_motion(event)

    def xview(self,*args):
        if self.view=="list": return super().xview(*args)
        return (0,1)

    def yview(self,*args):
        if self.view=="mosaic": return self.mosaic_yview(*args)
        result=super().yview(*args)
        if args and self.view=="detail":
            x,y=self.winfo_pointerx()-self.winfo_rootx(),self.winfo_pointery()-self.winfo_rooty()
            identity=self.identify_row(y) if 0<=x<self.winfo_width() and 0<=y<self.winfo_height() else None
            self.hover(identity)
            self.configure(cursor="hand2" if identity and self.open_hit(identity,x,y) else "")
        return result

    def cover(self,reference,width):
        key=(reference,width)
        if key not in self.covers:
            self.covers[key]=ImageTk.PhotoImage(contained_picture(self.library,reference,width,width*9//16),master=self)
            if len(self.covers)>192: self.covers.popitem(last=False)
        self.covers.move_to_end(key)
        return self.covers[key]

    def show_tip(self,identity,y):
        if self.view=="mosaic": return self.mosaic_tip(identity,y)
        if self.view=="list": return super().show_tip(identity,y)
        self.tip_timer=None
        if identity not in self.rows: return
        data=self.rows[identity]
        text=data["values"][0]
        if data.get("summary"): text+="\n"+data["summary"]
        text+="\nEmplacements : "+data["values"][1]
        for label,key in (("Catégories","categories"),("Tags","labels")):
            if data.get(key): text+="\n"+label+" : "+" · ".join(data[key])
        self.tip=tk.Label(self,text=text,font=("Segoe UI",9),background=C["ivory"],foreground=C["ink"],justify="left",anchor="w",padx=10,pady=8,wraplength=max(100,self.winfo_width()-48),highlightthickness=1,highlightbackground=C["line"])
        self.tip.update_idletasks()
        self.tip.place(x=12,y=max(self.header_height,min(y+20,self.winfo_height()-self.tip.winfo_reqheight()-8)),width=max(1,self.winfo_width()-24))
        self.tip.lift()

    def summary_lines(self,text,width):
        words=text.split();lines=[];line=""
        for index,word in enumerate(words):
            candidate=(line+" "+word).strip()
            if self.small_font.measure(candidate)>width:
                if line: lines.append(line)
                else: lines.append(shorten(self.small_font,word,width))
                line=word if line else ""
                if len(lines)==1:
                    rest=" ".join(([line] if line else [])+words[index+1:])
                    lines.append(shorten(self.small_font,rest,width));return lines
            else: line=candidate
        if line: lines.append(line)
        return lines[:2]

    def draw(self):
        if self.view=="mosaic": return self.draw_mosaic()
        if self.view=="list": return super().draw()
        self.delete_canvas();layout=self.layout()
        width,height=self.winfo_width(),self.winfo_height()
        if width<30 or height<30: return
        rounded(self,1,1,width-1,height-1,12,fill=C["ivory"],outline="")
        self.top=max(0,min(self.top,max(0,len(self.rows)*self.row_height-(height-self.header_height))))
        iw=layout["#0"][1];tx=self.text_x;tw=max(30,width-tx-42)
        for index,(identity,data) in enumerate(self.rows.items()):
            y=self.header_height+index*self.row_height-self.top
            if y+self.row_height<=self.header_height or y>=height: continue
            selected=identity in self.pick.ids
            fill=C["selection"] if selected else C["hover"] if identity==self.hovered else C["paper"]
            rounded(self,5,y+3,width-5,y+self.row_height-3,9,fill=fill,outline=C["pine"] if selected and identity==self.focused and self.focus_get()==self else C["line"])
            visual=data.get("visual")
            reference=visual.image if visual and visual.image else DEFAULTS["image"]
            picture=self.cover(reference,iw)
            iy=y+25
            rounded(self,15,iy-2,19+iw,iy+iw*9//16+2,5,fill=C["ivory"],outline=C["line"])
            self.create_image(17,iy,image=picture,anchor="nw",tags=("cover",identity))
            icon=self.icons.get(visual.icon if visual else None,visual.color if visual else None,20)
            self.create_image(tx+9,y+23,image=icon,tags=("identity",identity))
            self.create_text(tx+27,y+23,text=shorten(self.detail_title_font,data["values"][0],tw-31),anchor="w",font=self.detail_title_font,fill=C["ink"],tags=("title",identity))
            for n,line in enumerate(self.summary_lines(data.get("summary",""),tw)):
                self.create_text(tx,y+45+n*16,text=line,anchor="w",font=self.small_font,fill=C["muted"])
            self.create_text(tx,y+80,text=shorten(self.small_font,"↳ "+data["values"][1],tw),anchor="w",font=self.small_font,fill=C["pine"],tags=("context",identity))
            cats=data.get("categories",[]);tags=data.get("labels",[])
            badge_x,badge_width=(17,width-34) if width<470 else (tx,tw)
            cat_width=min(badge_width*.54,sum(self.small_font.measure(t)+21 for t in cats)+6) if cats else 0
            self.draw_badges(cats,badge_x,y+106,cat_width,True)
            self.draw_badges(tags,badge_x+cat_width,y+106,badge_width-cat_width,False)
            if "project" not in data.get("tags",()):
                ax=width-22
                if selected and self.action_focus and self.focus_get()==self:
                    rounded(self,ax-13,y+11,ax+13,y+37,4,fill="",outline=C["pine"])
                self.create_text(ax,y+24,text="↗",font=("Segoe UI",15),fill=C["pine"],tags=("open",identity))
        if not self.rows and height>160:
            self.create_text(width/2,min(height/2,160),text="Aucun résultat",font=("Segoe UI",12,"bold"),fill=C["pine"])
            self.create_text(width/2,min(height/2,160)+30,text="Changez de recherche, ou ajoutez un fil.",width=max(100,width-40),font=self.body_font,fill=C["muted"])
        if self.ycommand: self.ycommand(*self.yview())
        if self.xcommand: self.xcommand(0,1)

    def identify_at(self,x,y):
        return self.mosaic_identify(x,y) if self.view=="mosaic" else self.identify_row(y)

    def identify_row(self,y):
        if self.view=="mosaic": return self.mosaic_identify(self.winfo_pointerx()-self.winfo_rootx(),y)
        return super().identify_row(y)

    def motion(self,event):
        if self.view!="mosaic": return super().motion(event)
        self.hover(self.identify_at(event.x,event.y));self.hide_tip()
        identity=self.identify_at(event.x,event.y)
        if identity: self.tip_timer=self.after(600,lambda:self.show_tip(identity,event.y))

    def navigate(self,step,extend=False):
        if self.view=="mosaic": return self.mosaic_navigate(0,step,extend=extend)
        return super().navigate(step,extend=extend)

    def see(self,identity):
        if self.view=="mosaic": return self.mosaic_see(identity)
        return super().see(identity)

    def set_mosaic_size(self,size):
        if size not in ("normal","large"): raise ValueError("Taille de cartes inconnue")
        self.mosaic_size=size
        if self.view=="mosaic":
            self.hide_tip();self.top=0;self.draw()
            if self.selected in self.rows: self.see(self.selected)
            self.event_generate("<<MosaicLayout>>",when="tail")

    def mosaic_resize(self,event):
        if self.view=="mosaic":
            if self.selected in self.rows: self.see(self.selected)
            self.event_generate("<<MosaicLayout>>",when="tail")
