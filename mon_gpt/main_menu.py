"""Barre principale seulement ; commandes Tk conservées, aucun métier."""
import tkinter as tk
from tkinter.font import Font
from .atelier import MenuSkin, rounded
from .theme import COLORS as C


def menu_icon(canvas, label, x, y, color):
    """Petits traits vectoriels homogènes, sans boîte de fond."""
    def line(*points):
        canvas.create_line(*points, fill=color, width=1.25, capstyle="round", joinstyle="round")
    def box(a, b, c, d):
        canvas.create_rectangle(a, b, c, d, outline=color, width=1.2)
    if "Sauvegarder" in label or "Enregistrer" in label:
        line(x+1,y+15,x+1,y+1,x+12,y+1,x+15,y+4,x+15,y+15,x+1,y+15)
        box(x+4,y+1,x+11,y+6)
        box(x+4,y+10,x+12,y+15)
    elif "Restaurer" in label:
        canvas.create_arc(x+1,y+1,x+15,y+15,start=35,extent=295,style="arc",outline=color,width=1.3)
        line(x,y+1,x,y+6,x+5,y+6)
        line(x+8,y+4,x+8,y+8,x+11,y+10)
    elif "Dossier" in label or "projet" in label:
        line(x+1,y+14,x+1,y+3,x+6,y+3,x+8,y+5,x+15,y+5,x+15,y+14,x+1,y+14)
    elif "Quitter" in label:
        line(x+7,y+1,x+2,y+1,x+2,y+15,x+7,y+15)
        line(x+6,y+8,x+16,y+8,x+12,y+4)
        line(x+16,y+8,x+12,y+12)
    elif "fil" in label and "Nouveau" in label:
        line(x+1,y+2,x+15,y+2,x+15,y+12,x+7,y+12,x+3,y+16,x+3,y+12,x+1,y+12,x+1,y+2)
        line(x+5,y+7,x+11,y+7)
        line(x+8,y+4,x+8,y+10)
    elif "Renommer" in label or "Modifier" in label:
        line(x+2,y+12,x+11,y+3,x+14,y+6,x+5,y+15,x+1,y+16,x+2,y+12)
        line(x+9,y+5,x+12,y+8)
    elif "inspecteur" in label:
        box(x+1,y+2,x+15,y+14)
        line(x+10,y+2,x+10,y+14)
    elif "Rechercher" in label:
        canvas.create_oval(x+1,y+1,x+11,y+11,outline=color,width=1.3)
        line(x+10,y+10,x+15,y+15)
    elif "filtres" in label:
        line(x+1,y+2,x+15,y+2,x+10,y+8,x+10,y+14,x+6,y+16,x+6,y+8,x+1,y+2)
    elif "Fenêtre" in label or "Liste" in label:
        box(x+1,y+2,x+15,y+14)
        line(x+1,y+6,x+15,y+6)
        if "Liste" in label:
            line(x+4,y+9,x+12,y+9)
            line(x+4,y+12,x+12,y+12)
    else:
        canvas.create_oval(x+1,y+1,x+15,y+15,outline=color,width=1.2)
        canvas.create_text(x+8,y+8,text="?" if "Gestes" in label else "i",font=("Segoe UI",9),fill=color)


class MainMenuSkin(MenuSkin):
    """Même modèle MenuSkin, présentation réservée aux quatre rubriques."""
    def __init__(self, menu, bar, index):
        super().__init__(menu)
        self.bar, self.index = bar, index

    def popup(self, x=None, y=None, entry=""):
        self.bar.open(self.index)


