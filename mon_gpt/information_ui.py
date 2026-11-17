"""Fenêtres d'information de l'application ; aucune mutation métier."""
import tkinter as tk
from tkinter import ttk
import webbrowser
from .theme import COLORS as C
from . import __version__


HELP={
    'Navigation': "Tous les fils et À classer restent épinglés au-dessus des projets. Seuls les projets défilent.\n\nUn projet montre son contenu direct : discussions rattachées et sous-projets immédiats. Les descendants indirects se consultent dans leur propre dossier.\n\nFlèches dans l’arbre : parcourir les dossiers. À la frontière, Haut/Bas passe entre les entrées épinglées et les projets. Alt+↑ / Alt+↓ réorganise les projets en tri manuel.",
    'Sélection': "Ligne, titre, icône ou couverture : sélectionner, sans ouvrir ChatGPT.\n\nCtrl+clic ajoute ou retire un fil. Maj+clic sélectionne une plage dans l’ordre visible. Ctrl+Maj+clic ajoute la plage au lot.\n\nCtrl+A dans les résultats sélectionne tous les fils visibles selon les critères, même hors écran. Dans un champ, il sélectionne le texte. Les projets ne sont pas inclus dans les lots.\n\nMaj+flèches étend la sélection ; en Mosaïque les flèches suivent la grille. Échap réduit le lot après les traitements d’édition ou de glisser. Le passage entre les trois vues conserve le lot.",
    'Classement': "Une fiche ou plusieurs : les mêmes gestes.\n\nGlisser gauche vers un projet : déplacer le rattachement source commun vers ce projet. Les autres emplacements sont conservés.\n\nGlisser droit : choisir Déplacer ici ou Ajouter un rattachement ici. Ajouter signifie créer un emplacement supplémentaire, jamais dupliquer une fiche.\n\nClic droit / touche Menu : déplacer, ajouter ou retirer un rattachement. Une source connue s’applique directement ; s’il en existe plusieurs, choisir l’emplacement à remplacer.\n\nRetirer le dernier rattachement place le fil dans À classer, sans supprimer la fiche. Un projet garde un seul parent et se déplace individuellement.",
    'Ouvrir ↗': "↗ ouvre uniquement le fil visé dans ChatGPT, même avec un lot actif, sans détruire la sélection.\n\nAlt+Entrée active explicitement ↗ du fil focal. En Liste et Détaillée, Droite focalise aussi l’action ↗, puis Entrée l’active ; Gauche revient au titre.\n\nUn clic ou double-clic sur un titre ne lance aucune URL. Entrée sur une ligne n’ouvre pas ChatGPT tant que l’action ↗ n’est pas focalisée.\n\nL’aperçu possède aussi son bouton explicite d’ouverture. Les projets ne s’ouvrent pas dans ChatGPT.",
    'Édition': "F2 renomme la fiche sélectionnée. Modifier la fiche ouvre l’éditeur.\n\nLes emplacements enregistrés sont visibles en haut. Les rattachements actuels viennent en premier dans la liste ; Ctrl+clic permet d’en choisir plusieurs. Enregistrer applique les champs et les rattachements.\n\nRésumé et Notes restent distincts. Détaillée et Mosaïque affichent leurs extraits ; l’aperçu et l’éditeur donnent le texte complet.\n\nCtrl+S enregistre la fiche. Quitter une saisie non enregistrée conserve la règle existante : enregistrer, abandonner ou rester dans le brouillon. Images, icônes et couleurs des fils peuvent être personnelles ou héritées du projet.",
    'Recherche': "Ctrl+K focalise la recherche. Titres, résumés, notes, tags, catégories et informations sont recherchés sans distinction de casse ou d’accents.\n\nLes filtres peuvent combiner projet, tag et catégorie. Les pastilles × retirent un critère. Tous les fils retire le périmètre projet sans effacer les autres critères.\n\nLe bandeau renseigne le projet courant, même si un fil est sélectionné ; son identité visuelle peut refléter ce fil. L’aperçu reste facultatif.\n\nÀ la fermeture normale, vue, taille de cartes, critères, projet, branches et sélection simple sont mémorisés, sans ouvrir de fil au démarrage. Aucun lot caché n’est restauré.",
    'Colonnes': "Affichage → Colonnes de la liste… : choisir les colonnes, leur ordre et leurs largeurs. Appliquer mémorise ; Fermer ignore les changements non appliqués.\n\nGlisser un séparateur d’en-tête ajuste sa largeur. Le titre et ↗ restent épinglés, les colonnes secondaires défilent horizontalement dans l’ordre choisi.\n\nCréation et Modification sont les dates de la fiche locale Mon GPT<3, pas celles d’origine de la conversation ChatGPT. Leur tri est chronologique.\n\nCes réglages restent dans interface.json, hors catalogue et sauvegarde métier. La fenêtre Windows se redimensionne librement et sa taille est mémorisée.",
    'Raccourcis': "Ctrl+K — Rechercher\nCtrl+N — Nouveau fil\nCtrl+Maj+P — Nouveau projet\nCtrl+A — Tous les fils des résultats / texte du champ focalisé\nCtrl+clic — Ajouter ou retirer une sélection\nMaj+clic / Maj+flèches — Étendre la sélection\nCtrl+Maj+clic — Ajouter une plage\nAlt+Entrée — Activer ↗ du fil focal\nF2 — Renommer une fiche\nCtrl+S — Enregistrer l’éditeur\nMenu — Actions contextuelles\nAlt+↑ / Alt+↓ dans l’arbre — Ordre manuel\nÉchap — Annuler l’action en cours ou réduire un lot\n\nFichier propose l’import Collector et les sauvegardes/restaurations du catalogue avec ses images personnelles. Aucun classement local ne modifie le compte ChatGPT."
}


