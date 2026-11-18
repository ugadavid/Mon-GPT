"""Géométrie et rendu de grille ; aucune recherche, URL ou mutation métier."""
from dataclasses import dataclass
import math
import tkinter as tk
from .atelier import rounded, shorten
from .list_columns import display_date
from .identity import DEFAULTS
from .theme import COLORS as C


@dataclass(frozen=True)
class GridLayout:
    width: int
    size: str = "normal"
    extra: int = 0
    image_limit: int | None = None

    @property
    def gap(self): return 22 if self.size=="large" else 16

    @property
    def columns(self):
        minimum=320 if self.size=="large" else 220
        return max(1,(max(64,self.width)-16+self.gap)//(minimum+self.gap))

    @property
    def card_width(self):
        maximum=384 if self.size=="large" else 280
        return min(maximum,(max(64,self.width)-16-self.gap*(self.columns-1))//self.columns)

    @property
    def image_width(self):
        width=min(128 if self.size=="large" else 96,max(16,((self.card_width-20)//16)*16))
        return min(width,max(16,(self.image_limit//9)*16)) if self.image_limit is not None else width

    @property
    def image_height(self): return self.image_width*9//16

    @property
    def card_height(self): return self.image_height+76+self.extra

    @property
    def stride(self): return self.card_height+self.gap

    @property
    def left(self): return (self.width-self.columns*self.card_width-(self.columns-1)*self.gap)//2

    def box(self,index,top=0):
        return (self.left+(index%self.columns)*(self.card_width+self.gap),8+(index//self.columns)*self.stride-top,self.card_width,self.card_height)

    def total(self,count): return max(1,16+math.ceil(count/self.columns)*self.stride-self.gap) if count else 1

    def hit(self,x,y,top,count):
        x-=self.left;y+=top-8
        if x<0 or y<0: return None
        col=int(x//(self.card_width+self.gap));row=int(y//self.stride)
        if col>=self.columns or x%(self.card_width+self.gap)>=self.card_width or y%self.stride>=self.card_height: return None
        index=row*self.columns+col
        return index if index<count else None

    def visible(self,top,height,count):
        first=max(0,int((top-8)//self.stride))*self.columns
        end=min(count,(max(0,int((top+height-8)//self.stride))+1)*self.columns)
        return range(first,end)


class MosaicRenderer:
    """Mélange de rendu utilisant l’API commune du widget ResultsView."""
    def grid_layout(self):
        # En compact, conserver le titre et les repères entiers avant l'image.
        limit=max(9,self.winfo_height()-16-76-self.max_card_extra)
        return GridLayout(self.winfo_width(),self.mosaic_size,self.max_card_extra,limit)

    def mosaic_bbox(self,identity,column=None):
        if identity not in self.rows: return ""
        grid=self.grid_layout();x,y,w,h=grid.box(list(self.rows).index(identity),self.top)
        h=grid.image_height+76+self.card_extras.get(identity,0)
        if y+h<=0 or y>=self.winfo_height(): return ""
        if column=="title":
            project="project" in self.rows[identity].get("tags",())
            return x+38,y+grid.image_height+22,max(20,w-(54 if project else 76)),42
        return x,y,w,h

    def mosaic_identify(self,x,y):
        index=self.grid_layout().hit(x,y,self.top,len(self.rows))
        if index is None or not 0<=y<self.winfo_height():return ""
        identity=list(self.rows)[index];box=self.mosaic_bbox(identity)
        return identity if box and box[1]<=y<box[1]+box[3] else ""

    def mosaic_lines(self,identity,width):
        # Même découpage pour le dessin, le hit-test et l’accès au titre entier.
        font=self.detail_title_font;words=self.rows[identity]["values"][0].split()
        lines=[];line=""
        for i,word in enumerate(words):
            candidate=(line+" "+word).strip()
            if font.measure(candidate)>width:
                lines.append(line or shorten(font,word,width))
                remainder=" ".join(([word] if line else [])+words[i+1:])
                lines.append(shorten(font,remainder,width))
                return lines
            line=candidate
        return [line] if line else []

    def mosaic_open_hit(self,identity,x,y):
        if self.mosaic_identify(x,y)!=identity or "project" in self.rows.get(identity,{}).get("tags",()): return False
        box=self.mosaic_bbox(identity,"title")
        if not box: return False
        tx,ty,tw,_=box
        bx,by,bw,_=self.mosaic_bbox(identity)
        return bx+bw-35<=x<bx+bw-8 and ty<=y<ty+28

    def mosaic_see(self,identity):
        if identity not in self.rows: return
        grid=self.grid_layout();_,y,_,h=grid.box(list(self.rows).index(identity))
        h=grid.image_height+76+self.card_extras.get(identity,0)
        if y<self.top: self.top=max(0,y-8)
        elif y+h>self.top+self.winfo_height(): self.top=max(0,y+h-self.winfo_height()+8)
        self.draw()

    def mosaic_yview(self,*args):
        grid=self.grid_layout();total=grid.total(len(self.rows));visible=max(1,self.winfo_height())
        if args:
            self.hide_tip()
            self.top=float(args[1])*total if args[0]=="moveto" else self.top+int(args[1])*(grid.stride if args[2]=="units" else visible)
            self.top=max(0,min(self.top,max(0,total-visible)))
            self.draw()
            x,y=self.winfo_pointerx()-self.winfo_rootx(),self.winfo_pointery()-self.winfo_rooty()
            identity=self.mosaic_identify(x,y)
            self.hover(identity)
            self.configure(cursor="hand2" if identity and self.mosaic_open_hit(identity,x,y) else "")
            self.event_generate("<<MosaicLayout>>",when="tail")
        return self.top/total,min(1,(self.top+visible)/total)

    def mosaic_navigate(self,dx=0,dy=0,extend=False):
        identities=list(self.rows)
        if not identities: return "break"
        self.hide_tip();grid=self.grid_layout()
        index=max(0,min(len(identities)-1,identities.index(self.focused)+dx+dy*grid.columns)) if self.focused in identities else 0
        self.gesture_select(identities[index],extend=extend);self.see(self.focused)
        box=self.mosaic_bbox(self.focused,"title")
        if box and " ".join(self.mosaic_lines(self.focused,box[2]))!=self.rows[self.focused]["values"][0]:
            self.tip_timer=self.after(650,lambda:self.show_tip(self.focused,box[1]))
        return "break"

    def mosaic_tip(self,identity,y):
        self.tip_timer=None
        box=self.mosaic_bbox(identity)
        if not box: return
        x,cy,w,h=box
        data=self.rows[identity]
        text=data["values"][0]+"\n"+data["values"][1]
        for key,label in (("summary","Résumé"),("notes","Note")):
            if data.get(key):text+="\n"+label+" : "+data[key]
        for key,label in (("categories","Catégories"),("labels","Tags")):
            if data.get(key):text+="\n"+label+" : "+" · ".join(data[key])
        width=min(360,max(100,self.winfo_width()-24))
        self.tip=tk.Label(self,text=text,font=("Segoe UI",9),background=C["ivory"],foreground=C["ink"],justify="left",padx=10,pady=8,wraplength=width-22,highlightthickness=1,highlightbackground=C["line"])
        self.tip.update_idletasks()
        self.tip.place(x=max(4,min(x,self.winfo_width()-width-4)),y=max(4,min(cy+h,self.winfo_height()-self.tip.winfo_reqheight()-4)),width=width)
        self.tip.lift()

    def draw_mosaic(self):
        self.delete_canvas();width,height=self.winfo_width(),self.winfo_height()
        if width<64 or height<30: return
        grid=self.grid_layout();self.top=max(0,min(self.top,max(0,grid.total(len(self.rows))-height)))
        identities=list(self.rows)
        for index in grid.visible(self.top,height,len(identities)):
            identity=identities[index];data=self.rows[identity];x,y,w,h=grid.box(index,self.top)
            h=grid.image_height+76+self.card_extras.get(identity,0)
            if y+h<=0 or y>=height: continue
            selected=identity in self.pick.ids;hovered=identity==self.hovered
            fill=C["selection"] if selected else C["paper"]
            rounded(self,x+1,y+1,x+w-1,y+h-1,9,fill=fill,outline=C["pine"] if selected else C["muted"] if hovered else C["line"],width=2 if selected and identity==self.focused and self.focus_get()==self else 1)
            visual=data.get("visual");reference=visual.image if visual and visual.image else DEFAULTS["image"]
            picture=self.cover(reference,grid.image_width)
            ix=x+(w-grid.image_width)//2;iy=y+10
            self.create_image(ix,iy,image=picture,anchor="nw",tags=("cover",identity))
            tx,ty,tw,_=self.mosaic_bbox(identity,"title")
            icon=self.icons.get(visual.icon if visual else None,visual.color if visual else None,20)
            self.create_image(x+22,ty+10,image=icon,tags=("identity",identity))
            title_lines=self.mosaic_lines(identity,tw)
            for line_number,line in enumerate(title_lines):
                self.create_text(tx,ty+line_number*20,text=line,anchor="nw",font=self.detail_title_font,fill=C["ink"],tags=("title",identity))
            cy=ty+max(1,len(title_lines))*20+5
            excerpts=self.excerpts(data)
            for key,label,text in excerpts:
                caption=f"{label} : {text}"
                lines=self.summary_lines(caption,w-24) if grid.size=="large" or len(excerpts)==1 else [shorten(self.small_font,caption,w-24)]
                for line in lines:
                    self.create_text(x+12,cy,text=line,anchor="nw",font=self.small_font,fill=C["ink"] if key=="summary" else C["muted"],tags=(key,identity))
                    cy+=17
            self.create_text(x+12,cy+2,text=shorten(self.small_font,"↳ "+data["values"][1],w-24),anchor="nw",font=self.small_font,fill=C["pine"],tags=("context",identity))
            cy+=23
            cats,tags=data.get('categories',[]),data.get('labels',[])
            if cats or tags:
                badge_width=w-24
                tag_space=min(badge_width*.45,sum(self.small_font.measure(t)+21 for t in tags)+6) if tags else 0
                cat_width=min(badge_width-tag_space,sum(self.small_font.measure(t)+21 for t in cats)+6) if cats else 0
                self.draw_badges(cats,x+12,cy+11,cat_width,True)
                self.draw_badges(tags,x+12+cat_width,cy+11,badge_width-cat_width,False)
            if grid.size=="large":
                dates=[f"{label} · {display_date(data['cells'][key]).split()[0]}" for key,label in (("created","Créé"),("modified","Modifié")) if data.get("cells",{}).get(key)]
                if dates:
                    joined="     ".join(dates)
                    lines=[joined] if self.detail_date_font.measure(joined)<=w-24 else dates
                    footer=y+h-9-16*len(lines)
                    self.create_line(x+12,footer-4,x+w-12,footer-4,fill=C["line"])
                    for n,line in enumerate(lines):
                        self.create_text(x+12,footer+16*n,text=line,anchor="nw",font=self.detail_date_font,fill=C["muted"],tags=("dates",identity))
            if "project" not in data.get("tags",()):
                self.create_text(x+w-22,ty+10,text="↗",font=("Segoe UI",14),fill=C["pine"],tags=("open",identity))
        if not self.rows and height>100:
            self.create_text(width/2,min(height/2,150),text="Aucun résultat",font=("Segoe UI",12,"bold"),fill=C["pine"])
            self.create_text(width/2,min(height/2,150)+30,text="Changez de recherche, ou ajoutez un fil.",font=self.body_font,fill=C["muted"],width=max(100,width-40))
        if self.ycommand: self.ycommand(*self.mosaic_yview())
        if self.xcommand: self.xcommand(0,1)
