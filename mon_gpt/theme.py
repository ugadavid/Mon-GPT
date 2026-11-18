"""Charte Atelier chaleureux : couleurs, polices, styles et icônes locales."""
import tkinter as tk
from tkinter import ttk

COLORS = {
    "ivory": "#FAF5F0", "sand": "#F4EBE2", "pine": "#326442",
    "terracotta": "#BE7549", "ink": "#23282A", "line": "#E6DCD1",
    "muted": "#655F58", "selection": "#E8EDD4", "hover": "#F4EBDF",
    "link": "#884320", "error": "#923C2D", "invalid": "#F3D9CE",
    "paper": "#FCF8F4", "tag": "#E4EBDD", "category": "#F5E3D1",
    "inspector_ivory": "#F9F3EA", "inspector_sage": "#F1F4EB",
    "inspector_rule": "#E5E1D6",
    "stripe": "#F8F0E6", "shadow": "#EDE2D8", "leaf": "#789366",
}
FONT = ("Segoe UI", 11)


def apply_theme(root):
    c = COLORS
    root.configure(background=c["ivory"])
    root.option_add("*Menu.background", c["ivory"])
    root.option_add("*Menu.foreground", c["ink"])
    root.option_add("*Menu.activeBackground", c["selection"])
    root.option_add("*Menu.activeForeground", c["pine"])
    root.option_add("*Menu.font", FONT)
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", font=FONT, background=c["ivory"], foreground=c["ink"])
    style.configure("TFrame", background=c["ivory"])
    style.configure("Paper.TFrame", background=c["paper"])
    style.configure("TLabel", background=c["ivory"], foreground=c["ink"])
    style.configure("Title.TLabel", font=("Segoe UI", 23, "bold"), foreground=c["pine"])
    style.configure("Heading.TLabel", font=("Segoe UI", 14, "bold"), foreground=c["pine"])
    style.configure("Muted.TLabel", foreground=c["muted"])
    style.configure("Paper.TLabel", background=c["paper"])
    style.configure("PaperMuted.TLabel", background=c["paper"], foreground=c["muted"], font=("Segoe UI",10))
    style.configure("Caption.TLabel", background=c["paper"], foreground=c["muted"], font=("Segoe UI",9,"bold"))
    style.configure("Inspector.TLabel", background=c["paper"], foreground=c["pine"], font=("Segoe UI",18,"bold"))
    style.configure("WorkTitle.TLabel",background=c["paper"],foreground=c["pine"],font=("Segoe UI",14,"bold"))
    style.configure("Error.TLabel", foreground=c["error"])
    style.configure("TButton", padding=(11, 7), borderwidth=1, relief="flat", bordercolor=c["line"], background=c["ivory"])
    style.map("TButton", background=[("pressed", c["selection"]), ("active", c["hover"])], bordercolor=[("focus", c["pine"])])
    style.configure("Primary.TButton", background=c["pine"], foreground=c["ivory"], bordercolor=c["pine"])
    style.map("Primary.TButton", background=[("active", "#234B3E"), ("pressed", "#234B3E")], foreground=[("active", c["ivory"])])
    style.configure("Chip.TButton", padding=(8, 3), background=c["selection"], foreground=c["pine"])
    style.configure("Open.TButton", background=c["terracotta"], foreground=c["ink"])
    style.configure("TEntry", fieldbackground=c["paper"], bordercolor=c["line"], padding=9, font=("Segoe UI",11))
    style.configure("Quick.TEntry",padding=(10,5),bordercolor=c["line"],foreground=c["muted"])
    style.map("Quick.TEntry",fieldbackground=[("readonly",c["paper"])])
    style.configure("Search.TEntry", background=c["paper"], fieldbackground=c["paper"], borderwidth=0, relief="flat", padding=7, font=("Segoe UI",12))
    style.layout("Search.TEntry",[("Entry.padding",{"sticky":"nswe","children":[("Entry.textarea",{"sticky":"nswe"})]})])
    style.map("TEntry", bordercolor=[("focus", c["pine"])])
    style.configure("TCombobox", fieldbackground=c["ivory"], padding=5, arrowsize=14)
    style.map("TCombobox",fieldbackground=[("readonly",c["paper"])],background=[("readonly",c["paper"])],foreground=[("readonly",c["ink"])])
    style.configure("Treeview", background=c["ivory"], fieldbackground=c["ivory"], rowheight=39, borderwidth=0, font=FONT)
    style.map("Treeview", background=[("selected", c["selection"])], foreground=[("selected", c["pine"])], bordercolor=[("focus", c["pine"])])
    style.configure("Treeview.Heading", background=c["sand"], foreground=c["ink"], padding=(7, 9), relief="flat", font=("Segoe UI", 10, "bold"))
    style.map("Treeview.Heading", background=[("active", c["hover"])])
    style.configure("Nav.Treeview", rowheight=40, background=c["paper"], fieldbackground=c["paper"], borderwidth=0, font=("Segoe UI",11))
    style.map("Nav.Treeview", background=[("selected",c["pine"])], foreground=[("selected",c["paper"])])
    style.layout("Nav.Treeview",[("Treeview.treearea",{"sticky":"nswe"})])
    style.configure("TPanedwindow", background=c["ivory"])
    style.configure("TSeparator", background=c["line"])
    style.configure("Vertical.TScrollbar", background=c["line"], troughcolor=c["paper"], arrowsize=9, borderwidth=0)
    for orientation,sticky in [("Vertical","ns"),("Horizontal","we")]:
        style.layout(orientation+".TScrollbar",[(orientation+".Scrollbar.trough",{"sticky":sticky,"children":[(orientation+".Scrollbar.thumb",{"expand":1,"sticky":"nswe"})]})])
        style.configure(orientation+".TScrollbar",background=c["line"],troughcolor=c["paper"],bordercolor=c["paper"],lightcolor=c["line"],darkcolor=c["line"],arrowsize=8,borderwidth=0)


def make_icons(root):
    """Badges vectoriels pixellisés localement ; aucun fichier tiers."""
    icons = {}
    for kind in ("project", "item", "all", "unfiled"):
        img = tk.PhotoImage(master=root, width=32, height=32)
        bg = "#F2E4CF" if kind=="project" else "#E3EBDD"
        for y in range(32):
            for x in range(32):
                dx,dy=max(7-x,0,x-24),max(7-y,0,y-24)
                if dx*dx+dy*dy<=49:
                    img.put(bg,(x,y))
        color = COLORS["link"] if kind=="project" else COLORS["pine"]
        def rect(x1,y1,x2,y2,c=color): img.put(c,to=(x1,y1,x2,y2))
        if kind=="project":
            rect(6,11,26,25); rect(6,7,15,12); rect(8,13,24,23,bg)
        elif kind=="item":
            rect(6,7,26,23); rect(8,9,24,21,bg); rect(9,22,12,26)
            rect(11,12,21,14); rect(11,16,18,18)
        elif kind=="all":
            for y in (8,14,20): rect(7,y,25,y+3)
        else:
            rect(6,18,26,25); rect(8,15,10,20); rect(22,15,24,20); rect(13,20,19,22,bg)
        icons[kind]=img
    return icons
