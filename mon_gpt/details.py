"""Édition détaillée et protections MG-001, atteignables sur demande."""
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from .core import now
from .storage import encode, decode
from .widgets import ChipPicker, EditorDelete, editor_styles
from .inspector import InspectorAction
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
        editor_styles(self.editor)
        form=ttk.Frame(self.editor,style="Paper.TFrame")
        form.pack(fill="x")
        self.editor_controls={}
        wrapped=[]
        header=ttk.Frame(form,style="Paper.TFrame")
        header.pack(fill="x",pady=(0,8))
        self.button(header,text="← Aperçu",command=lambda:self.show_summary(self.current),width=92,height=28).pack(side="right")
        ttk.Label(header,text="Modifier la fiche",style="Paper.TLabel",font=("Segoe UI",12,"bold"),foreground=COLORS["pine"]).pack(side="left")
        self.fields = {}
        def label(text):
            widget=ttk.Label(form,text=text,style="Paper.TLabel",font=("Segoe UI",10,"bold"),wraplength=280)
            widget.pack(anchor="w",pady=(9,4))
            wrapped.append(widget)
        def hint(text):
            widget=ttk.Label(form,text=text,style="PaperMuted.TLabel",font=("Segoe UI",8),wraplength=280)
            widget.pack(anchor="w",pady=(3,0))
            wrapped.append(widget)
        def text_tab(event,back=False):
            target=event.widget.tk_focusPrev() if back else event.widget.tk_focusNext()
            target.focus_set()
            return "break"
        def field(key, title, value, lines=1):
            label(title)
            if key in ("tags", "categories"):
                picker = ChipPicker(form, getattr(r, key), lambda k=key: [v for row in self.cat.records.values() for v in getattr(row, k)], lambda: setattr(self, "dirty", True),category=key=="categories")
                picker.pack(fill="x")
                self.fields[key] = picker.get
                self.pickers[key] = picker
                return
            if lines == 1:
                var = tk.StringVar(value=value)
                widget = ttk.Entry(form, textvariable=var,style="Editor.TEntry",font=("Segoe UI",10),width=1)
                var.trace_add("write", lambda *args: setattr(self, "dirty", True))
                self.fields[key] = lambda v=var: v.get()
            else:
                widget = tk.Text(form, height=lines, wrap="word", font=("Segoe UI",10), relief="flat", borderwidth=0, undo=True, background=COLORS["paper"], foreground=COLORS["ink"], highlightbackground=COLORS["line"], highlightcolor=COLORS["pine"], highlightthickness=1,padx=6,pady=5,width=1,insertofftime=500)
                widget.insert("1.0", value)
                widget.edit_modified(False)
                def modified(e, w=widget):
                    if w.edit_modified():
                        self.dirty = True
                        w.edit_modified(False)
                widget.bind("<<Modified>>", modified)
                widget.bind("<Tab>",text_tab)
                widget.bind("<Shift-Tab>",lambda e:text_tab(e,True))
                self.fields[key] = lambda w=widget: w.get("1.0", "end-1c")
            self.editor_controls[key]=widget
            widget.pack(fill="x")
        self.pickers = {}
        field("title", "Titre", r.title)
        if r.kind == "item":
            field("url", "Lien", self.adapter.conversations[r.id].url)
        field("description", "Description" if r.kind == "project" else "Résumé", r.description, 2)
        field("notes", "Notes", r.notes, 3)
        field("tags", "Tags", r.tags)
        field("categories", "Catégories", r.categories)
        field("metadata", "Informations", "\n".join(f"{k}={v}" for k, v in r.metadata.items()), 2)
        hint("Une information par ligne : clé=valeur.")
        self.project_ids = sorted((p.id for p in self.cat.records.values() if p.kind == "project"), key=lambda p: self.project_label(p).casefold())
        if r.kind == "item":
            label("Emplacements")
            self.locations = tk.Listbox(form, selectmode="extended", exportselection=False, height=3, font=("Segoe UI",10),background=COLORS["paper"],foreground=COLORS["ink"],selectbackground=COLORS["pine"],selectforeground=COLORS["paper"],relief="flat",borderwidth=0,highlightbackground=COLORS["line"],highlightcolor=COLORS["pine"],highlightthickness=1,width=1)
            self.locations.pack(fill="x")
            for n, pid in enumerate(self.project_ids):
                self.locations.insert("end", self.project_label(pid))
                if pid in r.projects:
                    self.locations.selection_set(n)
            self.locations.bind("<<ListboxSelect>>", lambda e: setattr(self, "dirty", True))
            hint("Ctrl+clic : plusieurs emplacements.")
            self.button(form, text="Retirer les rattachements", command=self.clear_locations,height=28).pack(anchor="w",pady=(4,0))
        else:
            self.parent_ids = [None] + [p for p in self.project_ids if p not in self.cat.descendants(r.id)]
            label("Projet parent")
            self.parent_box = ttk.Combobox(form, state="readonly", values=["À la racine" if p is None else self.project_label(p) for p in self.parent_ids],style="Editor.TCombobox",font=("Segoe UI",10),width=1)
            self.parent_box.current(self.parent_ids.index(r.parent))
            self.parent_box.pack(fill="x")
            self.parent_box.bind("<<ComboboxSelected>>", lambda e: setattr(self, "dirty", True))
        actions = ttk.Frame(form,style="Paper.TFrame")
        actions.pack(fill="x", pady=(12,8))
        save_button=self.button(actions,text="Enregistrer",style="Primary.TButton",command=self.save_record,width=108,height=32)
        open_button=None
        if r.kind == "item":
            open_button=InspectorAction(actions,"open","Ouvrir le fil",self.open_thread)
        delete_button=EditorDelete(actions,text="Supprimer…",command=self.delete,width=102,height=32)
        delete_button.pack(side="right")
        if open_button: open_button.pack(side="right",padx=5)
        save_button.pack(side="left")
        fmt = lambda value: datetime.fromisoformat(value).astimezone().strftime("%d/%m/%Y %H:%M")
        dates=ttk.Label(form,text=f"Créé le {fmt(r.created)}\nModifié le {fmt(r.modified)}",style="PaperMuted.TLabel",font=("Segoe UI",8),wraplength=280)
        dates.pack(anchor="w")
        wrapped.append(dates)
        form.bind("<Configure>",lambda e:[w.configure(wraplength=max(40,e.width)) for w in wrapped])
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
