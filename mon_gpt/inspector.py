"""Présentation en lecture seule de l'inspecteur ; aucune règle métier."""
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from datetime import datetime
from .atelier import PillButton, AutoScrollbar, rounded
from .theme import COLORS as C, CATEGORY_COLORS, TAG_COLORS


class InspectorScrollbar(AutoScrollbar):
    def __init__(self,parent,canvas):
        self.content=canvas
        style=ttk.Style(parent)
        name="Inspector.Vertical.TScrollbar"
        style.layout(name,style.layout("Vertical.TScrollbar"))
        style.configure(name,background="#AC9C85",troughcolor="#EFE9DE",bordercolor=C["paper"],lightcolor="#AC9C85",darkcolor="#AC9C85",arrowsize=12,borderwidth=0)
        style.map(name,background=[("active","#8D7C63"),("pressed","#79674F")])
        super().__init__(parent,orient="vertical",command=canvas.yview,style=name)

    def set(self,first,last):
        if float(first)<=0 and float(last)>=1:
            self.pack_forget()
        elif not self.winfo_manager():
            # Réinsérer AVANT le Canvas expansible, même après un état sans scroll.
            options={"side":"right","fill":"y"}
            if self.content.winfo_manager()=="pack": options["before"]=self.content
            self.pack(**options)
        ttk.Scrollbar.set(self,first,last)


class InspectorAction(PillButton):
    def __init__(self,parent,kind,label,command):
        self.kind,self.label=kind,label
        self.tip_timer,self.tip=None,None
        super().__init__(parent,text=label,command=command,width=40,height=32,tone="warm" if kind=="open" else "quiet")
        self.bind("<Enter>",self.offer_tip,add="+")
        self.bind("<FocusIn>",self.offer_tip,add="+")
        self.bind("<Leave>",lambda e:self.hide_tip(),add="+")
        self.bind("<FocusOut>",lambda e:self.hide_tip(),add="+")
        self.bind("<Destroy>",lambda e:self.hide_tip(),add="+")

    def activate(self):
        self.hide_tip()
        return super().activate()

    def offer_tip(self,event=None):
        self.hide_tip()
        self.tip_timer=self.after(450,self.show_tip)

    def show_tip(self):
        self.tip_timer=None
        self.tip=tk.Toplevel(self)
        self.tip.overrideredirect(True)
        tk.Label(self.tip,text=self.label,font=("Segoe UI",9),background=C["ivory"],foreground=C["ink"],padx=8,pady=4,relief="solid",borderwidth=1).pack()
        self.tip.update_idletasks()
        root=self.winfo_toplevel()
        x=min(self.winfo_rootx(),root.winfo_rootx()+root.winfo_width()-self.tip.winfo_reqwidth()-8)
        self.tip.geometry(f"+{max(root.winfo_rootx(),x)}+{self.winfo_rooty()+self.winfo_height()+4}")

    def hide_tip(self):
        if self.tip_timer is not None:
            self.after_cancel(self.tip_timer)
            self.tip_timer=None
        if self.tip is not None:
            self.tip.destroy()
            self.tip=None

    def draw(self,event=None):
        self.delete("all")
        w,h=self.winfo_width(),self.winfo_height()
        warm=self.kind=="open"
        fill=("#B86C45" if self.hovered else C["terracotta"]) if warm else (C["hover"] if self.hovered else C["paper"])
        focused=self.focus_get()==self
        rounded(self,1,1,w-1,h-1,7,fill=fill,outline=C["pine"] if focused else C["line"],width=2 if focused else 1)
        color=C["paper"] if warm else C["pine"]
        x,y=w/2-8,h/2-8
        def line(*points): self.create_line(*points,fill=color,width=1.6,capstyle="round",joinstyle="round")
        if self.kind=="open":
            line(x+2,y+5,x+2,y+15,x+13,y+15,x+13,y+10)
            line(x+6,y+9,x+15,y,x+9,y)
            line(x+15,y,x+15,y+6)
        elif self.kind=="copy":
            line(x+5,y+3,x+2,y+3,x+2,y+15,x+12,y+15,x+12,y+12)
            self.create_rectangle(x+6,y,x+15,y+11,outline=color,width=1.4)
        elif self.kind=="edit":
            line(x+1,y+12,x+12,y+1,x+15,y+4,x+4,y+15,x,y+16,x+1,y+12)
            line(x+10,y+3,x+13,y+6)
        else:
            line(x+4,y+4,x+12,y+12)
            line(x+12,y+4,x+4,y+12)


class InspectorBadges(tk.Canvas):
    def __init__(self,parent,values,category):
        super().__init__(parent,height=28,highlightthickness=0,background=C["paper"])
        self.values,self.category=values,category
        self.font=Font(self,font=("Segoe UI",9))
        self.bind("<Configure>",self.draw)

    def draw(self,event=None):
        self.delete("all")
        width=max(24,self.winfo_width())
        x,y,row_height=0,2,0
        for value in self.values:
            bw=min(width-2,self.font.measure(value)+16)
            if x and x+bw>width:
                x,y,row_height=0,y+row_height+5,0
            item=self.create_text(x+8,y+4,text=value,font=self.font,anchor="nw",width=max(8,bw-16),fill=C["ink"])
            height=self.bbox(item)[3]-self.bbox(item)[1]+8
            palette=CATEGORY_COLORS if self.category else TAG_COLORS
            color=palette[sum((i+1)*ord(c) for i,c in enumerate(value.casefold()))%len(palette)]
            shape=rounded(self,x,y,x+bw,y+height,10,fill=color,outline=C["badge_edge"] if self.category else "")
            self.tag_lower(shape,item)
            row_height=max(row_height,height)
            x+=bw+5
        height=y+row_height+2
        if int(self.cget("height"))!=height: self.configure(height=height)


