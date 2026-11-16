"""Composants visuels Canvas de l'Atelier ; aucune règle métier."""
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from .selection import Selection
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
        super().__init__(parent, height=80, background=C["ivory"], highlightthickness=0)
        self.bind("<Configure>", self.draw)

    def draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        # Le repère de marque : carnet et plume, dessinés, pas un actif binaire.
        rounded(self, 8, 12, 46, 50, 10, fill=C["pine"], outline="")
        self.create_line(20,40,34,22, fill=C["paper"], width=2, capstyle="round")
        self.create_polygon(24,33,23,24,35,18,34,27, fill="#E5C9A1", outline="")
        self.create_line(19,42,35,42, fill="#92AA8A", width=1.5, capstyle="round")
        self.create_text(60, 23, text="Mon GPT<3", anchor="w", font=("Segoe UI",22 if w>=500 else 19,"bold"), fill=C["pine"])
        self.create_text(61, 47, text="Votre organisation, en local.", anchor="w", font=("Segoe UI",9), fill=C["muted"])
        self.create_text(10, 69, text="UN PEU D'ORDRE.  BEAUCOUP D'IDÉES.", anchor="w", font=("Segoe UI",7,"bold"), fill=C["link"])
        # Paysage d'atelier : collines, soleil, pages et feuillage.
        before=set(self.find_all())
        available=w
        w,start=500,0
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
        for item in set(self.find_all())-before:
            self.addtag_withtag("landscape",item)
        scale=.45 if available>=560 else .25 if available>=420 else .15
        self.scale("landscape",0,0,scale,scale)
        self.move("landscape",available-500*scale-8,78-114*scale)
        self.create_line(8,79,available-8,79,fill=C["line"])


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
    row_height, header_height = 42, 34
    keys = ["#0","title","context","categories","tags","modified","open","details"]

    def __init__(self, parent):
        super().__init__(parent, background=C["ivory"], highlightthickness=0, takefocus=1, height=60)
        self.rows, self.columns, self.headings = {}, {}, {}
        self.selected, self.focused, self.hovered = None, None, None
        self.pick=Selection()
        self.selection_guard=None
        self.pending_single=None
        self.gesture_blocked=False
        self.top, self.left = 0, 0
        self.ycommand, self.xcommand = None, None
        self.title_font = Font(self,font=("Segoe UI",10,"bold"))
        self.small_font = Font(self,font=("Segoe UI",9))
        self.body_font = Font(self,font=("Segoe UI",10))
        self.bind("<Configure>",lambda e:self.draw())
        self.bind("<Button-1>",self.select_click)
        self.bind("<Motion>",self.motion)
        self.bind("<Leave>",lambda e:(self.hide_tip(),self.hover(None)))
        self.bind("<Up>",lambda e:self.navigate(-1))
        self.bind("<Down>",lambda e:self.navigate(1))
        self.bind("<MouseWheel>",lambda e:self.yview("scroll",-int(e.delta/120 or (1 if e.delta>0 else -1))*2,"units"))
        self.bind("<FocusIn>",lambda e:self.draw())
        self.bind("<FocusOut>",lambda e:self.draw())
        self.action_focus=False
        self.sort_column,self.sort_reverse="title",False
        self.tip_timer,self.tip=None,None
        self.bind("<Right>",lambda e:self.focus_action(True))
        self.bind("<Left>",lambda e:self.focus_action(False))
        self.bind("<Control-a>",self.select_all)
        self.bind("<Shift-Up>",lambda e:self.navigate(-1,extend=True))
        self.bind("<Shift-Down>",lambda e:self.navigate(1,extend=True))
        self.resize_column = None
        self.title_resized = False
        self.separator_hover = None
        self.pending_draw = None
        self.bind("<B1-Motion>",self.resize_motion)
        self.bind("<ButtonRelease-1>",self.resize_release)
        self.bind("<Leave>",self.leave_header,add=True)

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
        return [self.layout().get(key,(0,0))[1] for key in self.keys]

    def layout(self):
        """Titre et action épinglés ; seules les colonnes secondaires défilent."""
        width=max(1,self.winfo_width())
        icon,action=32,36
        if width<440:
            self.secondary_order=[]
            self.secondary_start,self.secondary_visible=width-action-32,32
            return {"#0":(0,icon),"title":(icon,max(1,width-icon-action-32)),"details":(width-action-32,32),"open":(width-action,action)}
        order=["context","categories","tags"] if width>=900 else ["categories","tags","context"]
        self.secondary_order=order
        total=sum(self.columns.get(k,{}).get("width",150) for k in order)
        preferred=self.columns.get("title",{}).get("width",300)
        if self.title_resized:
            title=max(180,min(preferred,width-icon-action-90))
        else:
            title=max(180,min(preferred,int(width*.44)))
            title=max(title,width-icon-action-total)
        self.secondary_start=icon+title
        self.secondary_visible=max(1,width-action-self.secondary_start)
        self.left=min(self.left,max(0,total-self.secondary_visible))
        result={"#0":(0,icon),"title":(icon,title),"open":(width-action,action)}
        x=self.secondary_start-self.left
        for key in order:
            size=self.columns.get(key,{}).get("width",150)
            result[key]=(x,size)
            x+=size
        return result

    def visible_box(self,key):
        layout=self.layout()
        if key not in layout: return (0,0)
        x,width=layout[key]
        if key in self.secondary_order:
            start=max(x,self.secondary_start)
            end=min(x+width,self.winfo_width()-36)
            return (start,max(0,end-start))
        return x,width

    def open_hit(self,identity,x,y):
        if identity not in self.rows or "project" in self.rows[identity].get("tags",()): return False
        if self.identify_row(y)!=identity or not 0<=x<self.winfo_width(): return False
        layout=self.layout()
        tx,tw=layout["title"]
        text=shorten(self.title_font,self.rows[identity]["values"][0],tw-16)
        return x<32 or tx+6<=x<=tx+6+self.title_font.measure(text) or layout["open"][0]<=x<self.winfo_width()

    def focus_action(self,value):
        self.action_focus=value
        self.draw()
        return "break"

    def insert(self,parent,index,iid,**kwargs):
        self.rows[iid]=dict(kwargs)
        self.request_draw()
        return iid

    def delete(self,*identities):
        for identity in identities: self.rows.pop(identity,None)
        if self.selected not in self.rows: self.selected=None
        self.pick.set(self.pick.ids,list(self.rows),self.item_ids(),self.pick.anchor,self.pick.focal)
        self.request_draw()

    def request_draw(self):
        if self.pending_draw is None:
            self.pending_draw=self.after_idle(self.flush_draw)

    def flush_draw(self):
        self.pending_draw=None
        self.draw()

    def destroy(self):
        self.hide_tip()
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
        return self.pick.ids

    def selection_set(self,identity):
        identities=identity if isinstance(identity,(tuple,list,set)) else ([identity] if identity else [])
        self.set_selection(identities)

    def item_ids(self):
        return {i for i,row in self.rows.items() if "project" not in row.get("tags",())}

    def set_selection(self,identities,anchor=None,focal=None):
        old=self.pick.ids
        self.pick.set(identities,list(self.rows),self.item_ids(),anchor,focal)
        self.selected=self.pick.focal if self.pick.focal in self.pick.ids else next(iter(self.pick.ids),None)
        if self.pick.focal is not None: self.focused=self.pick.focal
        if old!=self.pick.ids:
            self.event_generate("<<TreeviewSelect>>",when="tail")
        self.draw()

    def gesture_select(self,identity,event=None,extend=False,control=False):
        self.gesture_blocked=False
        self.pending_single=None
        state=getattr(event,"state",0)
        control=control or bool(state&4)
        extend=extend or bool(state&1)
        proposed=Selection();proposed.ids=self.pick.ids;proposed.anchor=self.pick.anchor
        proposed.gesture(identity,list(self.rows),self.item_ids(),control,extend,project_alone=(event is not None or not extend))
        if proposed.ids!=self.pick.ids and self.selection_guard and not self.selection_guard():
            self.gesture_blocked=True
            return "break"
        if not control and not extend and event is not None and len(self.pick.ids)>1 and identity in self.pick.ids:
            self.pending_single=identity
            return "break"
        self.set_selection(proposed.ids,proposed.anchor,proposed.focal)
        return "break"

    def finish_single(self):
        identity=self.pending_single
        self.pending_single=None
        if identity in self.rows: self.selection_set(identity)

    def select_all(self,event=None):
        if self.selection_guard and not self.selection_guard(): return "break"
        self.set_selection(self.item_ids(),self.pick.anchor,self.focused)
        return "break"

    def collapse_selection(self):
        self.selection_set(self.focused if self.focused in self.pick.ids else next(iter(self.pick.ids),None))
        return "break"

    def focus(self,identity=None):
        if identity is not None: self.focused=identity
        return self.focused or ""

    def bbox(self,identity,column=None):
        if identity not in self.rows: return ""
        layout=self.layout()
        y=self.header_height+list(self.rows).index(identity)*self.row_height-self.top
        if y+self.row_height<=self.header_height or y>=self.winfo_height(): return ""
        x,width=layout.get(column,(0,0)) if column else (0,self.winfo_width())
        return (x,y,width,self.row_height)

    def identify_row(self,y):
        if y<self.header_height: return ""
        index=int((y-self.header_height+self.top)//self.row_height)
        return list(self.rows)[index] if 0<=index<len(self.rows) else ""

    def identify_column(self,x):
        self.layout()
        for key in ["#0","title","open","details"]+self.secondary_order:
            start,width=self.visible_box(key)
            if width and start<=x<start+width: return f"#{self.keys.index(key)}"
        return ""

    def select_click(self,event):
        self.hide_tip()
        self.focus_set()
        if event.y<self.header_height:
            key=self.separator_at(event.x,event.y)
            if key:
                layout=self.layout()
                # Figer la largeur réellement visible, sans saut au premier pixel.
                self.columns["title"]["width"]=layout["title"][1]
                self.title_resized=True
                self.resize_column=(key,event.x,layout[key][1])
                self.configure(cursor="sb_h_double_arrow")
                return
            col=self.identify_column(event.x)
            if col:
                fn=self.headings.get(self.keys[int(col[1:])],{}).get("command")
                if fn: fn()
            return
        identity=self.identify_row(event.y)
        if identity:
            self.gesture_select(identity,event)

    def resize_motion(self,event):
        if self.resize_column:
            key,start,width=self.resize_column
            self.columns[key]["width"]=max(self.columns[key].get("minwidth",44),width+event.x-start)
            self.draw()

    def separator_at(self,x,y):
        if not 0<=y<self.header_height or self.winfo_width()<440 or getattr(self,"view","list")!="list": return None
        layout=self.layout()
        for key in ["title"]+self.secondary_order:
            start,size=layout[key]
            edge=start+size
            if self.visible_box(key)[1]>0 and self.secondary_start<=edge<=self.winfo_width()-36 and abs(x-edge)<=7:
                return key
        return None

    def resize_release(self,event):
        self.resize_column=None
        self.motion(event)

    def leave_header(self,event=None):
        if self.separator_hover is not None:
            self.separator_hover=None
            self.draw()
        if not self.resize_column: self.configure(cursor="")

    def navigate(self,step,extend=False):
        identities=list(self.rows)
        if identities:
            index=identities.index(self.focused) if self.focused in identities else (-1 if step>0 else len(identities))
            target=identities[max(0,min(len(identities)-1,index+step))]
            self.gesture_select(target,extend=extend)
            self.see(self.focused)
        return "break"

    def motion(self,event):
        separator=self.separator_at(event.x,event.y)
        if separator!=self.separator_hover:
            self.separator_hover=separator
            self.draw()
        if separator or self.resize_column:
            self.configure(cursor="sb_h_double_arrow")
            self.hide_tip()
            return
        self.hover(self.identify_row(event.y))
        self.hide_tip()
        identity=self.identify_row(event.y)
        if identity:
            self.tip_timer=self.after(600,lambda:self.show_tip(identity,event.y))

    def hide_tip(self):
        if getattr(self,"tip_timer",None) is not None:
            self.after_cancel(self.tip_timer)
            self.tip_timer=None
        if getattr(self,"tip",None) is not None:
            self.tip.destroy()
            self.tip=None

    def show_tip(self,identity,y):
        self.tip_timer=None
        if identity not in self.rows: return
        data=self.rows[identity]
        vals=data["values"]
        text=vals[0]+"\nProjet : "+vals[1]
        text+="\nCatégories : "+(" · ".join(data.get("categories",[])) or "—")
        text+="\nTags : "+(" · ".join(data.get("labels",[])) or "—")
        if self.winfo_width()<900: text+="\nColonnes secondaires repliées ou défilantes."
        self.tip=tk.Label(self,text=text,font=("Segoe UI",9),background=C["ivory"],foreground=C["ink"],justify="left",anchor="w",padx=10,pady=8,wraplength=max(100,self.winfo_width()-48),highlightthickness=1,highlightbackground=C["line"])
        self.tip.update_idletasks()
        self.tip.place(x=12,y=max(self.header_height,min(y+20,self.winfo_height()-self.tip.winfo_reqheight()-8)),width=max(1,self.winfo_width()-24))
        self.tip.lift()

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
            self.hide_tip()
            self.top=float(args[1])*total if args[0]=="moveto" else self.top+int(args[1])*(self.row_height if args[2]=="units" else visible)
            self.top=max(0,min(self.top,max(0,total-visible)))
            self.draw()
        return (self.top/total,min(1,(self.top+visible)/total))

    def xview(self,*args):
        self.layout()
        if not self.secondary_order: return (0,1)
        total=max(1,sum(self.columns.get(k,{}).get("width",150) for k in self.secondary_order))
        visible=self.secondary_visible
        if args:
            self.hide_tip()
            self.left=float(args[1])*total if args[0]=="moveto" else self.left+int(args[1])*40
            self.left=max(0,min(self.left,max(0,total-visible)))
            self.draw()
        return (self.left/total,min(1,(self.left+visible)/total))

    def row_icon(self,x,y,project,color):
        if project:
            points=[x-8,y+6,x-8,y-6,x-2,y-6,x+1,y-3,x+8,y-3,x+8,y+6,x-8,y+6]
        else:
            points=[x-8,y-6,x+8,y-6,x+8,y+4,x-1,y+4,x-5,y+8,x-5,y+4,x-8,y+4,x-8,y-6]
        self.create_line(*points,fill=color,width=1.4,joinstyle="round")

    def draw_badges(self,labels,x,y,width,category):
        if width<28: return
        end=x+width-6
        for n,label in enumerate(labels):
            bw=self.small_font.measure(label)+16
            reserve=27 if n<len(labels)-1 else 0
            if x+bw+reserve>end:
                self.create_text(x,y,text="+"+str(len(labels)-n),anchor="w",font=self.small_font,fill=C["muted"])
                return
            palette=["#DDE4CF","#EDD4C6","#E8DEBF","#D6E2D8"] if category else ["#F0E7DA","#E7DDE7","#E4E9DC","#EBDFD8"]
            color=palette[sum((i+1)*ord(c) for i,c in enumerate(label.casefold()))%len(palette)]
            rounded(self,x,y-11,x+bw,y+11,11,fill=color,outline="#C6CBB7" if category else "")
            self.create_text(x+8,y,text=label,anchor="w",font=self.small_font,fill=C["ink"])
            x+=bw+5

    def draw(self):
        self.delete_canvas()
        width,height=self.winfo_width(),self.winfo_height()
        layout=self.layout()
        rounded(self,1,1,width-1,height-1,12,fill=C["paper"],outline=C["line"])
        self.top=max(0,min(self.top,max(0,len(self.rows)*self.row_height-(height-self.header_height))))
        for index,(identity,data) in enumerate(self.rows.items()):
            y=self.header_height+index*self.row_height-self.top
            if y+self.row_height<=self.header_height or y>=height: continue
            cy=y+self.row_height/2
            selected=identity in self.pick.ids
            fill="#E3E9D8" if selected else "#F1F0E7" if identity==self.hovered else C["paper"]
            rounded(self,4,y+2,width-5,y+self.row_height-2,6,fill=fill,outline="")
            if selected and identity==self.focused and self.focus_get()==self:
                rounded(self,4,y+2,width-5,y+self.row_height-2,6,fill="",outline="#91A38B")
            self.create_line(10,y+self.row_height-1,width-10,y+self.row_height-1,fill="#EEE9E0")
            vals=data.get("values",("",)*4)
            project="project" in data.get("tags",())
            if not project and data.get("visual") and data.get("image"):
                self.create_image(17,cy,image=data["image"],tags=("effective_icon",identity))
            else:
                self.row_icon(17,cy,project,C["link"] if project else C["pine"])
            tx,tw=layout["title"]
            self.create_text(tx+6,cy,text=shorten(self.title_font,vals[0],tw-16),font=self.title_font,fill=C["ink"],anchor="w")
            for key in self.secondary_order:
                x,size=self.visible_box(key)
                if size<20: continue
                if key=="context":
                    self.create_text(x+7,cy,text=shorten(self.small_font,vals[1],size-14),font=self.small_font,fill=C["muted"],anchor="w")
                else:
                    labels=data.get("categories" if key=="categories" else "labels",[])
                    self.draw_badges(labels,x+6,cy,size-8,key=="categories")
            if "details" in layout:
                x,size=layout["details"]
                count=len(data.get("categories",[]))+len(data.get("labels",[]))
                self.create_text(x+size/2,cy,text="+"+str(count) if count else "⋯",font=self.small_font,fill=C["muted"])
            if not project:
                x,size=layout["open"]
                if selected and self.action_focus and self.focus_get()==self:
                    rounded(self,x+4,cy-13,x+size-4,cy+13,4,fill="",outline=C["pine"])
                self.create_line(x+11,cy+3,x+11,cy+7,x+23,cy+7,x+23,cy+3,fill=C["pine"],width=1.25)
                self.create_line(x+15,cy+2,x+24,cy-7,x+18,cy-7,fill=C["pine"],width=1.3)
                self.create_line(x+24,cy-7,x+24,cy-1,fill=C["pine"],width=1.3)
        # En-tête fixe, au-dessus du défilement des lignes.
        self.create_rectangle(4,3,width-4,self.header_height,fill="#F0EBE2",outline="")
        for key in ["#0","title"]+self.secondary_order+["details","open"]:
            x,size=self.visible_box(key)
            if size<20: continue
            text=self.headings.get(key,{}).get("text","")
            if key=="details": text="⋯"
            if key=="open": text="↗"
            if key==self.sort_column: text+=(" ↓" if self.sort_reverse else " ↑")
            self.create_text(x+7,18,text=shorten(self.small_font,text,size-12),anchor="w",font=self.small_font,fill=C["muted"])
        self.create_line(6,self.header_height-1,width-6,self.header_height-1,fill=C["line"])
        grip=self.resize_column[0] if self.resize_column else self.separator_hover
        if grip and grip in layout:
            edge=sum(layout[grip])
            if self.secondary_start<=edge<=width-36:
                self.create_line(edge,8,edge,self.header_height-7,fill=C["pine"],width=2,tags="column_grip")
        if not self.rows and height>160:
            cx,cy=width/2,min(height/2,self.header_height+120)
            self.row_icon(cx,cy-30,False,C["pine"])
            self.create_text(cx,cy+8,text="Aucun résultat",font=("Segoe UI",12,"bold"),fill=C["pine"])
            self.create_text(cx,cy+38,text="Changez de recherche, ou ajoutez un fil.",font=self.body_font,fill=C["muted"],width=max(150,width-40))
        if self.ycommand: self.ycommand(*self.yview())
        if self.xcommand: self.xcommand(*self.xview())

    def delete_canvas(self):
        tk.Canvas.delete(self,"all")
