"""Références documentaires de la version depuis les sources, sans accès réseau."""
from dataclasses import dataclass
from pathlib import Path
import platform
import PIL


NOTICES=Path(__file__).with_name('notices')


@dataclass(frozen=True)
class Component:
    name: str
    role: str
    license: str
    reference: str
    file: str
    url: str
    detail: str


COMPONENTS=(
    Component('Python', 'Exécution et bibliothèque standard', 'PSF-2.0 et historiques', '3.13.17',
              'python-3.13.17-windows.txt','https://docs.python.org/3.13/license.html',
              'Interpréteur installé séparément. Tkinter fait partie de sa bibliothèque standard. '
              'Le texte de référence conserve les licences PSF, BeOpen, CNRI, CWI, les exemples sous 0BSD et les avis supplémentaires du runtime Windows observé.'),
    Component('Tcl', 'Moteur de l’interface Tk', 'Termes Tcl', '8.6.15',
              'tcl-8.6.15.txt','https://github.com/tcltk/tcl/blob/core-8-6-15/license.terms',
              'Runtime fourni avec l’installation Python/Tk de référence. Ses termes propres sont distincts de la licence Python et de ceux de Tk.'),
    Component('Tk', 'Fenêtres et composants graphiques', 'Termes Tk', '8.6.15',
              'tk-8.6.15.txt','https://github.com/tcltk/tk/blob/core-8-6-15/license.terms',
              'Bibliothèque graphique utilisée via Tkinter, ttk et Canvas. Le texte officiel de Tk est conservé séparément de celui de Tcl.'),
    Component('Pillow', 'Lecture et traitement des images', 'MIT-CMU', '13.0.0',
              'pillow-13.0.0-windows.txt','https://github.com/python-pillow/Pillow/blob/13.0.0/LICENSE',
              'Seule dépendance Python tierce d’exécution déclarée dans requirements.txt : Pillow==13.0.0. '
              'Les notices complètes de la wheel Windows de référence incluent ses avis de codecs et sous-composants ; ils ne sont pas tous des fonctions utilisées par Mon GPT<3.'),
)

INTRO='Mon GPT<3 utilise ces composants tiers. Merci à leurs auteurs et contributeurs, sans partenariat ni parrainage implicite.'
SCOPE=('Trucabule crée et distribue Mon GPT<3. La licence générale de son code n’est pas encore fixée. '
       'Les licences des composants tiers ne constituent pas une licence du logiciel Trucabule.\n\n'
       'Cette application fonctionne actuellement depuis les sources. Python et Tcl/Tk sont des prérequis installés séparément ; '
       'Pillow est installé via requirements.txt. Les versions affichées sont celles de cette session. Les notices locales sont '
       'des références complètes pour Python 3.13.17 Windows, Tcl/Tk 8.6.15 et Pillow 13.0.0 Windows x64 (CPython 3.13). '
       'Si votre installation diffère, consulter également les notices fournies avec celle-ci.\n\n'
       'Le Collector Chrome est un compagnon distinct. Puppeteer est réservé à ses tests et ne fait pas partie de l’application de bureau.\n\n'
       'RT-001 demeure un audit partiel. Cette fenêtre ne certifie pas une distribution binaire : runtimes, DLL, codecs et ressources '
       'effectivement redistribués devront être revérifiés au moment d’un futur packaging Windows. Les droits des illustrations '
       'ne sont pas déduits des licences de Python ou Pillow. Aucun installateur n’est préparé ici.')


def runtime_versions(root):
    return (platform.python_version(),str(root.tk.call('info','patchlevel')),
            str(root.tk.call('package','present','Tk')),PIL.__version__)


def read_notice(component):
    return (NOTICES/component.file).read_text(encoding='utf-8')
