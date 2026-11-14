import json
import os
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from .core import now
from .chatgpt import parse_url
from .storage import encode, decode


class App:
    def __init__(self, root, store, cat, adapter):
        self.root, self.store, self.cat, self.adapter = root, store, cat, adapter
        self.scope, self.current = "all", None
        self.dirty = False
        root.title("Mon GPT<3 — 0.1.0")
        root.geometry("1320x850")
        root.minsize(1000, 680)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10))
        style.configure("TButton", padding=(9, 6))
        style.configure("Treeview", rowheight=29)
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground="#245d65")
        header = ttk.Frame(root, padding=(16, 12))
        header.pack(fill="x")
        ttk.Label(header, text="Mon GPT<3", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="  Votre organisation, en local").pack(side="left")
        for label, command in [("Restaurer…", self.restore), ("Sauvegarder…", self.export), ("+ Fil", lambda: self.new("item")), ("+ Projet", lambda: self.new("project"))]:
            ttk.Button(header, text=label, command=command).pack(side="right", padx=3)
        filters = ttk.Frame(root, padding=(16, 0, 16, 10))
        filters.pack(fill="x")
        self.query, self.tag, self.category = tk.StringVar(), tk.StringVar(), tk.StringVar()
        for label, var, width in [("Rechercher", self.query, 27), ("Tag", self.tag, 15), ("Catégorie", self.category, 15)]:
            ttk.Label(filters, text=label).pack(side="left", padx=(0, 5))
            entry = ttk.Entry(filters, textvariable=var, width=width)
            entry.pack(side="left", padx=(0, 12))
            entry.bind("<Return>", lambda e: self.refresh_results())
        ttk.Button(filters, text="Rechercher", command=self.refresh_results).pack(side="left")
        ttk.Button(filters, text="Effacer", command=self.clear_filters).pack(side="left", padx=4)
        self.panes = ttk.Panedwindow(root, orient="horizontal")
        self.panes.pack(fill="both", expand=True, padx=16)
        left, middle, right = ttk.Frame(self.panes), ttk.Frame(self.panes), ttk.Frame(self.panes)
        for frame, weight in [(left, 2), (middle, 3), (right, 5)]:
            self.panes.add(frame, weight=weight)
        self.sort = tk.StringVar(value="Manuel")
        sorting = ttk.Combobox(left, textvariable=self.sort, values=["Manuel", "Alphabétique français"], state="readonly")
        sorting.pack(fill="x", pady=(0, 6))
        sorting.bind("<<ComboboxSelected>>", lambda e: self.refresh_tree())
        tree_box = ttk.Frame(left)
        tree_box.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_box, show="tree", selectmode="browse")
        tree_scroll = ttk.Scrollbar(tree_box, orient="vertical", command=self.tree.yview)
        tree_scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.select_scope)
        commands = ttk.Frame(left)
        commands.pack(fill="x")
        for label, step in [("Monter", -1), ("Descendre", 1)]:
            ttk.Button(commands, text=label, command=lambda s=step: self.reorder(s)).pack(side="left", expand=True, fill="x")
        ttk.Label(left, text="Projet sélectionné : descendants inclus", wraplength=220).pack(pady=7)
        self.results_label = ttk.Label(middle, text="Tous les fils")
        self.results_label.pack(anchor="w", padx=8, pady=5)
        results_box = ttk.Frame(middle)
        results_box.pack(fill="both", expand=True, padx=8)
        self.results = ttk.Treeview(results_box, columns=("type", "title"), show="headings", selectmode="browse")
        self.results.heading("type", text="Type")
        self.results.heading("title", text="Titre local")
        self.results.column("type", width=72, stretch=False)
        self.results.column("title", width=210)
        results_scroll = ttk.Scrollbar(results_box, orient="vertical", command=self.results.yview)
        results_scroll.pack(side="right", fill="y")
        self.results.configure(yscrollcommand=results_scroll.set)
        self.results.pack(side="left", fill="both", expand=True)
        self.results.bind("<<TreeviewSelect>>", self.select_record)
        ttk.Scrollbar(middle, orient="horizontal", command=self.results.xview).pack(fill="x", padx=8)
        self.canvas = tk.Canvas(right, highlightthickness=0, background="#f4f6f6")
        scrollbar = ttk.Scrollbar(right, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.editor = ttk.Frame(self.canvas, padding=14)
        window = self.canvas.create_window(0, 0, window=self.editor, anchor="nw")
        self.editor.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(window, width=e.width))
        self.status = tk.StringVar(value="Prêt — les modifications restent dans votre catalogue local.")
        ttk.Label(root, textvariable=self.status, padding=(16, 7), wraplength=1200).pack(fill="x")
        footer = ttk.Frame(root, padding=(16, 0, 16, 8))
        footer.pack(fill="x")
        ttk.Label(footer, text=str(store.path)).pack(side="left")
        ttk.Button(footer, text="Ouvrir les données", command=lambda: self.safe(lambda: os.startfile(store.directory))).pack(side="right")
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.bind("<Control-s>", lambda e: self.save_record())
        self.refresh_tree()
        self.refresh_results()
        self.show_record(None)

    def safe(self, action):
        try:
            return action()
        except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
            messagebox.showerror("Action impossible", str(exc), parent=self.root)
            return None

    def transaction(self, action):
        previous = encode(self.cat, self.adapter)
        try:
            result = action()
            self.store.save(self.cat, self.adapter)
            self.status.set("Enregistré dans le catalogue local.")
            return result
        except Exception:
            self.cat, self.adapter = decode(previous)
            raise

    def can_leave(self):
        if not self.dirty:
            return True
        answer = messagebox.askyesnocancel("Modifications en cours", "Enregistrer les modifications de la fiche ?\nNon : abandonner ces modifications.", parent=self.root)
        if answer is None:
            return False
        if answer:
            return bool(self.save_record())
        self.dirty = False
        return True

    def clear_filters(self):
        for var in (self.query, self.tag, self.category):
            var.set("")
        self.refresh_results()

    def project_label(self, identity):
        parts = []
        while identity:
            r = self.cat.records[identity]
            parts.append(r.title)
            identity = r.parent
        return " / ".join(reversed(parts))

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        self.tree.insert("", "end", iid="all", text="Tous les fils")
        self.tree.insert("", "end", iid="unfiled", text="À classer")
        # Itératif : aucune profondeur métier maximale.
        pending = [(r, "") for r in reversed(self.cat.children(None, self.sort.get() != "Manuel"))]
        while pending:
            r, parent = pending.pop()
            self.tree.insert(parent, "end", iid=r.id, text=r.title, open=True)
            pending.extend((c, r.id) for c in reversed(self.cat.children(r.id, self.sort.get() != "Manuel")))
        if self.tree.exists(self.scope):
            self.tree.selection_set(self.scope)

    def select_scope(self, event=None):
        selected = self.tree.selection()
        if not selected or selected[0] == self.scope:
            return
        if not self.can_leave():
            self.tree.selection_set(self.scope)
            return
        self.scope = selected[0]
        self.refresh_results()
        self.show_record(self.scope if self.scope in self.cat.records else None)

    def refresh_results(self):
        self.results.delete(*self.results.get_children())
        query = self.query.get().strip()
        scope = self.scope if self.scope in self.cat.records else None
        rows = self.cat.search(query, scope, self.tag.get().strip(), self.category.get().strip(), self.scope == "unfiled")
        if not query and not scope and not self.tag.get().strip() and not self.category.get().strip():
            rows = [r for r in rows if r.kind == "item"]
        for r in rows:
            self.results.insert("", "end", iid=r.id, values=("Projet" if r.kind == "project" else "Fil", r.title))
        label = self.project_label(scope) + " (descendants inclus)" if scope else ("À classer" if self.scope == "unfiled" else "Tous les fils · recherche globale")
        self.results_label.configure(text=f"{len(rows)} résultat(s) — {label}", wraplength=330)

    def select_record(self, event=None):
        selection = self.results.selection()
        if selection and selection[0] != self.current and self.can_leave():
            self.show_record(selection[0])

    def show_record(self, identity):
        self.current, self.dirty = identity, False
        for widget in self.editor.winfo_children():
            widget.destroy()
        if identity is None or identity not in self.cat.records:
            ttk.Label(self.editor, text="Sélectionnez une fiche" if self.cat.records else "Votre bibliothèque commence ici", style="Title.TLabel", wraplength=350).pack(anchor="w", pady=14)
            ttk.Label(self.editor, text="Créez un projet ou ajoutez un fil avec les boutons du haut.\n\nSélectionnez ensuite une fiche pour l'éditer.\nLes notes et classements restent sur cet ordinateur.", wraplength=350, justify="left").pack(anchor="w")
            return
        r = self.cat.records[identity]
        ttk.Label(self.editor, text="Projet" if r.kind == "project" else "Discussion", style="Title.TLabel").pack(anchor="w")
        self.fields = {}
        def field(key, label, value, lines=1):
            ttk.Label(self.editor, text=label).pack(anchor="w", pady=(8, 2))
            if lines == 1:
                var = tk.StringVar(value=value)
                widget = ttk.Entry(self.editor, textvariable=var)
                var.trace_add("write", lambda *args: setattr(self, "dirty", True))
                self.fields[key] = lambda v=var: v.get()
            else:
                widget = tk.Text(self.editor, height=lines, wrap="word", font=("Segoe UI", 10), relief="solid", borderwidth=1, undo=True)
                widget.insert("1.0", value)
                widget.edit_modified(False)
                def modified(e, w=widget):
                    if w.edit_modified():
                        self.dirty = True
                        w.edit_modified(False)
                widget.bind("<<Modified>>", modified)
                self.fields[key] = lambda w=widget: w.get("1.0", "end-1c")
            widget.pack(fill="x")
        field("title", "Titre local", r.title)
        if r.kind == "item":
            field("url", "Lien ChatGPT", self.adapter.conversations[r.id].url)
        field("description", "Description" if r.kind == "project" else "Résumé", r.description, 2)
        field("notes", "Notes", r.notes, 3)
        field("tags", "Tags (séparés par des virgules)", ", ".join(r.tags))
        field("categories", "Catégories (séparées par des virgules)", ", ".join(r.categories))
        field("metadata", "Informations personnalisées (une clé=valeur par ligne)", "\n".join(f"{k}={v}" for k, v in r.metadata.items()), 3)
        self.project_ids = sorted((p.id for p in self.cat.records.values() if p.kind == "project"), key=lambda p: self.project_label(p).casefold())
        if r.kind == "item":
            ttk.Label(self.editor, text="Emplacements — Ctrl+clic pour sélectionner plusieurs").pack(anchor="w", pady=(8, 2))
            self.locations = tk.Listbox(self.editor, selectmode="extended", exportselection=False, height=4, font=("Segoe UI", 10))
            self.locations.pack(fill="x")
            for n, pid in enumerate(self.project_ids):
                self.locations.insert("end", self.project_label(pid))
                if pid in r.projects:
                    self.locations.selection_set(n)
            self.locations.bind("<<ListboxSelect>>", lambda e: setattr(self, "dirty", True))
            ttk.Button(self.editor, text="Retirer tous les rattachements", command=self.clear_locations).pack(anchor="w")
        else:
            self.parent_ids = [None] + [p for p in self.project_ids if p not in self.cat.descendants(r.id)]
            ttk.Label(self.editor, text="Déplacer sous").pack(anchor="w", pady=(8, 2))
            self.parent_box = ttk.Combobox(self.editor, state="readonly", values=["À la racine" if p is None else self.project_label(p) for p in self.parent_ids])
            self.parent_box.current(self.parent_ids.index(r.parent))
            self.parent_box.pack(fill="x")
            self.parent_box.bind("<<ComboboxSelected>>", lambda e: setattr(self, "dirty", True))
        actions = ttk.Frame(self.editor)
        actions.pack(fill="x", pady=14)
        ttk.Button(actions, text="Enregistrer", command=self.save_record).pack(side="left")
        if r.kind == "item":
            ttk.Button(actions, text="Ouvrir le fil", command=self.open_thread).pack(side="left", padx=4)
        ttk.Button(actions, text="Supprimer…", command=self.delete).pack(side="right")
        fmt = lambda value: datetime.fromisoformat(value).astimezone().strftime("%d/%m/%Y %H:%M:%S")
        ttk.Label(self.editor, text=f"Créé le {fmt(r.created)}\nModifié le {fmt(r.modified)}", foreground="#5b6567").pack(anchor="w")
        self.canvas.yview_moveto(0)

    def clear_locations(self):
        self.locations.selection_clear(0, "end")
        self.dirty = True

    def save_record(self):
        if self.current is None:
            return False
        def action():
            r = self.cat.records[self.current]
            values = {k: read().strip() for k, read in self.fields.items()}
            if not values["title"]:
                raise ValueError("Le titre est obligatoire.")
            metadata = {}
            for line in values["metadata"].splitlines():
                if not line.strip():
                    continue
                key, sep, value = line.partition("=")
                key = key.strip()
                if not sep or not key or key in metadata:
                    raise ValueError("Chaque information doit avoir une clé unique, suivie de = et de sa valeur.")
                metadata[key] = value.strip()
            def mutate():
                if r.kind == "item":
                    self.adapter.change_url(r.id, values["url"])
                    self.cat.attach(r.id, [self.project_ids[i] for i in self.locations.curselection()])
                else:
                    parent = self.parent_ids[self.parent_box.current()]
                    if parent != r.parent:
                        self.cat.move(r.id, parent)
                for key in ("title", "description", "notes"):
                    setattr(r, key, values[key])
                for key in ("tags", "categories"):
                    setattr(r, key, list(dict.fromkeys(t.strip() for t in values[key].split(",") if t.strip())))
                r.metadata, r.modified = metadata, now()
            self.transaction(mutate)
            self.dirty = False
            self.refresh_tree()
            self.refresh_results()
            self.show_record(r.id)
            return True
        return self.safe(action)

    def new(self, kind):
        if not self.can_leave():
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter un projet" if kind == "project" else "Ajouter un fil")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("620x240")
        body = ttk.Frame(dialog, padding=18)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Titre local").pack(anchor="w")
        title = ttk.Entry(body)
        title.pack(fill="x", pady=6)
        title.focus_set()
        url = None
        if kind == "item":
            ttk.Label(body, text="URL de la conversation ChatGPT").pack(anchor="w")
            url = ttk.Entry(body)
            url.pack(fill="x", pady=6)
        ttk.Label(body, text="Emplacement : " + (self.project_label(self.scope) if self.scope in self.cat.records else "À la racine / à classer"), wraplength=570).pack(anchor="w")
        def submit():
            def action():
                project = self.scope if self.scope in self.cat.records else None
                if kind == "project":
                    r = self.transaction(lambda: self.cat.add(title.get(), "project", project))
                else:
                    identity, _ = parse_url(url.get())
                    existing = next((c for c in self.adapter.conversations.values() if c.conversation_id == identity), None)
                    if existing:
                        if not messagebox.askyesno("Fil déjà présent", "Afficher la fiche existante" + (" et la rattacher à ce projet" if project else "") + " ?\nSon titre et ses notes seront conservés.", parent=dialog):
                            return
                    def ingest():
                        r, _ = self.adapter.ingest(title.get(), url.get())
                        if project:
                            self.cat.attach(r.id, [*r.projects, project])
                        return r
                    r = self.transaction(ingest)
                dialog.destroy()
                self.refresh_tree()
                self.refresh_results()
                self.show_record(r.id)
            self.safe(action)
        ttk.Button(body, text="Créer" if kind == "project" else "Ajouter", command=submit).pack(anchor="e", pady=8)
        dialog.bind("<Return>", lambda e: submit())
        dialog.bind("<Escape>", lambda e: dialog.destroy())

    def reorder(self, step):
        if self.scope not in self.cat.records or not self.can_leave():
            return
        if self.sort.get() != "Manuel":
            messagebox.showinfo("Ordre manuel", "Choisissez le tri Manuel pour déplacer les projets frères.")
            return
        if self.safe(lambda: self.transaction(lambda: self.cat.reorder(self.scope, step))) is None:
            self.refresh_tree()

    def delete(self):
        if not self.current:
            return
        r = self.cat.records[self.current]
        effect = "Les sous-projets seront remontés au parent. Les rattachements à ce projet seront retirés. Toutes les discussions seront conservées." if r.kind == "project" else "La fiche locale et tous ses rattachements seront supprimés. Le fil chez ChatGPT reste intact."
        if messagebox.askyesno("Confirmer la suppression", f"Supprimer « {r.title} » ?\n\n{effect}", parent=self.root):
            def action():
                self.transaction(lambda: self.cat.delete(r.id))
                self.scope, self.dirty = "all", False
                self.refresh_tree()
                self.refresh_results()
                self.show_record(None)
            self.safe(action)

    def open_thread(self):
        if self.can_leave() and self.current in self.adapter.conversations:
            def action():
                _, url = parse_url(self.adapter.conversations[self.current].url)
                if not webbrowser.open(url, new=2):
                    raise ValueError("Le navigateur n'a pas pu être ouvert. Vérifiez votre navigateur par défaut.")
            self.safe(action)

    def export(self):
        if not self.can_leave():
            return
        path = filedialog.asksaveasfilename(parent=self.root, title="Sauvegarder tout le catalogue", defaultextension=".json", initialfile="mon-gpt-sauvegarde.json", filetypes=[("Sauvegarde JSON", "*.json")])
        if path:
            def action():
                self.store.export(path, self.cat, self.adapter)
                self.status.set("Sauvegarde créée : " + path)
            self.safe(action)

    def restore(self):
        if not self.can_leave():
            return
        path = filedialog.askopenfilename(parent=self.root, title="Choisir une sauvegarde à vérifier", filetypes=[("Sauvegarde JSON", "*.json")])
        if not path:
            return
        def action():
            candidate_cat, candidate_adapter = self.store.read(path)
            candidate = encode(candidate_cat, candidate_adapter)
            if not messagebox.askyesno("Remplacer le catalogue ?", f"Sauvegarde vérifiée : {len(candidate_cat.records)} fiches.\nLe catalogue actuel sera remplacé, après sauvegarde automatique dans le dossier des données.\nContinuer ?", parent=self.root):
                return
            self.cat, self.adapter, backup = self.store.restore(candidate, self.cat, self.adapter)
            self.scope, self.dirty = "all", False
            self.refresh_tree()
            self.refresh_results()
            self.show_record(None)
            self.status.set("Restauration terminée. État précédent : " + str(backup))
        self.safe(action)

    def close(self):
        if self.can_leave():
            self.root.destroy()
