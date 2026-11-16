"""Administration locale des colonnes de la Liste, sans mutation du catalogue."""
import tkinter as tk
from tkinter import ttk
from .list_columns import COLUMNS, BY_KEY, defaults, validate
from .theme import COLORS as C
from . import ui_state


class ListColumnsUI:
    def list_configuration(self):
        table=self.results
        return dict(order=list(table.list_order),visible=list(table.list_visible),
                    widths={c.key:table.column(c.key,'width') for c in COLUMNS},
                    sort=self.sort_column,reverse=self.sort_reverse)

    def install_columns(self,config):
        config=validate(config);table=self.results
        table.list_order=config['order'];table.list_visible=config['visible'];table.left=0
        for c in COLUMNS:table.column(c.key,width=config['widths'][c.key],minwidth=c.minimum,maxwidth=c.maximum)
        self.sort_column,self.sort_reverse=config['sort'],config['reverse']
        self.update_sort_caption()
        table.hide_tip();table.draw()

    def apply_columns(self,config):
        config=validate(config)
        if config['sort'] not in config['visible']:config['sort'],config['reverse']='title',False
        self.install_columns(config);self.refresh_results()
        return self.persist_columns()

    def persist_columns(self,event=None):
        if self.restoring_workspace:return True
        dialog=getattr(self,'columns_dialog',None)
        if event is not None and dialog is not None and dialog.winfo_exists():
            dialog.draft['widths']=self.list_configuration()['widths'];dialog.paint()
        try:
            self.save_preferences();return True
        except (ValueError,OSError) as exc:
            self.status.set('Préférences non enregistrées : '+str(exc));return False

    def open_columns(self):
        if getattr(self,'columns_dialog',None) and self.columns_dialog.winfo_exists():
            self.columns_dialog.lift();return
        self.columns_dialog=ColumnsDialog(self)

    def save_preferences(self):
        selection=self.results.selection()
        ui_state.save(self.preferences_path,self.inspector_visible,
            f'{max(1000,self.root.winfo_width())}x{max(680,self.root.winfo_height())}',self.view.get(),
            query=self.query.get(),tag=self.tag.get(),category=self.category.get(),scope=self.scope,
            mosaic_size=self.mosaic_size.get(),selected=selection[0] if len(selection)==1 else None,
            expanded_projects=[r.id for r in self.cat.records.values() if r.kind=='project' and self.tree.exists(r.id) and self.tree.item(r.id,'open')],
            list_columns=self.list_configuration())


class ColumnsDialog(tk.Toplevel):
    def __init__(self,app):
        super().__init__(app.root)
        self.app=app;self.draft=app.list_configuration()
        self.title('Colonnes de la liste · Mon GPT<3');self.transient(app.root)
        self.configure(background=C['ivory']);self.geometry('620x590');self.minsize(580,590)
        self.geometry(f'+{max(0,(self.winfo_screenwidth()-620)//2)}+{max(0,(self.winfo_screenheight()-590)//2-30)}')
        self.bind('<Escape>',lambda e:self.destroy())
        body=ttk.Frame(self,padding=24);body.pack(fill='both',expand=True)
        footer=ttk.Frame(body);footer.pack(side='bottom',fill='x')
        ttk.Label(body,text='Votre Liste, à votre façon',style='Heading.TLabel',font=('Segoe UI',19,'bold')).pack(anchor='w')
        ttk.Label(body,text='Choisissez les colonnes et leur ordre. Le titre et ↗ restent épinglés.',style='Muted.TLabel',wraplength=540).pack(anchor='w',pady=(7,16))
        self.rows=ttk.Frame(body);self.rows.pack(fill='x')
        self.message=ttk.Label(body,text='Appliquer mémorise les réglages. Fermer ignore les changements non appliqués.',style='Muted.TLabel',wraplength=530)
        self.message.pack(fill='x',pady=(12,8))
        ttk.Label(body,text='Largeurs : glissez les séparateurs de l’en-tête de la Liste.\nCréation / Modification : dates de la fiche locale dans Mon GPT<3.',style='Muted.TLabel',wraplength=530).pack(anchor='w',pady=(2,12))
        app.button(footer,text='Valeurs par défaut',command=self.reset,width=150).pack(side='left')
        app.button(footer,text='Fermer',command=self.destroy,width=78).pack(side='right')
        app.button(footer,text='Appliquer',command=self.apply,style='Primary.TButton',width=95).pack(side='right',padx=6)
        self.paint()

    def paint(self,focus=None):
        for child in self.rows.winfo_children():child.destroy()
        self.checks={};self.up={};self.down={}
        for col,text in enumerate(('Afficher','Largeur','Ordre')):
            ttk.Label(self.rows,text=text,style='Muted.TLabel').grid(row=0,column=col if col<2 else 2,columnspan=2 if col==2 else 1,sticky='w',pady=(0,7))
        for n,key in enumerate(self.draft['order']):
            variable=tk.BooleanVar(value=key in self.draft['visible'])
            check=ttk.Checkbutton(self.rows,text=BY_KEY[key].label,variable=variable,command=lambda k=key,v=variable:self.toggle(k,v.get()))
            check.grid(row=n+1,column=0,sticky='w',pady=5);self.checks[key]=check
            if key=='title':check.state(['disabled'])
            ttk.Label(self.rows,text=f"{self.draft['widths'][key]} px",style='Muted.TLabel').grid(row=n+1,column=1,sticky='w',padx=(10,18))
            for delta,label,target,column in ((-1,'Monter',self.up,2),(1,'Descendre',self.down,3)):
                button=ttk.Button(self.rows,text=label,command=lambda k=key,d=delta:self.move(k,d),width=10)
                button.grid(row=n+1,column=column,padx=3);target[key]=button
                if key=='title' or not 1<=n+delta<len(COLUMNS):button.state(['disabled'])
        self.rows.columnconfigure(0,weight=1)
        if focus:self.checks[focus].focus_set()

    def toggle(self,key,shown):
        if shown and key not in self.draft['visible']:self.draft['visible'].append(key)
        elif not shown and key in self.draft['visible'] and key!='title':self.draft['visible'].remove(key)

    def move(self,key,delta):
        order=self.draft['order'];index=order.index(key);other=index+delta
        if key=='title' or not 1<=other<len(order):return
        order[index],order[other]=order[other],order[index];self.paint(key)

    def reset(self):
        self.draft=defaults();self.paint();self.message.configure(text='Valeurs par défaut préparées. Appliquer pour les utiliser.')

    def apply(self):
        saved=self.app.apply_columns(self.draft);self.draft=self.app.list_configuration()
        self.paint();self.message.configure(text='Réglages appliqués et mémorisés. Les autres vues gardent leur présentation.' if saved else self.app.status.get())
