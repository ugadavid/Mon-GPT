"""Composants visuels Canvas de l'Atelier ; aucune règle métier."""
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from .theme import COLORS as C


def rounded(canvas, x1, y1, x2, y2, radius=14, **kwargs):
    r = max(0, min(radius, (x2-x1)/2, (y2-y1)/2))
    points = [x1+r,y1,x2-r,y1,x2,y1,x2,y1+r,x2,y2-r,x2,y2,x2-r,y2,x1+r,y2,x1,y2,x1,y2-r,x1,y1+r,x1,y1]
    return canvas.create_polygon(points, smooth=True, splinesteps=24, **kwargs)


def shorten(font, text, width):
    if font.measure(text) <= width:
        return text
    while text and font.measure(text+"…") > width:
        text = text[:-1]
    return text+"…" if text else ""


class PillButton(tk.Canvas):
    def __init__(self, parent, text, command, tone="quiet", width=None, height=34):
        self.text, self.command, self.tone = text, command, tone
        self.font = Font(parent, font=("Segoe UI", 10, "bold" if tone == "primary" else "normal"))
        bg = parent.cget("background") if isinstance(parent, tk.Canvas) else (C["paper"] if "Paper" in str(parent.cget("style")) else C["ivory"])
        super().__init__(parent, width=width or self.font.measure(text)+28, height=height, background=bg, highlightthickness=0, takefocus=1, cursor="hand2")
        self.hovered = False
        self.bind("<Configure>", self.draw)
        self.bind("<Enter>", lambda e: self.hover(True))
        self.bind("<Leave>", lambda e: self.hover(False))
        self.bind("<FocusIn>", self.draw)
        self.bind("<FocusOut>", self.draw)
        self.bind("<Button-1>", lambda e: self.activate())
        self.bind("<Return>", lambda e: self.activate())
        self.bind("<space>", lambda e: self.activate())

    def hover(self, value):
        self.hovered = value
        self.draw()

    def configure(self, cnf=None, **kwargs):
        if "command" in kwargs: self.command=kwargs.pop("command")
        if "text" in kwargs: self.text=kwargs.pop("text")
        result=super().configure(cnf,**kwargs)
        if hasattr(self,"hovered"): self.draw()
        return result

    def activate(self):
        self.focus_set()
        self.command()
        return "break"

    def draw(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        fills = {"primary": C["pine"], "warm": C["terracotta"], "chip": C["selection"], "quiet": C["paper"]}
        fill = fills[self.tone]
        if self.hovered:
            fill = "#254C3F" if self.tone == "primary" else C["hover"]
        focused = self.focus_get() == self
        rounded(self, 1, 1, w-1, h-1, h/2 if self.tone == "chip" else 10, fill=fill, outline=C["pine"] if focused else (C["line"] if self.tone == "quiet" else fill), width=2 if focused else 1)
        self.create_text(w/2, h/2, text=self.text, fill=C["paper"] if self.tone == "primary" else C["pine"] if self.tone == "chip" else C["ink"], font=self.font)


class Surface(tk.Canvas):
    def __init__(self, parent, padding=14, **kwargs):
        super().__init__(parent, background=C["ivory"], highlightthickness=0, **kwargs)
        self.padding = padding
        self.body = ttk.Frame(self, style="Paper.TFrame")
        self.window = self.create_window(padding, padding, window=self.body, anchor="nw")
        self.bind("<Configure>", self.draw)

    def draw(self, event=None):
        w, h = self.winfo_width(), self.winfo_height()
        self.delete("surface")
        rounded(self, 2, 4, w-1, h-1, 18, fill="#EAE2D5", outline="", tags="surface")
        rounded(self, 1, 1, w-3, h-4, 18, fill=C["paper"], outline=C["line"], tags="surface")
        self.tag_lower("surface")
        self.itemconfigure(self.window, width=max(1,w-2*self.padding), height=max(1,h-2*self.padding))


class Masthead(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, height=114, background=C["ivory"], highlightthickness=0)
        self.bind("<Configure>", self.draw)

    def draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        target_height=90 if w<1100 else 114
        if int(self.cget("height"))!=target_height:
            self.configure(height=target_height)
        # Le repère de marque : carnet et plume, dessinés, pas un actif binaire.
        rounded(self, 26, 26, 80, 80, 15, fill=C["pine"], outline="")
        self.create_line(44,64,63,39, fill=C["paper"], width=3, capstyle="round")
        self.create_polygon(50,54,48,42,64,35,63,47, fill="#E5C9A1", outline="")
        self.create_line(43,66,65,66, fill="#92AA8A", width=2, capstyle="round")
        self.create_text(96, 39, text="Mon GPT<3", anchor="w", font=("Segoe UI",27,"bold"), fill=C["pine"])
        self.create_text(98, 73, text="Votre organisation, en local.", anchor="w", font=("Segoe UI",11), fill=C["muted"])
        self.create_text(28, 104, text="UN PEU D'ORDRE.  BEAUCOUP D'IDÉES.", anchor="w", font=("Segoe UI",8,"bold"), fill=C["link"])
        # Paysage d'atelier : collines, soleil, pages et feuillage.
        start = max(465, w-500)
        self.create_oval(w-170,7,w-106,71, fill="#E9C58E", outline="")
        self.create_polygon(start,109,start+80,62,start+175,80,start+260,37,w,82,w,114, fill="#E5E6CF", smooth=True, outline="")
        self.create_polygon(start+40,114,start+160,73,start+260,104,w-75,64,w,88,w,114, fill="#CAD5B9", smooth=True, outline="")
        self.create_polygon(start+155,114,start+255,91,w-120,102,w-24,81,w,94,w,114, fill="#94AF91", smooth=True, outline="")
        bx, by = w-303, 74
        rounded(self, bx,by-24,bx+63,by+27,6, fill=C["paper"], outline="#CEBA9C")
        self.create_line(bx+30,by-20,bx+30,by+22, fill="#CEBA9C", width=1)
        for y in (by-8,by,by+8):
            self.create_line(bx+8,y,bx+23,y-2, fill="#B7B6A3", width=1)
            self.create_line(bx+37,y-2,bx+54,y, fill="#B7B6A3", width=1)
        for x, y, scale in [(w-76,84,1), (w-389,88,.7)]:
            self.create_line(x,110,x,y-30*scale,fill=C["pine"],width=2)
            for side,dy in [(-1,-23),(1,-13),(-1,-4)]:
                self.create_oval(x if side>0 else x-17*scale,y+dy,x+17*scale if side>0 else x,y+dy+13*scale, fill=C["pine"] if side>0 else "#6F9275", outline="")
        self.create_line(24,113,w-24,113,fill=C["line"])
        if w<1100:
            self.scale("all",0,0,1,.78)


class AutoScrollbar(ttk.Scrollbar):
    """Disparaît lorsque tout le contenu tient dans la zone visible."""
    def pack(self, **kwargs):
        self.pack_options = kwargs
        super().pack(**kwargs)

    def set(self, first, last):
        if float(first) <= 0 and float(last) >= 1:
            self.pack_forget()
        elif not self.winfo_manager():
            super().pack(**getattr(self, "pack_options", {}))
        super().set(first, last)


class MenuSkin:
    """Présentation Canvas d'un vrai Menu Tk : commandes et états restent natifs."""
    def __init__(self, menu):
        self.menu, self.window = menu, None

    def popup(self, x, y, entry=""):
        if self.window and self.window.winfo_exists():
            self.window.destroy()
        menu = self.menu
        indices = list(range((menu.index("end") or 0)+1))
        font = Font(menu, font=("Segoe UI",11))
        width = max([230]+[font.measure(menu.entrycget(i,"label"))+font.measure(menu.entrycget(i,"accelerator"))+76 for i in indices if menu.type(i) != "separator"])
        heights = [12 if menu.type(i)=="separator" else 38 for i in indices]
        height = sum(heights)+16
        owner=menu.master
        while not isinstance(owner,(tk.Tk,tk.Toplevel)):
            owner=owner.master
        # Le menu reste dans la fenêtre : focus stable et aucun popup OS gris.
        win = self.window = tk.Frame(owner,background=C["ivory"],borderwidth=0,highlightthickness=0)
        x=min(max(0,x-owner.winfo_rootx()),max(0,owner.winfo_width()-width-6))
        y=min(max(0,y-owner.winfo_rooty()),max(0,owner.winfo_height()-height-6))
        win.place(x=x,y=y,width=width,height=height)
        win.lift()
        canvas = tk.Canvas(win, width=width, height=height, background=C["ivory"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        self.active = next((i for i in indices if menu.type(i)!="separator" and menu.entrycget(i,"state")!="disabled"), None)
        self.bounds = []
        pos = 8
        for i, h in zip(indices, heights):
            self.bounds.append((i,pos,pos+h))
            pos += h
        def draw():
            canvas.delete("all")
            rounded(canvas,1,1,width-2,height-2,13,fill=C["paper"],outline=C["line"])
            for i, top, bottom in self.bounds:
                if menu.type(i)=="separator":
                    canvas.create_line(16,(top+bottom)/2,width-16,(top+bottom)/2,fill=C["line"])
                    continue
                disabled = menu.entrycget(i,"state")=="disabled"
                if i==self.active and not disabled:
                    rounded(canvas,7,top+1,width-7,bottom-1,8,fill=C["selection"],outline="")
                label = menu.entrycget(i,"label")
                color = C["muted"] if disabled else C["error"] if "Supprimer" in label else C["pine"] if i==self.active else C["ink"]
                symbol=next((symbol for word,symbol in [("Sauvegarder","▣"),("Restaurer","↶"),("Dossier","▱"),("Nouveau","+"),("Renommer","✎"),("Modifier","✎"),("Déplacer","↳"),("Ajouter","+"),("Retirer","−"),("Copier","⧉"),("Supprimer","×"),("Ouvrir","↗")] if word in label),"·")
                rounded(canvas,12,top+7,36,bottom-7,6,fill=C["hover"],outline="")
                canvas.create_text(24,(top+bottom)/2,text=symbol,font=("Segoe UI",12),fill=color)
                canvas.create_text(45,(top+bottom)/2,text=label.removeprefix("↗ "),anchor="w",font=font,fill=color)
                canvas.create_text(width-17,(top+bottom)/2,text=menu.entrycget(i,"accelerator"),anchor="e",font=("Segoe UI",9),fill=C["muted"])
        def motion(e):
            self.active = next((i for i,a,b in self.bounds if a<=e.y<b and menu.type(i)!="separator" and menu.entrycget(i,"state")!="disabled"),None)
            draw()
        def close(e=None):
            if win.winfo_exists():
                win.grab_release()
                win.destroy()
            return "break"
        def invoke(e=None):
            selected = self.active
            close()
            if selected is not None:
                menu.invoke(selected)
            return "break"
        def step(delta):
            valid=[i for i in indices if menu.type(i)!="separator" and menu.entrycget(i,"state")!="disabled"]
            if valid:
                self.active=valid[(valid.index(self.active)+delta)%len(valid)] if self.active in valid else valid[0]
                draw()
            return "break"
        canvas.bind("<Motion>",motion)
        canvas.bind("<ButtonRelease-1>",lambda e:(motion(e),invoke())[1])
        win.bind("<Escape>",close)
        win.bind("<Return>",invoke)
        win.bind("<Down>",lambda e:step(1))
        win.bind("<Up>",lambda e:step(-1))
        def focus_out(e):
            def check():
                if win.winfo_exists() and owner.focus_get() is None:
                    close()
            owner.after_idle(check)
        win.bind("<FocusOut>",focus_out)
        win.bind("<ButtonPress-1>",lambda e:close() if not (0<=e.x_root-win.winfo_rootx()<width and 0<=e.y_root-win.winfo_rooty()<height) else None)
        draw()
        win.grab_set()
        win.focus_force()


def skin_menu(menu):
    # Un Menu remplacé par un mock dans les tests conserve son contrat inchangé.
    if isinstance(menu, tk.Misc):
        menu._atelier_skin = MenuSkin(menu)
        menu.tk_popup = menu._atelier_skin.popup
    return menu


class CatalogList(tk.Canvas):
    """Liste à colonnes dessinées : API limitée aux interactions déjà utilisées."""
    row_height, header_height = 62, 42

    def __init__(self, parent):
        super().__init__(parent, background=C["ivory"], highlightthickness=0, takefocus=1, height=60)
        self.rows, self.columns, self.headings = {}, {}, {}
        self.selected, self.focused, self.hovered = None, None, None
        self.top, self.left = 0, 0
        self.ycommand, self.xcommand = None, None
        self.title_font = Font(self,font=("Segoe UI",12,"bold"))
        self.small_font = Font(self,font=("Segoe UI",9))
        self.body_font = Font(self,font=("Segoe UI",10))
        self.bind("<Configure>",lambda e:self.draw())
        self.bind("<Button-1>",self.select_click)
        self.bind("<Motion>",self.motion)
        self.bind("<Leave>",lambda e:self.hover(None))
        self.bind("<Up>",lambda e:self.navigate(-1))
        self.bind("<Down>",lambda e:self.navigate(1))
        self.bind("<MouseWheel>",lambda e:self.yview("scroll",-int(e.delta/120 or (1 if e.delta>0 else -1))*2,"units"))
        self.bind("<FocusIn>",lambda e:self.draw())
        self.bind("<FocusOut>",lambda e:self.draw())
        self.resize_column = None
        self.pending_draw = None
        self.bind("<B1-Motion>",self.resize_motion)
        self.bind("<ButtonRelease-1>",lambda e:setattr(self,"resize_column",None))

    def configure(self, cnf=None, **kwargs):
        if "yscrollcommand" in kwargs: self.ycommand=kwargs.pop("yscrollcommand")
        if "xscrollcommand" in kwargs: self.xcommand=kwargs.pop("xscrollcommand")
        return super().configure(cnf, **kwargs)

    config = configure

    def heading(self, column, **kwargs):
        self.headings.setdefault(column,{}).update(kwargs)

    def column(self, column, option=None, **kwargs):
        if kwargs: self.columns.setdefault(column,{}).update(kwargs)
        return self.columns.get(column,{}).get(option) if option else self.columns.get(column,{})

    def widths(self):
        keys=["#0","title","context","tags","modified"]
        sizes=[self.columns.get(k,{}).get("width",100) for k in keys]
        sizes[1]=max(sizes[1],self.winfo_width()-sum(sizes[:1]+sizes[2:])-8)
        return sizes

    def insert(self,parent,index,iid,**kwargs):
        self.rows[iid]=dict(kwargs)
        self.request_draw()
        return iid

    def delete(self,*identities):
        for identity in identities: self.rows.pop(identity,None)
        if self.selected not in self.rows: self.selected=None
        self.request_draw()

    def request_draw(self):
        if self.pending_draw is None:
            self.pending_draw=self.after_idle(self.flush_draw)

    def flush_draw(self):
        self.pending_draw=None
        self.draw()

    def destroy(self):
        if getattr(self,"pending_draw",None) is not None:
            self.after_cancel(self.pending_draw)
            self.pending_draw=None
        super().destroy()

    def get_children(self,parent=""):
        return tuple(self.rows)

    def exists(self,identity):
        return identity in self.rows

    def item(self,identity,option=None,**kwargs):
        self.rows[identity].update(kwargs)
        if kwargs: self.draw()
        return self.rows[identity].get(option) if option else self.rows[identity]

    def selection(self):
        return (self.selected,) if self.selected in self.rows else ()

    def selection_set(self,identity):
        if isinstance(identity,(tuple,list)): identity=identity[0] if identity else None
        if identity != self.selected:
            self.selected=identity
            self.event_generate("<<TreeviewSelect>>",when="tail")
        self.draw()

    def focus(self,identity=None):
        if identity is not None: self.focused=identity
        return self.focused or ""

    def bbox(self,identity,column=None):
        if identity not in self.rows: return ""
        keys=["#0","title","context","tags","modified"]
        index=keys.index(column) if column in keys else 0
        widths=self.widths()
        y=self.header_height+list(self.rows).index(identity)*self.row_height-self.top
        if y+self.row_height<=self.header_height or y>=self.winfo_height(): return ""
        return (sum(widths[:index])-self.left,y,widths[index] if column else sum(widths),self.row_height)

    def identify_row(self,y):
        if y<self.header_height: return ""
        index=int((y-self.header_height+self.top)//self.row_height)
        return list(self.rows)[index] if 0<=index<len(self.rows) else ""

    def identify_column(self,x):
        position=-self.left
        for i,width in enumerate(self.widths()):
            position+=width
            if x<position: return f"#{i}"
        return ""

    def select_click(self,event):
        self.focus_set()
        if event.y<self.header_height:
            x=-self.left
            keys=["#0","title","context","tags","modified"]
            for key,width in zip(keys,self.widths()):
                x+=width
                if abs(event.x-x)<7:
                    self.resize_column=(key,event.x,self.columns[key]["width"])
                    return
            col=self.identify_column(event.x)
            if col:
                fn=self.headings.get(keys[int(col[1:])],{}).get("command")
                if fn: fn()
            return
        identity=self.identify_row(event.y)
        if identity:
            self.focused=identity
            self.selection_set(identity)

    def resize_motion(self,event):
        if self.resize_column:
            key,start,width=self.resize_column
            self.columns[key]["width"]=max(self.columns[key].get("minwidth",44),width+event.x-start)
            self.draw()

    def navigate(self,step):
        identities=list(self.rows)
        if identities:
            index=identities.index(self.focused) if self.focused in identities else (-1 if step>0 else len(identities))
            self.focused=identities[max(0,min(len(identities)-1,index+step))]
            self.selection_set(self.focused)
            self.see(self.focused)
        return "break"

    def motion(self,event):
        self.hover(self.identify_row(event.y))

    def hover(self,identity):
        if identity!=self.hovered:
            self.hovered=identity
            self.draw()

    def see(self,identity):
        if identity in self.rows:
            y=list(self.rows).index(identity)*self.row_height
            height=max(1,self.winfo_height()-self.header_height)
            if y<self.top: self.top=y
            elif y+self.row_height>self.top+height: self.top=y+self.row_height-height
            self.draw()

    def yview(self,*args):
        total=max(1,len(self.rows)*self.row_height)
        visible=max(1,self.winfo_height()-self.header_height)
        if args:
            self.top=float(args[1])*total if args[0]=="moveto" else self.top+int(args[1])*(self.row_height if args[2]=="units" else visible)
            self.top=max(0,min(self.top,max(0,total-visible)))
            self.draw()
        return (self.top/total,min(1,(self.top+visible)/total))

    def xview(self,*args):
        total=max(1,sum(self.widths()))
        visible=max(1,self.winfo_width())
        if args:
            self.left=float(args[1])*total if args[0]=="moveto" else self.left+int(args[1])*40
            self.left=max(0,min(self.left,max(0,total-visible)))
            self.draw()
        return (self.left/total,min(1,(self.left+visible)/total))

    def draw(self):
        self.delete_canvas()
        width,height=self.winfo_width(),self.winfo_height()
        row_height=54 if width<800 else 62
        if row_height!=self.row_height:
            self.top=self.top/self.row_height*row_height
            self.row_height=row_height
        rounded(self,1,1,width-1,height-1,16,fill=C["paper"],outline=C["line"])
        sizes=self.widths()
        self.left=min(self.left,max(0,sum(sizes)-width))
        self.top=min(self.top,max(0,len(self.rows)*self.row_height-(height-self.header_height)))
        for index,(identity,data) in enumerate(self.rows.items()):
            y=self.header_height+index*self.row_height-self.top
            if y+self.row_height<=self.header_height or y>=height: continue
            selected=identity==self.selected
            fill=C["selection"] if selected else C["hover"] if identity==self.hovered else C["paper"]
            rounded(self,4,y+3,width-6,y+self.row_height-3,11,fill=fill,outline=C["pine"] if selected and self.focus_get()==self else "")
            if selected: rounded(self,5,y+15,9,y+self.row_height-15,2,fill=C["pine"],outline="")
            vals=data.get("values",("",)*4)
            is_project="project" in data.get("tags",())
            x=-self.left
            self.create_image(x+25,y+self.row_height/2,image=data.get("image"))
            x+=sizes[0]
            self.create_text(x+10,y+24,text=shorten(self.title_font,vals[0],sizes[1]-24),font=self.title_font,fill=C["pine"] if selected else C["ink"],anchor="w")
            self.create_text(x+10,y+45,text="PROJET" if is_project else "↗  Ouvrir la discussion",font=("Segoe UI",8),fill=C["muted"] if is_project else C["link"],anchor="w")
            x+=sizes[1]
            self.create_text(x+10,y+32,text=shorten(self.body_font,vals[1],sizes[2]-20),font=self.body_font,fill=C["muted"],anchor="w")
            x+=sizes[2]
            tags=data.get("badges",[v.strip() for v in vals[2].split(" · ") if v.strip()])
            bx=x+8
            for n,badge in enumerate(tags):
                text=shorten(self.small_font,str(badge),max(24,sizes[3]-30))
                bw=self.small_font.measure(text)+18
                if bx+bw>x+sizes[3]-5:
                    self.create_text(bx,y+32,text="+"+str(len(tags)-n),anchor="w",font=self.small_font,fill=C["muted"])
                    break
                is_tag=data.get("badge_types",["tag"]*len(tags))[n]=="tag"
                rounded(self,bx,y+20,bx+bw,y+44,12,fill=C["tag"] if is_tag else C["category"],outline="")
                self.create_text(bx+9,y+32,text=text,anchor="w",font=self.small_font,fill=C["pine"] if is_tag else C["link"])
                bx+=bw+5
            x+=sizes[3]
            self.create_text(x+9,y+32,text=vals[3],font=self.small_font,fill=C["muted"],anchor="w")
        # En-tête fixe ; dessiné après les lignes pour masquer le défilement dessous.
        self.create_rectangle(8,8,width-8,self.header_height,fill=C["paper"],outline="")
        x=-self.left
        for key,size in zip(["#0","title","context","tags","modified"],sizes):
            text=self.headings.get(key,{}).get("text","")
            self.create_text(x+10,22,text=shorten(self.small_font,text,size-15),anchor="w",font=("Segoe UI",9,"bold"),fill=C["muted"])
            x+=size
        self.create_line(8,self.header_height-1,width-8,self.header_height-1,fill=C["line"])
        if not self.rows and height>160:
            cx,cy=width/2,min(height/2,self.header_height+140)
            rounded(self,cx-34,cy-55,cx+34,cy+9,12,fill=C["selection"],outline="")
            self.create_line(cx-16,cy-34,cx+16,cy-34,fill=C["pine"],width=2)
            self.create_line(cx-16,cy-22,cx+8,cy-22,fill=C["pine"],width=2)
            self.create_line(cx-16,cy-10,cx+13,cy-10,fill=C["pine"],width=2)
            self.create_text(cx,cy+39,text="Rien ici, pour le moment.",font=("Segoe UI",15,"bold"),fill=C["pine"])
            self.create_text(cx,cy+70,text="Changez de recherche, ou ajoutez un fil.",font=("Segoe UI",10),fill=C["muted"],width=max(150,width-60))
        if self.ycommand: self.ycommand(*self.yview())
        if self.xcommand: self.xcommand(*self.xview())

    def delete_canvas(self):
        tk.Canvas.delete(self,"all")
