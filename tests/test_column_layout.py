"""Régressions de géométrie, sans modifier les contrats métier précédents."""
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store
from mon_gpt.ui import App


class ColumnLayoutTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.cat=Catalog()
        self.project=self.cat.add("Projet fictif au titre long","project")
        self.adapter=ChatGPT(self.cat)
        self.item,_=self.adapter.ingest("Fil fictif","https://chatgpt.com/c/00000000-0000-4000-8000-000000000007")
        self.item.tags=["Créativité"]
        self.item.categories=["Écriture"]
        self.cat.attach(self.item.id,[self.project.id])
        self.app=App(self.root,Store(self.temp.name),self.cat,self.adapter,Mock(return_value=True))
        self.root.deiconify()
        self.root.update()
        self.app.place_initial_sash(force=True)
        self.root.update()
        self.root.focus_force()

    def assert_inside(self,child,parent):
        self.assertGreaterEqual(child.winfo_rootx(),parent.winfo_rootx())
        self.assertLessEqual(child.winfo_rootx()+child.winfo_width(),parent.winfo_rootx()+parent.winfo_width())

    def test_columns_start_below_menu_and_search_is_bounded(self):
        for width,height in [(1360,820),(1000,680),(1800,1000)]:
            self.app.resize(width,height)
            self.root.update()
            menu_bottom=self.app.main_menu.winfo_rooty()+self.app.main_menu.winfo_height()
            self.assertLessEqual(self.app.left.winfo_rooty()-menu_bottom,20)
            self.assertEqual(self.app.left.winfo_rooty(),self.app.middle.winfo_rooty())
            self.assertIs(self.app.masthead.master,self.app.middle)
            self.assertLessEqual(self.app.search_line.winfo_width(),760)
            self.assertLessEqual(self.app.search_line.winfo_height(),40)
            self.assert_inside(self.app.search_line,self.app.middle)
            self.assertGreater(self.app.results.winfo_height(),300)
            self.assertFalse(self.app.chips.winfo_ismapped())

    def test_compact_repeated_preview_and_suggestions_keep_selection_and_filters(self):
        self.app.resize(1000,680)
        self.app.scope=self.project.id
        self.app.tag.set("Créativité")
        self.app.category.set("Écriture")
        self.app.refresh_results()
        self.app.select_identity(self.item.id,checked=True)
        self.root.update()
        for _ in range(3):
            wide=self.app.middle.winfo_width()
            self.app.toggle_inspector()
            self.root.update()
            self.assertEqual(self.app.left.winfo_rooty(),self.app.right.winfo_rooty())
            self.assertGreater(self.app.middle.winfo_width(),300)
            self.assertGreater(self.app.right.winfo_width(),250)
            for widget in (self.app.search_line,self.app.search_filters,self.app.search_clear,self.app.new_fil_button,self.app.preview_button):
                self.assertTrue(widget.winfo_ismapped())
                self.assert_inside(widget,self.app.middle)
            for chip in self.app.chips.winfo_children():
                self.assert_inside(chip,self.app.middle)
            self.app.focus_search()
            self.root.update()
            self.assertIs(self.root.focus_get(),self.app.search_entry)
            self.app.show_suggestions(True)
            self.root.update()
            self.assert_inside(self.app.suggestion_box,self.app.middle)
            self.app.hide_suggestions()
            self.app.toggle_inspector()
            self.root.update()
            self.assertGreaterEqual(self.app.middle.winfo_width(),wide)
            self.assertEqual(self.app.current,self.item.id)
            self.assertEqual(self.app.tag.get(),"Créativité")
            self.assertEqual(self.app.category.get(),"Écriture")


if __name__=="__main__":
    unittest.main()
