"""Assistant Collector : lecture en arrière-plan, décisions explicites, un commit."""
from collections import Counter
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog

from .theme import COLORS as C
from .core import fold
from .storage import encode, decode
from .collector_import import (read_export, initial_decisions, build_plan,
                               project_path, Decision, ImportProblem)

PAGE_SIZE = 60
ACTIONS = ("Créer séparément", "Associer à un existant", "Fusionner vers un projet de l’export", "Ignorer cet import")
ACTION_KEYS = ("create", "existing", "merge", "ignore")


class ImportWizard(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.title("Importer depuis Mon GPT Collector")
        self.configure(background=C["ivory"])
        width=min(1160,self.winfo_screenwidth()-80)
        height=min(900,self.winfo_screenheight()-100)
        x=max(0,(self.winfo_screenwidth()-width)//2)
        y=max(0,(self.winfo_screenheight()-height)//2-20)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(940, 700)
        self.transient(app.root)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.bind("<Escape>", lambda e: self.cancel())
        self.bind("<Control-f>", lambda e: self.search.focus_set())
        self.bind("<Return>", self.enter)
        self.observations = self.plan = None
        self.decisions, self.issues = {}, []
        self.page, self.busy, self.finished, self.confirming = 0, False, False, False
        self.messages = queue.Queue()
        self.query, self.filter = tk.StringVar(), tk.StringVar(value="Tout")
        self.accept_separate = tk.BooleanVar(value=False)
        self.progress = tk.StringVar(value="Un export Collector ajoute des fiches. Une restauration remplace le catalogue.")
        self.action, self.target, self.local_title = tk.StringVar(value=ACTIONS[0]), tk.StringVar(), tk.StringVar()
        self.selected_key = None
        self.destinations = []
        self.tabs = {}
        self.build()
        self.bind("<Configure>",self.resize_text,add="+")
        self.grab_set()
        self.choose_button.focus_set()
        self.poll_id=self.after(60, self.poll)

    def build(self):
        style = ttk.Style(self)
        style.configure("Import.Treeview", rowheight=38, background=C["paper"], fieldbackground=C["paper"], font=("Segoe UI",10))
        style.configure("Import.TNotebook", background=C["ivory"], borderwidth=0)
        style.configure("Import.TNotebook.Tab", padding=(18,9), font=("Segoe UI",10))
        head = ttk.Frame(self, padding=(26,20,26,12))
        head.pack(fill="x")
        ttk.Label(head,text="DEPUIS MON GPT COLLECTOR",style="Muted.TLabel",font=("Segoe UI",9,"bold")).pack(anchor="w")
        ttk.Label(head,text="Vos projets prennent leur place",style="Title.TLabel").pack(anchor="w",pady=(4,8))
        ttk.Label(head,text="1  Choisir    →    2  Organiser    →    3  Vérifier et importer",style="Muted.TLabel").pack(anchor="w")
        self.filebar=ttk.Frame(self,padding=(26,0,26,12))
        self.filebar.pack(fill="x")
        self.choose_button=ttk.Button(self.filebar,text="Choisir un export JSON…",command=self.choose)
        self.choose_button.pack(side="left")
        self.file_label=ttk.Label(self.filebar,text="Collector v2 uniquement · aucune ouverture de ChatGPT",style="Muted.TLabel")
        self.file_label.pack(side="left",padx=14)
        self.stats=ttk.Label(self,text="Analyse sans modification · aperçu avant confirmation",foreground=C["pine"],font=("Segoe UI",11,"bold"),padding=(26,8),wraplength=1080)
        self.stats.pack(fill="x")
        tools=ttk.Frame(self,padding=(26,8))
        tools.pack(fill="x")
        ttk.Label(tools,text="Rechercher").pack(side="left",padx=(0,8))
        self.search=ttk.Entry(tools,textvariable=self.query,width=32)
        self.search.pack(side="left",fill="x",expand=True)
        self.filter_box=ttk.Combobox(tools,state="readonly",textvariable=self.filter,values=("Tout","Homonymes / collisions","À traiter / à classer"),width=25)
        self.filter_box.pack(side="left",padx=(12,0))
        self.query.trace_add("write",lambda *a:self.reset_page())
        self.filter.trace_add("write",lambda *a:self.reset_page())
        self.book=ttk.Notebook(self,style="Import.TNotebook")
        self.book.pack(fill="both",expand=True,padx=26,pady=(4,0))
        for name,columns in (("Projets",("Projet source","Clé source","Fils","Décision","Destination locale")),
                             ("Discussions",("Titre observé","UUID","Projets source","Destination locale","État")),
                             ("Anomalies",("Contrôle","Motif et action"))):
            frame=ttk.Frame(self.book,style="Paper.TFrame")
            self.book.add(frame,text=name)
            table=ttk.Treeview(frame,columns=list(range(len(columns))),show="headings",style="Import.Treeview",selectmode="browse")
            widths = (230,110,50,150,290) if name=="Projets" else ((250,100,200,230,190) if name=="Discussions" else (120,760))
            for i,(label,width) in enumerate(zip(columns,widths)):
                table.heading(str(i),text=label)
                table.column(str(i),width=width,minwidth=45,stretch=(i!=1))
            sy=ttk.Scrollbar(frame,orient="vertical",command=table.yview)
            sx=ttk.Scrollbar(frame,orient="horizontal",command=table.xview)
            table.configure(yscrollcommand=sy.set,xscrollcommand=sx.set)
            table.grid(row=0,column=0,sticky="nsew")
            sy.grid(row=0,column=1,sticky="ns")
            sx.grid(row=1,column=0,sticky="ew")
            frame.rowconfigure(0,weight=1);frame.columnconfigure(0,weight=1)
            table.tag_configure("attention",foreground=C["link"],background=C["category"])
            table.tag_configure("known",foreground=C["pine"])
            table.bind("<<TreeviewSelect>>",self.select_row)
            self.tabs[name]=table
        self.book.bind("<<NotebookTabChanged>>",lambda e:self.reset_page())
        pages=ttk.Frame(self,padding=(26,7))
        pages.pack(fill="x")
        ttk.Button(pages,text="‹ Précédent",command=lambda:self.turn(-1)).pack(side="left")
        self.page_label=ttk.Label(pages,text="0 élément",style="Muted.TLabel")
        self.page_label.pack(side="left",padx=12)
        ttk.Button(pages,text="Suivant ›",command=lambda:self.turn(1)).pack(side="left")
        self.detail=ttk.Label(self,text="Sélectionnez une ligne pour lire son identité et sa destination complètes.",style="Muted.TLabel",padding=(26,4),wraplength=1080,justify="left")
        self.detail.pack(fill="x")
        self.edit=ttk.Frame(self,padding=(26,6))
        self.edit.pack(fill="x")
        self.action_box=ttk.Combobox(self.edit,textvariable=self.action,values=ACTIONS,state="readonly",width=31)
        self.action_box.grid(row=0,column=0,sticky="ew",padx=(0,8))
        self.action_box.bind("<<ComboboxSelected>>",lambda e:self.update_destinations())
        self.target_box=ttk.Combobox(self.edit,textvariable=self.target,state="readonly",width=49)
        self.target_box.grid(row=0,column=1,sticky="ew",padx=(0,8))
        self.title_entry=ttk.Entry(self.edit,textvariable=self.local_title,width=28)
        self.title_entry.grid(row=0,column=2,sticky="ew",padx=(0,8))
        self.apply_choice=ttk.Button(self.edit,text="Appliquer le choix",command=self.change_choice)
        self.apply_choice.grid(row=0,column=3)
        self.edit.columnconfigure(1,weight=1)
        self.separate=ttk.Checkbutton(self,text="Je confirme la création séparée des homonymes et des noms déjà présents localement.",variable=self.accept_separate,command=self.invalidate_confirmation)
        self.separate.pack(anchor="w",padx=26,pady=(2,4))
        self.notice=ttk.Label(self,textvariable=self.progress,wraplength=1070,justify="left",padding=(26,8),foreground=C["pine"])
        self.notice.pack(fill="x")
        self.bar=ttk.Progressbar(self,mode="indeterminate")
        self.bar.pack(fill="x",padx=26)
        footer=ttk.Frame(self,padding=(26,12,26,18))
        footer.pack(fill="x")
        self.cancel_button=ttk.Button(footer,text="Annuler",command=self.cancel)
        self.cancel_button.pack(side="left")
        self.back_button=ttk.Button(footer,text="Revenir aux choix",command=self.back)
        self.back_button.pack(side="left",padx=10)
        self.next_button=ttk.Button(footer,text="Vérifier l’import →",style="Primary.TButton",command=self.next,state="disabled")
        self.next_button.pack(side="right")
        self.toggle_editor(False)
        # Seul le tableau cède de la hauteur sur les petits écrans ; les choix,
        # messages et confirmations restent toujours dans la fenêtre.
        sections=self.pack_slaves()
        for widget in sections:
            widget.pack_forget()
        for index,widget in enumerate(sections):
            widget.grid(row=index,column=0,sticky="nsew" if widget==self.book else "ew",padx=26 if widget in (self.book,self.separate,self.bar) else 0)
            self.rowconfigure(index,weight=1 if widget==self.book else 0)
        self.columnconfigure(0,weight=1)

    def resize_text(self,event):
        if event.widget==self:
            for label in (self.stats,self.detail,self.notice):
                label.configure(wraplength=max(300,event.width-64))

    def enter(self,event):
        widget=self.focus_get()
        if isinstance(widget,ttk.Button):
            widget.invoke()
            return "break"
        if widget in (self.title_entry,self.target_box,self.action_box):
            self.change_choice()
            return "break"

    def tab_name(self):
        return self.book.tab(self.book.select(),"text")

    def toggle_editor(self,enabled):
        for widget in (self.action_box,self.target_box):
            widget.configure(state="readonly" if enabled else "disabled")
        for widget in (self.title_entry,self.apply_choice):
            widget.configure(state="normal" if enabled else "disabled")

    def run(self,work,callback):
        self.busy=True
        self.next_button.configure(state="disabled")
        self.choose_button.configure(state="disabled")
        self.toggle_editor(False)
        self.bar.start(15)
        def worker():
            try: result=(True,work())
            except Exception as exc: result=(False,exc)
            self.messages.put((callback,result))
        threading.Thread(target=worker,daemon=True).start()

    def poll(self):
        if not self.winfo_exists(): return
        try:
            callback,(ok,value)=self.messages.get_nowait()
        except queue.Empty:
            pass
        else:
            self.busy=False
            self.bar.stop()
            self.choose_button.configure(state="normal" if not self.finished else "disabled")
            if ok: callback(value)
            else: self.failed(value)
        self.poll_id=self.after(60,self.poll)

    def destroy(self):
        if getattr(self,"poll_id",None):
            self.after_cancel(self.poll_id)
            self.poll_id=None
        super().destroy()

    def choose(self):
        if self.busy or self.finished: return
        path=filedialog.askopenfilename(parent=self,title="Choisir un export Mon GPT Collector v2",filetypes=[("Export JSON du Collector","*.json")])
        if path: self.load_path(path)

    def load_path(self,path):
        self.plan=None
        self.observations=None
        self.selected_key=None
        self.issues=[]
        self.confirming=False
        self.accept_separate.set(False)
        self.file_label.configure(text=Path(path).name)
        self.progress.set("Lecture et validation du fichier… aucune modification du catalogue.")
        self.run(lambda:read_export(path),self.loaded)

    def loaded(self,value):
        self.observations=value
        self.decisions=initial_decisions(value,self.app.cat,self.app.adapter)
        self.names={r["projectKey"]:r["observedName"] or "Nom non observé" for r in value.projects}
        self.homonyms=Counter(r["observedName"] for r in value.projects if r["observedName"])
        local={fold(r.title) for r in self.app.cat.records.values() if r.kind=="project"}
        self.collisions={r["projectKey"] for r in value.projects if self.homonyms[r["observedName"]]>1 or (r["observedName"] and fold(r["observedName"]) in local)}
        self.source_counts=Counter(k for r in value.conversations for k in r["observedProjectKeys"])
        self.stats.configure(text=f"{len(value.projects)} projets source · {sum(r['observedName'] is not None for r in value.projects)} nommés · {sum(v>1 for v in self.homonyms.values())} groupes homonymes · {len(value.conversations)} discussions · 0 rejet")
        self.replan()

    def replan(self):
        self.confirming=False
        self.plan=None
        self.next_button.configure(text="Vérifier l’import →")
        self.render()
        if any(d.action=="resolve" for d in self.decisions.values()):
            self.progress.set("À traiter : nom source absent ou projet local supprimé. Choisissez un titre, une destination ou Ignorer.")
            return
        snapshot=encode(self.app.cat,self.app.adapter)
        choices=dict(self.decisions)
        def work():
            cat,adapter=decode(snapshot)
            return build_plan(self.observations,choices,cat,adapter)
        self.progress.set("Préparation de l’aperçu… aucun enregistrement.")
        self.run(work,self.planned)

    def planned(self,plan):
        self.plan=plan
        n=plan.counts
        self.stats.configure(text=f"{len(self.observations.projects)} projets source · {sum(v>1 for v in self.homonyms.values())} groupes homonymes · {n['created_threads']} fils nouveaux · {n['existing_threads']} existants · {n['unfiled_threads']} à classer · 0 rejet")
        self.next_button.configure(state="normal")
        self.progress.set(plan.summary()+" · 0 rejet\nLes fiches déjà présentes conservent tous leurs champs et leur classement.")
        self.render()

    def failed(self,error):
        self.plan=None
        self.confirming=False
        self.cancel_button.configure(state="normal")
        self.back_button.configure(state="normal")
        self.issues=error.issues if isinstance(error,ImportProblem) else [str(error)]
        self.progress.set(f"Opération refusée · {len(self.issues)} anomalie(s). Catalogue inchangé. Corrigez les choix ou le fichier.")
        self.stats.configure(text=f"{len(self.issues)} anomalie(s) · aucun import partiel autorisé")
        self.book.select(2)
        self.render()

    def reset_page(self):
        self.page=0
        self.render()

    def turn(self,delta):
        self.page=max(0,self.page+delta)
        self.render()

    def render(self):
        if not self.tabs: return
        name=self.tab_name()
        previous=self.selected_key
        table=self.tabs[name]
        table.delete(*table.get_children())
        query=fold(self.query.get().strip())
        rows=[]
        if name=="Projets" and self.observations:
            planned={r["key"]:r for r in self.plan.projects} if self.plan else {}
            for row in self.observations.projects:
                key=row["projectKey"];d=self.decisions[key]
                conflict=key in self.collisions
                if self.filter.get()=="Homonymes / collisions" and not conflict: continue
                if self.filter.get()=="À traiter / à classer" and d.action not in ("resolve","ignore"): continue
                dest=planned.get(key,{}).get("destination",self.destination_label(d))
                if planned.get(key,{}).get("target"):
                    dest+=" ["+planned[key]["target"][:8]+"]"
                label=ACTIONS[ACTION_KEYS.index(d.action)] if d.action in ACTION_KEYS else "À résoudre"
                title=row["observedName"] or "Nom non observé · titre requis"
                values=(title,key[-10:],self.source_counts[key],label,dest)
                tags=("attention",) if conflict or d.action=="resolve" else (("known",) if d.action=="existing" else ())
                suggestions=[project_path(self.app.cat,r.id)+" ["+r.id[:8]+"]" for r in self.app.cat.records.values() if r.kind=="project" and fold(r.title)==fold(title)]
                hint=("\nMême nom local : "+" · ".join(suggestions[:3])+". Association uniquement sur votre choix.") if suggestions and d.action=="create" else ""
                rows.append((key,values,tags,f"{title} · {key}\n{label} → {dest}"+hint))
        elif name=="Discussions" and self.plan:
            cat,_=decode(self.plan.data)
            for row in self.plan.conversations:
                if self.filter.get()=="À traiter / à classer" and row["targets"] and not row["provisional"]: continue
                if self.filter.get()=="Homonymes / collisions" and not set(row["sources"]).intersection(self.collisions): continue
                sources=" · ".join(self.names[k]+" ["+k[-6:]+"]" for k in row["sources"]) or "Sans projet source"
                dest=" · ".join(project_path(cat,k)+" ["+k[:8]+"]" for k in row["targets"]) or "À classer"
                values=(row["title"],row["identity"][:8],sources,dest,row["status"])
                rows.append((row["identity"],values,("known",) if row["status"].startswith("Déjà") else (),f"{row['title']} · {row['identity']}\nSource : {sources}\nDestination : {dest} · {row['status']}"))
        elif name=="Anomalies":
            rows=[(str(i),(f"Anomalie {i+1}",issue),("attention",),issue) for i,issue in enumerate(self.issues)]
        rows=[r for r in rows if query in fold(" ".join(map(str,r[1]))+" "+r[0])]
        self.page=min(self.page,max(0,(len(rows)-1)//PAGE_SIZE))
        self.row_details={r[0]:r[3] for r in rows}
        for identity,values,tags,_ in rows[self.page*PAGE_SIZE:(self.page+1)*PAGE_SIZE]:
            table.insert("","end",iid=identity,values=values,tags=tags)
        self.page_label.configure(text=f"Page {self.page+1} / {max(1,(len(rows)+PAGE_SIZE-1)//PAGE_SIZE)} · {len(rows)} éléments")
        self.selected_key=None
        self.detail.configure(text="Sélectionnez une ligne pour lire son identité et sa destination complètes.")
        self.toggle_editor(False)
        if previous and table.exists(previous):
            table.selection_set(previous)
            self.detail.configure(text=self.row_details[previous])
            self.select_row()

    def destination_label(self,d):
        if d.action=="existing" and d.target in self.app.cat.records:
            return project_path(self.app.cat,d.target)+" ["+d.target[:8]+"]"
        if d.action=="merge": return self.names.get(d.target,"Source absente")+" ["+d.target[-6:]+"]"
        if d.action=="ignore": return "À classer si aucune autre destination"
        return d.title or ("Nouveau dossier indépendant" if d.action=="create" else "Choix requis")

    def select_row(self,event=None):
        name=self.tab_name();selected=self.tabs[name].selection()
        if not selected: return
        identity=selected[0]
        self.detail.configure(text=self.row_details.get(identity,""))
        if name!="Projets" or self.busy or self.finished or self.confirming: return
        self.selected_key=identity
        d=self.decisions[identity]
        self.action.set(ACTIONS[ACTION_KEYS.index(d.action)] if d.action in ACTION_KEYS else ACTIONS[0])
        self.local_title.set(d.title or next(r["observedName"] or "" for r in self.observations.projects if r["projectKey"]==identity))
        self.toggle_editor(True)
        self.update_destinations()
        for label,key in self.destinations:
            if key==d.target: self.target.set(label)

    def update_destinations(self):
        action=ACTION_KEYS[ACTIONS.index(self.action.get())]
        if action=="existing":
            self.destinations=sorted(((project_path(self.app.cat,r.id)+" ["+r.id[:8]+"]",r.id) for r in self.app.cat.records.values() if r.kind=="project"),key=lambda value:(fold(self.app.cat.records[value[1]].title)!=fold(self.names.get(self.selected_key,"")),fold(value[0])))
        elif action=="merge":
            self.destinations=[(self.names[k]+" ["+k[-10:]+"]",k) for k in self.names if k!=self.selected_key]
        else: self.destinations=[]
        self.target_box.configure(values=[v for v,k in self.destinations],state="readonly" if self.destinations else "disabled")
        self.target.set(self.destinations[0][0] if self.destinations else "Destination selon le choix")
        self.title_entry.configure(state="normal" if action=="create" else "disabled")

    def change_choice(self):
        if not self.selected_key or self.busy or self.finished or self.confirming: return
        action=ACTION_KEYS[ACTIONS.index(self.action.get())]
        target=next((key for label,key in self.destinations if label==self.target.get()),"")
        self.decisions[self.selected_key]=Decision(action,target,self.local_title.get() if action=="create" else "")
        self.issues=[]
        self.replan()

    def invalidate_confirmation(self):
        if self.confirming: self.back()

    def next(self):
        if self.busy or self.finished or not self.plan: return
        if not self.confirming:
            if any(self.decisions[k].action=="create" for k in self.collisions) and not self.accept_separate.get():
                self.progress.set("Confirmez les créations séparées avec la case ci-dessus, ou modifiez leurs destinations. Aucun nom ne provoque une fusion automatique.")
                self.separate.focus_set()
                return
            self.confirming=True
            self.toggle_editor(False)
            self.progress.set(self.plan.summary()+"\nConfirmer ? Une sauvegarde ZIP complète précédera toute modification. Aucune discussion ne sera ouverte." if self.plan.changed else self.plan.summary()+"\nAucun changement : aucune sauvegarde supplémentaire ne sera créée.")
            self.next_button.configure(text="Confirmer et importer" if self.plan.changed else "Confirmer · aucun changement")
        else:
            self.progress.set("Sauvegarde complète et enregistrement… veuillez patienter.")
            self.cancel_button.configure(state="disabled")
            self.back_button.configure(state="disabled")
            self.run(lambda:self.app.store.commit_import(self.plan,self.app.cat,self.app.adapter),self.committed)

    def back(self):
        if self.busy or self.finished: return
        self.confirming=False
        self.next_button.configure(text="Vérifier l’import →")
        if self.plan: self.progress.set(self.plan.summary()+"\nVos choix sont conservés. Vous pouvez encore les modifier.")

    def committed(self,value):
        cat,adapter,backup=value
        self.app.cat,self.app.adapter=cat,adapter
        self.app.refresh_tree()
        self.app.refresh_results()
        self.app.select_identity(self.app.current if self.app.current in cat.records else None,checked=True)
        if self.app.inspector_visible:
            self.app.show_summary(self.app.current,checked=True)
        self.app.status.set("Import Collector terminé · "+self.plan.summary().replace("\n"," · "))
        self.finished=True
        self.progress.set("Import terminé.\n"+self.plan.summary()+"\n"+("Sauvegarde complète conservée dans le dossier des données." if backup else "Catalogue inchangé · aucune nouvelle sauvegarde."))
        self.next_button.configure(state="disabled",text="Terminé")
        self.choose_button.configure(state="disabled")
        self.cancel_button.configure(state="normal",text="Fermer")
        self.cancel_button.focus_set()

    def cancel(self):
        # L'analyse peut finir en arrière-plan ; elle ne touche jamais au disque.
        if self.busy and self.confirming: return
        self.grab_release()
        self.destroy()


def open_import(app):
    if not app.can_leave(): return
    ImportWizard(app)