class MainMenuBar(tk.Canvas):
    def __init__(self, root, menus):
        super().__init__(root, height=36, background=C["ivory"], highlightthickness=0, takefocus=1)
        self.root, self.menus = root, menus
        self.font = Font(root, font=("Segoe UI", 10))
        self.menu_font = Font(root, font=("Segoe UI", 10))
        self.shortcut_font = Font(root, font=("Segoe UI", 9))
        self.bounds, x = [], 16
        for label, menu in menus:
            width = self.font.measure(label)+42
            self.bounds.append((x,x+width))
            x += width+2
            skin = MainMenuSkin(menu,self,len(self.bounds)-1)
            menu._atelier_skin = skin
            menu.tk_popup = skin.popup
        self.active, self.hovered, self.window = None, None, None
        self.clicked_heading = None
        self.saved_focus = None
        self.bind("<Configure>",lambda e:self.draw())
        self.bind("<Motion>",self.motion)
        self.bind("<Leave>",lambda e:self.hover(None))
        self.bind("<Button-1>",self.press)
        self.bind("<Down>",lambda e:self.open(self.hovered or 0,keyboard=True))
        self.bind("<Return>",lambda e:self.open(self.hovered or 0,keyboard=True))
        self.bind("<Right>",lambda e:self.bar_step(1))
        self.bind("<Left>",lambda e:self.bar_step(-1))
        self.bind("<Escape>",lambda e:self.close())
        self.bind("<FocusIn>",lambda e:self.draw())
        self.bind("<FocusOut>",lambda e:self.draw())
        root.bind("<F10>",self.keyboard_bar,add="+")
        for key,index in [("f",0),("e",1),("a",2),("i",3)]:
            root.bind(f"<Alt-{key}>",lambda e,i=index:self.open(i,keyboard=True),add="+")

    def draw(self):
        self.delete("all")
        self.create_line(16,35,max(16,self.winfo_width()-16),35,fill=C["line"])
        for i,((a,b),(label,menu)) in enumerate(zip(self.bounds,self.menus)):
            if i==self.active or i==self.hovered:
                rounded(self,a,4,b,32,5,fill=C["selection"] if i==self.active else C["hover"],outline="")
            self.create_text(a+12,18,text=label,anchor="w",font=self.font,fill=C["ink"])
            self.create_line(b-18,16,b-15,19,b-12,16,fill=C["ink"],width=1.1)
            if self.focus_get()==self and i==self.hovered:
                self.create_line(a+12,28,b-25,28,fill=C["pine"])

    def header_at(self, x_root, y_root):
        if not self.winfo_rooty() <= y_root < self.winfo_rooty()+36:
            return None
        x=x_root-self.winfo_rootx()
        return next((i for i,(a,b) in enumerate(self.bounds) if a<=x<b),None)

    def hover(self,index):
        self.hovered=index
        self.draw()

    def motion(self,event):
        index=self.header_at(event.x_root,event.y_root)
        if index is not None and self.active is not None and index!=self.active:
            self.open(index)
        elif self.active is None:
            self.hover(index)

    def press(self,event):
        index=self.header_at(event.x_root,event.y_root)
        if index is not None:
            if index==self.active and index==self.clicked_heading:
                self.close()
            else:
                self.open(index)
                self.clicked_heading=index
        return "break"

    def keyboard_bar(self,event=None):
        if self.active is not None or self.focus_get()==self:
            return self.close()
        self.saved_focus=self.root.focus_get()
        self.hovered=0
        self.focus_set()
        self.draw()
        return "break"

    def bar_step(self,delta):
        self.hover(((self.hovered or 0)+delta)%len(self.menus))
        return "break"

    def close(self,restore=True):
        if self.window is not None:
            if self.window.winfo_exists():
                self.window.grab_release()
                self.window.destroy()
            self.window=None
        self.active=None
        self.hovered=None
        if restore:
            self.clicked_heading=None
            target=self.saved_focus
            self.saved_focus=None
            if target is not None and target.winfo_exists():
                target.focus_set()
        self.draw()
        return "break"

    def open(self,index,keyboard=False):
        if self.active is None and self.root.focus_get()!=self:
            self.saved_focus=self.root.focus_get()
        self.close(restore=False)
        self.active=self.hovered=index
        menu=self.menus[index][1]
        indices=list(range((menu.index("end") or 0)+1))
        valid=[i for i in indices if menu.type(i)!="separator" and menu.entrycget(i,"state")!="disabled"]
        # Pas de sélection arbitraire au clic : seul le survol colore une commande.
        self.selected=valid[0] if keyboard and valid else None
        width=max([250]+[self.menu_font.measure(menu.entrycget(i,"label"))+self.shortcut_font.measure(menu.entrycget(i,"accelerator"))+80 for i in indices if menu.type(i)!="separator"])
        pos=7
        self.rows=[]
        for i in indices:
            height=9 if menu.type(i)=="separator" else 31
            self.rows.append((i,pos,pos+height))
            pos+=height
        height=pos+7
        x=min(self.bounds[index][0],max(0,self.root.winfo_width()-width-8))
        y=self.winfo_y()+33
        win=self.window=tk.Frame(self.root,background=C["ivory"],borderwidth=0)
        menu._atelier_skin.window=win
        win.place(x=x,y=y,width=width+7,height=height+7)
        win.lift()
        canvas=self.popup_canvas=tk.Canvas(win,background=C["ivory"],highlightthickness=0)
        canvas.pack(fill="both",expand=True)
        def draw():
            canvas.delete("all")
            rounded(canvas,3,4,width+5,height+5,9,fill="#E2DDD2",outline="")
            rounded(canvas,2,2,width+3,height+3,8,fill="#ECE7DD",outline="")
            rounded(canvas,0,0,width,height,7,fill=C["paper"],outline="#BFB9AE")
            for i,top,bottom in self.rows:
                if menu.type(i)=="separator":
                    canvas.create_line(10,(top+bottom)/2,width-10,(top+bottom)/2,fill=C["line"])
                    continue
                disabled=menu.entrycget(i,"state")=="disabled"
                if i==self.selected and not disabled:
                    rounded(canvas,5,top,width-5,bottom,4,fill=C["hover"],outline="")
                color="#A49F95" if disabled else C["ink"]
                label=menu.entrycget(i,"label")
                menu_icon(canvas,label,18,(top+bottom)/2-8,color)
                canvas.create_text(46,(top+bottom)/2,text=label,anchor="w",font=self.menu_font,fill=color)
                canvas.create_text(width-17,(top+bottom)/2,text=menu.entrycget(i,"accelerator"),anchor="e",font=self.shortcut_font,fill="#A49F95" if disabled else C["muted"])
        def row_at(event):
            px,py=event.x_root-win.winfo_rootx(),event.y_root-win.winfo_rooty()
            return next((i for i,a,b in self.rows if 0<=px<width and a<=py<b and i in valid),None)
        def motion(event):
            self.motion(event)
            if self.window==win:
                self.selected=row_at(event)
                draw()
        def press(event):
            header=self.header_at(event.x_root,event.y_root)
            if header is not None:
                return self.press(event)
            px,py=event.x_root-win.winfo_rootx(),event.y_root-win.winfo_rooty()
            if not (0<=px<width and 0<=py<height):
                return self.close()
        def invoke(event=None):
            if event is not None:
                if self.header_at(event.x_root,event.y_root) is not None:
                    return "break"
                self.selected=row_at(event)
            selected=self.selected
            if selected in valid:
                self.close()
                menu.invoke(selected)
            return "break"
        def step(delta):
            if valid:
                self.selected=valid[(valid.index(self.selected)+delta)%len(valid)] if self.selected in valid else valid[0 if delta>0 else -1]
                draw()
            return "break"
        for widget in (win,canvas):
            widget.bind("<Motion>",motion)
            widget.bind("<ButtonPress-1>",press)
            widget.bind("<ButtonRelease-1>",invoke)
        win.bind("<Down>",lambda e:step(1))
        win.bind("<Up>",lambda e:step(-1))
        win.bind("<Return>",lambda e:invoke())
        win.bind("<Escape>",lambda e:self.close())
        win.bind("<Left>",lambda e:self.open((index-1)%len(self.menus),keyboard=True))
        win.bind("<Right>",lambda e:self.open((index+1)%len(self.menus),keyboard=True))
        win.bind("<F10>",lambda e:self.close())
        def lost_focus(event):
            def check():
                if self.window==win and self.root.focus_get() is None:
                    self.close()
            self.root.after_idle(check)
        win.bind("<FocusOut>",lost_focus)
        draw()
        self.draw()
        win.grab_set()
        win.focus_set()
        return "break"
