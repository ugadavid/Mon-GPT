"""Petits composants ttk réutilisables dans les écrans d'organisation."""
import tkinter as tk
from tkinter import ttk
from .core import fold


class ChipPicker(ttk.Frame):
    def __init__(self, parent, values, suggestions, changed):
        super().__init__(parent)
        self.values = list(values)
        self.suggestions, self.changed = suggestions, changed
        self.chips = ttk.Frame(self)
        self.chips.pack(fill="x")
        row = ttk.Frame(self)
        row.pack(fill="x", pady=(3, 0))
        self.input = ttk.Combobox(row, values=self.known(), width=18)
        self.input.pack(side="left", fill="x", expand=True)
        self.input.bind("<<ComboboxSelected>>", self.add)
        self.input.bind("<Return>", self.add)
        self.input.bind("<KeyRelease>", self.suggest)
        ttk.Button(row, text="+ Ajouter", command=self.add).pack(side="left", padx=(5, 0))
        self.hint = ttk.Label(self, style="Muted.TLabel", wraplength=300)
        self.hint.pack(anchor="w")
        self.redraw()

    def known(self):
        return sorted(set(self.suggestions()), key=fold)

    def suggest(self, event=None):
        value = fold(self.input.get())
        self.input.configure(values=[x for x in self.known() if value in fold(x)])

    def add(self, event=None):
        value = self.input.get().strip()
        if value and "," not in value:
            value = next((known for known in self.known() if fold(known) == fold(value)), value)
            if value not in self.values:
                self.values.append(value)
                self.changed()
            self.input.set("")
            self.redraw()
        elif value:
            self.hint.configure(text="Ajoutez une valeur à la fois, sans virgule.")
        return "break"

    def remove(self, value):
        self.values.remove(value)
        self.changed()
        self.redraw()

    def redraw(self):
        for child in self.chips.winfo_children():
            child.destroy()
        for n, value in enumerate(self.values):
            ttk.Button(self.chips, text=value + " ×", style="Chip.TButton", command=lambda v=value: self.remove(v)).grid(row=n//2, column=n%2, sticky="w", padx=(0, 4), pady=2)
        self.hint.configure(text="Choisissez une valeur connue ou saisissez-en une nouvelle." if self.known() else "Aucune valeur connue : créez la première ici.")

    def get(self):
        return list(self.values)
