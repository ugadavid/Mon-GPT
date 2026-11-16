"""Signaux et confirmation des lots, séparés des règles génériques."""
import tkinter as tk
from tkinter import ttk
from .theme import COLORS as C
from .atelier import skin_menu
from .identity_ui import ControlTip
from .batch import common_sources,build_batch
from .storage import encode,decode

LABELS={"move":"Déplacer des rattachements…","add":"Ajouter un rattachement…","remove":"Retirer un rattachement…"}


class BatchActions:
    def group_ids(self):
        return tuple(i for i in self.results.selection() if i in self.cat.records and self.cat.records[i].kind=="item")

    def individual_allowed(self):
        if len(self.group_ids())>1:
            self.status.set("Plusieurs discussions sélectionnées : utilisez les actions groupées ou sélectionnez une seule fiche.")
            return False
        return True

    def build_group_bar(self):
        self.group_bar=ttk.Frame(self.middle,padding=(9,4,9,6))
        top=ttk.Frame(self.group_bar);top.pack(fill="x")
        self.group_caption=ttk.Label(top,foreground=C["pine"],font=("Segoe UI",10,"bold"))
        self.group_caption.pack(side="left",fill="x",expand=True)
        self.button(top,"Désélectionner",self.clear_group,width=108,height=28).pack(side="right")
        actions=ttk.Frame(self.group_bar);actions.pack(fill="x",pady=(4,0))
        self.group_buttons={}
        for column,(mode,label) in enumerate(LABELS.items()):
            button=self.button(actions,label,lambda m=mode:self.open_batch(m),width=1,height=30)
            button.grid(row=0,column=column,sticky="ew",padx=(0,4))
            actions.columnconfigure(column,weight=1,uniform="batch")
            button.tip=ControlTip(button,label)
            self.group_buttons[mode]=button
        def resize(event):
            self.group_caption.configure(wraplength=max(110,event.width-125))
            for mode,button in self.group_buttons.items():
                button.configure(text=LABELS[mode] if event.width>=640 else {"move":"Déplacer…","add":"Ajouter…","remove":"Retirer…"}[mode])
        self.group_bar.bind("<Configure>",resize)
        self._group_active=False

    def sync_group(self):
        if not hasattr(self,"group_bar"): return
        ids=self.group_ids();active=len(ids)>1
        was=self._group_active;self._group_active=active
        if was!=active:
            menu=self.main_menu.menus[1][1]
            for index in range(menu.index('end')+1):
                if menu.type(index)!='separator' and menu.entrycget(index,'label') in ('Renommer','Modifier la fiche','Enregistrer la fiche'):
                    menu.entryconfigure(index,state='disabled' if active else 'normal')
        if active:
            self.current=None;self.editing=False
            self.group_caption.configure(text=f"{len(ids)} discussions sélectionnées")
            if not self.group_bar.winfo_manager():self.group_bar.pack(fill="x",before=self.results_box)
            self.update_identity()
            if self.inspector_visible:self.show_group_summary()
        else:
            self.group_bar.pack_forget()
            if was:
                target=self.results.selected
                self.current=None
                if target:self.select_identity(target,checked=True)
                elif self.inspector_visible:self.show_summary(None,checked=True)

    def show_group_summary(self):
        count=len(self.group_ids())
        if not getattr(self,"group_summary",None) or not self.group_summary.winfo_exists():
            for child in self.editor.winfo_children():child.destroy()
            self.group_summary=ttk.Frame(self.editor,style="Paper.TFrame",padding=(0,12))
            self.group_summary.pack(fill="x")
            self.group_summary_title=ttk.Label(self.group_summary,style="Inspector.TLabel",wraplength=270)
            self.group_summary_title.pack(anchor="w")
            ttk.Label(self.group_summary,text="Classez ce lot avec Déplacer, Ajouter ou Retirer un rattachement.\n\nPour ouvrir ou modifier une discussion, sélectionnez-la seule.",style="PaperMuted.TLabel",wraplength=270,justify="left").pack(anchor="w",pady=16)
        self.group_summary_title.configure(text=f"{count} discussions sélectionnées")

    def clear_group(self):
        self.results.selection_set(())
        self.current=None
        self.sync_group()
        self.results.focus_set()

    def group_menu(self,x,y):
        menu=skin_menu(tk.Menu(self.root,tearoff=False))
        for mode,label in LABELS.items():menu.add_command(label=label,command=lambda m=mode:self.open_batch(m))
        menu.add_separator();menu.add_command(label="Désélectionner",command=self.clear_group)
        self.active_menu=menu;menu.tk_popup(x,y)
        return "break"

    def open_batch(self,mode):
        if len(self.group_ids())<2:
            self.status.set("Sélectionnez au moins deux discussions.")
            return
        if not self.can_leave():return
        self.batch_dialog=BatchDialog(self,mode)


