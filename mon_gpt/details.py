"""Édition détaillée et protections MG-001, atteignables sur demande."""
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from .core import now
from .storage import encode, decode
from .widgets import ChipPicker
from .theme import COLORS


class DetailEditor:
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

    def project_label(self, identity):
        parts = []
        while identity:
            r = self.cat.records[identity]
            parts.append(r.title)
            identity = r.parent
        return " / ".join(reversed(parts))

    def render_editor(self, identity):
        self.current, self.dirty = identity, False
        for widget in self.editor.winfo_children():
            widget.destroy()
        if identity is None or identity not in self.cat.records:
            ttk.Label(self.editor, text="Sélectionnez une fiche" if self.cat.records else "Votre bibliothèque commence ici", style="Title.TLabel", wraplength=350).pack(anchor="w", pady=14)
            ttk.Label(self.editor, text="Créez un projet ou un fil depuis Édition ou le menu + de votre espace.\n\nVos notes restent sur cet ordinateur.", style="PaperMuted.TLabel", wraplength=280, justify="left").pack(anchor="w")
            return
        r = self.cat.records[identity]
        ttk.Label(self.editor, text="Votre fiche locale", style="Inspector.TLabel").pack(anchor="w",pady=(0,8))
        self.fields = {}
        def field(key, label, value, lines=1):
            ttk.Label(self.editor, text=label.upper(),style="Caption.TLabel",wraplength=280).pack(anchor="w", pady=(14, 5))
            if key in ("tags", "categories"):
                picker = ChipPicker(self.editor, getattr(r, key), lambda k=key: [v for row in self.cat.records.values() for v in getattr(row, k)], lambda: setattr(self, "dirty", True))
                picker.pack(fill="x")
                self.fields[key] = picker.get
                self.pickers[key] = picker
                return
            if lines == 1:
                var = tk.StringVar(value=value)
                widget = ttk.Entry(self.editor, textvariable=var)
                var.trace_add("write", lambda *args: setattr(self, "dirty", True))
                self.fields[key] = lambda v=var: v.get()
            else:
                widget = tk.Text(self.editor, height=lines, wrap="word", font=("Segoe UI", 11), relief="solid", borderwidth=1, undo=True, background=COLORS["ivory"], foreground=COLORS["ink"], highlightcolor=COLORS["pine"], highlightthickness=1)
                widget.insert("1.0", value)
                widget.edit_modified(False)
                def modified(e, w=widget):
                    if w.edit_modified():
                        self.dirty = True
                        w.edit_modified(False)
                widget.bind("<<Modified>>", modified)
                self.fields[key] = lambda w=widget: w.get("1.0", "end-1c")
            widget.pack(fill="x")
        self.pickers = {}
        self.button(self.editor, text="← Revenir à l'aperçu", command=lambda: self.show_summary(self.current),height=30).pack(anchor="w",pady=(0,8))
        field("title", "Titre local", r.title)
        if r.kind == "item":
            field("url", "Lien ChatGPT", self.adapter.conversations[r.id].url)
        field("description", "Description" if r.kind == "project" else "Résumé", r.description, 2)
        field("notes", "Notes", r.notes, 3)
        field("tags", "Tags · étiquettes", r.tags)
        field("categories", "Catégories · classification", r.categories)
        field("metadata", "Informations personnalisées (une clé=valeur par ligne)", "\n".join(f"{k}={v}" for k, v in r.metadata.items()), 3)
        self.project_ids = sorted((p.id for p in self.cat.records.values() if p.kind == "project"), key=lambda p: self.project_label(p).casefold())
        if r.kind == "item":
            ttk.Label(self.editor, text="EMPLACEMENTS · Ctrl+clic pour sélectionner plusieurs",style="Caption.TLabel",wraplength=280).pack(anchor="w", pady=(14, 5))
            self.locations = tk.Listbox(self.editor, selectmode="extended", exportselection=False, height=4, font=("Segoe UI", 10),background=COLORS["paper"],foreground=COLORS["ink"],selectbackground=COLORS["pine"],selectforeground=COLORS["paper"],relief="flat",highlightbackground=COLORS["line"],highlightthickness=1)
            self.locations.pack(fill="x")
            for n, pid in enumerate(self.project_ids):
                self.locations.insert("end", self.project_label(pid))
                if pid in r.projects:
                    self.locations.selection_set(n)
            self.locations.bind("<<ListboxSelect>>", lambda e: setattr(self, "dirty", True))
            self.button(self.editor, text="Retirer tous les rattachements", command=self.clear_locations,height=30).pack(anchor="w",pady=5)
        else:
            self.parent_ids = [None] + [p for p in self.project_ids if p not in self.cat.descendants(r.id)]
            ttk.Label(self.editor, text="DÉPLACER SOUS",style="Caption.TLabel").pack(anchor="w", pady=(14, 5))
            self.parent_box = ttk.Combobox(self.editor, state="readonly", values=["À la racine" if p is None else self.project_label(p) for p in self.parent_ids])
            self.parent_box.current(self.parent_ids.index(r.parent))
            self.parent_box.pack(fill="x")
            self.parent_box.bind("<<ComboboxSelected>>", lambda e: setattr(self, "dirty", True))
        actions = ttk.Frame(self.editor,style="Paper.TFrame")
        actions.pack(fill="x", pady=14)
        self.button(actions, text="Enregistrer",style="Primary.TButton", command=self.save_record).pack(side="left")
        if r.kind == "item":
            self.button(actions, text="↗", command=self.open_thread,width=33).pack(side="left", padx=4)
        self.button(actions, text="Supprimer…", command=self.delete).pack(side="right")
        fmt = lambda value: datetime.fromisoformat(value).astimezone().strftime("%d/%m/%Y %H:%M:%S")
        ttk.Label(self.editor, text=f"Créé le {fmt(r.created)}\nModifié le {fmt(r.modified)}", style="PaperMuted.TLabel").pack(anchor="w")
        self.canvas.yview_moveto(0)

    def clear_locations(self):
        self.locations.selection_clear(0, "end")
        self.dirty = True

    def save_record(self):
        if self.current is None:
            return False
        def action():
            r = self.cat.records[self.current]
            values = {k: (read() if k in ("tags", "categories") else read().strip()) for k, read in self.fields.items()}
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
                    parts = values[key] if isinstance(values[key], list) else values[key].split(",")
                    setattr(r, key, list(dict.fromkeys(t.strip() for t in parts if t.strip())))
                r.metadata, r.modified = metadata, now()
            self.transaction(mutate)
            self.dirty = False
            self.refresh_tree()
            self.refresh_results()
            self.show_record(r.id)
            return True
        return self.safe(action)

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
                self.select_identity(None, checked=True)
                if self.inspector_visible:
                    self.show_summary(None, checked=True)
            self.safe(action)

    def export(self):
        if not self.can_leave():
            return
        path = filedialog.asksaveasfilename(parent=self.root, title="Sauvegarder tout le catalogue", defaultextension=".json", initialdir=self.store.directory, initialfile="mon-gpt-sauvegarde.json", filetypes=[("Sauvegarde JSON", "*.json")])
        if path:
            def action():
                self.store.export(path, self.cat, self.adapter)
                self.status.set("Sauvegarde créée : " + path)
            self.safe(action)

    def restore(self):
        if not self.can_leave():
            return
        path = filedialog.askopenfilename(parent=self.root, title="Choisir une sauvegarde à vérifier", initialdir=self.store.directory, filetypes=[("Sauvegarde JSON", "*.json")])
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
            self.select_identity(None, checked=True)
            if self.inspector_visible:
                self.show_summary(None, checked=True)
            self.status.set("Restauration terminée. État précédent : " + str(backup))
        self.safe(action)
