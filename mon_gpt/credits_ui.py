"""Fenêtre documentaire native ; même cycle de vie que l’aide et À propos."""
import tkinter as tk
from tkinter import ttk
import webbrowser
from .information_ui import InformationWindow
from .credits import COMPONENTS, INTRO, SCOPE, runtime_versions, read_notice
from .theme import COLORS as C


class CreditsWindow(InformationWindow):
    def __init__(self,app):
        super().__init__(app,'Licences et crédits',860,640)
        # Garder les quatre composants, les actions et une zone de lecture
        # utilisables ensemble, y compris avec les métriques du thème Windows.
        self.minsize(600,500)
        self.versions=runtime_versions(app.root)
        self.tabs=ttk.Notebook(self.content);self.tabs.pack(fill='both',expand=True)
        components=ttk.Frame(self.tabs,padding=10)
        notices=ttk.Frame(self.tabs,padding=10)
        scope=ttk.Frame(self.tabs,padding=10)
        for frame,title in ((components,'Composants'),(notices,'Notices locales'),(scope,'Périmètre')):
            self.tabs.add(frame,text=title)
        intro=ttk.Label(components,text=INTRO,wraplength=760,justify='left')
        intro.pack(fill='x',pady=(0,10))
        actions=ttk.Frame(components);actions.pack(side='bottom',fill='x',pady=(10,0))
        self.notice_button=ttk.Button(actions,text='Consulter les notices',command=self.consult)
        self.notice_button.pack(side='left')
        self.source_button=ttk.Button(actions,text='Source officielle ↗',command=self.open_source)
        self.source_button.pack(side='left',padx=8)
        self.table=ttk.Treeview(components,columns=('role','version','license'),show='tree headings',selectmode='browse',height=4)
        for key,title,width in (('#0','Composant',100),('role','Fonction',240),('version','Installée',90),('license','Licence',185)):
            self.table.heading(key,text=title);self.table.column(key,width=width,minwidth=60,stretch=True)
        self.table.pack(fill='x')
        for n,(component,version) in enumerate(zip(COMPONENTS,self.versions)):
            self.table.insert('','end',iid=str(n),text=component.name,values=(component.role,version,component.license))
        self.detail=self.text_area(components,height=3)
        self.table.bind('<<TreeviewSelect>>',self.describe)
        self.table.bind('<Return>',lambda e:(self.consult(),'break')[1])
        self.table.bind('<Double-1>',lambda e:self.consult())
        ttk.Label(notices,text='Textes originaux complets, conservés dans leur langue. Sélectionnez du texte puis Ctrl+C pour le copier.',wraplength=760,justify='left').pack(fill='x',pady=(0,10))
        self.notice_choice=ttk.Combobox(notices,state='readonly',values=[f'{c.name} — référence {c.reference}' for c in COMPONENTS])
        self.notice_choice.pack(fill='x',pady=(0,8))
        self.notice_text=self.text_area(notices,font=('Consolas',10))
        self.notice_choice.bind('<<ComboboxSelected>>',self.show_notice)
        self.notice_choice.current(0);self.show_notice()
        self.scope_text=self.text_area(scope)
        self.fill(self.scope_text,SCOPE)
        components.bind('<Configure>',lambda e:intro.configure(wraplength=max(100,e.width-20)))
        notices.bind('<Configure>',lambda e:notices.winfo_children()[0].configure(wraplength=max(100,e.width-20)))
        self.table.selection_set('0');self.describe();self.table.focus('0');self.table.focus_set()

    def text_area(self,parent,height=1,font=('Segoe UI',10)):
        frame=ttk.Frame(parent);frame.pack(fill='both',expand=True,pady=(8,0))
        text=tk.Text(frame,wrap='word',width=1,height=height,font=font,background=C['paper'],foreground=C['ink'],relief='flat',padx=10,pady=8)
        bar=ttk.Scrollbar(frame,command=text.yview);bar.pack(side='right',fill='y')
        text.configure(yscrollcommand=bar.set);text.pack(fill='both',expand=True)
        text.bind('<Tab>',lambda e:(text.tk_focusNext().focus_set(),'break')[1])
        text.bind('<Shift-Tab>',lambda e:(text.tk_focusPrev().focus_set(),'break')[1])
        text.bind('<Control-a>',lambda e:(text.tag_add('sel','1.0','end-1c'),'break')[1])
        return text

    @staticmethod
    def fill(widget,text):
        widget.configure(state='normal');widget.delete('1.0','end');widget.insert('1.0',text)
        widget.configure(state='disabled');widget.yview_moveto(0)

    def selected(self):return int(self.table.selection()[0]) if self.table.selection() else 0

    def describe(self,event=None):
        n=self.selected();c=COMPONENTS[n]
        self.fill(self.detail,f'{c.name} · {c.role}\nLicence : {c.license} · version installée : {self.versions[n]}\n\n{c.detail}\n\nNotice locale de référence : {c.reference}. Les versions installées peuvent différer ; voir Périmètre.')

    def consult(self):
        self.notice_choice.current(self.selected());self.show_notice();self.tabs.select(1);self.notice_choice.focus_set()

    def show_notice(self,event=None):
        n=self.notice_choice.current()
        if n<0:return
        try:text=read_notice(COMPONENTS[n])
        except (OSError,UnicodeError):text='Notice locale indisponible. Le fichier de référence doit être rétabli depuis les sources de Mon GPT<3. Aucun téléchargement automatique.'
        self.fill(self.notice_text,text)

    def open_source(self):webbrowser.open(COMPONENTS[self.selected()].url,new=2)