class BatchDialog(tk.Toplevel):
    def __init__(self,app,mode):
        super().__init__(app.root)
        self.app,self.mode=app,mode
        self.ids=app.group_ids();self.expected=encode(app.cat,app.adapter)
        self.catalog,_=decode(self.expected)
        self.plan=None;self.finished=False
        self.title("Classement groupé · Mon GPT<3")
        self.transient(app.root);self.configure(background=C["ivory"])
        self.geometry("760x650");self.minsize(620,560)
        self.geometry(f"+{max(0,(self.winfo_screenwidth()-760)//2)}+{max(0,(self.winfo_screenheight()-650)//2-30)}")
        self.protocol("WM_DELETE_WINDOW",self.cancel)
        self.bind("<Escape>",lambda e:(self.cancel(),"break")[1])
        self.source=tk.StringVar();self.destination=tk.StringVar()
        body=ttk.Frame(self,padding=24);body.pack(fill="both",expand=True)
        ttk.Label(body,text="CLASSEMENT GROUPÉ",style="Muted.TLabel",font=("Segoe UI",9,"bold")).pack(anchor="w")
        ttk.Label(body,text=LABELS[mode].rstrip('…'),style="Heading.TLabel",font=("Segoe UI",20,"bold")).pack(anchor="w",pady=(7,6))
        ttk.Label(body,text=f"{len(self.ids)} discussions distinctes · aucune fiche ne sera dupliquée.",style="Muted.TLabel").pack(anchor="w",pady=(0,16))
        self.projects={app.project_label(r.id)+" ["+r.id+"]":r.id for r in self.catalog.records.values() if r.kind=="project"}
        self.project_values=sorted(self.projects)
        common,unfiled=common_sources(self.catalog,self.ids)
        self.sources={label:identity for label,identity in self.projects.items() if identity in common}
        self.unfiled=unfiled
        self.source_box=None;self.destination_box=None
        if mode in ("move","remove"):
            ttk.Label(body,text="Rattachement source · commun à tout le lot",font=("Segoe UI",10,"bold")).pack(anchor="w")
            values=["Choisir la source…",*sorted(self.sources)]
            if unfiled and mode=="move":values=["À classer · aucun rattachement à retirer"]
            self.source_box=ttk.Combobox(body,state="readonly",textvariable=self.source,values=values)
            self.source_box.pack(fill="x",pady=(5,12));self.source.set(values[0])
            if app.scope in common:
                self.source.set(next(label for label,identity in self.sources.items() if identity==app.scope))
        if mode in ("move","add"):
            ttk.Label(body,text="Projet destination",font=("Segoe UI",10,"bold")).pack(anchor="w")
            self.destination_box=ttk.Combobox(body,state="readonly",textvariable=self.destination,values=["Choisir la destination…",*self.project_values])
            self.destination_box.pack(fill="x",pady=(5,12));self.destination.set("Choisir la destination…")
        self.summary=ttk.Label(body,foreground=C["pine"],wraplength=690,justify="left",font=("Segoe UI",11,"bold"))
        self.summary.pack(fill="x",pady=(4,10))
        self.preview=tk.Text(body,height=7,wrap="word",font=("Segoe UI",10),background=C["paper"],foreground=C["ink"],relief="flat",padx=12,pady=10,takefocus=True)
        self.preview.pack(fill="both",expand=True)
        self.notice=ttk.Label(body,text="Les notes, tags, catégories, autres rattachements, URL et couvertures seront conservés.",style="Muted.TLabel",wraplength=690,justify="left")
        self.notice.pack(fill="x",pady=(12,8))
        self.error=ttk.Label(body,background=C["invalid"],foreground=C["error"],wraplength=690,padding=8)
        self.error.pack(fill="x",pady=(0,8))
        actions=ttk.Frame(body);actions.pack(fill="x")
        self.cancel_button=ttk.Button(actions,text="Annuler",command=self.cancel);self.cancel_button.pack(side="left")
        self.refresh_button=ttk.Button(actions,text="Actualiser l’aperçu",command=self.reload);self.refresh_button.pack(side="left",padx=8)
        self.confirm_button=ttk.Button(actions,text="Confirmer",style="Primary.TButton",command=self.confirm);self.confirm_button.pack(side="right")
        for variable in (self.source,self.destination):variable.trace_add("write",lambda *a:self.rebuild())
        self.rebuild();self.grab_set()
        for box in (self.source_box,self.destination_box):
            if box:box.tip=ControlTip(box,lambda w=box:w.get())
        (self.destination_box or self.source_box or self.cancel_button).focus_set()

    def rebuild(self):
        if self.finished:return
        self.plan=None
        self.confirm_button.configure(state="disabled")
        try:
            src=self.sources.get(self.source.get()) if self.mode!="add" else None
            dst=self.projects.get(self.destination.get()) if self.mode!="remove" else None
            self.plan=build_batch(self.catalog,self.ids,self.mode,src,dst)
            p=self.plan
            self.summary.configure(text=f"{p.changed} discussion(s) modifiée(s) · {p.unchanged} inchangée(s)\n{p.already} déjà dans la destination · {p.unfiled} devenant À classer")
            self.error.pack_forget()
            self.confirm_button.configure(state="normal",text="Confirmer" if p.changed else "Fermer · aucun changement")
            lines=[]
            for identity in p.ids[:6]:
                r=self.catalog.records[identity]
                dest=p.changes.get(identity,r.projects)
                label=" · ".join(self.path(i) for i in dest) or "À classer"
                lines.append(r.title+"\n→ "+label)
            if len(p.ids)>6:lines.append(f"… et {len(p.ids)-6} autres discussions.")
            if self.mode=="move" and p.source==p.destination:lines.insert(0,"Source et destination identiques : aucun changement.")
            text="\n\n".join(lines)
        except ValueError as exc:
            self.summary.configure(text="Aucun changement appliqué.")
            self.error.configure(text=str(exc));self.error.pack(fill="x",before=self.confirm_button.master,pady=(0,8))
            text="Choisissez les rattachements ci-dessus pour prévisualiser le classement.\n\nAucune source commune ? Sélectionnez un lot homogène ou utilisez Ajouter un rattachement."
        self.preview.configure(state="normal");self.preview.delete("1.0","end");self.preview.insert("1.0",text);self.preview.configure(state="disabled")

    def reload(self):
        if self.finished:return
        if self.ids!=self.app.group_ids():
            self.error.configure(text="La sélection a changé : fermez ce dialogue et recommencez avec le lot visible.")
            self.error.pack(fill="x",before=self.confirm_button.master);self.confirm_button.configure(state="disabled")
            return
        self.expected=encode(self.app.cat,self.app.adapter);self.catalog,_=decode(self.expected)
        self.projects={self.path(r.id)+" ["+r.id+"]":r.id for r in self.catalog.records.values() if r.kind=="project"}
        common,self.unfiled=common_sources(self.catalog,self.ids)
        self.sources={label:i for label,i in self.projects.items() if i in common}
        if self.destination_box:self.destination_box.configure(values=["Choisir la destination…",*sorted(self.projects)])
        if self.source_box:self.source_box.configure(values=["À classer · aucun rattachement à retirer"] if self.unfiled and self.mode=="move" else ["Choisir la source…",*sorted(self.sources)])
        self.rebuild()

    def path(self,identity):
        parts=[]
        while identity:
            r=self.catalog.records[identity];parts.append(r.title);identity=r.parent
        return " / ".join(reversed(parts))

    def confirm(self):
        if self.finished or self.plan is None:return
        try:
            if self.app.group_ids()!=self.ids:raise ValueError("La sélection visible a changé : recommencez l’aperçu.")
            cat,adapter=self.app.store.commit_batch(self.plan,self.app.cat,self.app.adapter,self.expected)
            self.app.cat,self.app.adapter=cat,adapter
            self.app.refresh_tree();self.app.refresh_results();self.app.sync_group()
            self.finished=True
            message=f"Classement terminé · {self.plan.changed} modifiée(s), {self.plan.unchanged} inchangée(s), {self.plan.unfiled} à classer."
            self.summary.configure(text=message);self.app.status.set(message)
            self.confirm_button.configure(state="disabled",text="Terminé")
            self.refresh_button.configure(state="disabled");self.cancel_button.configure(text="Fermer")
            for box in (self.source_box,self.destination_box):
                if box:box.configure(state="disabled")
            self.cancel_button.focus_set()
        except (ValueError,OSError) as exc:
            self.error.configure(text="Opération annulée. "+str(exc))
            self.error.pack(fill="x",before=self.confirm_button.master);self.confirm_button.configure(state="disabled")

    def cancel(self):
        self.grab_release();self.destroy()
        self.app.results.focus_set()
