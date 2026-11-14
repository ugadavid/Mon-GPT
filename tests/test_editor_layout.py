"""Régressions locales de la disposition et des getters de l'éditeur."""
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store
from mon_gpt.ui import App


class EditorLayoutTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.cat=Catalog()
        self.p=self.cat.add("Premier projet","project")
        self.q=self.cat.add("Second projet","project")
        self.adapter=ChatGPT(self.cat)
        self.item,_=self.adapter.ingest("Un titre fictif long pour vérifier tous les champs","https://chatgpt.com/c/00000000-0000-4000-8000-000000000007?exemple=fictif")
        self.cat.attach(self.item.id,[self.p.id,self.q.id])
        self.item.tags=["Été","Mer","Idées","Lune","Une très longue étiquette fictive qui revient à la ligne sans masquer son retrait"]
        self.item.categories=["Écriture","Voyage","Imaginaire"]
        self.item.notes=("Note complète, à conserver.\n"*50).strip()
        self.item.metadata={"État":"Fictif","Atelier":"Recette"}
        self.store=Store(self.temp.name)
        self.app=App(self.root,self.store,self.cat,self.adapter,Mock(return_value=True))
        self.root.deiconify()
        self.root.update()
        self.app.show_record(self.item.id)
        self.root.update()
        self.root.focus_force()

    def test_flow_chips_and_full_width_input_at_both_window_sizes(self):
        for width,height in [(1360,820),(1000,680)]:
            self.app.resize(width,height)
            self.root.update()
            for picker in self.app.pickers.values():
                self.assertGreater(picker.input.winfo_width(),picker.winfo_width()-50)
                children=picker.chips.winfo_children()
                self.assertTrue(any(w.winfo_y()==0 and w.winfo_x()>130 for w in children))
                for chip in children:
                    self.assertGreaterEqual(chip.winfo_x(),0)
                    self.assertLessEqual(chip.winfo_x()+chip.winfo_width(),picker.chips.winfo_width())
                    self.assertLessEqual(chip.winfo_y()+chip.winfo_height(),picker.chips.winfo_height())
                self.assertGreaterEqual(picker.chips.winfo_height(),27)
            self.assertGreater(self.app.pickers["tags"].chips.winfo_height(),27)
            for key in ("description","notes","metadata"):
                field=self.app.editor_controls[key]
                self.assertEqual(field.cget("relief"),"flat")
                self.assertEqual(int(field.cget("borderwidth")),0)
                self.assertEqual(int(field.cget("highlightthickness")),1)
        description=self.app.editor_controls["description"]
        notes=self.app.editor_controls["notes"]
        before=description.get("1.0","end-1c")
        description.focus_set()
        self.root.update()
        description.event_generate("<Tab>")
        self.root.update()
        self.assertIs(self.root.focus_get(),notes)
        notes.event_generate("<Shift-Tab>")
        self.root.update()
        self.assertIs(self.root.focus_get(),description)
        self.assertEqual(description.get("1.0","end-1c"),before)
        def descendants(widget):
            for child in widget.winfo_children():
                yield child
                yield from descendants(child)
        save=next(w for w in descendants(self.app.editor) if getattr(w,"text",None)=="Enregistrer")
        self.assertEqual(getattr(save.tk_focusNext(),"kind",None),"open")
        self.assertEqual(getattr(save.tk_focusNext().tk_focusNext(),"text",None),"Supprimer…")

    def test_chip_add_remove_normalization_ctrl_s_and_persistence_preserve_fields(self):
        picker=self.app.pickers["tags"]
        picker.input.set("ete")
        picker.add()
        self.assertEqual(picker.get().count("Été"),1)
        picker.input.set("Graine")
        picker.add()
        picker.remove("Mer")
        before=(self.item.notes,dict(self.item.metadata),list(self.item.projects))
        self.root.event_generate("<Control-s>")
        self.root.update()
        loaded,_=self.store.load()
        saved=loaded.records[self.item.id]
        self.assertIn("Graine",saved.tags)
        self.assertNotIn("Mer",saved.tags)
        self.assertEqual((saved.notes,saved.metadata,saved.projects),before)
        self.app.show_summary(self.item.id)
        self.assertFalse(self.app.editing)

    def test_project_parent_and_all_generic_fields_remain_editable(self):
        self.app.show_record(self.p.id)
        self.root.update()
        self.assertNotIn("url",self.app.fields)
        self.assertEqual(set(self.app.fields),{"title","description","notes","tags","categories","metadata"})
        self.app.parent_box.current(self.app.parent_ids.index(self.q.id))
        self.assertTrue(self.app.save_record())
        loaded,_=self.store.load()
        self.assertEqual(loaded.records[self.p.id].parent,self.q.id)


if __name__=="__main__": unittest.main()
