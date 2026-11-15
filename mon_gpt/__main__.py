import argparse
import os
import tkinter as tk
from tkinter import messagebox
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Mon GPT<3 — catalogue local")
    parser.add_argument("--data-dir", type=Path, default=Path(os.environ.get("LOCALAPPDATA", Path.home())) / "MonGPT")
    parser.add_argument("--simulate-open", action="store_true", help="Recette isolée : journaliser l'ouverture au lieu de lancer le navigateur")
    args = parser.parse_args()
    if args.simulate_open and args.data_dir.resolve() == (Path(os.environ.get("LOCALAPPDATA", Path.home())) / "MonGPT").resolve():
        parser.error("--simulate-open exige un --data-dir isolé du catalogue utilisateur.")
    root = tk.Tk()
    root.withdraw()
    try:
        from .storage import Store
        from .ui import App
    except ModuleNotFoundError as exc:
        if exc.name!="PIL": raise
        messagebox.showerror("Prérequis manquant", "Pillow est nécessaire pour les images.\nDepuis le dossier de Mon GPT<3, exécutez :\npython -m pip install -r requirements.txt",parent=root)
        root.destroy()
        return 1
    store = Store(args.data_dir)
    try:
        store.acquire()
        catalog, adapter = store.load()
    except (OSError, ValueError) as exc:
        messagebox.showerror("Catalogue inaccessible", f"{exc}\n\nDonnées conservées : {store.path}\nAucune réinitialisation n'a été effectuée.", parent=root)
        root.destroy()
        return 1
    opener = None
    if args.simulate_open:
        def opener(url, new=2):
            with (store.directory / "ouvertures-recette.log").open("a", encoding="utf-8") as log:
                log.write(url + "\n")
            return True
    app = App(root, store, catalog, adapter, opener=opener)
    root.deiconify()
    root.update()
    app.place_initial_sash(force=True)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
