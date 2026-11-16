from pathlib import Path
import tempfile
import time
import tkinter as tk
import unittest
from unittest.mock import Mock,patch
from types import SimpleNamespace

from mon_gpt.ui import App
from mon_gpt.storage import Store,encode
from mon_gpt.batch_ui import BatchDialog
from batch_fixtures import fixture


class BatchUITests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.cat,self.adapter,self.projects,self.items=fixture()
        self.p,self.q,self.twin,self.r,self.child=self.projects
        self.store=Store(self.temp.name);self.store.save(self.cat,self.adapter)
        self.root=tk.Tk();self.addCleanup(self.destroy)
        self.opener=Mock(return_value=True)
        self.app=App(self.root,self.store,self.cat,self.adapter,self.opener)
        self.root.update();self.app.place_initial_sash(force=True);self.root.update();self.root.focus_force()
        self.table=self.app.results;self.stamp=10000

    def destroy(self):
        try:
            if self.root.winfo_exists():self.root.destroy()
        except tk.TclError:pass

    def visible(self):return [i for i in self.table.get_children() if self.app.cat.records[i].kind=='item']

    def point(self,identity,title=False):
        self.table.see(identity);self.root.update()
        if title:
            x,y,w,h=self.table.bbox(identity,'title');return int(x+35),int(y+min(12,h/2))
        x,y,w,h=self.table.bbox(identity)
        if self.app.view.get()=='list':
            tx,tw=self.table.layout()['title'];return int(tx+tw-12),int(y+h/2)
        return int(x+30),int(y+60)

    def click(self,identity,state=0,title=False,button=1):
        x,y=self.point(identity,title);self.stamp+=1000
        self.table.event_generate(f'<ButtonPress-{button}>',x=x,y=y,state=state,time=self.stamp)
        self.root.update()
        # Le bandeau peut déplacer le widget entre pression et relâchement.
        self.table.event_generate(f'<ButtonRelease-{button}>',x=x,y=y,state=state,time=self.stamp+30)
        self.root.update()

    def key(self,key):
        self.table.focus_force();self.root.update();self.table.event_generate(key);self.root.update()

    def select(self,n=3):
        ids=self.visible()[:n]
        self.table.selection_set(ids);self.root.update()
        return ids

    def choose(self,dialog,box,identity):
        mapping=dialog.sources if box=='source' else dialog.projects
        getattr(dialog,box).set(next(label for label,value in mapping.items() if value==identity))
        self.root.update()

    def test_control_toggle_shift_range_and_control_shift_without_open_three_views(self):
        for view in ('list','detail','mosaic'):
            self.table.selection_set(());self.app.set_view(view);self.root.update()
            ids=self.visible()
            self.click(ids[0]);self.click(ids[2],4,title=True)
            self.assertEqual(self.table.selection(),(ids[0],ids[2]))
            self.click(ids[2],4,title=True);self.assertEqual(self.table.selection(),(ids[0],))
            self.click(ids[4],1,title=True);self.assertEqual(self.table.selection(),tuple(ids[:5]))
            self.click(ids[6],5);self.assertEqual(self.table.selection(),tuple(ids[:7]))
        self.opener.assert_not_called()

    def test_control_a_only_visible_threads_and_text_control_a_untouched(self):
        self.app.tree.selection_set(self.p.id);self.app.select_scope();self.root.update()
        self.key('<Control-a>');self.assertNotIn(self.child.id,self.table.selection())
        self.assertEqual(set(self.table.selection()),set(self.visible()))
        self.app.query.set('imaginaire 001');self.app.refresh_results();self.root.update()
        ids=self.visible();self.key('<Control-a>')
        self.assertEqual(self.table.selection(),tuple(ids));self.assertNotIn(self.child.id,self.table.selection())
        self.app.query.set('texte de recherche');self.app.focus_search();self.root.update()
        self.app.search_entry.event_generate('<Control-a>');self.root.update()
        self.assertTrue(self.app.search_entry.selection_present())
        self.assertEqual(self.table.selection(),tuple(ids))

    def test_shift_arrows_mosaic_2d_and_escape_keeps_inspector(self):
        ids=self.visible();self.click(ids[0]);self.key('<Shift-Down>')
        self.assertEqual(self.table.selection(),tuple(ids[:2]))
        self.app.set_view('mosaic');self.root.update();self.table.selection_set(ids[0])
        columns=self.table.grid_layout().columns
        self.key('<Shift-Down>');self.assertEqual(self.table.selection(),tuple(ids[:columns+1]))
        self.app.toggle_inspector();self.root.update()
        self.assertIsNone(self.app.current);self.assertTrue(self.app.inspector_visible)
        self.assertIn('sélectionnées',self.app.group_summary_title.cget('text'))
        self.key('<Escape>');self.assertEqual(len(self.table.selection()),1);self.assertTrue(self.app.inspector_visible)
        self.opener.assert_not_called()

    def test_preserve_views_sort_prune_filters_and_project_not_in_lot(self):
        ids=self.select(5);anchor=self.table.pick.anchor
        for view in ('detail','mosaic','list'):
            self.app.set_view(view);self.root.update();self.assertEqual(set(self.table.selection()),set(ids))
        self.app.sort_results('title');self.root.update()
        self.assertEqual(set(self.table.selection()),set(ids));self.assertEqual(self.table.pick.anchor,anchor)
        self.app.query.set('0010');self.app.refresh_results();self.root.update()
        self.assertTrue(set(self.table.selection()).issubset(self.visible()))
        self.app.query.set('');self.app.tree.selection_set(self.p.id);self.app.select_scope();self.root.update()
        self.select(3);self.click(self.child.id,state=4)
        self.assertEqual(self.table.selection(),(self.child.id,));self.assertEqual(self.app.group_ids(),())

    def test_group_inspector_shortcuts_menu_and_invalid_drop(self):
        ids=self.select();self.app.toggle_inspector();self.root.update()
        self.assertIsNone(self.app.current);self.assertFalse(self.app.editing)
        before=encode(self.app.cat,self.app.adapter)
        for key in ('<Return>','<F2>','<Control-s>'):self.key(key)
        self.opener.assert_not_called();self.assertIsNone(self.app.inline)
        x,y=self.point(ids[0]);self.app.result_double(SimpleNamespace(x=x,y=y,state=4))
        self.opener.assert_not_called()
        # Réinstaller le lot après le Ctrl du double-clic synthétique.
        self.table.selection_set(ids);self.root.update()
        with patch('mon_gpt.atelier.MenuSkin.popup'):
            self.click(ids[0],button=3)
            menu=self.app.active_menu
            self.assertIn('Déplacer des rattachements…',[menu.entrycget(i,'label') for i in range(menu.index('end')+1) if menu.type(i)!='separator'])
            self.assertEqual(set(self.table.selection()),set(ids))
            self.click(self.visible()[5],button=3);self.assertEqual(len(self.table.selection()),1)
        self.table.selection_set(ids);self.root.update();x,y=self.point(ids[0])
        self.table.event_generate('<ButtonPress-1>',x=x,y=y,time=60000);self.root.update()
        self.table.event_generate('<B1-Motion>',x=x+50,y=y+30,state=256,time=60100)
        self.table.event_generate('<ButtonRelease-1>',x=x+50,y=y+30,time=60200);self.root.update()
        self.assertEqual(set(self.table.selection()),set(ids));self.assertIn('Cible interdite',self.app.status.get())
        self.assertEqual(encode(self.app.cat,self.app.adapter),before)

    def test_dirty_editor_cancel_leaves_draft_and_selection_intact(self):
        first,other=self.visible()[:2];self.table.selection_set(first);self.root.update()
        self.app.show_record(first);self.root.update()
        self.app.dirty=True
        old=self.app.editor.winfo_children();before=encode(self.app.cat,self.app.adapter)
        with patch('mon_gpt.details.messagebox.askyesnocancel',return_value=None):self.click(other,state=4)
        self.assertEqual(self.table.selection(),(first,));self.assertEqual(self.app.editor.winfo_children(),old)
        self.assertTrue(self.app.dirty);self.assertEqual(encode(self.app.cat,self.app.adapter),before)

    def test_dialog_cancel_add_commit_once_and_noop(self):
        ids=self.select(10);before=encode(self.app.cat,self.app.adapter)
        self.app.open_batch('add');dialog=self.app.batch_dialog
        self.choose(dialog,'destination',self.q.id)
        self.assertEqual(dialog.plan.changed,10);dialog.cancel()
        self.assertEqual(encode(self.app.cat,self.app.adapter),before)
        self.app.open_batch('add');dialog=self.app.batch_dialog;self.choose(dialog,'destination',self.q.id)
        with patch.object(self.store,'save',wraps=self.store.save) as save:
            dialog.confirm();self.root.update();dialog.confirm();save.assert_called_once()
        self.assertTrue(dialog.finished);self.assertEqual(len(self.app.adapter.conversations),22)
        self.assertTrue(all(self.q.id in self.app.cat.records[i].projects for i in ids));dialog.cancel()
        self.app.open_batch('add');dialog=self.app.batch_dialog;self.choose(dialog,'destination',self.q.id)
        self.assertEqual(dialog.plan.changed,0)
        with patch.object(self.store,'save',side_effect=AssertionError('no-op écrit')):dialog.confirm()
        dialog.cancel()

    def test_move_source_explicit_in_global_prefilled_in_project_remove_prunes(self):
        self.select();self.app.open_batch('move');dialog=self.app.batch_dialog
        self.choose(dialog,'destination',self.q.id);self.assertIsNone(dialog.plan)
        self.choose(dialog,'source',self.p.id);self.assertIsNotNone(dialog.plan);dialog.cancel()
        self.app.tree.selection_set(self.p.id);self.app.select_scope();self.root.update();ids=self.select(3)
        self.app.open_batch('remove');dialog=self.app.batch_dialog
        self.assertEqual(dialog.plan.source,self.p.id)
        dialog.confirm();self.root.update();self.assertFalse(set(ids).intersection(self.table.selection()))
        self.assertFalse(self.app.group_bar.winfo_manager());self.assertIsNone(self.app.current);dialog.cancel()

    def test_dialog_errors_stale_selection_destination_and_write_failure(self):
        self.select();self.app.open_batch('add');dialog=self.app.batch_dialog;self.choose(dialog,'destination',self.q.id)
        before=encode(self.app.cat,self.app.adapter)
        with patch.object(self.store,'save',side_effect=OSError('Échec fictif')):dialog.confirm()
        self.assertFalse(dialog.finished);self.assertEqual(encode(self.app.cat,self.app.adapter),before)
        self.assertIn('annulée',dialog.error.cget('text'));dialog.cancel()
        self.app.open_batch('add');dialog=self.app.batch_dialog;self.choose(dialog,'destination',self.q.id)
        self.app.cat.delete(self.q.id);changed=encode(self.app.cat,self.app.adapter)
        dialog.confirm();self.assertEqual(encode(self.app.cat,self.app.adapter),changed);self.assertFalse(dialog.finished)
        dialog.reload();self.assertIsNone(dialog.plan);dialog.cancel()

    def test_1429_filtered_control_a_hundred_and_bounded_canvas_all_views(self):
        cat,adapter,projects,items=fixture(1429)
        self.app.cat,self.app.adapter=cat,adapter;self.app.scope='all';self.app.query.set('');self.app.refresh_results();self.root.update()
        ids=self.visible();self.table.selection_set(ids[:100]);self.root.update()
        for view in ('list','detail','mosaic'):
            self.app.set_view(view);self.root.update()
            self.assertEqual(len(self.table.selection()),100)
            self.key('<Control-a>');self.assertEqual(len(self.table.selection()),1429)
            self.assertLess(len(self.table.find_all()),2000)
            self.table.selection_set(ids[:100]);self.root.update()
        self.assertLessEqual(len(self.table.winfo_children()),1)  # Une infobulle éventuelle.

    def test_group_column_resize_and_fast_control_double_click_never_open(self):
        ids=self.select();x,width=self.table.layout()['title'];edge=int(x+width)
        self.table.event_generate('<Motion>',x=edge,y=12);self.root.update()
        self.assertEqual(self.table.cget('cursor'),'sb_h_double_arrow')
        self.table.event_generate('<ButtonPress-1>',x=edge,y=12,time=90000)
        self.table.event_generate('<B1-Motion>',x=edge-35,y=12,state=256,time=90100)
        self.table.event_generate('<ButtonRelease-1>',x=edge-35,y=12,time=90200);self.root.update()
        self.assertEqual(set(self.table.selection()),set(ids));self.assertFalse(self.app.sort_reverse)
        x,y=self.point(ids[0],title=True)
        for stamp in (100000,100100):
            self.table.event_generate('<ButtonPress-1>',x=x,y=y,state=4,time=stamp)
            self.table.event_generate('<ButtonRelease-1>',x=x,y=y,state=4,time=stamp+20);self.root.update()
        self.assertEqual(set(self.table.selection()),set(ids));self.opener.assert_not_called()

    def test_close_reopen_never_restores_hidden_mass_selection(self):
        self.select(5);self.app.toggle_inspector();self.root.update()
        self.app.close()
        import json
        state=json.loads((self.store.directory/'interface.json').read_text(encoding='utf-8'))
        self.assertIsNone(state['selected'])
        self.root=tk.Tk();cat,adapter=self.store.load()
        app=App(self.root,self.store,cat,adapter,opener=self.opener);self.root.update()
        self.assertEqual(app.results.selection(),());self.assertFalse(app.group_bar.winfo_manager())
        self.opener.assert_not_called()
