"""Contrôles d'intégration des formulaires (distincts de la recette visuelle)."""
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store, encode
from mon_gpt.ui import App


class FormTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.cat = Catalog()
        self.adapter = ChatGPT(self.cat)
        self.project = self.cat.add("Équipe fictive", "project")
        self.project.tags = ["Créativité"]
        self.item, _ = self.adapter.ingest("Fil fictif", "https://chatgpt.com/c/00000000-0000-4000-8000-000000000010")
        self.store = Store(self.temp.name)
        self.app = App(self.root, self.store, self.cat, self.adapter)
        self.root.update_idletasks()

    def test_save_common_fields_and_multiple_locations(self):
        second = self.cat.add("Autre projet", "project")
        self.app.show_record(self.item.id)
        self.app.fields["notes"] = lambda: "Été partagé"
        self.app.fields["metadata"] = lambda: "État=Fictif\nÉquipe=Imaginaire"
        self.app.locations.selection_set(0, "end")
        self.assertTrue(self.app.save_record())
        loaded, _ = self.store.load()
        saved = loaded.records[self.item.id]
        self.assertEqual(saved.notes, "Été partagé")
        self.assertEqual(set(saved.projects), {self.project.id, second.id})
        self.assertEqual(saved.metadata["État"], "Fictif")

    def test_failed_write_rolls_back_memory_and_preserves_form(self):
        self.app.show_record(self.item.id)
        self.app.fields["notes"] = lambda: "Saisie à récupérer"
        self.app.dirty = True
        before = encode(self.cat, self.adapter)
        with patch.object(self.store, "save", side_effect=OSError("Panne fictive")), patch("mon_gpt.ui.messagebox.showerror"):
            self.assertIsNone(self.app.save_record())
        self.assertEqual(encode(self.app.cat, self.app.adapter), before)
        self.assertTrue(self.app.dirty)
        self.assertEqual(self.app.fields["notes"](), "Saisie à récupérer")

    def test_project_tag_filter_without_search_text(self):
        self.app.tag.set("creativite")
        self.app.refresh_results()
        self.assertEqual(self.app.results.get_children(), (self.project.id,))

    def test_unsaved_cancel_prevents_leaving(self):
        self.app.show_record(self.item.id)
        self.app.dirty = True
        with patch("mon_gpt.ui.messagebox.askyesnocancel", return_value=None):
            self.assertFalse(self.app.can_leave())
        self.assertTrue(self.app.dirty)

    def test_open_revalidates_url_before_browser(self):
        self.app.show_record(self.item.id)
        with patch("mon_gpt.ui.webbrowser.open", return_value=True) as browser:
            self.app.open_thread()
            browser.assert_called_once_with(self.adapter.conversations[self.item.id].url, new=2)
        self.adapter.conversations[self.item.id].url = "javascript:alert(1)"
        with patch("mon_gpt.ui.webbrowser.open") as browser, patch("mon_gpt.ui.messagebox.showerror"):
            self.app.open_thread()
            browser.assert_not_called()


if __name__ == "__main__":
    unittest.main()
