"""Contrats voisins des commandes à icônes et de l'en-tête de fiche."""
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock

from mon_gpt.chatgpt import ChatGPT
from mon_gpt.core import Catalog
from mon_gpt.inspector import InspectorAction
from mon_gpt.storage import Store, encode
from mon_gpt.ui import App


class GraphicPolishTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=tk.Tk()
        self.addCleanup(self.root.destroy)
        self.cat=Catalog();self.project=self.cat.add('Projet fictif','project')
        self.adapter=ChatGPT(self.cat)
        self.items=[self.adapter.ingest(f'Note fictive {n}',f'https://chatgpt.com/c/00000000-0000-4000-8000-{n:012d}')[0] for n in (1,2)]
        self.opener=Mock(return_value=True)
        self.app=App(self.root,Store(self.temp.name),self.cat,self.adapter,self.opener)
        self.root.update()

    def test_named_icon_commands_keep_filters_group_and_keyboard_actions(self):
        snapshot=encode(self.cat,self.adapter)
        self.app.query.set('fictive');self.app.perform_search();self.root.update()
        ids=tuple(item.id for item in self.items)
        self.app.results.selection_set(ids);self.root.update()
        for key,label in (('detail','Détaillée'),('mosaic','Mosaïque'),('list','Liste')):
            button=self.app.view_buttons[key]
            self.assertEqual(button.text,label)
            button.focus_force();self.root.update()
            button.event_generate('<Return>');self.root.update()
            self.assertEqual(self.app.view.get(),key)
            self.assertEqual(set(self.app.results.selection()),set(ids))
            self.assertEqual(self.app.query.get(),'fictive')
            button.tip.hide();button.tip.show();self.root.update()
            self.assertEqual(button.tip.window.winfo_children()[0].cget('text'),label)
            button.tip.hide()
        self.assertEqual(encode(self.cat,self.adapter),snapshot)
        self.opener.assert_not_called()

    def test_inspector_real_title_empty_group_and_close_keep_their_roles(self):
        self.app.ensure_inspector();self.app.show_summary(None,checked=True);self.root.update()
        self.app.panes.sashpos(1,self.app.panes.winfo_width()-250);self.root.update()
        self.assertLessEqual(int(self.app.summary.title.cget('wraplength')),self.app.summary.title.winfo_width())
        close=next(w for frame in self.app.summary.winfo_children() for w in frame.winfo_children() if isinstance(w,InspectorAction) and w.kind=='close')
        close.activate();self.root.update()
        self.assertFalse(self.app.inspector_visible)
        self.app.ensure_inspector()
        for record in (self.project,self.items[0]):
            self.app.show_summary(record.id,checked=True);self.root.update()
            self.assertEqual(self.app.summary.title.cget('text'),record.title)
            self.assertEqual(set(self.app.summary.actions),{'edit'} if record.kind=='project' else {'open','copy','edit'})
        self.app.results.selection_set([item.id for item in self.items]);self.root.update()
        self.app.sync_group();self.root.update()
        self.assertIsNone(self.app.current)
        self.assertEqual(self.app.group_summary_title.cget('text'),'2 discussions sélectionnées')
        self.opener.assert_not_called()
