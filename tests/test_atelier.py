"""Corrections ciblées MG-002a ; pas une recette visuelle native."""
import tempfile
import tkinter as tk
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store
from mon_gpt.ui import App
from mon_gpt.atelier import skin_menu


class AtelierTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.cat=Catalog()
        self.a=self.cat.add("Écriture","project")
        self.b=self.cat.add("Carnet","project",self.a.id)
        self.c=self.cat.add("Laboratoire","project")
        self.adapter=ChatGPT(self.cat)
        self.item,_=self.adapter.ingest("Fil fictif","https://chatgpt.com/c/00000000-0000-4000-8000-000000000007")
        self.item.notes="Note commune, à conserver."
        self.cat.attach(self.item.id,[self.a.id])
        self.app=App(self.root,Store(self.temp.name),self.cat,self.adapter,Mock(return_value=True))
        self.root.update_idletasks()

    def test_current_project_is_hidden_only_in_presentation(self):
        self.assertIn(self.a,self.cat.search(project=self.a.id))
        self.app.scope=self.a.id
        self.app.refresh_results()
        self.assertNotIn(self.a.id,self.app.results.get_children())
        self.assertIn(self.b.id,self.app.results.get_children())
        self.assertIn(self.item.id,self.app.results.get_children())

    def test_unambiguous_global_drop_is_immediate(self):
        self.app.drop_action(self.item.id,self.c.id,"move","all")
        self.assertIsNone(self.app.draft)
        self.assertEqual(self.item.projects,[self.c.id])
        self.assertEqual(self.item.notes,"Note commune, à conserver.")

    def test_inspector_restored_before_mapping_keeps_all_panes_visible(self):
        self.app.ensure_inspector()
        self.app.show_summary(None,checked=True)
        self.root.deiconify()
        self.root.update()
        self.app.place_initial_sash(force=True)
        self.root.update()
        self.assertGreater(self.app.panes.sashpos(0),180)
        self.assertGreater(self.app.panes.sashpos(1)-self.app.panes.sashpos(0),250)
        self.assertGreater(self.app.right.winfo_width(),200)

    def test_multi_attachment_drop_asks_without_removing_anything(self):
        self.cat.attach(self.item.id,[self.a.id,self.b.id])
        self.app.drop_action(self.item.id,self.c.id,"move","all")
        self.assertEqual(self.item.projects,[self.a.id,self.b.id])
        self.assertEqual(self.app.source_box.current(),-1)
        self.app.escape()
        self.assertEqual(self.item.projects,[self.a.id,self.b.id])

    def test_inspector_wheel_does_not_steal_tree_or_list_focus(self):
        self.root.deiconify()
        self.app.ensure_inspector()
        self.app.show_summary(self.item.id,checked=True)
        self.root.update()
        before=self.app.canvas.yview()
        focused=self.root.focus_get()
        for widget in (self.app.tree,self.app.results,self.app.search_entry):
            self.assertIsNone(self.app.inspector_wheel(SimpleNamespace(widget=widget,delta=-120)))
        self.assertEqual(self.app.canvas.yview(),before)
        self.assertEqual(self.app.inspector_wheel(SimpleNamespace(widget=self.app.editor,delta=-120)),"break")
        self.root.update()
        self.assertGreater(self.app.canvas.yview()[0],before[0])
        self.assertEqual(self.root.focus_get(),focused)

    def test_styled_menu_escape_and_keyboard_invoke(self):
        self.root.deiconify()
        self.root.update()
        action=Mock()
        menu=skin_menu(tk.Menu(self.root,tearoff=False))
        menu.add_command(label="Action fictive",command=action)
        menu.tk_popup(200,200)
        self.root.update()
        self.assertTrue(menu._atelier_skin.window.winfo_ismapped())
        self.assertEqual(menu._atelier_skin.window.master,self.root)
        menu._atelier_skin.window.event_generate("<Escape>")
        self.root.update()
        action.assert_not_called()
        menu.tk_popup(200,200)
        self.root.update()
        menu._atelier_skin.window.event_generate("<Return>")
        self.root.update()
        action.assert_called_once()

    def test_styled_menu_click_uses_clicked_row_not_stale_hover(self):
        self.root.deiconify()
        self.root.update()
        first,second=Mock(),Mock()
        menu=skin_menu(tk.Menu(self.root,tearoff=False))
        menu.add_command(label="Première action",command=first)
        menu.add_command(label="Deuxième action",command=second)
        menu.tk_popup(200,200)
        self.root.update()
        canvas=menu._atelier_skin.window.winfo_children()[0]
        canvas.event_generate("<ButtonRelease-1>",x=80,y=64)
        self.root.update()
        first.assert_not_called()
        second.assert_called_once()
