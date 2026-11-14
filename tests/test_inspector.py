"""Régressions ciblées du panneau droit MG-002b-04."""
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store
from mon_gpt.ui import App


class InspectorTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.cat=Catalog()
        self.project=self.cat.add("Projet fictif","project")
        self.adapter=ChatGPT(self.cat)
        self.item,_=self.adapter.ingest("Un long titre fictif pour notre inspecteur compact et lisible","https://chatgpt.com/c/00000000-0000-4000-8000-000000000007")
        self.opener=Mock(return_value=True)
        self.app=App(self.root,Store(self.temp.name),self.cat,self.adapter,self.opener)
        self.root.deiconify()
        self.root.update()
        self.app.ensure_inspector()
        self.root.update()
        self.root.focus_force()

    def show(self,identity):
        self.app.show_summary(identity,checked=True)
        self.root.update()

    def test_three_actions_same_row_at_both_sizes_and_keyboard_callbacks(self):
        for width,height in [(1360,820),(1000,680)]:
            self.app.resize(width,height)
            self.show(self.item.id)
            actions=self.app.summary.actions
            self.assertEqual(set(actions),{"open","copy","edit"})
            self.assertEqual(len({w.winfo_rooty() for w in actions.values()}),1)
            for w in actions.values():
                self.assertTrue(w.winfo_ismapped())
                self.assertLessEqual(w.winfo_rootx()+w.winfo_width(),self.app.right.winfo_rootx()+self.app.right.winfo_width())
        actions["open"].focus_set()
        self.root.update()
        actions["open"].event_generate("<Return>")
        self.root.update()
        self.opener.assert_called_once_with(self.adapter.conversations[self.item.id].url,new=2)
        actions["copy"].activate()
        self.assertEqual(self.root.clipboard_get(),self.adapter.conversations[self.item.id].url)
        actions["edit"].activate()
        self.assertTrue(self.app.editing)
        self.app.show_summary(self.item.id)
        self.assertFalse(self.app.editing)

    def test_long_notes_complete_scrollbar_reappears_and_new_fiche_starts_at_top(self):
        self.show(None)
        self.assertFalse(self.app.inspector_scrollbar.winfo_ismapped())
        self.item.notes="Début de note fictive.\n"*200+"FIN CONSERVÉE"
        self.show(self.item.id)
        self.assertFalse(self.app.summary.notes.expanded)
        self.app.summary.notes.toggle()
        self.root.update()
        self.assertEqual(self.app.summary.notes.body.cget("text"),self.item.notes)
        self.assertTrue(self.app.inspector_scrollbar.winfo_ismapped())
        self.assertGreaterEqual(self.app.inspector_scrollbar.winfo_width(),9)
        self.app.canvas.yview_moveto(1)
        self.root.update()
        self.assertGreater(self.app.canvas.yview()[0],0)
        self.show(self.project.id)
        self.assertEqual(self.app.canvas.yview()[0],0)

    def test_project_empty_fields_and_no_chatgpt_actions(self):
        self.show(self.project.id)
        self.assertEqual(set(self.app.summary.actions),{"edit"})
        text="\n".join(w.cget("text") for w in self.app.summary.labels)
        for value in ("Pas de description","À la racine","Aucune catégorie","Aucun tag"):
            self.assertIn(value,text)
        self.assertEqual(self.app.summary.notes.body.cget("text"),"Aucune note")
        self.opener.assert_not_called()

    def test_action_tooltip_has_text_and_disappears_on_change(self):
        self.show(self.item.id)
        button=self.app.summary.actions["copy"]
        button.show_tip()
        self.root.update()
        tip=button.tip
        self.assertTrue(tip.winfo_ismapped())
        self.assertEqual(tip.winfo_children()[0].cget("text"),"Copier le lien")
        self.show(self.project.id)
        self.assertFalse(tip.winfo_exists())


if __name__=="__main__": unittest.main()