class InformationWindow(tk.Toplevel):
    def __init__(self,app,title,width=760,height=560):
        super().__init__(app.root)
        self.app=app;self.previous_focus=app.root.focus_get()
        self.title(title+' · Mon GPT<3');self.transient(app.root);self.configure(background=C['ivory'])
        self.geometry(f'{width}x{height}+{max(0,(self.winfo_screenwidth()-width)//2)}+{max(0,(self.winfo_screenheight()-height)//2-30)}')
        self.minsize(600,430);self.protocol('WM_DELETE_WINDOW',self.close)
        self.bind('<Escape>',lambda e:(self.close(),'break')[1])
        outer=ttk.Frame(self,padding=22);outer.pack(fill='both',expand=True)
        footer=ttk.Frame(outer);footer.pack(side='bottom',fill='x',pady=(12,0))
        self.close_button=ttk.Button(footer,text='Fermer',command=self.close);self.close_button.pack(side='right')
        ttk.Label(outer,text=title,style='Heading.TLabel',font=('Segoe UI',19,'bold')).pack(anchor='w',pady=(0,14))
        self.content=ttk.Frame(outer);self.content.pack(fill='both',expand=True)

    def close(self):
        target=self.previous_focus
        self.destroy()
        if target is not None and target.winfo_exists():target.focus_set()
        else:self.app.results.focus_set()


class HelpWindow(InformationWindow):
    def __init__(self,app):
        super().__init__(app,'Gestes et raccourcis')
        self.sections=tk.Listbox(self.content,width=17,exportselection=False,font=('Segoe UI',10),background=C['paper'],foreground=C['ink'],selectbackground=C['selection'],selectforeground=C['pine'],relief='flat',highlightthickness=1,highlightbackground=C['line'])
        self.sections.pack(side='left',fill='y',padx=(0,16))
        for name in HELP:self.sections.insert('end',name)
        right=ttk.Frame(self.content);right.pack(side='left',fill='both',expand=True)
        self.section_title=ttk.Label(right,font=('Segoe UI',13,'bold'),foreground=C['pine']);self.section_title.pack(anchor='w',pady=(0,8))
        self.text=tk.Text(right,wrap='word',font=('Segoe UI',10),background=C['paper'],foreground=C['ink'],relief='flat',padx=12,pady=10,width=1,height=1)
        scroll=ttk.Scrollbar(right,command=self.text.yview);scroll.pack(side='right',fill='y')
        self.text.configure(yscrollcommand=scroll.set);self.text.pack(fill='both',expand=True)
        self.text.bind('<Tab>',lambda e:(self.text.tk_focusNext().focus_set(),'break')[1])
        self.text.bind('<Shift-Tab>',lambda e:(self.text.tk_focusPrev().focus_set(),'break')[1])
        self.sections.bind('<<ListboxSelect>>',self.show_section)
        self.sections.selection_set(0);self.show_section();self.sections.focus_set()

    def show_section(self,event=None):
        if not self.sections.curselection():return
        name=list(HELP)[self.sections.curselection()[0]];self.section_title.configure(text=name)
        self.text.configure(state='normal');self.text.delete('1.0','end');self.text.insert('1.0',HELP[name]);self.text.configure(state='disabled');self.text.yview_moveto(0)


class AboutWindow(InformationWindow):
    def __init__(self,app):
        super().__init__(app,'À propos de Mon GPT<3',640,460)
        for text,font in [(f'Version {__version__}',('Segoe UI',15,'bold')),
            ('Votre organisation, en local.',('Segoe UI',12)),
            ('Mon GPT<3 organise les discussions en projets et permet de retrouver leurs liens, notes et repères personnels.',('Segoe UI',11)),
            ('Les classements, notes, images et préférences restent locaux. Déplacer ou ajouter un rattachement ne modifie jamais votre compte ChatGPT.',('Segoe UI',11)),
            ('Une ouverture explicite par ↗ lance le navigateur vers le fil choisi.',('Segoe UI',11))]:
            label=ttk.Label(self.content,text=text,font=font,wraplength=580,justify='left');label.pack(anchor='w',fill='x',pady=(0,12))
            self.content.bind('<Configure>',lambda e,w=label:w.configure(wraplength=max(100,e.width)),add='+')
        self.repository=ttk.Button(self.content,text='Voir le dépôt GitHub ↗',command=lambda:webbrowser.open('https://github.com/ugadavid/Mon-GPT',new=2))
        self.repository.pack(anchor='w',pady=4);self.close_button.focus_set()


def open_information(app,kind):
    if kind=='credits':
        from .credits_ui import CreditsWindow
        factory=CreditsWindow
    else:factory={'help':HelpWindow,'about':AboutWindow}[kind]
    attribute={'help':'help_window','about':'about_window','credits':'credits_window'}[kind]
    window=getattr(app,attribute,None)
    if window is not None and window.winfo_exists():window.lift();window.focus_set();return window
    window=factory(app)
    setattr(app,attribute,window)
    return window