class InspectorNotes(ttk.Frame):
    def __init__(self,parent,value):
        super().__init__(parent,style="Paper.TFrame")
        self.value=value
        self.expanded=len(value)<=600
        self.body=ttk.Label(self,text=value or "Aucune note",style="Paper.TLabel",font=("Segoe UI",10),foreground=C["ink"] if value else C["muted"],wraplength=280,justify="left")
        self.button=None
        if len(value)>600:
            self.button=PillButton(self,text="",command=self.toggle,height=27,width=245)
            self.button.pack(anchor="w")
        self.bind("<Configure>",self.fit)
        self.render()

    def toggle(self):
        self.expanded=not self.expanded
        self.render()

    def render(self):
        if self.button:
            self.button.configure(text=("▾ Replier" if self.expanded else "▸ Lire")+f" · {len(self.value):,} caractères".replace(","," "))
        if self.expanded: self.body.pack(fill="x",pady=(4,0) if self.button else 0)
        else: self.body.pack_forget()

    def fit(self,event):
        self.body.configure(wraplength=max(40,event.width))
        if self.button: self.button.configure(width=max(40,min(245,event.width)))


class InspectorSummary(ttk.Frame):
    def __init__(self,parent,record,project_label,close,open_thread,copy_link,edit):
        super().__init__(parent,style="Paper.TFrame")
        self.labels=[]
        self.actions={}
        self.bind("<Configure>",self.fit)
        top=ttk.Frame(self,style="Paper.TFrame")
        top.pack(fill="x",pady=(0,8))
        InspectorAction(top,"close","Replier l’aperçu",close).pack(side="right")
        if record is None:
            self.title=ttk.Label(top,text="Sélectionnez une fiche",style="Inspector.TLabel",font=("Segoe UI",15,"bold"),wraplength=220)
            self.title.pack(side="left",fill="x",expand=True)
            self.text("Choisissez une discussion ou un projet dans la Liste.",muted=True)
            return
        title=ttk.Frame(top,style="Paper.TFrame")
        title.pack(side="left",fill="x",expand=True,padx=(0,8))
        icon=tk.Canvas(title,width=24,height=26,background=C["paper"],highlightthickness=0)
        icon.pack(side="left",anchor="n",padx=(0,5))
        points=[3,18,3,6,9,6,12,9,21,9,21,18,3,18] if record.kind=="project" else [3,5,21,5,21,17,12,17,7,22,7,17,3,17,3,5]
        icon.create_line(*points,fill=C["pine"],width=1.5,joinstyle="round")
        self.title=ttk.Label(title,text=record.title,font=("Segoe UI",16,"bold"),foreground=C["pine"],style="Paper.TLabel",wraplength=230,justify="left")
        self.title.pack(side="left",fill="x",expand=True)
        self.text("Projet" if record.kind=="project" else f"Discussion · {len(record.projects)} emplacement(s)",muted=True,pady=(4,8))
        row=ttk.Frame(self,style="Paper.TFrame")
        row.pack(fill="x",pady=(0,3))
        choices=[] if record.kind=="project" else [("open","Ouvrir le fil",open_thread),("copy","Copier le lien",copy_link)]
        choices.append(("edit","Modifier la fiche",edit))
        for kind,label,command in choices:
            button=InspectorAction(row,kind,label,command)
            button.pack(side="left",padx=(0,7))
            self.actions[kind]=button
        self.section("Description" if record.kind=="project" else "Résumé")
        self.text(record.description or ("Pas de description" if record.kind=="project" else "Pas de résumé"),muted=not record.description)
        self.section("Emplacements")
        locations=record.projects if record.kind=="item" else ([record.parent] if record.parent else [])
        for pid in locations: self.text("▱  "+project_label(pid),muted=True,pady=(0,3))
        if not locations: self.text("À classer" if record.kind=="item" else "À la racine",muted=True)
        for label,values,category in [("Catégories",record.categories,True),("Tags",record.tags,False)]:
            self.section(label)
            if values: InspectorBadges(self,values,category).pack(fill="x")
            else: self.text("Aucune catégorie" if category else "Aucun tag",muted=True)
        self.section("Notes")
        self.notes=InspectorNotes(self,record.notes)
        self.notes.pack(fill="x")
        self.section("Informations")
        for key,value in record.metadata.items(): self.text(f"{key} : {value}",pady=(0,3))
        if not record.metadata: self.text("Aucune information personnalisée",muted=True)
        fmt=lambda value:datetime.fromisoformat(value).astimezone().strftime("%d/%m/%Y à %H:%M")
        self.text(f"Créé le {fmt(record.created)}\nModifié le {fmt(record.modified)}",muted=True,pady=(10,0),font=("Segoe UI",8))

    def section(self,title):
        ttk.Label(self,text=title,style="Caption.TLabel",font=("Segoe UI",10,"bold"),foreground=C["pine"],padding=(7,4),background=C["stripe"]).pack(fill="x",pady=(12,6))

    def text(self,value,muted=False,pady=0,font=("Segoe UI",10),color=None):
        label=ttk.Label(self,text=value,style="Paper.TLabel",font=font,foreground=color or C["muted" if muted else "ink"],wraplength=280,justify="left")
        label.pack(fill="x",pady=pady)
        self.labels.append(label)
        return label

    def fit(self,event):
        for label in self.labels: label.configure(wraplength=max(40,event.width))
        if hasattr(self,"title"): self.title.configure(wraplength=max(40,event.width-85))
