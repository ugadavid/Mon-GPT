"""Contrats du menu principal, distinct des menus contextuels MG-002a."""
import tkinter as tk
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from mon_gpt.main_menu import MainMenuBar


class MainMenuTests(unittest.TestCase):
    def setUp(self):
        self.root=tk.Tk()
        self.root.geometry("1000x680")
        self.addCleanup(self.root.destroy)
        self.actions=[Mock() for _ in range(4)]
        self.menus=[]
        for name,action in zip(("Fichier","Édition","Affichage","Aide"),self.actions):
            menu=tk.Menu(self.root,tearoff=False)
            menu.add_command(label="Indisponible",state="disabled")
            menu.add_separator()
            menu.add_command(label=name,command=action,accelerator="Ctrl+S" if name=="Édition" else "")
            self.menus.append((name,menu))
        self.bar=MainMenuBar(self.root,self.menus)
        self.bar.pack(fill="x")
        self.entry=tk.Entry(self.root)
        self.entry.pack()
        self.root.update()
        self.root.focus_force()
        self.entry.focus_set()
        self.root.update()

    def test_escape_restores_content_focus_and_releases_grab(self):
        self.bar.open(0)
        self.root.update()
        self.assertIs(self.root.grab_current(),self.bar.window)
        self.bar.window.event_generate("<Escape>")
        self.root.update()
        self.assertIs(self.root.focus_get(),self.entry)
        self.assertIsNone(self.root.grab_current())
        self.assertIsNone(self.bar.active)

    def test_keyboard_crosses_headings_skips_disabled_and_invokes_once(self):
        self.bar.keyboard_bar()
        self.bar.event_generate("<Down>")
        self.root.update()
        self.bar.window.event_generate("<Right>")
        self.root.update()
        self.assertEqual(self.bar.active,1)
        self.bar.window.event_generate("<Down>")
        self.bar.window.event_generate("<Return>")
        self.root.update()
        self.actions[1].assert_called_once()
        self.actions[0].assert_not_called()
        self.assertIs(self.root.focus_get(),self.entry)
        self.assertEqual(self.menus[1][1].entrycget(2,"accelerator"),"Ctrl+S")

    def test_hover_switch_and_outside_click_close_without_action(self):
        self.bar.open(0)
        self.root.update()
        old=self.bar.window
        a,b=self.bar.bounds[2]
        self.bar.motion(SimpleNamespace(x_root=self.bar.winfo_rootx()+a+10,y_root=self.bar.winfo_rooty()+18))
        self.root.update()
        self.assertEqual(self.bar.active,2)
        self.assertFalse(old.winfo_exists())
        self.bar.press(SimpleNamespace(x_root=self.bar.winfo_rootx()+a+10,y_root=self.bar.winfo_rooty()+18))
        self.root.update()
        self.assertEqual(self.bar.active,2)  # Cliquer la nouvelle rubrique après survol la garde ouverte.
        win=self.bar.window
        win.event_generate("<ButtonPress-1>",x=800,y=450)
        self.root.update()
        self.assertIsNone(self.bar.active)
        self.assertIsNone(self.root.grab_current())
        self.assertIs(self.root.focus_get(),self.entry)
        for action in self.actions:
            action.assert_not_called()

    def test_click_uses_hit_row_and_restores_focus(self):
        self.bar.open(0)
        self.root.update()
        self.bar.selected=0  # Une ancienne position ne doit jamais être invoquée.
        self.bar.popup_canvas.event_generate("<ButtonRelease-1>",x=90,y=62)
        self.root.update()
        self.actions[0].assert_called_once()
        self.assertIs(self.root.focus_get(),self.entry)
        self.assertIsNone(self.root.grab_current())


if __name__=="__main__":
    unittest.main()
