"""Vue Liste : retrouver, ouvrir et classer ; édition détaillée volontaire."""
import os
import time
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.font import Font
from datetime import datetime
from .core import fold, now
from .chatgpt import parse_url
from .details import DetailEditor
from .theme import COLORS, FONT, apply_theme, make_icons
from . import ui_state, __version__


class App(DetailEditor):
    def __init__(self, root, store, cat, adapter, opener=None):
        self.root, self.store, self.cat, self.adapter = root, store, cat, adapter
        self.opener = opener
        self.scope, self.current, self.dirty = "all", None, False
        self.editing, self.inspector_visible = False, False
        self.draft, self.inline, self.drag = None, None, None
        self.sort_column, self.sort_reverse = "title", False
        self.last_open = (None, 0)
        self.search_timer = None
        self.preferences_path = store.directory / "interface.json"
        preferences, warning = ui_state.load(self.preferences_path)
        apply_theme(root)
        self.icons = make_icons(root)
        self.font = Font(root, font=FONT)
        root.title(f"Mon GPT<3 — {__version__}" + (" · RECETTE · ouvertures simulées" if opener else ""))
        root.geometry(preferences.get("geometry", "1360x820"))
        root.minsize(1000, 680)
        self.status = tk.StringVar(value=warning or "Prêt · un clic sur un titre ouvre le fil ; ailleurs, sélectionnez.")
        self.query, self.tag, self.category = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.sort = tk.StringVar(value="Manuel")
        self.build_menus()
        self.build_shell()
        self.bind_keys()
        self.refresh_tree()
        self.refresh_results()
        if preferences.get("inspector"):
            self.toggle_inspector()
        root.protocol("WM_DELETE_WINDOW", self.close)

    def build_menus(self):
        bar = tk.Menu(self.root, tearoff=False)
        file = tk.Menu(bar, tearoff=False)
        file.add_command(label="Sauvegarder le catalogue…", command=self.export)
        file.add_command(label="Restaurer le catalogue…", command=self.restore)
        file.add_separator()
        file.add_command(label="Dossier de données", command=self.open_data)
        file.add_command(label="Quitter", command=self.close)
        bar.add_cascade(label="Fichier", menu=file)
        edit = tk.Menu(bar, tearoff=False)
        edit.add_command(label="Nouveau fil", accelerator="Ctrl+N", command=lambda: self.new("item"))
        edit.add_command(label="Nouveau projet", accelerator="Ctrl+Maj+P", command=lambda: self.new("project"))
        edit.add_separator()
        edit.add_command(label="Renommer", accelerator="F2", command=self.rename_selected)
        edit.add_command(label="Modifier la fiche", command=lambda: self.edit_selected())
        edit.add_command(label="Enregistrer la fiche", accelerator="Ctrl+S", command=self.save_record)
        bar.add_cascade(label="Édition", menu=edit)
        view = tk.Menu(bar, tearoff=False)
        view.add_command(label="Liste · vue actuelle", state="disabled")
        view.add_command(label="Afficher / masquer l'inspecteur", command=self.toggle_inspector)
        view.add_command(label="Rechercher", accelerator="Ctrl+K", command=self.focus_search)
        view.add_command(label="Retirer les filtres", command=self.clear_filters)
        view.add_separator()
        view.add_command(label="Fenêtre compacte · 1000 × 680", command=lambda: self.resize(1000, 680))
        view.add_command(label="Fenêtre confortable · 1360 × 820", command=lambda: self.resize(1360, 820))
        bar.add_cascade(label="Affichage", menu=view)
        help_menu = tk.Menu(bar, tearoff=False)
        help_menu.add_command(label="Gestes et raccourcis", command=self.help)
        help_menu.add_command(label="À propos de Mon GPT<3", command=lambda: messagebox.showinfo("Mon GPT<3", f"Version {__version__} · Atelier chaleureux\nCatalogue local, aucune modification dans ChatGPT.\nDétaillée, Mosaïque et couvertures : prévues, non livrées.", parent=self.root))
        bar.add_cascade(label="Aide", menu=help_menu)
        self.root.configure(menu=bar)
        self.plus = tk.Menu(self.root, tearoff=False)
        self.plus.add_command(label="Nouveau fil", accelerator="Ctrl+N", command=lambda: self.new("item"))
        self.plus.add_command(label="Nouveau projet", accelerator="Ctrl+Maj+P", command=lambda: self.new("project"))

    def build_shell(self):
        header = ttk.Frame(self.root, padding=(22, 14))
        header.pack(fill="x")
        ttk.Label(header, text="♡", foreground=COLORS["terracotta"], font=("Segoe UI", 27)).pack(side="left", padx=(0, 8))
        ttk.Label(header, text="Mon GPT<3", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="  Votre organisation, en local", style="Muted.TLabel").pack(side="left")
        ttk.Button(header, text="Inspecteur", command=self.toggle_inspector).pack(side="right")
        ttk.Button(header, text="+ Nouveau ▾", style="Primary.TButton", command=lambda: self.plus.tk_popup(header.winfo_rootx()+header.winfo_width()-260, header.winfo_rooty()+48)).pack(side="right", padx=8)
        search_area = ttk.Frame(self.root, padding=(22, 0, 22, 10))
        search_area.pack(fill="x")
        line = ttk.Frame(search_area)
        line.pack(fill="x")
        ttk.Label(line, text="Rechercher", style="Heading.TLabel").pack(side="left", padx=(0, 12))
        self.search_entry = ttk.Entry(line, textvariable=self.query, font=("Segoe UI", 12))
        self.search_entry.pack(side="left", expand=True, fill="x")
        self.search_entry.bind("<Return>", self.search_enter)
        self.search_entry.bind("<KeyRelease>", self.search_changed)
        self.search_entry.bind("<Down>", self.focus_suggestions)
        ttk.Button(line, text="Filtres ▾", command=lambda: self.show_suggestions(True)).pack(side="left", padx=6)
        ttk.Button(line, text="Effacer", command=self.clear_filters).pack(side="left")
        self.chips = ttk.Frame(search_area)
        self.chips.pack(fill="x", pady=(7, 0))
        self.suggestion_box = ttk.Frame(search_area)
        self.suggestions = tk.Listbox(self.suggestion_box, height=5, font=FONT, background=COLORS["ivory"], foreground=COLORS["ink"], selectbackground=COLORS["selection"], selectforeground=COLORS["pine"], relief="solid", borderwidth=1, exportselection=False)
        self.suggestions.pack(fill="x")
        self.suggestions.bind("<ButtonRelease-1>", self.choose_suggestion)
        self.suggestions.bind("<Return>", self.choose_suggestion)
        self.suggestions.bind("<Escape>", lambda e: self.hide_suggestions())
        self.panes = ttk.Panedwindow(self.root, orient="horizontal", height=400)
        self.panes.pack(fill="both", expand=True, padx=18)
        self.left, self.middle, self.right = (ttk.Frame(self.panes, padding=8) for _ in range(3))
        self.panes.add(self.left, weight=0)
        self.panes.add(self.middle, weight=1)
        self.left.configure(width=250)
        ttk.Label(self.left, text="Mon organisation", style="Heading.TLabel").pack(anchor="w", pady=(2, 10))
        self.sorting = ttk.Combobox(self.left, textvariable=self.sort, values=["Manuel", "Alphabétique français"], state="readonly", width=22)
        self.sorting.pack(fill="x", pady=(0, 8))
        self.sorting.bind("<<ComboboxSelected>>", lambda e: self.refresh_tree())
        tree_box = ttk.Frame(self.left)
        tree_box.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_box, show="tree", selectmode="browse", style="Nav.Treeview", height=1)
        self.tree.column("#0", width=238, minwidth=150)
        sb = ttk.Scrollbar(tree_box, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", expand=True, fill="both")
        self.tree.bind("<<TreeviewSelect>>", self.select_scope)
        for tag, color in [("drop", COLORS["selection"]), ("forbidden", COLORS["invalid"])]:
            self.tree.tag_configure(tag, background=color)
        ttk.Separator(self.left).pack(fill="x", pady=8)
        ttk.Label(self.left, text="Déposez un projet dans l'arbre.\nPour la racine : Tous les fils.\nClic droit : classer et organiser.", style="Muted.TLabel", wraplength=235).pack(anchor="w", pady=4)
        titlebar = ttk.Frame(self.middle)
        titlebar.pack(fill="x", pady=(2, 10))
        self.results_label = ttk.Label(titlebar, text="Tous les fils", style="Heading.TLabel")
        self.results_label.pack(side="left", fill="x", expand=True)
        ttk.Label(titlebar, text="≡ Liste", foreground=COLORS["pine"]).pack(side="right")
        self.work = ttk.Frame(self.middle)
        self.work.pack(fill="x")
        self.work_error = tk.StringVar()
        self.work_content = ttk.Frame(self.work)
        self.work_content.pack(fill="x")
        ttk.Label(self.work, textvariable=self.work_error, style="Error.TLabel", wraplength=650).pack(anchor="w")
        box = ttk.Frame(self.middle)
        self.results_box = box
        box.pack(fill="both", expand=True)
        self.results = ttk.Treeview(box, columns=("title", "context", "tags", "modified"), show="tree headings", selectmode="browse", height=1)
        self.results.heading("#0", text="↗")
        self.results.column("#0", width=37, minwidth=37, stretch=False)
        for key, label, width in [("title", "Titre · ouvrir d'un clic", 390), ("context", "Emplacements", 150), ("tags", "Tags / catégories", 130), ("modified", "Modifié", 100)]:
            self.results.heading(key, text=label, command=lambda k=key: self.sort_results(k))
            self.results.column(key, width=width, minwidth=230 if key == "title" else 80, stretch=(key == "title"))
        sb = ttk.Scrollbar(box, orient="vertical", command=self.results.yview)
        sb.pack(side="right", fill="y")
        self.results.configure(yscrollcommand=sb.set)
        self.results.pack(side="left", fill="both", expand=True)
        horizontal = ttk.Scrollbar(self.middle, orient="horizontal", command=self.results.xview)
        self.horizontal_scroll = horizontal
        horizontal.pack(fill="x")
        self.results.configure(xscrollcommand=horizontal.set)
        self.results.bind("<<TreeviewSelect>>", self.select_record)
        self.results.bind("<Return>", self.result_enter)
        self.results.bind("<Double-Button-1>", self.result_double)
        self.results.bind("<Motion>", self.hover_result)
        self.empty = ttk.Label(self.middle, text="", style="Muted.TLabel", padding=(10, 8), wraplength=650)
        self.empty.pack(anchor="w")
        ttk.Label(self.middle, text="Titre ou ↗ : ouvrir  ·  Autre colonne : sélectionner  ·  Entrée : ouvrir  ·  F2 : renommer", style="Muted.TLabel", wraplength=900).pack(anchor="w", pady=(3, 5))
        self.canvas = tk.Canvas(self.right, highlightthickness=0, background=COLORS["ivory"])
        sb = ttk.Scrollbar(self.right, orient="vertical", command=self.canvas.yview)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=sb.set)
        self.editor = ttk.Frame(self.canvas, padding=12)
        window = self.canvas.create_window(0, 0, window=self.editor, anchor="nw")
        self.editor.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(window, width=e.width))
        for widget in (self.tree, self.results):
            for button in (1, 3):
                widget.bind(f"<ButtonPress-{button}>", lambda e, w=widget, b=button: self.drag_press(e, w, b), add=True)
                widget.bind(f"<B{button}-Motion>", self.drag_motion, add=True)
                widget.bind(f"<ButtonRelease-{button}>", lambda e, w=widget, b=button: self.drag_release(e, w, b), add=True)
        footer = ttk.Frame(self.root, padding=(22, 8))
        footer.pack(fill="x")
        ttk.Label(footer, textvariable=self.status, style="Muted.TLabel", wraplength=1350).pack(anchor="w")
        self.data_label = ttk.Label(footer, text="Catalogue local · " + str(self.store.path), style="Muted.TLabel", cursor="hand2")
        self.data_label.pack(anchor="w", pady=(4, 0))
        self.data_label.bind("<Button-1>", lambda e: self.open_data())
        self.work.pack_forget()
        self.root.after_idle(lambda: self.panes.sashpos(0, 265))

    def bind_keys(self):
        for key, action in [("<Control-k>", self.focus_search), ("<Control-n>", lambda: self.new("item")), ("<Control-Shift-P>", lambda: self.new("project")), ("<Control-s>", self.save_record), ("<F2>", self.rename_selected), ("<Escape>", self.escape)]:
            self.root.bind(key, lambda e, fn=action: (fn(), "break")[1])
        self.tree.bind("<Alt-Up>", lambda e: (self.reorder(-1), "break")[1])
        self.tree.bind("<Alt-Down>", lambda e: (self.reorder(1), "break")[1])
        self.tree.bind("<Menu>", lambda e: self.context_menu(self.scope, self.tree.winfo_rootx()+40, self.tree.winfo_rooty()+80))
        self.results.bind("<Menu>", lambda e: self.context_menu(self.current, self.results.winfo_rootx()+80, self.results.winfo_rooty()+80))

    def open_data(self):
        self.safe(lambda: os.startfile(self.store.directory))

    def resize(self, width, height):
        self.root.state("normal")
        self.root.geometry(f"{width}x{height}")

    def help(self):
        messagebox.showinfo("Gestes et raccourcis", "Titre ou icône ↗ : ouvrir le fil. Autre colonne : sélectionner.\nDouble-clic sur une ligne / Entrée dans la liste : ouvrir.\nCtrl+K : rechercher · Ctrl+N : nouveau fil\nCtrl+Maj+P : nouveau projet · F2 : renommer\nCtrl+S : enregistrer la fiche · Échap : annuler l'édition intégrée\nAlt+↑/↓ dans l'arbre : ordre manuel\nClic droit / touche Menu : actions de classement\nGlisser gauche : déplacer · Glisser droit : choix à la dépose\nLes autres rattachements sont préservés.\nFichier : sauvegarde/restauration du catalogue.", parent=self.root)

    def focus_search(self):
        self.search_entry.focus_set()
        self.search_entry.selection_range(0, "end")

    def search_enter(self, event=None):
        self.refresh_results()
        self.hide_suggestions()
        return "break"

    def search_changed(self, event=None):
        if event and event.keysym in ("Return", "Escape", "Down", "Up"):
            return
        if self.search_timer:
            self.root.after_cancel(self.search_timer)
        self.search_timer = self.root.after(180, self.perform_search)

    def perform_search(self):
        self.search_timer = None
        self.refresh_results()
        if self.query.get().strip():
            self.show_suggestions()
        else:
            self.hide_suggestions()

    def show_suggestions(self, all_values=False):
        needle = "" if all_values else fold(self.query.get().strip())
        choices = [("global", "", "Partout · tous les projets")]
        for key, label in [("tags", "Tag"), ("categories", "Catégorie")]:
            values = sorted({v for r in self.cat.records.values() for v in getattr(r, key)}, key=fold)
            choices.extend((key, v, f"{label} · {v}") for v in values if needle in fold(v))
        choices.extend(("project", r.id, "Projet · " + self.project_label(r.id)) for r in self.cat.records.values() if r.kind == "project" and needle in fold(self.project_label(r.id)))
        self.suggestion_values = choices
        self.suggestions.delete(0, "end")
        for _, _, label in choices:
            self.suggestions.insert("end", label)
        if len(choices) == 1:
            self.suggestions.insert("end", "Aucun tag/catégorie/projet correspondant. Les titres restent recherchés.")
        self.suggestions.configure(height=min(6, max(2, len(choices))))
        self.suggestion_box.pack(fill="x", pady=(5, 0))

    def hide_suggestions(self):
        self.suggestion_box.pack_forget()
        return "break"

    def focus_suggestions(self, event=None):
        self.show_suggestions()
        self.suggestions.focus_set()
        self.suggestions.selection_set(0)
        return "break"

    def choose_suggestion(self, event=None):
        selected = self.suggestions.curselection()
        if not selected or selected[0] >= len(self.suggestion_values):
            return "break"
        key, value, _ = self.suggestion_values[selected[0]]
        if key in ("global", "project"):
            if not self.can_leave():
                return "break"
            self.scope = value if key == "project" else "all"
            self.refresh_tree()
        else:
            (self.tag if key == "tags" else self.category).set(value)
            self.query.set("")
        self.refresh_results()
        self.hide_suggestions()
        self.search_entry.focus_set()
        return "break"

    def refresh_chips(self):
        for child in self.chips.winfo_children():
            child.destroy()
        scope_text = "Projet : " + self.cat.records[self.scope].title[:36] + " · descendants ×" if self.scope in self.cat.records else ("À classer ×" if self.scope == "unfiled" else "Partout")
        ttk.Button(self.chips, text=scope_text, style="Chip.TButton", command=self.global_scope).pack(side="left", padx=(0, 5))
        for var, label in [(self.tag, "Tag"), (self.category, "Catégorie")]:
            if var.get():
                ttk.Button(self.chips, text=f"{label} : {var.get()} ×", style="Chip.TButton", command=lambda v=var: self.remove_filter(v)).pack(side="left", padx=(0, 5))
        if not self.tag.get() and not self.category.get():
            ttk.Label(self.chips, text="Titres, notes, tags, catégories, informations personnalisées · Ctrl+K", style="Muted.TLabel").pack(side="left")

    def global_scope(self):
        if self.can_leave():
            self.scope = "all"
            self.refresh_tree()
            self.refresh_results()

    def remove_filter(self, var):
        var.set("")
        self.refresh_results()

    def clear_filters(self):
        for var in (self.query, self.tag, self.category):
            var.set("")
        self.hide_suggestions()
        self.refresh_results()

    def refresh_tree(self):
        opened = {p for p in self.cat.records if self.tree.exists(p) and self.tree.item(p, "open")}
        self.tree.delete(*self.tree.get_children())
        self.tree.insert("", "end", iid="all", text="Tous les fils", image=self.icons["all"])
        self.tree.insert("", "end", iid="unfiled", text="À classer", image=self.icons["unfiled"])
        pending = [(r, "") for r in reversed(self.cat.children(None, self.sort.get() != "Manuel"))]
        while pending:
            r, parent = pending.pop()
            self.tree.insert(parent, "end", iid=r.id, text=r.title, image=self.icons["project"], open=(r.id in opened or not opened))
            pending.extend((c, r.id) for c in reversed(self.cat.children(r.id, self.sort.get() != "Manuel")))
        if not self.tree.exists(self.scope):
            self.scope = "all"
        self.tree.selection_set(self.scope)

    def select_scope(self, event=None):
        selection = self.tree.selection()
        if not selection or selection[0].startswith("__") or selection[0] == self.scope:
            return
        if not self.can_leave():
            self.tree.selection_set(self.scope)
            return
        self.cancel_inline()
        self.scope = selection[0]
        self.refresh_results()
        self.select_identity(self.scope if self.scope in self.cat.records else None, checked=True)

    def refresh_results(self):
        selected = self.current
        self.results.delete(*self.results.get_children())
        scope = self.scope if self.scope in self.cat.records else None
        rows = self.cat.search(self.query.get().strip(), scope, self.tag.get().strip(), self.category.get().strip(), self.scope == "unfiled")
        if not scope and not self.query.get().strip() and not self.tag.get() and not self.category.get():
            rows = [r for r in rows if r.kind == "item"]
        def values(r):
            context = self.project_label(r.parent) if r.kind == "project" and r.parent else (" · ".join(self.project_label(p) for p in r.projects) if r.kind == "item" else "À la racine")
            if r.kind == "item" and not r.projects:
                context = "À classer"
            return {"title": r.title, "context": context, "tags": " · ".join(r.tags + r.categories), "modified": r.modified}
        rows.sort(key=lambda r: fold(values(r)[self.sort_column]), reverse=self.sort_reverse)
        for r in rows:
            v = values(r)
            self.results.insert("", "end", iid=r.id, image=self.icons[r.kind], values=(r.title, v["context"], v["tags"], datetime.fromisoformat(r.modified).strftime("%d/%m/%Y")))
        if selected and self.results.exists(selected):
            self.results.selection_set(selected)
            self.results.focus(selected)
        self.results_label.configure(text=f"{len(rows)} résultat(s) · " + ("Projet et descendants" if scope else ("À classer" if self.scope == "unfiled" else "Tous les fils")))
        self.empty.configure(text="" if rows else "Aucun résultat. Modifiez la recherche ou les filtres, ou créez votre premier fil avec + Nouveau.")
        self.refresh_chips()

    def sort_results(self, column):
        self.sort_reverse = not self.sort_reverse if self.sort_column == column else False
        self.sort_column = column
        self.refresh_results()

    def select_record(self, event=None):
        selection = self.results.selection()
        if selection and selection[0] != self.current:
            if not self.select_identity(selection[0]):
                if self.current and self.results.exists(self.current):
                    self.results.selection_set(self.current)

    def select_identity(self, identity, checked=False):
        if identity == self.current:
            return True
        if not checked and not self.can_leave():
            return False
        self.current, self.dirty, self.editing = identity, False, False
        if self.inspector_visible:
            self.show_summary(identity, checked=True)
        return True

    def ensure_inspector(self):
        if not self.inspector_visible:
            self.panes.add(self.right, weight=0)
            self.inspector_visible = True
            self.root.update_idletasks()
            self.panes.sashpos(1, max(550, self.panes.winfo_width()-370))

    def toggle_inspector(self):
        if self.inspector_visible:
            if not self.can_leave():
                return
            self.panes.forget(self.right)
            self.inspector_visible, self.editing = False, False
        else:
            self.ensure_inspector()
            self.show_summary(self.current, checked=True)

    def show_summary(self, identity, checked=False):
        if not checked and not self.can_leave():
            return
        self.current, self.dirty, self.editing = identity, False, False
        for child in self.editor.winfo_children():
            child.destroy()
        ttk.Button(self.editor, text="Replier l'inspecteur →", command=self.toggle_inspector).pack(anchor="e")
        if identity not in self.cat.records:
            ttk.Label(self.editor, text="Un aperçu, quand vous voulez", style="Heading.TLabel", wraplength=290).pack(anchor="w", pady=14)
            ttk.Label(self.editor, text="Sélectionnez une ligne par son emplacement. Ouvrez un fil directement par son titre.", wraplength=290).pack(anchor="w")
            return
        r = self.cat.records[identity]
        ttk.Label(self.editor, text="Projet" if r.kind == "project" else "Discussion", style="Muted.TLabel").pack(anchor="w", pady=(18, 4))
        ttk.Label(self.editor, text=r.title, style="Heading.TLabel", wraplength=300).pack(anchor="w", pady=(0, 15))
        if r.kind == "item":
            ttk.Button(self.editor, text="↗ Ouvrir le fil", style="Open.TButton", command=lambda: self.open_thread(identity)).pack(fill="x")
            ttk.Button(self.editor, text="Copier le lien", command=lambda: self.copy_link(identity)).pack(fill="x", pady=6)
        ttk.Button(self.editor, text="Modifier les détails", command=lambda: self.show_record(identity)).pack(fill="x", pady=8)
        for label, value in [("Résumé" if r.kind == "item" else "Description", r.description), ("Emplacements", "\n".join(self.project_label(p) for p in r.projects) if r.kind == "item" else (self.project_label(r.parent) if r.parent else "À la racine")), ("Tags", " · ".join(r.tags)), ("Catégories", " · ".join(r.categories)), ("Notes", r.notes[:250] + ("…" if len(r.notes)>250 else ""))]:
            ttk.Separator(self.editor).pack(fill="x", pady=10)
            ttk.Label(self.editor, text=label, style="Muted.TLabel").pack(anchor="w")
            ttk.Label(self.editor, text=value or "Non renseigné", wraplength=300, justify="left").pack(anchor="w", pady=(3, 0))
        self.canvas.yview_moveto(0)

    def show_record(self, identity):
        """Entrée explicite de l'édition, également conservée pour les tests MG-001."""
        self.ensure_inspector()
        self.editing = True
        self.render_editor(identity)

    def edit_selected(self, identity=None):
        identity = identity or self.current
        if identity in self.cat.records and self.can_leave():
            self.show_record(identity)

    def save_record(self):
        if not self.editing or self.current not in self.cat.records:
            return False
        return super().save_record()

    def open_thread(self, identity=None):
        identity = identity or self.current
        if identity not in self.cat.records or self.cat.records[identity].kind != "item":
            return False
        def action():
            if identity not in self.adapter.conversations:
                raise ValueError("Ce fil n'a pas de lien ChatGPT valide. Modifiez sa fiche.")
            _, url = parse_url(self.adapter.conversations[identity].url)
            if not (self.opener or webbrowser.open)(url, new=2):
                raise ValueError("Impossible d'ouvrir le navigateur par défaut.")
            self.status.set(("RECETTE · ouverture simulée : " if self.opener else "Fil ouvert : ") + self.cat.records[identity].title)
            return True
        return self.safe(action)

    def copy_link(self, identity):
        def action():
            _, url = parse_url(self.adapter.conversations[identity].url)
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            self.status.set("Lien copié.")
        self.safe(action)

    def title_hit(self, event, identity):
        if self.cat.records[identity].kind != "item":
            return False
        column = self.results.identify_column(event.x)
        if column == "#0":
            return True
        if column == "#1":
            x, y, width, height = self.results.bbox(identity, "title")
            return event.x <= x + min(width, self.font.measure(self.cat.records[identity].title)+14)
        return False

    def open_click(self, identity):
        previous, timestamp = self.last_open
        if previous == identity and time.monotonic()-timestamp < 0.5:
            return
        self.last_open = (identity, time.monotonic())
        self.open_thread(identity)

    def result_enter(self, event=None):
        if self.root.focus_get() == self.results:
            identity = self.results.focus()
            if identity in self.cat.records:
                if self.cat.records[identity].kind == "project":
                    self.tree.selection_set(identity)
                    self.tree.see(identity)
                else:
                    self.open_thread(identity)
        return "break"

    def result_double(self, event):
        identity = self.results.identify_row(event.y)
        if identity in self.cat.records:
            if self.cat.records[identity].kind == "item":
                self.open_click(identity)
            else:
                self.tree.selection_set(identity)
                self.tree.item(identity, open=True)
        if self.drag:
            self.drag["double"] = True
        return "break"

    def hover_result(self, event):
        identity = self.results.identify_row(event.y)
        self.results.configure(cursor="hand2" if identity in self.cat.records and self.title_hit(event, identity) else "")

    def clear_work(self):
        for child in self.work_content.winfo_children():
            child.destroy()
        self.work_error.set("")
        self.draft = None
        self.work.pack_forget()

    def new(self, kind):
        if not self.can_leave():
            return
        self.cancel_inline()
        self.clear_work()
        parent = self.scope if self.scope in self.cat.records else None
        if kind == "project":
            host = parent or ""
            if parent:
                self.tree.item(parent, open=True)
            self.tree.insert(host, "end", iid="__draft__", text="", image=self.icons["project"])
            self.tree.see("__draft__")
            self.root.update_idletasks()
            self.inline = ttk.Entry(self.tree)
            x, y, width, height = self.tree.bbox("__draft__")
            self.inline.place(x=x+24, y=y, width=max(150, width-25), height=height)
            self.inline.focus_set()
            self.draft = {"kind": "project", "parent": parent}
            self.inline.bind("<Return>", self.commit_inline)
            self.inline.bind("<Escape>", lambda e: self.cancel_inline())
            self.status.set("Nouveau projet · Entrée : créer · Échap : annuler. Aucune image à choisir.")
            return
        self.draft = {"kind": "item", "parent": parent}
        self.work.pack(fill="x", before=self.results_box)
        ttk.Label(self.work_content, text="Nouveau fil · " + (self.project_label(parent) if parent else "À classer"), style="Heading.TLabel").pack(anchor="w", pady=4)
        self.new_title = ttk.Entry(self.work_content)
        self.new_title.pack(fill="x", pady=3)
        self.new_title.insert(0, "")
        ttk.Label(self.work_content, text="Titre ci-dessus · Lien ChatGPT ci-dessous", style="Muted.TLabel").pack(anchor="w")
        self.new_url = ttk.Entry(self.work_content)
        self.new_url.pack(fill="x", pady=3)
        row = ttk.Frame(self.work_content)
        row.pack(fill="x", pady=4)
        ttk.Button(row, text="Ajouter le fil", style="Primary.TButton", command=self.submit_item).pack(side="left")
        ttk.Button(row, text="Annuler · Échap", command=self.clear_work).pack(side="left", padx=5)
        for entry in (self.new_title, self.new_url):
            entry.bind("<Return>", self.submit_item)
        self.new_title.focus_set()

    def submit_item(self, event=None, use_existing=False, expected_identity=None):
        if not self.draft or self.draft["kind"] != "item":
            return "break"
        try:
            identity, _ = parse_url(self.new_url.get())
            if expected_identity is not None and identity != expected_identity:
                raise ValueError("Le lien a changé. Utilisez Ajouter le fil pour vérifier cette nouvelle URL.")
            parent = self.draft["parent"]
            existing = next((c for c in self.adapter.conversations.values() if c.conversation_id == identity), None)
            if existing and not use_existing:
                self.work_error.set("Ce fil existe déjà. Son titre et ses notes seront conservés.")
                if not self.draft.get("duplicate_button"):
                    button = ttk.Button(self.work_content, text="Afficher la fiche existante" + (" et rattacher ici" if parent else ""))
                    button.pack(anchor="w", pady=4)
                    self.draft["duplicate_button"] = button
                self.draft["duplicate_button"].configure(command=lambda expected=identity: self.submit_item(use_existing=True, expected_identity=expected))
                return "break"
            def mutate():
                r, _ = self.adapter.ingest(self.new_title.get(), self.new_url.get())
                if parent:
                    self.cat.attach(r.id, [*r.projects, parent])
                return r
            r = self.transaction(mutate)
            self.clear_work()
            self.refresh_results()
            self.select_identity(r.id, checked=True)
            if self.results.exists(r.id):
                self.results.selection_set(r.id)
                self.results.see(r.id)
            self.status.set("Fil existant retrouvé, informations conservées." if existing else "Fil ajouté dans le catalogue local.")
        except (ValueError, OSError) as exc:
            self.work_error.set(str(exc))
        return "break"

    def cancel_inline(self):
        if self.inline is not None:
            self.inline.destroy()
            self.inline = None
        if self.tree.exists("__draft__"):
            self.tree.delete("__draft__")
        if self.draft and self.draft.get("kind") in ("project", "rename"):
            self.draft = None
        return "break"

    def commit_inline(self, event=None):
        if not self.inline or not self.draft:
            return "break"
        title = self.inline.get().strip()
        try:
            if not title:
                raise ValueError("Le nom est obligatoire.")
            draft = self.draft
            def mutate():
                if draft["kind"] == "project":
                    return self.cat.add(title, "project", draft["parent"])
                r = self.cat.records[draft["id"]]
                r.title, r.modified = title, now()
                return r
            r = self.transaction(mutate)
            self.cancel_inline()
            self.refresh_tree()
            self.refresh_results()
            self.select_identity(r.id, checked=True)
            if r.kind == "project":
                self.tree.selection_set(r.id)
                self.tree.see(r.id)
            self.status.set("Projet créé." if draft["kind"] == "project" else "Nom local modifié.")
        except (ValueError, OSError) as exc:
            self.status.set(str(exc) + " · Corrigez ou appuyez sur Échap.")
        return "break"

    def rename_selected(self, identity=None):
        identity = identity or (self.scope if self.root.focus_get() == self.tree else self.current)
        if identity not in self.cat.records or not self.can_leave():
            return
        self.cancel_inline()
        self.clear_work()
        widget = self.tree if self.cat.records[identity].kind == "project" else self.results
        if not widget.exists(identity):
            return
        widget.see(identity)
        self.root.update_idletasks()
        bbox = widget.bbox(identity, "#0" if widget == self.tree else "title")
        if not bbox:
            return
        x, y, width, height = bbox
        self.inline = ttk.Entry(widget)
        self.inline.place(x=x+(24 if widget == self.tree else 0), y=y, width=max(140, width-24), height=height)
        self.inline.insert(0, self.cat.records[identity].title)
        self.inline.selection_range(0, "end")
        self.inline.focus_set()
        self.draft = {"kind": "rename", "id": identity}
        self.inline.bind("<Return>", self.commit_inline)
        self.inline.bind("<Escape>", lambda e: self.cancel_inline())

    def escape(self):
        if self.drag:
            self.clear_drop()
            self.drag = None
        if self.inline:
            self.cancel_inline()
            self.status.set("Édition intégrée annulée.")
        elif self.draft:
            self.clear_work()
            self.status.set("Action intégrée annulée.")
        elif self.suggestion_box.winfo_manager():
            self.hide_suggestions()
        elif self.inspector_visible:
            self.toggle_inspector()

    def reorder(self, step, identity=None):
        identity = identity or self.scope
        if identity not in self.cat.records or not self.can_leave():
            return
        if self.sort.get() != "Manuel":
            self.status.set("Choisissez le tri Manuel pour ranger les projets frères.")
            return
        def action():
            self.transaction(lambda: self.cat.reorder(identity, step))
            self.refresh_tree()
        self.safe(action)

    def with_record(self, identity, action):
        if self.can_leave():
            self.select_identity(identity, checked=True)
            action()

    def context_menu(self, identity, x, y):
        menu = tk.Menu(self.root, tearoff=False)
        r = self.cat.records.get(identity)
        if r and r.kind == "item":
            menu.add_command(label="↗ Ouvrir le fil", command=lambda: self.open_thread(identity))
            menu.add_command(label="Copier le lien", command=lambda: self.copy_link(identity))
        else:
            menu.add_command(label="Nouveau projet ici", command=lambda: self.new_at(identity, "project"))
            menu.add_command(label="Nouveau fil ici", command=lambda: self.new_at(identity, "item"))
        if r:
            menu.add_separator()
            menu.add_command(label="Renommer", accelerator="F2", command=lambda: self.rename_selected(identity))
            menu.add_command(label="Modifier les détails", command=lambda: self.edit_selected(identity))
            menu.add_command(label="Déplacer…", command=lambda: self.transfer_panel(identity, "move"))
            if r.kind == "item":
                menu.add_command(label="Ajouter un rattachement…", command=lambda: self.transfer_panel(identity, "add"))
                if r.projects:
                    menu.add_command(label="Retirer un rattachement…", command=lambda: self.transfer_panel(identity, "remove"))
            else:
                menu.add_command(label="Monter", accelerator="Alt+↑", command=lambda: self.reorder(-1, identity))
                menu.add_command(label="Descendre", accelerator="Alt+↓", command=lambda: self.reorder(1, identity))
            menu.add_separator()
            menu.add_command(label="Supprimer…", command=lambda: self.with_record(identity, self.delete))
        self.active_menu = menu
        menu.tk_popup(x, y)
        return "break"

    def new_at(self, identity, kind):
        if not self.can_leave():
            return
        self.scope = identity if identity in self.cat.records else "all"
        self.refresh_tree()
        self.refresh_results()
        self.new(kind)

    def transfer(self, identity, destination, mode, source=None):
        """Orchestration UI : un lien explicite déplacé, tous les autres conservés."""
        r = self.cat.records[identity]
        if r.kind == "project":
            if mode != "move":
                raise ValueError("Un projet a un seul parent et ne peut pas être copié.")
            return self.cat.move(identity, destination)
        if mode not in ("move", "add", "remove"):
            raise ValueError("Action de classement inconnue.")
        projects = list(r.projects)
        if mode in ("move", "remove"):
            if source is None and projects:
                raise ValueError("Choisissez explicitement le rattachement à modifier.")
            if source is not None:
                if source not in projects:
                    raise ValueError("Ce rattachement n'existe plus.")
                projects.remove(source)
        if mode != "remove":
            if destination not in self.cat.records or self.cat.records[destination].kind != "project":
                raise ValueError("Choisissez un projet destination.")
            projects.append(destination)
        self.cat.attach(identity, projects)

    def transfer_panel(self, identity, mode, destination=None, origin=None):
        if not self.can_leave():
            return
        self.cancel_inline()
        self.clear_work()
        r = self.cat.records[identity]
        self.draft = {"kind": "transfer", "id": identity}
        self.work.pack(fill="x", before=self.results_box)
        title = {"move": "Déplacer", "add": "Ajouter un rattachement", "remove": "Retirer un rattachement"}[mode]
        ttk.Label(self.work_content, text=f"{title} · {r.title}", style="Heading.TLabel", wraplength=650).pack(anchor="w", pady=4)
        source_ids = list(r.projects) if r.kind == "item" else []
        self.source_box = None
        context = origin if origin is not None else self.scope
        if r.kind == "item" and mode in ("move", "remove") and source_ids:
            ttk.Label(self.work_content, text="Seul ce rattachement sera retiré ; tous les autres seront conservés.").pack(anchor="w")
            self.source_box = ttk.Combobox(self.work_content, state="readonly", values=[self.project_label(p) for p in source_ids])
            self.source_box.pack(fill="x", pady=4)
            if context in source_ids:
                self.source_box.current(source_ids.index(context))
            else:
                self.source_box.set("Choisir le rattachement de départ…")
        destinations = [None] if r.kind == "project" else []
        forbidden = self.cat.descendants(identity) if r.kind == "project" else set()
        destinations += sorted((p.id for p in self.cat.records.values() if p.kind == "project" and p.id not in forbidden), key=self.project_label)
        self.destination_box = None
        if mode != "remove":
            ttk.Label(self.work_content, text="Destination").pack(anchor="w")
            self.destination_box = ttk.Combobox(self.work_content, state="readonly", values=[self.project_label(p) if p else "À la racine" for p in destinations])
            self.destination_box.pack(fill="x", pady=4)
            if destination in destinations:
                self.destination_box.current(destinations.index(destination))
            elif destinations:
                self.destination_box.set("Choisir une destination…")
        row = ttk.Frame(self.work_content)
        row.pack(fill="x", pady=6)
        def apply():
            try:
                source = None
                if self.source_box is not None:
                    if self.source_box.current() < 0:
                        raise ValueError("Choisissez le rattachement de départ. Rien n'a été modifié.")
                    source = source_ids[self.source_box.current()]
                target = None
                if self.destination_box is not None:
                    if self.destination_box.current() < 0:
                        raise ValueError("Choisissez une destination.")
                    target = destinations[self.destination_box.current()]
                self.transaction(lambda: self.transfer(identity, target, mode, source))
                self.clear_work()
                self.refresh_tree()
                self.refresh_results()
                if self.inspector_visible:
                    self.show_summary(self.current, checked=True)
                self.status.set("Classement mis à jour · même fiche, notes conservées.")
            except (ValueError, OSError) as exc:
                self.work_error.set(str(exc))
        ttk.Button(row, text=title, style="Primary.TButton", command=apply).pack(side="left")
        ttk.Button(row, text="Annuler", command=self.clear_work).pack(side="left", padx=5)
        self.apply_transfer = apply

    def drag_press(self, event, widget, button):
        identity = widget.identify_row(event.y)
        self.drag = {"id": identity, "widget": widget, "button": button, "x": event.x_root, "y": event.y_root, "active": False, "origin": self.scope, "double": False}

    def clear_drop(self):
        for identity in ("all", "unfiled", *self.cat.records):
            if self.tree.exists(identity):
                self.tree.item(identity, tags=())
        self.tree.configure(cursor="")
        self.results.configure(cursor="")

    def drop_target(self, x_root, y_root):
        x, y = x_root-self.tree.winfo_rootx(), y_root-self.tree.winfo_rooty()
        if not (0 <= x < self.tree.winfo_width() and 0 <= y < self.tree.winfo_height()):
            return None, False
        identity = self.tree.identify_row(y)
        if not self.drag or self.drag["id"] not in self.cat.records:
            return identity, False
        r = self.cat.records[self.drag["id"]]
        if r.kind == "project":
            return identity, identity == "all" or (identity in self.cat.records and identity not in self.cat.descendants(r.id))
        return identity, identity in self.cat.records and self.cat.records[identity].kind == "project"

    def drag_motion(self, event):
        if not self.drag or self.drag["id"] not in self.cat.records:
            return
        if abs(event.x_root-self.drag["x"])+abs(event.y_root-self.drag["y"]) < 9:
            return
        self.drag["active"] = True
        target, allowed = self.drop_target(event.x_root, event.y_root)
        self.clear_drop()
        if target and self.tree.exists(target):
            self.tree.item(target, tags=("drop" if allowed else "forbidden",))
            self.tree.see(target)
        self.drag["widget"].configure(cursor="hand2" if allowed else "no")
        self.status.set(("Déposer ici : " + (self.project_label(target) if target in self.cat.records else "À la racine") + (" · choix Déplacer / Ajouter à la dépose" if self.drag["button"] == 3 else " · déplacer le lien de départ seulement")) if allowed else "Cible interdite · aucun changement tant qu'une dépose valide n'est pas faite.")

    def drag_release(self, event, widget, button):
        drag = self.drag
        if not drag:
            return
        target, allowed = self.drop_target(event.x_root, event.y_root)
        self.clear_drop()
        self.drag = None
        identity = drag["id"]
        if drag["active"]:
            if not allowed:
                self.status.set("Déplacement annulé : cible interdite, catalogue inchangé.")
                return "break"
            if button == 3 and self.cat.records[identity].kind == "item":
                menu = tk.Menu(self.root, tearoff=False)
                menu.add_command(label="Déplacer ici", command=lambda: self.drop_action(identity, target, "move", drag["origin"]))
                menu.add_command(label="Ajouter un rattachement ici", command=lambda: self.drop_action(identity, target, "add", drag["origin"]))
                menu.add_command(label="Annuler", command=lambda: self.status.set("Dépose annulée · catalogue inchangé."))
                self.active_menu = menu
                menu.tk_popup(event.x_root, event.y_root)
            elif button == 1:
                self.drop_action(identity, target, "move", drag["origin"])
            else:
                self.status.set("Projet : utilisez le glisser gauche ou Déplacer dans son menu.")
            return "break"
        if button == 3:
            return self.context_menu(identity, event.x_root, event.y_root)
        if widget == self.results and not drag["double"] and identity in self.cat.records and self.title_hit(event, identity):
            self.open_click(identity)

    def drop_action(self, identity, target, mode, origin):
        if not self.can_leave():
            return
        r = self.cat.records[identity]
        if r.kind == "item" and mode == "move" and r.projects and origin not in r.projects:
            self.transfer_panel(identity, mode, target, origin)
            self.status.set("Choisissez le lien de départ : aucun autre rattachement ne sera retiré.")
            return
        def action():
            self.transaction(lambda: self.transfer(identity, None if target == "all" else target, mode, origin if r.kind == "item" and origin in r.projects else None))
            self.refresh_tree()
            self.refresh_results()
            if self.inspector_visible:
                self.show_summary(self.current, checked=True)
            self.status.set("Rattachement ajouté · même fiche, notes conservées." if mode == "add" else "Déplacement effectué · autres rattachements conservés.")
        self.safe(action)

    def close(self):
        if not self.can_leave():
            return
        try:
            ui_state.save(self.preferences_path, self.inspector_visible, f"{max(1000,self.root.winfo_width())}x{max(680,self.root.winfo_height())}")
        except OSError as exc:
            messagebox.showwarning("Préférences non enregistrées", f"Le catalogue reste intact.\n{exc}", parent=self.root)
        if self.search_timer:
            self.root.after_cancel(self.search_timer)
        self.root.destroy()
