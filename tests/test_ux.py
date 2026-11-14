"""Tests de contrats de gestes ; distincts de la recette par entrées Windows."""
import json
import tempfile
import tkinter as tk
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from pathlib import Path
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store, encode
from mon_gpt.ui import App
from mon_gpt import ui_state


class GestureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(lambda: self.root.destroy() if self.root.winfo_exists() else None)
        self.cat = Catalog()
        self.a = self.cat.add("Atelier des idées", "project")
        self.b = self.cat.add("Écriture", "project", self.a.id)
        self.c = self.cat.add("Laboratoire", "project")
        self.adapter = ChatGPT(self.cat)
        self.item, _ = self.adapter.ingest("Exploration imaginaire", "https://chatgpt.com/c/00000000-0000-4000-8000-000000000001")
        self.item.notes, self.item.tags, self.item.categories = "Note commune", ["Été"], ["Idées"]
        self.cat.attach(self.item.id, [self.a.id, self.b.id])
        self.store = Store(self.temp.name)
        self.opener = Mock(return_value=True)
        self.app = App(self.root, self.store, self.cat, self.adapter, self.opener)
        self.root.update_idletasks()

    def test_selection_does_not_show_inspector_or_open(self):
        self.app.results.selection_set(self.item.id)
        self.app.select_record()
        self.assertEqual(self.app.current, self.item.id)
        self.assertFalse(self.app.inspector_visible)
        self.assertFalse(self.app.editing)
        self.opener.assert_not_called()
        self.app.open_thread(self.item.id)
        self.opener.assert_called_once()
        self.assertFalse(self.app.inspector_visible)
        self.app.open_thread(self.a.id)
        self.assertEqual(self.opener.call_count, 1)

    def test_enter_is_scoped_to_results_not_search_or_editor(self):
        self.app.results.focus(self.item.id)
        for widget in (self.app.search_entry, self.app.editor):
            with patch.object(self.root, "focus_get", return_value=widget):
                self.app.result_enter()
        self.opener.assert_not_called()
        with patch.object(self.root, "focus_get", return_value=self.app.results):
            self.app.result_enter()
        self.opener.assert_called_once()

    def test_project_inline_cancel_has_no_ghost_or_popup(self):
        self.root.deiconify()
        self.root.update()
        before = encode(self.cat, self.adapter)
        with patch("mon_gpt.ui.tk.Toplevel", side_effect=AssertionError("Popup ordinaire interdite")):
            self.app.new("project")
            self.app.inline.insert(0, "Projet à annuler")
            self.app.cancel_inline()
        self.assertFalse(self.app.tree.exists("__draft__"))
        self.assertEqual(encode(self.cat, self.adapter), before)
        self.app.scope = self.b.id
        self.app.new("project")
        self.app.inline.insert(0, "Sous-projet créé")
        self.app.commit_inline()
        created = next(r for r in self.cat.records.values() if r.title == "Sous-projet créé")
        self.assertEqual(created.parent, self.b.id)
        self.assertEqual(encode(*self.store.load())["schema"], 1)

    def test_item_inline_invalid_duplicate_and_cancel(self):
        before = encode(self.cat, self.adapter)
        self.app.scope = self.c.id
        self.app.new("item")
        self.app.new_title.insert(0, "Titre qui ne doit rien écraser")
        self.app.new_url.insert(0, "javascript:alert(1)")
        self.app.submit_item()
        self.assertEqual(encode(self.cat, self.adapter), before)

        self.assertTrue(self.app.work_error.get())
        self.app.new_url.delete(0, "end")
        self.app.new_url.insert(0, "https://chatgpt.com/g/g-fiction/c/00000000-0000-4000-8000-000000000001?x=1")
        self.app.submit_item()
        self.assertEqual(encode(self.cat, self.adapter), before)
        self.app.submit_item(use_existing=True)
        self.assertEqual(self.item.title, "Exploration imaginaire")
        self.assertEqual(self.item.notes, "Note commune")
        self.assertEqual(len([r for r in self.cat.records.values() if r.kind == "item"]), 1)
        self.assertEqual(set(self.item.projects), {self.a.id, self.b.id, self.c.id})
        self.app.new("item")
        self.app.new_title.insert(0, "Annulé")
        before = encode(self.cat, self.adapter)
        self.app.escape()
        self.assertEqual(encode(self.cat, self.adapter), before)

    def test_duplicate_action_cannot_apply_to_a_changed_url(self):
        self.app.new("item")
        self.app.new_title.insert(0, "Une saisie non validée")
        self.app.new_url.insert(0, "https://chatgpt.com/c/00000000-0000-4000-8000-000000000099")
        before = encode(self.cat, self.adapter)
        self.app.submit_item(use_existing=True, expected_identity="00000000-0000-4000-8000-000000000001")
        self.assertEqual(encode(self.cat, self.adapter), before)
        self.assertIn("changé", self.app.work_error.get())

    def test_transfer_preserves_other_links_notes_and_identity(self):
        self.app.transaction(lambda: self.app.transfer(self.item.id, self.c.id, "move", self.a.id))
        self.assertEqual(set(self.item.projects), {self.b.id, self.c.id})
        self.app.transaction(lambda: self.app.transfer(self.item.id, self.a.id, "add"))
        self.assertEqual(set(self.item.projects), {self.a.id, self.b.id, self.c.id})
        self.assertEqual(self.item.notes, "Note commune")
        self.assertEqual(len(self.adapter.conversations), 1)
        before = encode(self.cat, self.adapter)
        with self.assertRaises(ValueError):
            self.app.transaction(lambda: self.app.transfer(self.item.id, self.c.id, "move"))
        self.assertEqual(encode(self.app.cat, self.app.adapter), before)

    def test_ambiguous_move_panel_and_cancel_have_no_mutation(self):
        before = encode(self.cat, self.adapter)
        self.app.drop_action(self.item.id, self.c.id, "move", "all")
        self.assertEqual(self.app.source_box.current(), -1)
        self.app.apply_transfer()
        self.assertEqual(encode(self.cat, self.adapter), before)
        self.app.escape()
        self.assertEqual(encode(self.cat, self.adapter), before)

    def test_project_cycle_rejected_and_manual_order_preserved(self):
        before = encode(self.cat, self.adapter)
        self.app.drag = {"id": self.a.id}
        self.root.update_idletasks()
        with self.assertRaises(ValueError):
            self.app.transaction(lambda: self.app.transfer(self.a.id, self.b.id, "move"))
        self.assertEqual(encode(self.app.cat, self.app.adapter), before)
        manual = [r.id for r in self.app.cat.children()]
        self.app.sort.set("Alphabétique français")
        self.app.refresh_tree()
        self.app.sort.set("Manuel")
        self.app.refresh_tree()
        self.assertEqual([r.id for r in self.app.cat.children()], manual)

    def test_known_chips_new_values_and_persistence(self):
        self.app.show_record(self.item.id)
        picker = self.app.pickers["tags"]
        self.assertIn("Été", picker.known())
        picker.input.set("Océan")
        picker.add()
        self.app.pickers["categories"].input.set("Idées")
        self.app.pickers["categories"].add()
        self.assertTrue(self.app.save_record())
        cat, _ = self.store.load()
        self.assertEqual(cat.records[self.item.id].tags, ["Été", "Océan"])
        self.assertEqual(cat.records[self.item.id].categories, ["Idées"])
        self.app.query.set("ocean")
        self.app.refresh_results()
        self.assertEqual(self.app.results.get_children(), (self.item.id,))

    def test_filter_suggestions_chips_and_unique_results(self):
        self.app.query.set("ete")
        self.app.show_suggestions()
        index = next(i for i, (key, value, _) in enumerate(self.app.suggestion_values) if key == "tags" and value == "Été")
        self.app.suggestions.selection_set(index)
        self.app.choose_suggestion()
        self.assertEqual(self.app.tag.get(), "Été")
        self.assertEqual(self.app.query.get(), "")
        self.assertEqual(self.app.results.get_children(), (self.item.id,))
        self.app.remove_filter(self.app.tag)
        self.assertFalse(self.app.tag.get())

    def test_preferences_are_separate_and_corruption_does_not_touch_catalog(self):
        before = encode(self.cat, self.adapter)
        path = Path(self.temp.name) / "interface.json"
        ui_state.save(path, True, "1000x680")
        values, warning = ui_state.load(path)
        self.assertTrue(values["inspector"])
        self.assertFalse(warning)
        self.assertEqual(encode(self.cat, self.adapter), before)
        path.write_text("{invalide", encoding="utf-8")
        self.assertTrue(ui_state.load(path)[1])
        self.assertEqual(path.read_text(encoding="utf-8"), "{invalide")
        self.assertEqual(encode(self.cat, self.adapter), before)

    def test_compact_layout_keeps_scroll_and_data_path_visible(self):
        self.root.deiconify()
        self.app.resize(1000, 680)
        self.root.update()
        self.assertTrue(self.app.horizontal_scroll.winfo_ismapped())
        self.assertGreater(self.app.horizontal_scroll.winfo_height(), 5)
        for widget in (self.app.horizontal_scroll, self.app.data_label):
            self.assertLess(widget.winfo_rooty()+widget.winfo_height(), self.root.winfo_rooty()+self.root.winfo_height()+1)

    def test_schema_one_remains_strict_and_business_modules_unchanged(self):
        self.store.save(self.cat, self.adapter)
        data = json.loads(self.store.path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], 1)
        self.assertNotIn("view", data)
        self.assertNotIn("cover", data["records"][0])

    def test_delete_project_via_ui_preserves_fiche_and_never_contacts_browser(self):
        self.app.current = self.a.id
        with patch("mon_gpt.details.messagebox.askyesno", return_value=True):
            self.app.delete()
        self.assertIn(self.item.id, self.cat.records)
        self.assertEqual(self.item.projects, [self.b.id])
        self.assertIsNone(self.b.parent)
        self.opener.assert_not_called()
        self.assertFalse(self.app.inspector_visible)

    def test_restore_via_menu_keeps_hidden_inspector_and_schema_one(self):
        backup = Path(self.temp.name) / "export.json"
        self.store.export(backup, self.cat, self.adapter)
        self.cat.add("Fiche supprimée par remplacement", "project")
        with patch("mon_gpt.details.filedialog.askopenfilename", return_value=str(backup)), patch("mon_gpt.details.messagebox.askyesno", return_value=True):
            self.app.restore()
        self.assertEqual(len(self.app.cat.records), 4)
        self.assertFalse(self.app.inspector_visible)
        self.assertEqual(encode(*self.store.load())["schema"], 1)
        self.assertEqual(len(list(Path(self.temp.name).glob("avant-restauration-*.json"))), 1)

    def test_rename_and_manual_order_keyboard_bindings(self):
        self.root.deiconify()
        self.root.update()
        self.app.select_identity(self.item.id)
        self.app.results.focus_force()
        self.app.results.event_generate("<F2>")
        self.root.update()
        self.assertIsNotNone(self.app.inline)
        self.app.inline.delete(0, "end")
        self.app.inline.insert(0, "Nom local renommé")
        self.app.inline.event_generate("<Return>")
        self.root.update()
        self.assertEqual(self.item.title, "Nom local renommé")
        self.assertEqual(self.item.notes, "Note commune")
        self.app.scope = self.a.id
        self.app.tree.selection_set(self.a.id)
        self.app.tree.focus_force()
        self.root.update()
        self.app.tree.event_generate("<Alt-Down>")
        self.root.update()
        self.assertEqual([r.id for r in self.cat.children()], [self.c.id, self.a.id])
        self.assertEqual(self.app.scope, self.a.id)
        self.opener.assert_not_called()

    def event_at(self, widget, identity, column=None):
        x, y, width, height = widget.bbox(identity, column) if column else widget.bbox(identity)
        return SimpleNamespace(x=x+min(20,width//2), y=y+height//2, x_root=widget.winfo_rootx()+x+min(20,width//2), y_root=widget.winfo_rooty()+y+height//2)

    def test_right_drop_menu_defers_mutation_until_choice(self):
        self.root.deiconify()
        self.root.update()
        before = encode(self.cat, self.adapter)
        start = self.event_at(self.app.results, self.item.id, "context")
        end = self.event_at(self.app.tree, self.c.id)
        self.app.drag_press(start, self.app.results, 3)
        self.app.drag_motion(end)
        self.assertEqual(encode(self.cat, self.adapter), before)
        with patch("mon_gpt.ui.tk.Menu") as menu:
            self.app.drag_release(end, self.app.results, 3)
            actions = {call.kwargs["label"]: call.kwargs["command"] for call in menu.return_value.add_command.call_args_list}
            self.assertEqual(set(actions), {"Déplacer ici", "Ajouter un rattachement ici", "Annuler"})
            self.assertEqual(encode(self.cat, self.adapter), before)
            actions["Ajouter un rattachement ici"]()
        self.assertEqual(set(self.item.projects), {self.a.id, self.b.id, self.c.id})
        self.assertEqual(self.item.notes, "Note commune")

    def test_click_title_opens_but_context_click_does_not(self):
        self.root.deiconify()
        self.root.update()
        context = self.event_at(self.app.results, self.item.id, "context")
        title = self.event_at(self.app.results, self.item.id, "title")
        self.app.drag_press(context, self.app.results, 1)
        self.app.drag_release(context, self.app.results, 1)
        self.opener.assert_not_called()
        self.app.drag_press(title, self.app.results, 1)
        self.app.drag_release(title, self.app.results, 1)
        self.opener.assert_called_once()
        self.assertFalse(self.app.inspector_visible)
