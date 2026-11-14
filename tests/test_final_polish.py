"""Régressions ciblées : navigation, validations locales et confirmation sûre."""
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock,patch
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store,encode
from mon_gpt.ui import App
from mon_gpt.details import confirm_delete


class FinalPolishTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.cat=Catalog()
        self.project=self.cat.add("Projet fictif avec un très long titre à retrouver entièrement","project")
        self.child=self.cat.add("Sous-projet","project",self.project.id)
        self.adapter=ChatGPT(self.cat)
        self.item,_=self.adapter.ingest("Fil fictif","https://chatgpt.com/c/00000000-0000-4000-8000-000000000007")
        self.cat.attach(self.item.id,[self.project.id,self.child.id])
        self.item.notes="Note commune conservée."
        self.app=App(self.root,Store(self.temp.name),self.cat,self.adapter,Mock(return_value=True))
        self.root.deiconify()
        self.root.update()
        self.root.focus_force()

    def test_long_tree_label_and_parent_survive_elision_hover_and_resize(self):
        tree=self.app.tree
        self.assertEqual(tree.item(self.project.id,"text"),self.project.title)
        self.assertEqual(tree.item(self.project.id)["text"],self.project.title)
        self.assertEqual(tree.parent(self.child.id),self.project.id)
        tree.show_tip(self.project.id,40)
        self.root.update()
        self.assertEqual(tree.tip.winfo_children()[0].cget("text"),self.project.title)
        tree.hide_tip()
        self.app.resize(1000,680)
        self.root.update()
        self.assertEqual(tree.item(self.project.id,"text"),self.project.title)
        self.assertNotEqual(tree.item(self.project.id,"image"),self.app.icons["project"])

    def test_title_error_is_inline_no_write_preserves_draft_and_clears(self):
        self.app.show_record(self.item.id)
        self.root.update()
        field=self.app.editor_controls["title"]
        field.delete(0,"end")
        self.app.editor_controls["notes"].insert("end"," Brouillon à garder.")
        before=encode(self.cat,self.adapter)
        with patch.object(self.app.store,"save") as save,patch("mon_gpt.details.messagebox.showerror") as popup:
            self.assertFalse(self.app.save_record())
            save.assert_not_called();popup.assert_not_called()
        self.root.update()
        self.assertTrue(self.app.editor_errors["title"].winfo_ismapped())
        self.assertIs(self.root.focus_get(),field)
        self.assertEqual(encode(self.cat,self.adapter),before)
        self.assertIn("Brouillon à garder",self.app.fields["notes"]())
        field.insert(0,"Titre corrigé")
        self.root.update()
        self.assertFalse(self.app.editor_errors["title"].winfo_ismapped())
        self.assertTrue(self.app.save_record())
        self.assertEqual(self.item.projects,[self.project.id,self.child.id])

    def test_link_and_metadata_errors_are_local_and_storage_errors_still_alert(self):
        self.app.show_record(self.item.id)
        self.root.update()
        link=self.app.editor_controls["url"]
        link.delete(0,"end");link.insert(0,"http://exemple.invalid")
        before=encode(self.cat,self.adapter)
        with patch("mon_gpt.details.messagebox.showerror") as popup:
            self.assertFalse(self.app.save_record());popup.assert_not_called()
        self.assertEqual(encode(self.cat,self.adapter),before)
        self.assertTrue(self.app.editor_errors["url"].winfo_manager())
        link.delete(0,"end");link.insert(0,self.adapter.conversations[self.item.id].url)
        self.app.fields["metadata"]=lambda:"clé sans égal"
        with patch("mon_gpt.details.messagebox.showerror") as popup:
            self.assertFalse(self.app.save_record());popup.assert_not_called()
        self.assertTrue(self.app.editor_errors["metadata"].winfo_manager())
        self.app.fields["metadata"]=lambda:"Clé=Valeur"
        with patch.object(self.app.store,"save",side_effect=OSError("Panne fictive")),patch("mon_gpt.details.messagebox.showerror") as popup:
            self.assertIsNone(self.app.save_record());popup.assert_called_once()

    def test_delete_default_no_and_project_impact_keep_original_effects(self):
        self.app.current=self.project.id
        before=encode(self.cat,self.adapter)
        with patch("mon_gpt.details.confirm_delete",return_value=False) as confirm:
            self.app.delete()
        self.assertEqual(encode(self.cat,self.adapter),before)
        self.assertIn("1 sous-projet(s), 1 rattachement(s)",confirm.call_args.args[1])
        self.assertNotIn("ChatGPT",confirm.call_args.args[1])
        with patch("mon_gpt.details.confirm_delete",return_value=True): self.app.delete()
        self.assertIsNone(self.child.parent)
        self.assertEqual(self.item.projects,[self.child.id])
        self.assertEqual(self.item.notes,"Note commune conservée.")
        self.app.current=self.item.id
        with patch("mon_gpt.details.confirm_delete",return_value=False) as confirm: self.app.delete()
        self.assertEqual(confirm.call_args.args[1],"Supprimer « Fil fictif » ?")

    def test_paper_confirmation_no_escape_close_and_yes(self):
        for action in ("default","escape","close","yes"):
            observed=[]
            watchdog=[]
            def answer():
                dialog=next(w for w in self.root.winfo_children() if isinstance(w,tk.Toplevel))
                watchdog.append(self.root.after(700,lambda:dialog.destroy() if dialog.winfo_exists() else None))
                buttons=dialog.winfo_children()[0].winfo_children()[1].winfo_children()
                observed.append(dialog.focus_get()==buttons[0])
                if action=="default": dialog.event_generate("<Return>")
                elif action=="escape": dialog.event_generate("<Escape>")
                elif action=="close": dialog.tk.call(dialog.protocol("WM_DELETE_WINDOW"))
                else: buttons[1].invoke()
            self.root.after(150,answer)
            self.assertEqual(confirm_delete(self.root,"Supprimer « Fictif » ?"),action=="yes")
            for timer in watchdog: self.root.after_cancel(timer)
            self.assertEqual(observed,[True])


if __name__=="__main__": unittest.main()
