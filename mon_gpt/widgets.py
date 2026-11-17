"""Petits composants ttk réutilisables dans les écrans d'organisation."""
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from .core import fold
from .atelier import PillButton, rounded
from .theme import COLORS as C


def editor_styles(parent):
    style=ttk.Style(parent)
    for name in ("Editor.TEntry","Editor.TCombobox"):
        style.configure(name,fieldbackground=C["paper"],background=C["paper"],foreground=C["ink"],bordercolor=C["line"],lightcolor=C["paper"],darkcolor=C["paper"],borderwidth=1,relief="flat",padding=(6,4))
        style.map(name,bordercolor=[("focus",C["pine"])],fieldbackground=[("readonly",C["paper"])])


class EditorChip(PillButton):
    def __init__(self,parent,value,category,command):
        self.value,self.category=value,category
        super().__init__(parent,text=value,command=command,tone="chip",height=28)
        self.font=Font(self,font=("Segoe UI",9))

    def height_for(self,width):
        item=self.create_text(0,0,text=self.value,font=self.font,anchor="nw",width=max(10,width-34))
        bounds=self.bbox(item)
        tk.Canvas.delete(self,item)
        return max(27,bounds[3]-bounds[1]+10)

    def draw(self,event=None):
        self.delete("all")
        w,h=self.winfo_width(),self.winfo_height()
        palette=["#DDE4CF","#EDD4C6","#E8DEBF","#D6E2D8"] if self.category else ["#F0E7DA","#E7DDE7","#E4E9DC","#EBDFD8"]
        fill=palette[sum((i+1)*ord(c) for i,c in enumerate(self.value.casefold()))%len(palette)]
        focused=self.focus_get()==self
        rounded(self,1,1,w-1,h-1,11,fill=C["hover"] if self.hovered else fill,outline=C["pine"] if focused else "#C6CBB7" if self.category else "",width=2 if focused else 1)
        self.create_text(8,h/2,text=self.value,font=self.font,fill=C["ink"],width=max(10,w-34),anchor="w")
        self.create_text(w-12,h/2,text="×",font=("Segoe UI",11),fill=C["muted"])


class EditorDelete(PillButton):
    def draw(self,event=None):
        self.delete("all")
        w,h=self.winfo_width(),self.winfo_height()
        rounded(self,1,1,w-1,h-1,8,fill="#F5E3DC" if self.hovered else C["paper"],outline=C["error"] if self.focus_get()==self else "#D9BFB4")
        self.create_text(w/2,h/2,text=self.text,font=self.font,fill=C["error"])


class ChipPicker(ttk.Frame):
    def __init__(self, parent, values, suggestions, changed, category=False):
        super().__init__(parent, style="Paper.TFrame")
        editor_styles(parent)
        self.category=category
        self.values = list(values)
        self.suggestions, self.changed = suggestions, changed
        self.chips = ttk.Frame(self, style="Paper.TFrame",height=1)
        self.chips.pack(fill="x")
        self.chips.pack_propagate(False)
        self.chips.bind("<Configure>",lambda e:self.layout_chips())
        row = ttk.Frame(self, style="Paper.TFrame")
        row.pack(fill="x", pady=(3, 0))
        self.input = ttk.Combobox(row, values=self.known(), width=1,style="Editor.TCombobox",font=("Segoe UI",10))
        self.add_button=PillButton(row, text="+", command=self.add, width=30, height=28)
        self.add_button.pack(side="right", padx=(5, 0))
        self.input.pack(side="left", fill="x", expand=True)
        self.input.bind("<<ComboboxSelected>>", self.add)
        self.input.bind("<Return>", self.add)
        self.input.bind("<KeyRelease>", self.suggest)
        self.hint = ttk.Label(self, style="PaperMuted.TLabel",font=("Segoe UI",8),wraplength=280)
        self.hint.pack(anchor="w")
        self.bind("<Configure>",lambda e:self.hint.configure(wraplength=max(40,e.width)))
        self.redraw()

    def known(self):
        return sorted(set(self.suggestions()), key=fold)

    def suggest(self, event=None):
        value = fold(self.input.get())
        self.input.configure(values=[x for x in self.known() if value in fold(x)])

    def add(self, event=None):
        value = self.input.get().strip()
        if value and "," not in value:
            value = next((known for known in self.known() if fold(known) == fold(value)), value)
            if value not in self.values:
                self.values.append(value)
                self.changed()
            self.input.set("")
            self.redraw()
        elif value:
            self.hint.configure(text="Ajoutez une valeur à la fois, sans virgule.")
        return "break"

    def remove(self, value):
        self.values.remove(value)
        self.changed()
        self.redraw()

    def redraw(self):
        for child in self.chips.winfo_children():
            child.destroy()
        for value in self.values:
            EditorChip(self.chips,value,self.category,command=lambda v=value:(self.remove(v),self.input.focus_set()))
        self.layout_chips()
        self.hint.configure(text="Choisissez une valeur connue ou saisissez-en une nouvelle." if self.known() else "Aucune valeur connue : créez la première ici.")

    def get(self):
        return list(self.values)

    def layout_chips(self):
        width=self.chips.winfo_width()
        if width<40: return
        x,y,row_height=0,0,0
        for chip in self.chips.winfo_children():
            w=min(width,chip.font.measure(chip.value)+34)
            h=chip.height_for(w)
            if x and x+w>width:
                x,y,row_height=0,y+row_height+4,0
            chip.place(x=x,y=y,width=w,height=h)
            x+=w+4
            row_height=max(row_height,h)
        self.chips.configure(height=max(1,y+row_height))
