"""Charte Atelier chaleureux : couleurs, polices, styles et icônes locales."""
import tkinter as tk
from tkinter import ttk

COLORS = {
    "ivory": "#F7F3EA", "sand": "#E7D9C5", "pine": "#315E4F",
    "terracotta": "#C87A50", "ink": "#292D30", "line": "#D8CEBE",
    "muted": "#625B53", "selection": "#DBE5D7", "hover": "#EFE7DA",
    "link": "#884320", "error": "#923C2D", "invalid": "#F3D9CE",
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
    style.configure("TLabel", background=c["ivory"], foreground=c["ink"])
    style.configure("Title.TLabel", font=("Segoe UI", 23, "bold"), foreground=c["pine"])
    style.configure("Heading.TLabel", font=("Segoe UI", 14, "bold"), foreground=c["pine"])
    style.configure("Muted.TLabel", foreground=c["muted"])
    style.configure("Error.TLabel", foreground=c["error"])
    style.configure("TButton", padding=(11, 7), borderwidth=1, relief="flat", bordercolor=c["line"], background=c["ivory"])
    style.map("TButton", background=[("pressed", c["selection"]), ("active", c["hover"])], bordercolor=[("focus", c["pine"])])
    style.configure("Primary.TButton", background=c["pine"], foreground=c["ivory"], bordercolor=c["pine"])
    style.map("Primary.TButton", background=[("active", "#234B3E"), ("pressed", "#234B3E")], foreground=[("active", c["ivory"])])
    style.configure("Chip.TButton", padding=(8, 3), background=c["selection"], foreground=c["pine"])
    style.configure("Open.TButton", background=c["terracotta"], foreground=c["ink"])
    style.configure("TEntry", fieldbackground="#FFFDF8", bordercolor=c["line"], padding=7)
    style.map("TEntry", bordercolor=[("focus", c["pine"])])
    style.configure("TCombobox", fieldbackground=c["ivory"], padding=5, arrowsize=14)
    style.configure("Treeview", background=c["ivory"], fieldbackground=c["ivory"], rowheight=39, borderwidth=0, font=FONT)
    style.map("Treeview", background=[("selected", c["selection"])], foreground=[("selected", c["pine"])], bordercolor=[("focus", c["pine"])])
    style.configure("Treeview.Heading", background=c["sand"], foreground=c["ink"], padding=(7, 9), relief="flat", font=("Segoe UI", 10, "bold"))
    style.map("Treeview.Heading", background=[("active", c["hover"])])
    style.configure("Nav.Treeview", rowheight=34)
    style.configure("TPanedwindow", background=c["line"])
    style.configure("TSeparator", background=c["line"])
    style.configure("Vertical.TScrollbar", background=c["sand"], troughcolor=c["ivory"], arrowsize=12)


def make_icons(root):
    """Petits pictogrammes homogènes, sans fichiers externes ni maquettes."""
    icons = {}
    for kind in ("project", "item", "all", "unfiled"):
        img = tk.PhotoImage(master=root, width=20, height=20)
        color = COLORS["pine"] if kind != "item" else COLORS["terracotta"]
        if kind == "project":
            img.put(color, to=(2, 6, 18, 17))
            img.put(color, to=(2, 3, 9, 7))
            img.put(COLORS["ivory"], to=(4, 8, 16, 15))
        elif kind == "item":
            img.put(color, to=(4, 3, 17, 6))
            img.put(color, to=(14, 3, 17, 16))
            for i in range(11):
                img.put(color, to=(3+i, 14-i, 6+i, 17-i))
        else:
            for y in (4, 9, 14):
                img.put(color, to=(3, y, 17, y+2))
        icons[kind] = img
    return icons
