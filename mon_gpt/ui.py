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
from .atelier import rounded, Surface, PillButton, IconButton, AutoScrollbar, skin_menu, shorten
from .main_menu import MainMenuBar
from .inspector import InspectorSummary, InspectorScrollbar
from .navigation import NavigationTree, navigation_icons
from .identity import resolve_identity, inherited_identity, DEFAULTS
from .identity_ui import ContextMasthead, ProjectVisualStrip, ControlTip
from .project_icons import ProjectIconCache
from .results import ResultsView
from .batch_ui import BatchActions
from .project_choices import project_choices
from .columns_ui import ListColumnsUI
from .list_columns import COLUMNS, BY_KEY, defaults as default_columns, sort_value
from . import ui_state, __version__


class App(ListColumnsUI,BatchActions,DetailEditor):
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
        scope=preferences.get("scope","all")
        selected=preferences.get("selected")
        if (scope not in ("all","unfiled") and (scope not in cat.records or cat.records[scope].kind!="project")) or (selected is not None and selected not in cat.records):
            preferences,warning={},ui_state.WARNING
        self.restoring_workspace=True
        self.view=tk.StringVar(value=preferences.get("view","list"))
        self.mosaic_size=tk.StringVar(value=preferences.get("mosaic_size","normal"))
        self.sort_caption="Tri · Titre ↑"
        apply_theme(root)
        self.icons = make_icons(root)
        self.project_icons=ProjectIconCache(root)
        self.font = Font(root, font=FONT)
        root.iconphoto(True,self.project_icons.get("feather","atelier",32))
        root.title(f"Mon GPT<3 — {__version__}" + (" · RECETTE · ouvertures simulées" if opener else ""))
        root.geometry(preferences.get("geometry", "1360x820"))
        root.minsize(1000, 680)
        self.status = tk.StringVar(value=warning or "Prêt · sélectionnez une ligne ; ↗ ouvre le fil.")
        self.query, self.tag, self.category = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.sort = tk.StringVar(value="Manuel")
        self.quick_click_tag=f"QuickDraftClick{root}"
        root.bind_class(self.quick_click_tag,"<ButtonPress-1>",self.dismiss_quick_draft)
        root.bind("<Map>",lambda e:self.tag_quick_click(e.widget),add="+")
        self.tag_quick_click(root)
        self.build_menus()
        self.build_shell()
        self.bind_keys()
        config=preferences.get("list_columns",default_columns())
        if self.view.get()=="list" and config["sort"] not in config["visible"]:
            config=dict(config,sort="title",reverse=False)
        self.install_columns(config)
        self.restore_workspace(preferences)
        root.protocol("WM_DELETE_WINDOW", self.close)

    def restore_workspace(self,preferences):
        self.scope=preferences.get("scope","all")
        for key in ("query","tag","category"):
            getattr(self,key).set(preferences.get(key,""))
        self.refresh_tree(expanded=preferences.get("expanded_projects"))
        self.refresh_results()
        selected=preferences.get("selected")
        if selected and self.results.exists(selected):
            self.current=selected
            self.results.selection_set(selected)
            self.results.focus(selected)
        else:
            self.current=None
        self.update_identity()
        if preferences.get("inspector"):
            self.ensure_inspector()
            self.show_summary(self.current,checked=True)
        self.root.after_idle(self.finish_workspace_restore)

    def finish_workspace_restore(self):
        # Vider les événements initiaux pendant la garde, avant la reprise normale.
        self.root.update_idletasks()
        self.tree.see(self.scope)
        if self.current and self.results.exists(self.current): self.results.see(self.current)
        self.restoring_workspace=False

    def build_menus(self):
        bar = tk.Menu(self.root, tearoff=False)
        file = tk.Menu(bar, tearoff=False)
        file.add_command(label="Sauvegarder le catalogue…", command=self.export)
        file.add_command(label="Restaurer le catalogue…", command=self.restore)
        file.add_command(label="Importer depuis Mon GPT Collector (JSON)…", command=self.import_collector)
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
        self.view_menu=view
        view.add_command(label="Liste", command=lambda:self.set_view("list"))
        view.add_command(label="Détaillée", command=lambda:self.set_view("detail"))
        view.add_command(label="Mosaïque", command=lambda:self.set_view("mosaic"))
        self.update_view_menu()
        view.add_command(label="Colonnes de la liste…",command=self.open_columns)
        view.add_command(label="Afficher / masquer l'inspecteur", command=self.toggle_inspector)
        view.add_command(label="Rechercher", accelerator="Ctrl+K", command=self.focus_search)
        view.add_command(label="Retirer les filtres", command=self.clear_filters)
        bar.add_cascade(label="Affichage", menu=view)
        help_menu = tk.Menu(bar, tearoff=False)
        help_menu.add_command(label="Gestes et raccourcis", command=self.help)
        help_menu.add_command(label="Licences et crédits…",command=self.credits)
        help_menu.add_command(label="À propos de Mon GPT<3",command=self.about)
        bar.add_cascade(label="Aide", menu=help_menu)
        self.main_menu = MainMenuBar(self.root, [("Fichier", file), ("Édition", edit), ("Affichage", view), ("Aide", help_menu)])
        self.main_menu.pack(fill="x")
        self.plus = skin_menu(tk.Menu(self.root, tearoff=False))
        self.plus.add_command(label="Nouveau fil", accelerator="Ctrl+N", command=lambda: self.new("item"))
        self.plus.add_command(label="Nouveau projet", accelerator="Ctrl+Maj+P", command=lambda: self.new("project"))

    def import_collector(self):
        from .import_ui import open_import
        open_import(self)

    def update_view_menu(self):
        for index,(key,label) in enumerate((("list","Liste"),("detail","Détaillée"),("mosaic","Mosaïque"))):
            self.view_menu.entryconfigure(index,label=label+(" · vue actuelle" if self.view.get()==key else ""))

    def update_view_buttons(self):
        for key,button in self.view_buttons.items():
            button.tone="chip" if self.view.get()==key else "segment"
            button.draw()
        if self.view.get()=="detail":
            self.detail_sort_button.pack(side="right")
        else:
            self.detail_sort_button.pack_forget()
        if self.view.get()=="mosaic":
            self.mosaic_tools.pack(side="right")
        else:
            self.mosaic_tools.pack_forget()
        self.layout_view_controls()

    def layout_view_controls(self,event=None):
        narrow=self.viewbar.winfo_width()<410
        caption="Tri" if narrow else self.sort_caption
        width=42 if narrow else self.detail_sort_button.font.measure(caption)+24
        for button in (self.detail_sort_button,self.mosaic_sort_button):
            button.configure(text=caption,width=width)
        self.mosaic_size_button.configure(text="Cartes · "+("Grand" if self.mosaic_size.get()=="large" else "Normal")+" ⌄")

    def mosaic_size_popup(self):
        menu=skin_menu(tk.Menu(self.root,tearoff=False))
        for value,label in (("normal","Normal"),("large","Grand")):
            menu.add_command(label=label+(" · actuel" if self.mosaic_size.get()==value else ""),command=lambda v=value:self.set_mosaic_size(v))
        self.active_menu=menu
        button=self.mosaic_size_button
        menu.tk_popup(button.winfo_rootx(),button.winfo_rooty()+button.winfo_height())

    def set_mosaic_size(self,size):
        if size not in ("normal","large"): return
        self.mosaic_size.set(size);self.results.set_mosaic_size(size)
        self.layout_view_controls()
        self.position_mosaic_rename()

    def position_mosaic_rename(self,event=None):
        if self.view.get()!="mosaic" or self.inline is None or self.inline.master!=self.results: return
        bbox=self.results.bbox(self.draft["id"],"title")
        if bbox:
            x,y,width,height=bbox
            self.inline.place(x=x,y=y,width=max(40,width),height=28)
        else: self.inline.place_forget()

    def results_context_menu(self):
        if len(self.group_ids())>1:
            return self.group_menu(self.results.winfo_rootx()+60,self.results.winfo_rooty()+40)
        box=self.results.bbox(self.current) if self.current else None
        if self.view.get()=="mosaic" and box:
            x,y,width,height=box
            return self.context_menu(self.current,self.results.winfo_rootx()+int(x+width/2),self.results.winfo_rooty()+int(max(0,y)+30))
        return self.context_menu(self.current,self.results.winfo_rootx()+80,self.results.winfo_rooty()+80)

    def detail_sort_popup(self,anchor=None):
        menu=skin_menu(tk.Menu(self.root,tearoff=False))
        for key,label in ((c.key,c.label) for c in COLUMNS):
            menu.add_command(label=label+(" ↓" if self.sort_reverse else " ↑") if key==self.sort_column else label,command=lambda k=key:self.sort_results(k))
        self.active_menu=menu
        button=anchor or self.detail_sort_button
        menu.tk_popup(button.winfo_rootx(),button.winfo_rooty()+button.winfo_height())

    def set_view(self,view):
        if view not in ui_state.VIEWS or view==self.view.get(): return
        # Une bascule de présentation ne quitte pas une fiche en cours d’édition.
        self.clear_drop()
        self.drag=None
        if view=="list" and self.sort_column not in self.results.list_visible:
            self.sort_column,self.sort_reverse="title",False
            self.update_sort_caption();self.refresh_results()
            self.status.set("Tri ramené à Titre : la colonne de tri était masquée dans la Liste.")
        self.view.set(view)
        self.results.set_view(view)
        if self.inline is not None and self.inline.master==self.results:
            bbox=self.results.bbox(self.draft["id"],"title")
            if bbox:
                x,y,width,height=bbox
                self.inline.place(x=x,y=y,width=max(40,width),height=height)
        self.update_view_menu()
        self.update_view_buttons()
        if self.root.focus_get()==self.results: self.results.focus_set()

    def button(self, parent, text, command=lambda: None, style=None, **kwargs):
        tone = {"Primary.TButton": "primary", "Open.TButton": "warm", "Chip.TButton": "chip"}.get(style, "quiet")
        return PillButton(parent, text, command, tone=tone, **kwargs)

    def icon_button(self,parent,label,glyph,command,width=35):
        button=IconButton(parent,label,glyph,command,width)
        button.tip=ControlTip(button,label)
        return button

    def build_shell(self):
        self.panes = ttk.Panedwindow(self.root,orient="horizontal",height=360)
        self.panes.pack(fill="both",expand=True,padx=8,pady=(5,0))
        self._sash_ready = False
        self.panes.bind("<Configure>", lambda e: self.place_initial_sash())
        self.left,self.middle,self.right=(ttk.Frame(self.panes,padding=6) for _ in range(3))
        self.panes.add(self.left,weight=0)
        self.panes.add(self.middle,weight=1)
        self.left.configure(width=252)
        self.masthead=ContextMasthead(self.middle,self.store.images)
        self.masthead.pack(fill="x",padx=4)
        self.search_area=search_area = ttk.Frame(self.middle, padding=(8, 4, 8, 6))
        search_area.pack(fill="x")
        self.search_line=line = ttk.Frame(search_area,width=760,height=40)
        line.pack(anchor="w")
        line.pack_propagate(False)
        self.search_shell=search_shell = Surface(line,height=38,padding=4)
        search_card = search_shell.body
        tk.Label(search_card, text="⌕", background=COLORS["paper"], foreground=COLORS["pine"], font=("Segoe UI",18)).pack(side="left", padx=(7,3))
        field = ttk.Frame(search_card, style="Paper.TFrame")
        field.pack(side="left", expand=True, fill="x", pady=3)
        self.search_entry = ttk.Entry(field, textvariable=self.query, font=("Segoe UI",10), style="Search.TEntry")
        self.search_entry.pack(fill="x")
        placeholder = tk.Label(field, text="Rechercher un fil, un projet…", font=("Segoe UI",10), foreground=COLORS["muted"], background=COLORS["paper"])
        def placeholder_state(event=None):
            if self.query.get() or self.root.focus_get()==self.search_entry:
                placeholder.place_forget()
            else:
                placeholder.place(x=7,y=2)
        placeholder.bind("<Button-1>",lambda e:self.search_entry.focus_set())
        self.query.trace_add("write",lambda *args:placeholder_state())
        self.search_entry.bind("<FocusIn>",placeholder_state)
        self.search_entry.bind("<FocusOut>",placeholder_state)
        placeholder_state()
        self.search_hint=tk.Label(search_card, text="Ctrl K", background=COLORS["paper"], foreground=COLORS["muted"], font=("Segoe UI",8))
        self.search_entry.bind("<Return>",self.search_enter)
        self.search_entry.bind("<KeyRelease>",self.search_changed)
        self.search_entry.bind("<Down>",self.focus_suggestions)
        view_group=Surface(line,width=100,height=39,padding=3)
        view_group.pack(side="right",padx=(30,0))
        self.mode_buttons_frame=view_group.body
        self.search_filters=self.icon_button(line,"Filtres","\ue71c",lambda:self.show_suggestions(True))
        self.search_clear=self.icon_button(line,"Effacer les filtres","\ue75c",self.clear_filters)
        self.search_clear.pack(side="right")
        self.search_filters.pack(side="right",padx=(6,4))
        search_shell.pack(side="left",expand=True,fill="x")
        search_area.bind("<Configure>",self.layout_search)
        self.chips = ttk.Frame(search_area,height=32)
        self.chips.pack_propagate(False)
        self.chips.bind("<Configure>",lambda e:self.refresh_chips())
        self.suggestion_box = ttk.Frame(search_area,style="Paper.TFrame",padding=12)
        ttk.Label(self.suggestion_box,text="SUGGESTIONS  ·  TOUT LE CATALOGUE",style="Caption.TLabel").pack(anchor="w",pady=(0,5))
        self.suggestions = tk.Listbox(self.suggestion_box,height=5,font=("Segoe UI",11),background=COLORS["paper"],foreground=COLORS["ink"],selectbackground=COLORS["pine"],selectforeground=COLORS["paper"],relief="flat",borderwidth=0,highlightthickness=0,exportselection=False)
        self.suggestions.pack(fill="x")
        self.suggestions.bind("<ButtonRelease-1>",self.choose_suggestion)
        self.suggestions.bind("<Return>",self.choose_suggestion)
        self.suggestions.bind("<Escape>",lambda e:self.hide_suggestions())
        nav_surface=Surface(self.left,width=230,height=120)
        nav_surface.pack(fill="both",expand=True)
        nav=nav_surface.body
        nav_title=ttk.Frame(nav,style="Paper.TFrame")
        nav_title.pack(fill="x",pady=(3,10))
        ttk.Label(nav_title,text="Votre espace",style="Inspector.TLabel",font=("Segoe UI",12,"bold")).pack(side="left")
        plus=self.icon_button(self.masthead,"Nouveau fil ou projet","\ue710",lambda:self.plus.tk_popup(plus.winfo_rootx(),plus.winfo_rooty()+34))
        plus.place(x=60,y=69)
        self.preview_button=self.icon_button(self.masthead,"Afficher ou replier l’aperçu","eye",self.toggle_inspector)
        self.preview_button.place(x=101,y=69)
        self.sort_buttons={}
        for mode in ("Alphabétique français","Manuel"):
            command=lambda m=mode:self.set_navigation_sort(m)
            if mode=="Manuel":
                button=self.icon_button(nav_title,"Tri manuel","dots",command,width=35)
            else:
                button=self.button(nav_title,"A-Z",command,width=35,height=32)
                button.tip=ControlTip(button,"Tri alphabétique français")
            button.tone="chip" if mode==self.sort.get() else "quiet"
            button.pack(side="right")
            self.sort_buttons[mode]=button
        tree_box=ttk.Frame(nav,style="Paper.TFrame")
        tree_box.pack(fill="both",expand=True)
        self.nav_icons=navigation_icons(self.root)
        self.tree=NavigationTree(tree_box)
        self.tree.column("#0",width=194,minwidth=140)
        self.tree.pack(side="left",expand=True,fill="both")
        self.tree.bind("<<TreeviewSelect>>",self.select_scope)
        for tag,color in [("drop",COLORS["selection"]),("forbidden",COLORS["invalid"])]:
            self.tree.tag_configure(tag,background=color)
        self.drop_label=ttk.Label(nav,style="PaperMuted.TLabel",padding=7,wraplength=195)
        titlebar=ttk.Frame(self.middle,padding=(8,7,4,8))
        titlebar.pack(fill="x")
        self.results_label=ttk.Label(titlebar,style="Heading.TLabel",font=("Segoe UI",13,"bold"))
        self.results_label.pack(side="left")
        count_pill=tk.Canvas(titlebar,background=COLORS["ivory"],height=25,highlightthickness=0)
        count_pill.pack(side="left",padx=7)
        self.result_count=tk.Label(count_pill,background=COLORS["selection"],foreground=COLORS["pine"],
                                   borderwidth=0,padx=0,pady=0,font=("Segoe UI",9))
        def size_count(event=None):
            width=self.result_count.winfo_reqwidth()+20
            count_pill.configure(width=width)
            count_pill.delete("pill")
            rounded(count_pill,0,1,width,24,12,fill=COLORS["selection"],outline="",tags="pill")
            count_pill.tag_lower("pill")
        count_pill.create_window(10,12,anchor="w",window=self.result_count)
        self.result_count.bind("<Configure>",size_count)
        self.viewbar=ttk.Frame(self.middle)
        self.viewbar.pack(fill="x")
        self.view_buttons={}
        for key,label,glyph in (("list","Liste","\ue8fd"),("detail","Détaillée","\ue8a9"),("mosaic","Mosaïque","\ue80a")):
            button=self.icon_button(self.mode_buttons_frame,label,glyph,lambda k=key:self.set_view(k),width=30)
            button.pack(side="left")
            self.view_buttons[key]=button
        self.detail_sort_button=self.button(self.viewbar,text="Tri · Titre ↑",command=self.detail_sort_popup,width=112,height=28)
        self.mosaic_tools=ttk.Frame(self.viewbar)
        self.mosaic_size_button=self.button(self.mosaic_tools,text="Cartes · Normal ⌄",command=self.mosaic_size_popup,width=136,height=28)
        self.mosaic_size_button.pack(side="left")
        self.mosaic_sort_button=self.button(self.mosaic_tools,text=self.sort_caption,command=lambda:self.detail_sort_popup(self.mosaic_sort_button),width=112,height=28)
        self.mosaic_sort_button.pack(side="right",padx=(5,0))
        self.viewbar.bind("<Configure>",self.layout_view_controls)
        self.update_view_buttons()
        self.work=ttk.Frame(self.middle,padding=12,style="Paper.TFrame")
        self.work_error=tk.StringVar()
        self.work_content=ttk.Frame(self.work,style="Paper.TFrame")
        self.work_content.pack(fill="x")
        self.work_error_label=error_label=ttk.Label(self.work,textvariable=self.work_error,style="Error.TLabel",background=COLORS["paper"],wraplength=650)
        self.work_error.trace_add("write",lambda *args:error_label.pack(anchor="w",pady=(6,0)) if self.work_error.get() else error_label.pack_forget())
        self.results_box=box=ttk.Frame(self.middle,padding=(3,3,3,8))
        box.pack(fill="both",expand=True)
        self.results=ResultsView(box,self.store.images,self.project_icons,self.view.get(),self.mosaic_size.get())
        self.results.heading("#0",text="")
        self.results.column("#0",width=32,minwidth=32,stretch=False)
        for c in COLUMNS:
            self.results.heading(c.key,text=c.label,command=lambda k=c.key:self.sort_results(k))
            self.results.column(c.key,width=c.width,minwidth=c.minimum,maxwidth=c.maximum,stretch=(c.key=='title'))
        self.results.bind("<<ListColumnsChanged>>",self.persist_columns)
        # La largeur des cartes reste stable quand apparaît la barre verticale.
        gutter=ttk.Frame(box,width=8)
        gutter.pack(side="right",fill="y")
        gutter.pack_propagate(False)
        sb=AutoScrollbar(gutter,orient="vertical",command=self.results.yview)
        sb.pack(side="right",fill="y")
        self.results.configure(yscrollcommand=sb.set)
        self.results.pack(side="left",fill="both",expand=True)
        self.results.selection_guard=lambda:self.can_leave()
        self.build_group_bar()
        self.horizontal_scroll=AutoScrollbar(self.middle,orient="horizontal",command=self.results.xview)
        self.horizontal_scroll.pack(fill="x",padx=10)
        self.results.configure(xscrollcommand=self.horizontal_scroll.set)
        self.results.bind("<<TreeviewSelect>>",self.select_record)
        self.results.bind("<<MosaicLayout>>",self.position_mosaic_rename)
        self.results.bind("<Return>",self.result_enter)
        self.results.bind("<Alt-Return>",self.open_focused_action)
        self.results.bind("<Double-Button-1>",self.result_double)
        self.results.bind("<Motion>",self.hover_result,add=True)
        self.empty=ttk.Label(self.middle,text="",style="Muted.TLabel",padding=(12,6),wraplength=600)
        self.empty.pack(anchor="w")
        self.quick_bar=Surface(self.middle,height=52,padding=8)
        self.quick_bar.pack(side="bottom",fill="x",padx=3)
        self.new_fil_button=self.button(self.quick_bar.body,"＋   Nouveau fil",command=lambda:self.new("item"),style="Primary.TButton",height=33)
        self.new_fil_button.pack(side="right")
        self.quick_prompt=ttk.Entry(self.quick_bar.body,style="Quick.TEntry",cursor="xterm",font=("Segoe UI",11))
        self.quick_prompt.insert(0,"Titre du nouveau fil…")
        self.quick_prompt.state(["readonly"])
        self.quick_prompt.bind("<FocusIn>",lambda e:self.new("item"))
        self.quick_prompt.bind("<Button-1>",lambda e:self.new("item") or "break")
        self.quick_prompt.pack(side="left",fill="x",expand=True,padx=(2,8))
        self.quick_scope=ttk.Label(self.quick_bar.body,background=COLORS["selection"],foreground=COLORS["pine"],padding=(7,3))
        self.quick_scope.pack(side="left",padx=4)
        ttk.Label(self.quick_bar.body,text="Ctrl N",style="PaperMuted.TLabel").pack(side="right",padx=(0,8))
        inspector_surface=Surface(self.right,padding=8,width=330,height=120)
        inspector_surface.pack(fill="both",expand=True)
        holder=inspector_surface.body
        self.canvas=tk.Canvas(holder,highlightthickness=0,background=COLORS["paper"],height=80)
        sb=self.inspector_scrollbar=InspectorScrollbar(holder,self.canvas)
        sb.pack(side="right",fill="y")
        self.canvas.pack(side="left",fill="both",expand=True)
        self.canvas.configure(yscrollcommand=sb.set)
        self.editor=ttk.Frame(self.canvas,padding=15,style="Paper.TFrame")
        window=self.canvas.create_window(0,0,window=self.editor,anchor="nw")
        self.editor.bind("<Configure>",lambda e:self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",lambda e:self.canvas.itemconfigure(window,width=e.width))
        self.root.bind_all("<MouseWheel>",self.inspector_wheel,add=True)
        for widget in (self.tree,self.results):
            for button in (1,3):
                widget.bind(f"<ButtonPress-{button}>",lambda e,w=widget,b=button:self.drag_press(e,w,b),add=True)
                widget.bind(f"<B{button}-Motion>",self.drag_motion,add=True)
                widget.bind(f"<ButtonRelease-{button}>",lambda e,w=widget,b=button:self.drag_release(e,w,b),add=True)
        footer=ttk.Frame(self.root,padding=(18,4))
        footer.pack(fill="x")
        ttk.Label(footer,textvariable=self.status,style="Muted.TLabel",font=("Segoe UI",9),wraplength=660).pack(side="left")
        self.data_label=ttk.Label(footer,text="⌂  Catalogue local · "+str(self.store.path),style="Muted.TLabel",font=("Segoe UI",8),cursor="hand2")
        self.data_label.pack(side="right")
        self.data_label.bind("<Button-1>",lambda e:self.open_data())
        self.root.after_idle(self.place_initial_sash)

    def set_navigation_sort(self,mode):
        self.sort.set(mode)
        for name,button in self.sort_buttons.items():
            button.tone="chip" if name==mode else "quiet"
            button.draw()
        self.refresh_tree()

    def layout_search(self,event):
        width=max(1,min(760,event.width-16))
        self.search_line.configure(width=width)
        if width>=600:
            self.search_hint.pack(side="right",padx=8)
        else:
            self.search_hint.pack_forget()

    def place_initial_sash(self, force=False):
        if (force or not self._sash_ready) and self.panes.winfo_ismapped() and self.panes.winfo_width()>600:
            if len(self.panes.panes())==3:
                self.panes.sashpos(1,max(550,self.panes.winfo_width()-min(340,self.panes.winfo_width()//3)))
            self.panes.sashpos(0,min(259,self.panes.winfo_width()//5))
            self._sash_ready = self.panes.sashpos(0)>100

    def bind_keys(self):
        for key, action in [("<Control-k>", self.focus_search), ("<Control-n>", lambda: self.new("item")), ("<Control-Shift-P>", lambda: self.new("project")), ("<Control-s>", self.save_record), ("<F2>", self.rename_selected), ("<Escape>", self.escape)]:
            self.root.bind(key, lambda e, fn=action: (fn(), "break")[1])
        self.tree.bind("<Alt-Up>", lambda e: (self.reorder(-1), "break")[1])
        self.tree.bind("<Alt-Down>", lambda e: (self.reorder(1), "break")[1])
        self.tree.bind("<Menu>", lambda e: self.context_menu(self.scope, self.tree.winfo_rootx()+40, self.tree.winfo_rooty()+80))
        self.results.bind("<Menu>", lambda e:self.results_context_menu())
        # Tk/Windows nomme la touche de menu contextuel « App ».
        self.tree.bind("<App>",lambda e:self.context_menu(self.scope,self.tree.winfo_rootx()+40,self.tree.winfo_rooty()+80))
        self.results.bind("<App>",lambda e:self.results_context_menu())

    def open_data(self):
        self.safe(lambda: os.startfile(self.store.directory))

    def inspector_wheel(self, event):
        if not self.inspector_visible:
            return
        widget = event.widget
        while widget is not None and widget != self.right:
            widget = getattr(widget, "master", None)
        if widget != self.right:
            return
        if isinstance(event.widget, tk.Text) and event.widget.yview() != (0.0, 1.0):
            return
        delta = event.delta
        if delta:
            self.canvas.yview_scroll(-int(delta/120 or (1 if delta>0 else -1))*3,"units")
        return "break"

    def resize(self, width, height):
        self.root.state("normal")
        self.root.geometry(f"{width}x{height}")

    def help(self):
        from .information_ui import open_information
        return open_information(self,'help')

    def about(self):
        from .information_ui import open_information
        return open_information(self,'about')

    def credits(self):
        from .information_ui import open_information
        return open_information(self,'credits')

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
        choices=[]
        if self.scope!="all":
            scope_text = "Projet : " + self.cat.records[self.scope].title + " · contenu direct ×" if self.scope in self.cat.records else "À classer ×"
            choices.append((scope_text,self.global_scope))
        for var, label in [(self.tag, "Tag"), (self.category, "Catégorie")]:
            if var.get():
                choices.append((f"{label} : {var.get()} ×",lambda v=var:self.remove_filter(v)))
        if not choices:
            self.chips.pack_forget()
            return
        self.chips.pack(fill="x",pady=(4,0),after=self.search_line)
        slot=max(30,(self.chips.winfo_width()-5*len(choices))//len(choices))
        for label,command in choices:
            width=min(slot,self.font.measure(label)+28)
            self.button(self.chips,text=shorten(self.font,label,max(4,width-24)),width=width,height=30,style="Chip.TButton",command=command).pack(side="left",padx=(0,5))

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

    def refresh_tree(self,expanded=None):
        had_projects=any(r.kind=="project" and self.tree.exists(r.id) for r in self.cat.records.values())
        opened = set(expanded) if expanded is not None else {p for p in self.cat.records if self.tree.exists(p) and self.tree.item(p, "open")}
        initial_open=expanded is None and not had_projects
        self.tree.delete(*self.tree.get_children())
        self.tree.insert("", "end", iid="all", text="Tous les fils", image=self.nav_icons["all"])
        self.tree.insert("", "end", iid="unfiled", text="À classer", image=self.nav_icons["unfiled"])
        pending = [(r, "") for r in reversed(self.cat.children(None, self.sort.get() != "Manuel"))]
        while pending:
            r, parent = pending.pop()
            self.tree.insert(parent, "end", iid=r.id, text=r.title, image=self.project_icons.for_project(r), open=(r.id in opened or initial_open))
            pending.extend((c, r.id) for c in reversed(self.cat.children(r.id, self.sort.get() != "Manuel")))
        if not self.tree.exists(self.scope):
            self.scope = "all"
        self.tree.selection_set(self.scope)

    def select_scope(self, event=None):
        if self.restoring_workspace: return
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
        selected=self.results.selection() or ((self.current,) if self.current else ())
        anchor,focal=self.results.pick.anchor,self.results.focused
        if getattr(self,"results_scope",self.scope)!=self.scope:selected=()
        self.results_scope=self.scope
        self.results.delete(*self.results.get_children())
        scope = self.scope if self.scope in self.cat.records else None
        rows = self.cat.search(self.query.get().strip(), scope, self.tag.get().strip(), self.category.get().strip(), self.scope == "unfiled")
        if scope:
            # La recherche générique reste récursive ; la navigation montre
            # les rattachements directs et les enfants immédiats uniquement.
            rows = [r for r in rows if (r.kind=="item" and scope in r.projects) or (r.kind=="project" and r.parent==scope)]
        rows = [r for r in rows if r.id != scope]
        if not scope and not self.query.get().strip() and not self.tag.get() and not self.category.get():
            rows = [r for r in rows if r.kind == "item"]
        def values(r):
            context = self.project_label(r.parent) if r.kind == "project" and r.parent else (" · ".join(self.project_label(p) for p in r.projects) if r.kind == "item" else "À la racine")
            if r.kind == "item" and not r.projects:
                context = "À classer"
            return {"title": r.title, "context": context, "categories": list(r.categories), "tags": list(r.tags), "created": r.created, "modified": r.modified}
        rows.sort(key=lambda r: sort_value(values(r),self.sort_column), reverse=self.sort_reverse)
        for r in rows:
            v = values(r)
            visual=resolve_identity(self.cat,r.id,self.scope)
            self.results.insert("", "end", iid=r.id, image=self.project_icons.get(visual.icon,visual.color,20) if r.kind=="item" else self.icons[r.kind], tags=(r.kind,), categories=r.categories, labels=r.tags, summary=r.description, notes=r.notes, visual=visual, cells=v, values=(r.title, v["context"], " · ".join(v["tags"]), datetime.fromisoformat(r.modified).strftime("%d/%m/%Y")))
        self.results.set_selection(selected,anchor,focal)
        self.results.sort_column,self.results.sort_reverse=self.sort_column,self.sort_reverse
        self.results_label.configure(text="Contenu du projet" if scope else "Discussions")
        discussions=sum(r.kind=='item' for r in rows);projects=len(rows)-discussions
        counts=[]
        if discussions:counts.append(f"{discussions} discussion"+('s' if discussions!=1 else ''))
        if projects:counts.append(f"{projects} sous-projet"+('s' if projects!=1 else ''))
        if not counts:counts=['0 discussion']
        self.result_count.configure(text=' · '.join(counts))
        self.empty.configure(text="" if rows else "Ajoutez un fil avec + Fil, ou changez la recherche.")
        if rows:
            self.empty.pack_forget()
        elif not self.empty.winfo_manager():
            self.empty.pack(anchor="w",padx=6)
        self.refresh_chips()
        self.quick_scope.configure(text=shorten(self.font,self.cat.records[scope].title if scope else "À classer",108))
        self.scope_discussions=sum(r.kind=="item" and scope in r.projects for r in self.cat.records.values()) if scope else 0

        self.update_identity()
        self.sync_group()

    def sort_results(self, column):
        self.sort_reverse = not self.sort_reverse if self.sort_column == column else False
        self.sort_column = column
        self.update_sort_caption()
        self.refresh_results()
        self.persist_columns()

    def update_sort_caption(self):
        self.sort_caption="Tri · "+BY_KEY[self.sort_column].label+(" ↓" if self.sort_reverse else " ↑")
        self.mosaic_sort_button.configure(text=self.sort_caption)
        self.layout_view_controls()

    def select_record(self, event=None):
        if self.restoring_workspace: return
        selection = self.results.selection()
        if len(self.group_ids())>1:
            if self.dirty and not self.can_leave():
                self.results.selection_set(getattr(self,"accepted_selection",(self.current,) if self.current else ()))
                return
            self.accepted_selection=selection
            self.sync_group()
            return
        self.sync_group()
        if selection and selection[0] != self.current:
            if not self.select_identity(selection[0]):
                if self.current and self.results.exists(self.current):
                    self.results.selection_set(self.current)
                return
        self.accepted_selection=self.results.selection()

    def select_identity(self, identity, checked=False):
        if identity == self.current:
            return True
        if not checked and not self.can_leave():
            return False
        self.current, self.dirty, self.editing = identity, False, False
        self.update_identity()
        if self.inspector_visible:
            self.show_summary(identity, checked=True)
        return True

    def update_identity(self):
        self.masthead.set_context(resolve_identity(self.cat,self.current,self.scope),self.cat.records.get(self.scope),
                                  getattr(self,"scope_discussions",0),"À classer" if self.scope=="unfiled" else "Tous les fils")

    def ensure_inspector(self):
        if not self.inspector_visible:
            self.panes.add(self.right, weight=0)
            self.inspector_visible = True
            self.root.update_idletasks()
            self.panes.sashpos(1, max(550, self.panes.winfo_width()-min(340,self.panes.winfo_width()//3)))

    def toggle_inspector(self):
        if self.inspector_visible:
            if not self.can_leave():
                return
            self.panes.forget(self.right)
            self.inspector_visible, self.editing = False, False
        else:
            self.ensure_inspector()
            if len(self.group_ids())>1:self.show_group_summary()
            else:self.show_summary(self.current, checked=True)

    def show_summary(self, identity, checked=False):
        if not checked and not self.can_leave():
            return
        if len(self.group_ids())>1:
            self.current=None;self.editing=False
            self.update_identity();self.show_group_summary()
            return
        self.current,self.dirty,self.editing=identity,False,False
        self.update_identity()
        for child in self.editor.winfo_children():
            child.destroy()
        record=self.cat.records.get(identity)
        visual=resolve_identity(self.cat,identity,self.scope)
        def context_project(pid):
            parent=self.cat.records[pid]
            return parent.title,self.project_icons.for_project(parent,size=18)

        self.summary=InspectorSummary(self.editor,record,self.project_label,
            self.toggle_inspector,lambda:self.open_thread(identity),lambda:self.copy_link(identity),lambda:self.show_record(identity),
            self.project_icons.get(visual.icon,visual.color,24),context_project,self.project_icons.get(size=18))
        if record:
            base=inherited_identity(self.cat,record.id,self.scope)
            inherited={"image":base.image or DEFAULTS["image"],"icon":base.icon,"color":base.color} if record.kind=="item" else None
            origin=self.cat.records[base.project].title if base.project else None
            parent=self.summary.visual_row
            self.summary.visual_strip=ProjectVisualStrip(parent,self.store.images,record.visual,inherited=inherited,origin=origin)
            self.summary.arrange_actions()
            parent.bind("<Configure>",self.summary.arrange_actions)
        self.summary.pack(fill="x")
        self.canvas.yview_moveto(0)

    def show_record(self, identity):
        """Entrée explicite de l'édition, également conservée pour les tests MG-001."""
        if not self.individual_allowed():return
        self.ensure_inspector()
        self.editing = True
        self.render_editor(identity)
        self.update_identity()

    def edit_selected(self, identity=None):
        if not self.individual_allowed():return
        identity = identity or self.current
        if identity in self.cat.records and self.can_leave():
            self.show_record(identity)

    def save_record(self):
        if not self.individual_allowed():return False
        if not self.editing or self.current not in self.cat.records:
            return False
        if getattr(self,"visual_layer",None): self.visual_layer.accept()
        return super().save_record()

    def open_thread(self, identity=None):
        if identity is None and not self.individual_allowed():return False
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
        if not self.individual_allowed():return
        def action():
            _, url = parse_url(self.adapter.conversations[identity].url)
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            self.status.set("Lien copié.")
        self.safe(action)

    def title_hit(self, event, identity):
        if self.cat.records[identity].kind != "item":
            return False
        return self.results.open_hit(identity,event.x,event.y)

    def open_click(self, identity):
        previous, timestamp = self.last_open
        if previous == identity and time.monotonic()-timestamp < 0.5:
            return
        self.last_open = (identity, time.monotonic())
        self.open_thread(identity)

    def result_enter(self, event=None):
        if self.root.focus_get()==self.results:
            if self.results.action_focus and self.view.get()!='mosaic':return self.open_focused_action(event)
            identity=self.results.focus()
            if identity in self.cat.records and self.cat.records[identity].kind=="project":
                self.tree.selection_set(identity);self.tree.see(identity)
        return "break"

    def open_focused_action(self,event=None):
        """Activation explicite de ↗ au clavier, sans ouverture sur Entrée seule."""
        if self.root.focus_get()==self.results:
            identity=self.results.focus()
            if identity in self.results.selection():self.open_click(identity)
        return "break"

    def result_double(self, event):
        if getattr(event,"state",0)&5:
            self.results.select_click(event)
            return "break"
        identity=self.results.identify_at(event.x,event.y)
        if identity in self.cat.records and self.cat.records[identity].kind=="project":
            self.tree.selection_set(identity);self.tree.item(identity,open=True)
        # Le second relâchement sur ↗ passe par le même anti-rebond que le premier.
        return "break"

    def hover_result(self, event):
        if self.view.get()=="list" and (self.results.resize_column or self.results.separator_at(event.x,event.y)):
            self.results.configure(cursor="sb_h_double_arrow")
            return
        identity = self.results.identify_at(event.x,event.y)
        opening=identity in self.cat.records and self.title_hit(event,identity)
        self.results.configure(cursor="hand2" if opening else "")
        if opening:
            self.results.hide_tip()
            self.results.tip_timer=self.results.after(450,lambda:self.results.show_open_tip(identity,event.y))

    def tag_quick_click(self,widget):
        # Un bindtag en tête voit aussi les boutons Canvas qui consomment le clic.
        if isinstance(widget,tk.Misc) and self.quick_click_tag not in widget.bindtags():
            widget.bindtags((self.quick_click_tag,*widget.bindtags()))

    def dismiss_quick_draft(self,event):
        draft=self.draft
        if not draft or draft["kind"]!="item" or self.root.grab_current():
            return
        widget=event.widget
        while widget!=self.root:
            if widget==self.work or isinstance(widget,(tk.Menu,tk.Toplevel)) or widget is None:
                return
            widget=widget.master
        # Laisser la cible recevoir son clic, même si refermer le formulaire
        # déplace cette cible ou si son action ouvre un autre brouillon.
        self.root.after_idle(lambda:self.clear_work() if self.draft is draft else None)

    def clear_work(self):
        for child in self.work_content.winfo_children():
            child.destroy()
        self.work_error.set("")
        self.draft = None
        self.work.pack_forget()
        self.work_error_label.configure(foreground=COLORS["error"])
        if not self.quick_bar.winfo_manager():
            self.quick_bar.pack(side="bottom",fill="x",padx=3)

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
            self.tree.insert(host, "end", iid="__draft__", text="", image=self.project_icons.get())
            self.tree.see("__draft__")
            self.root.update_idletasks()
            self.inline = ttk.Entry(self.tree)
            x, y, width, height = self.tree.bbox("__draft__")
            depth=0
            ancestor=host
            while ancestor:
                depth+=1
                ancestor=self.tree.parent(ancestor)
            offset=38+18*depth
            self.inline.place(x=x+offset, y=y, width=max(48,width-offset-2), height=height)
            self.inline.focus_set()
            self.draft = {"kind": "project", "parent": parent}
            self.inline.bind("<Return>", self.commit_inline)
            self.inline.bind("<Escape>", lambda e: self.cancel_inline())
            self.status.set("Nouveau projet · Entrée : créer · Échap : annuler. Aucune image à choisir.")
            return
        self.draft = {"kind": "item", "parent": parent}
        self.quick_bar.pack_forget()
        self.work.pack(side="bottom",fill="x")
        self.work_error_label.configure(foreground=COLORS["form_hint"])
        heading=ttk.Frame(self.work_content,style="Paper.TFrame")
        heading.pack(fill="x")
        ttk.Label(heading,text="Nouveau fil",style="WorkTitle.TLabel").pack(side="left")
        ttk.Label(heading,text=self.project_label(parent) if parent else "À classer",
                  style="PaperMuted.TLabel",wraplength=180).pack(side="right")
        fields=ttk.Frame(self.work_content,style="Paper.TFrame")
        fields.pack(fill="x",pady=(4,6))
        fields.columnconfigure(0,weight=1,uniform="saisie")
        fields.columnconfigure(1,weight=1,uniform="saisie")
        for column,label in enumerate(("Titre du fil","Lien ChatGPT")):
            ttk.Label(fields,text=label,style="PaperMuted.TLabel").grid(row=0,column=column,sticky="w")
        self.new_title=ttk.Entry(fields)
        self.new_url=ttk.Entry(fields)
        self.new_title.grid(row=1,column=0,sticky="ew",padx=(0,4))
        self.new_url.grid(row=1,column=1,sticky="ew",padx=(4,0))
        row=ttk.Frame(self.work_content,style="Paper.TFrame")
        row.pack(fill="x")
        self.button(row,text="→ Ajouter",style="Chip.TButton",command=self.submit_item).pack(side="right")
        self.button(row,text="Annuler · Échap",command=self.clear_work).pack(side="right",padx=(0,20))
        for entry in (self.new_title, self.new_url):
            entry.bind("<Return>", self.submit_item)
        self.root.update_idletasks()
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
                    button = self.button(self.work_content, text="Afficher la fiche existante" + (" et rattacher ici" if parent else ""))
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
            if self.view.get()=="mosaic" and self.inspector_visible and not self.editing:
                self.show_summary(r.id,checked=True)
            if r.kind == "project":
                self.tree.selection_set(r.id)
                self.tree.see(r.id)
            self.status.set("Projet créé." if draft["kind"] == "project" else "Nom local modifié.")
        except (ValueError, OSError) as exc:
            self.status.set(str(exc) + " · Corrigez ou appuyez sur Échap.")
        return "break"

    def rename_selected(self, identity=None):
        if not self.individual_allowed():return
        identity = identity or (self.scope if self.tree.owns_focus() else self.current)
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
        if widget==self.results and self.view.get()=="mosaic":
            self.inline.place(x=x,y=y,width=max(40,width),height=28)
        else:
            self.inline.place(x=x+(24 if widget == self.tree else 0), y=y, width=max(140, width-24), height=height)
        self.inline.insert(0, self.cat.records[identity].title)
        self.inline.selection_range(0, "end")
        self.inline.focus_set()
        self.draft = {"kind": "rename", "id": identity}
        self.inline.bind("<Return>", self.commit_inline)
        self.inline.bind("<Escape>", lambda e: self.cancel_inline())

    def escape(self):
        if getattr(self,"visual_layer",None):
            self.visual_layer.cancel()
            return
        if self.drag:
            self.clear_drop()
            self.drag = None
            return
        if self.inline:
            self.cancel_inline()
            self.status.set("Édition intégrée annulée.")
        elif self.draft:
            self.clear_work()
            self.status.set("Action intégrée annulée.")
        elif self.suggestion_box.winfo_manager():
            self.hide_suggestions()
        elif len(self.group_ids())>1 and not self.editing:
            self.results.collapse_selection()
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
        if len(self.group_ids())>1 and identity in self.group_ids():return self.group_menu(x,y)
        menu = skin_menu(tk.Menu(self.root, tearoff=False))
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
        ttk.Label(self.work_content, text=f"{title} · {r.title}", style="Inspector.TLabel", wraplength=650).pack(anchor="w", pady=4)
        source_ids = list(project_choices(self.cat,r.projects).values()) if r.kind == "item" else []
        self.source_box = None
        context = origin if origin is not None else self.scope
        if r.kind == "item" and mode in ("move", "remove") and source_ids:
            ttk.Label(self.work_content, text="Seul ce rattachement sera retiré ; les autres seront conservés.",style="PaperMuted.TLabel",wraplength=600).pack(anchor="w")
            self.source_box = ttk.Combobox(self.work_content, state="readonly", values=list(project_choices(self.cat,source_ids)))
            self.source_box.pack(fill="x", pady=4)
            if context in source_ids:
                self.source_box.current(source_ids.index(context))
            else:
                self.source_box.set("Choisir le rattachement de départ…")
        destinations = [None] if r.kind == "project" else []
        forbidden = self.cat.descendants(identity) if r.kind == "project" else set()
        destinations += sorted((p.id for p in self.cat.records.values() if p.kind == "project" and p.id not in forbidden), key=self.project_label)
        choices=project_choices(self.cat,[p for p in destinations if p])
        destinations=([None] if r.kind=="project" else [])+list(choices.values())
        self.destination_box = None
        if mode != "remove":
            ttk.Label(self.work_content, text="DESTINATION",style="Caption.TLabel").pack(anchor="w")
            self.destination_box = ttk.Combobox(self.work_content, state="readonly", values=(["À la racine"] if r.kind=="project" else [])+list(choices))
            self.destination_box.pack(fill="x", pady=4)
            if destination in destinations:
                self.destination_box.current(destinations.index(destination))
            elif destinations:
                self.destination_box.set("Choisir une destination…")
        row = ttk.Frame(self.work_content,style="Paper.TFrame")
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
                if r.kind=='item':
                    self.apply_classification((identity,),mode,source,target)
                    self.clear_work()
                    return
                self.transaction(lambda: self.transfer(identity, target, mode, source))
                self.clear_work()
                self.refresh_tree()
                self.refresh_results()
                if self.inspector_visible:
                    self.show_summary(self.current, checked=True)
                if r.kind=='project':self.status.set("Projet déplacé.")
            except (ValueError, OSError) as exc:
                self.work_error.set(str(exc))
        self.button(row, text=title, style="Primary.TButton", command=apply).pack(side="left")
        self.button(row, text="Annuler", command=self.clear_work).pack(side="left", padx=5)
        self.apply_transfer = apply

    def drag_press(self, event, widget, button):
        if widget==self.results and self.view.get()=="list" and event.y<self.results.header_height:
            self.drag=None;return
        identity=widget.identify_at(event.x,event.y) if widget==self.results else widget.identify_row(event.y)
        modified=bool(getattr(event,"state",0)&5)
        if widget==self.results:
            if self.results.gesture_blocked:self.drag=None;return
            if button==3 and identity not in self.results.selection() and identity in self.cat.records:
                if not self.can_leave():self.drag=None;return
                self.results.selection_set(identity);self.select_record()
        ids=self.group_ids() if widget==self.results and identity in self.results.selection() else (identity,)
        self.drag={"id":identity,"ids":ids,"widget":widget,"button":button,"x":event.x_root,"y":event.y_root,
                   "active":False,"origin":self.scope,"double":False,"modified":modified,
                   "open":widget==self.results and not modified and self.title_hit(event,identity) if identity in self.cat.records else False}

    def clear_drop(self):
        for identity in ("all", "unfiled", *self.cat.records):
            if self.tree.exists(identity):
                self.tree.item(identity, tags=())
        self.tree.configure(cursor="")
        self.results.configure(cursor="")
        self.drop_label.pack_forget()

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
        if self.drag and (self.drag.get("modified") or self.drag.get("open")):return
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
        self.drop_label.pack(fill="x",pady=4)
        self.drop_label.configure(background=COLORS["selection" if allowed else "invalid"],text=("↳  Déposer dans " + (self.cat.records[target].title if target in self.cat.records else "la racine")) if allowed else "×  Cible interdite",foreground=COLORS["pine"] if allowed else COLORS["error"])
        count=len(self.drag.get("ids",(self.drag["id"],)))
        subject="le projet" if self.cat.records[self.drag['id']].kind=='project' else f"{count} discussion(s)"
        self.status.set((f"Déplacer {subject} vers " + (self.project_label(target) if target in self.cat.records else "la racine")) if allowed else "Cible interdite.")

    def drag_release(self, event, widget, button):
        drag=self.drag
        if not drag:return
        target,allowed=self.drop_target(event.x_root,event.y_root)
        self.clear_drop();self.drag=None
        identity=drag["id"]
        if drag.get("modified"):return "break"
        if drag["active"]:
            self.results.pending_single=None
            if not allowed:
                self.status.set("Cible interdite.");return "break"
            ids=drag.get("ids",(identity,))
            if button==3 and self.cat.records[identity].kind=="item":
                menu=skin_menu(tk.Menu(self.root,tearoff=False))
                menu.add_command(label="Déplacer ici",command=lambda:self.drop_items(ids,target,"move",drag["origin"]))
                menu.add_command(label="Ajouter un rattachement ici",command=lambda:self.drop_items(ids,target,"add",drag["origin"]))
                menu.add_command(label="Annuler",command=lambda:None)
                self.active_menu=menu;menu.tk_popup(event.x_root,event.y_root)
            elif button==1:
                if self.cat.records[identity].kind=="item":self.drop_items(ids,target,"move",drag["origin"])
                else:self.drop_action(identity,target,"move",drag["origin"])
            return "break"
        if button==3:return self.context_menu(identity,event.x_root,event.y_root)
        if (widget==self.tree and identity==drag["origin"]==self.scope and
                identity in self.cat.records and target==identity and self.current!=identity):
            # Seul un clic explicite terminé sur le projet courant reprend sa fiche.
            # Les notifications de restauration et de rafraîchissement restent passives.
            if self.can_leave():
                self.results.selection_set(())
                self.sync_group()
                self.select_identity(identity,checked=True)
        if widget==self.results:
            if drag.get("open") and identity in self.cat.records and self.title_hit(event,identity):
                self.results.pending_single=None;self.open_click(identity)
            else:
                self.results.finish_single();self.select_record()
        return "break"

    def drop_action(self, identity, target, mode, origin):
        if not self.can_leave():return
        r=self.cat.records.get(identity)
        if r is None:return
        if r.kind=="item":return self.drop_items((identity,),target,mode,origin)
        def action():
            self.transaction(lambda:self.transfer(identity,None if target=="all" else target,mode))
            self.refresh_tree();self.refresh_results()
            if self.inspector_visible:self.show_summary(self.current,checked=True)
            self.status.set("Projet déplacé.")
        self.safe(action)

    def close(self):
        if not self.can_leave():
            return
        try:
            self.save_preferences()
        except (OSError,ValueError) as exc:
            messagebox.showwarning("Préférences non enregistrées", f"Le catalogue reste intact.\n{exc}", parent=self.root)
        if self.search_timer:
            self.root.after_cancel(self.search_timer)
        self.root.destroy()
