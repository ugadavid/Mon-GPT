"""Intégration du véritable assistant Tk ; uniquement des données fictives."""
import json
from pathlib import Path
import tempfile
import time
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store, encode
from mon_gpt.ui import App
from mon_gpt.import_ui import ImportWizard, open_import
from collector_fixtures import export_fixture


class ImportUITests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=tk.Tk();self.root.withdraw();self.addCleanup(self.root.destroy)
        cat=Catalog();self.store=Store(self.temp.name)
        self.app=App(self.root,self.store,cat,ChatGPT(cat),opener=Mock())
        self.path=Path(self.temp.name)/'fictif.json'
        self.path.write_text(json.dumps(export_fixture(58,115)),encoding='utf-8')
        self.root.update()

    def wait(self,wizard):
        # Une VM Windows peut retarder les événements Tk lors des captures et
        # changements de fenêtres ; attendre le worker, sans délai fixe court.
        deadline=time.monotonic()+45
        while wizard.busy and time.monotonic()<deadline:
            self.root.update();time.sleep(.01)
        self.root.update()
        self.assertFalse(wizard.busy,wizard.progress.get())

    def load(self):
        w=ImportWizard(self.app);w.load_path(self.path);self.wait(w)
        self.assertIsNotNone(w.plan,w.progress.get())
        return w

    def test_menu_distinct_and_unsaved_cancel(self):
        menu=self.app.main_menu.menus[0][1]
        labels=[menu.entrycget(i,'label') for i in range(menu.index('end')+1) if menu.type(i)!='separator']
        self.assertIn('Restaurer le catalogue…',labels)
        self.assertIn('Importer depuis Mon GPT Collector (JSON)…',labels)
        with patch.object(self.app,'can_leave',return_value=False),patch('mon_gpt.import_ui.ImportWizard') as dialog:
            open_import(self.app);dialog.assert_not_called()

    def test_compact_window_keeps_confirmation_and_cancel_visible(self):
        self.root.deiconify()
        w=ImportWizard(self.app);w.geometry('940x700');self.root.update()
        for widget in (w.cancel_button,w.next_button,w.apply_choice,w.separate):
            self.assertTrue(widget.winfo_viewable())
            self.assertLessEqual(widget.winfo_rooty()+widget.winfo_height(),w.winfo_rooty()+w.winfo_height())
        w.cancel()

    def test_paging_search_cancel_and_no_preview_mutation(self):
        before=encode(self.app.cat,self.app.adapter)
        w=self.load()
        self.assertEqual(len(w.tabs['Projets'].get_children()),58)
        w.book.select(1);self.root.update()
        self.assertEqual(len(w.tabs['Discussions'].get_children()),60)
        w.turn(1);self.assertEqual(len(w.tabs['Discussions'].get_children()),55)
        w.query.set('jardin');self.root.update()
        self.assertTrue(len(w.tabs['Discussions'].get_children())>0)
        w.cancel();self.assertEqual(encode(self.app.cat,self.app.adapter),before)
        self.assertFalse(self.store.path.exists())

    def test_homonym_confirmation_commit_and_all_views_refresh_without_opening(self):
        w=self.load()
        w.next();self.assertFalse(w.confirming)
        w.accept_separate.set(True);w.next();self.assertTrue(w.confirming)
        self.assertFalse(self.store.path.exists())
        w.back();self.assertFalse(w.confirming)
        w.next();w.next();self.wait(w)
        self.assertTrue(w.finished)
        self.assertEqual(len(self.app.adapter.project_links),58)
        self.assertEqual(len(self.app.adapter.conversations),115)
        w.cancel()
        for view in ('list','detail','mosaic'):
            self.app.set_view(view);self.root.update()
            self.assertEqual(len(self.app.results.get_children()),115)
        self.app.opener.assert_not_called()

    def test_choices_kept_on_back_merge_with_existing_and_anomaly_recovery(self):
        local=self.app.cat.add('Atelier local','project')
        w=self.load();keys=list(w.decisions)
        table=w.tabs['Projets'];table.selection_set(keys[0]);w.select_row()
        w.action.set('Associer à un existant');w.update_destinations();w.change_choice();self.wait(w)
        table.selection_set(keys[1]);w.select_row()
        w.action.set('Fusionner vers un projet de l’export');w.update_destinations();w.change_choice();self.wait(w)
        self.assertEqual(w.plan.data['chatgpt_projects'][keys[1]],local.id)
        w.next();self.assertTrue(w.confirming);w.back()
        self.assertEqual(w.decisions[keys[0]].target,local.id)
        self.assertEqual(w.plan.counts['created_projects'],56)
        self.assertEqual(len(self.app.cat.records),1)
        w.cancel()

    def test_invalid_file_and_write_failure_are_visible_no_partial_import(self):
        self.path.write_text('{"schemaVersion":1}')
        w=ImportWizard(self.app);w.load_path(self.path);self.wait(w)
        self.assertIsNone(w.plan);self.assertTrue(w.issues)
        self.assertFalse(self.store.path.exists())
        self.path.write_text(json.dumps(export_fixture()))
        w.load_path(self.path);self.wait(w)
        w.accept_separate.set(True);w.next()
        with patch.object(self.store,'save',side_effect=OSError('Écriture fictive refusée')):
            w.next();self.wait(w)
        self.assertFalse(w.finished);self.assertEqual(len(self.app.cat.records),0)
        self.assertEqual(str(w.cancel_button['state']),'normal')
        self.assertFalse(self.store.path.exists())
        self.assertEqual(len(list(Path(self.temp.name).glob('avant-import-*.zip'))),1)
        w.cancel()
