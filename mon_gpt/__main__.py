import argparse
import os
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from .storage import Store
from .ui import App


def main():
    parser = argparse.ArgumentParser(description="Mon GPT<3 — catalogue local")
    parser.add_argument("--data-dir", type=Path, default=Path(os.environ.get("LOCALAPPDATA", Path.home())) / "MonGPT")
    args = parser.parse_args()
    root = tk.Tk()
    root.withdraw()
    store = Store(args.data_dir)
    try:
        store.acquire()
        catalog, adapter = store.load()
    except (OSError, ValueError) as exc:
        messagebox.showerror("Catalogue inaccessible", f"{exc}\n\nDonnées conservées : {store.path}\nAucune réinitialisation n'a été effectuée.", parent=root)
        root.destroy()
        return 1
    App(root, store, catalog, adapter)
    root.deiconify()
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
