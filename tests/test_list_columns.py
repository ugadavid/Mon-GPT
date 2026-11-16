"""MG-010c : préférences v1, rendu virtuel, horodatages et gestes validés."""
import copy
import json
import unittest
from unittest.mock import patch
import test_batch_ui as helpers
import test_natural_gestures as natural
from mon_gpt import ui_state
from mon_gpt.list_columns import defaults, validate, display_date, sort_value
from mon_gpt.storage import encode
from mon_gpt.ui import App


class ColumnTests(unittest.TestCase):
    setUp=helpers.BatchUITests.setUp
    destroy=helpers.BatchUITests.destroy
    visible=helpers.BatchUITests.visible
    point=helpers.BatchUITests.point
    gesture=natural.NaturalGesturesTests.gesture
    arrow=natural.NaturalGesturesTests.arrow
    event_click=natural.NaturalGesturesTests.event_click
    scope=natural.NaturalGesturesTests.scope

    def config(self):
        c=defaults();c['order']=['title','modified','context','created','tags','categories']
        c['visible']=['title','modified','context','created']
        c['widths'].update(title=220,context=180,created=165,modified=170)
        return c

    def drag_width(self,key,delta):
        self.table.xview('moveto',0);self.table.draw();self.root.update()
        if key!='title':
            # Amener le bord droit dans la bande des colonnes secondaires.
            total=sum(self.table.column(k,'width') for k in self.table.secondary_order)
            end=sum(self.table.column(k,'width') for k in self.table.secondary_order[:self.table.secondary_order.index(key)+1])
            self.table.xview('moveto',max(0,(end-self.table.secondary_visible+15)/max(1,total)))
            self.root.update()
        x=sum(self.table.layout()[key]);self.assertEqual(self.table.separator_at(x,15),key)
        self.stamp+=2000
        self.table.event_generate('<ButtonPress-1>',x=int(x),y=15,time=self.stamp);self.root.update()
        self.table.event_generate('<B1-Motion>',x=int(x+delta),y=15,state=256,time=self.stamp+100);self.root.update()
        self.table.event_generate('<ButtonRelease-1>',x=int(x+delta),y=15,time=self.stamp+200);self.root.update()

    def test_old_preferences_and_invalid_columns_preserve_workspace_and_catalog(self):
        path=self.app.preferences_path
        base=dict(version=1,view='detail',inspector=True,geometry='1600x900',query='imaginaire',scope=self.p.id,selected=self.items[3].id,expanded_projects=[self.p.id])
        path.write_text(json.dumps(base),encoding='utf-8')
        self.assertEqual(ui_state.load(path),(base,''))
        before=encode(self.cat,self.adapter)
        mutations=[None,[],{},dict(self.config(),order=['title']*6),dict(self.config(),order=['title','unknown','context','created','tags','categories']),
                   dict(self.config(),visible=['context']),dict(self.config(),visible=['title','title']),dict(self.config(),visible=['title',[]]),
                   dict(self.config(),widths=dict(defaults()['widths'],title='310')),dict(self.config(),widths=dict(defaults()['widths'],created=True)),
                   dict(self.config(),widths=dict(defaults()['widths'],title=99999)),dict(self.config(),sort='unknown'),dict(self.config(),reverse=1)]
        for config in mutations:
            with self.subTest(config=str(config)[:70]):
                path.write_text(json.dumps(dict(base,list_columns=config)),encoding='utf-8')
                result,warning=ui_state.load(path)
                self.assertTrue(warning);self.assertEqual(result['list_columns'],defaults())
                for key,value in base.items():self.assertEqual(result[key],value)
        self.assertEqual(encode(self.cat,self.adapter),before)
        path.write_text(json.dumps(dict(base,list_columns=self.config())),encoding='utf-8')
        result,warning=ui_state.load(path);self.assertFalse(warning);self.assertEqual(result['list_columns'],validate(self.config()))

    def test_dialog_keyboard_visibility_reorder_apply_defaults_cancel_no_catalog_writes(self):
        before=encode(self.cat,self.adapter);disk=self.store.path.read_bytes()
        self.app.set_view('detail');self.app.open_columns();d=self.app.columns_dialog;self.root.update()
        self.assertGreaterEqual(d.winfo_rootx(),0);self.assertGreaterEqual(d.winfo_rooty(),0)
        from mon_gpt.atelier import PillButton
        def descendants(widget):
            for child in widget.winfo_children():
                yield child;yield from descendants(child)
        for button in descendants(d):
            if isinstance(button,PillButton) and button.text in ('Appliquer','Fermer'):
                self.assertTrue(button.winfo_viewable())
                self.assertLessEqual(button.winfo_rooty()+button.winfo_height(),d.winfo_rooty()+d.winfo_height())
        self.assertTrue(d.checks['title'].instate(['disabled']))
        d.checks['created'].focus_force();d.checks['created'].event_generate('<space>');self.root.update()
        self.assertIn('created',d.draft['visible'])
        d.up['created'].invoke();self.root.update();self.assertEqual(d.draft['order'][3],'created')
        d.checks['categories'].invoke();self.root.update();d.apply();self.root.update()
        self.assertIn('created',self.table.list_visible);self.assertNotIn('categories',self.table.list_visible)
        self.assertEqual(self.app.view.get(),'detail');self.assertEqual(self.table.row_height,126)
        applied=self.app.list_configuration();d.reset();self.assertEqual(self.app.list_configuration(),applied)
        d.destroy();self.assertEqual(self.app.list_configuration(),applied)
        self.app.open_columns();d=self.app.columns_dialog;d.reset();d.apply();d.destroy();self.root.update()
        self.assertEqual(self.app.list_configuration(),defaults())
        self.assertEqual(encode(self.cat,self.adapter),before);self.assertEqual(self.store.path.read_bytes(),disk)

    def test_resize_four_widths_saves_once_after_release_retains_order_across_views_reopen(self):
        self.app.resize(1600,900);self.root.update();self.app.apply_columns(self.config())
        ids=self.visible()[:3];self.table.selection_set(ids);self.root.update();before=encode(self.cat,self.adapter)
        with patch('mon_gpt.ui_state.atomic_write',wraps=ui_state.atomic_write) as write:
            for key in ('title','modified','context','created'):
                old=self.table.column(key,'width');self.drag_width(key,20)
                self.assertEqual(self.table.column(key,'width'),old+20)
            self.assertEqual(write.call_count,4)
        config=self.app.list_configuration();saved,_=ui_state.load(self.app.preferences_path);self.assertEqual(saved['list_columns'],config)
        for view in ('detail','mosaic','list'):
            self.app.set_view(view);self.root.update();self.assertEqual(set(self.table.selection()),set(ids))
            self.assertEqual(self.app.list_configuration(),config)
        self.assertEqual(self.table.secondary_order,['modified','context','created'])
        self.assertEqual(encode(self.cat,self.adapter),before)
        self.app.query.set('imaginaire');self.app.tag.set('Fiction');self.app.save_preferences()
        self.root.destroy()
        import tkinter as tk
        self.root=tk.Tk();self.app=App(self.root,self.store,self.cat,self.adapter,self.opener);self.root.update()
        self.table=self.app.results
        self.assertEqual(self.app.list_configuration(),config)
        self.assertEqual((self.app.query.get(),self.app.tag.get()),('imaginaire','Fiction'))
        self.opener.assert_not_called()

    def test_true_date_sort_minutes_offsets_local_display_and_project_dates(self):
        rows=self.items[:4]
        dates=['2025-12-31T12:00:00+00:00','2026-01-01T00:01:00+00:00','2026-11-16T14:45:00+01:00','2026-11-16T14:46:00+01:00']
        for i,(row,date) in enumerate(zip(rows,dates)):
            row.title=f'Tri date fictif {i}';row.created=date;row.modified=dates[3-i]
        self.app.query.set('Tri date fictif');c=self.config();c['sort']='created';self.app.apply_columns(c);self.root.update()
        before=encode(self.cat,self.adapter)
        self.assertEqual(self.table.get_children(),tuple(r.id for r in rows))
        self.app.sort_results('created');self.root.update();self.assertEqual(self.table.get_children(),tuple(r.id for r in reversed(rows)))
        self.app.sort_results('modified');self.root.update();self.assertEqual(self.table.get_children(),tuple(r.id for r in reversed(rows)))
        self.app.sort_results('modified');self.root.update();self.assertEqual(self.table.get_children(),tuple(r.id for r in rows))
        self.table.show_tip(rows[0].id,50);self.root.update()
        self.assertIn(display_date(rows[0].created,seconds=True),self.table.tip.cget('text'));self.table.hide_tip()
        for text in (self.table.itemcget(i,'text') for i in self.table.find_withtag('created')):
            self.assertTrue(text=='…' or '2025' in text or '2026' in text)
        self.assertEqual(encode(self.cat,self.adapter),before)
        # Le tri compare des instants, même quand les heures/offsets ISO trompent.
        self.assertLess(sort_value({'created':'2026-01-01T00:30:00+02:00'},'created'),sort_value({'created':'2025-12-31T23:00:00+00:00'},'created'))
        self.app.query.set('');self.scope(self.p.id);self.app.sort_results('created');self.root.update()
        self.assertEqual(self.table.item(self.child.id)['cells']['created'],self.child.created)

    def test_hidden_sort_reset_and_other_views_keep_layout(self):
        c=self.config();c['sort']='created';self.app.apply_columns(c)
        c=self.app.list_configuration();c['visible'].remove('created');self.app.apply_columns(c)
        self.assertEqual(self.app.sort_column,'title')
        self.app.set_view('mosaic');self.app.sort_results('modified');self.root.update()
        self.table.layout()
        self.assertEqual(self.table.view,'mosaic');self.assertEqual(self.table.header_height,0)
        self.app.set_view('detail');self.root.update();self.assertEqual(self.table.row_height,126)
        c=self.app.list_configuration();c['visible'].remove('modified');self.app.apply_columns(c)
        self.app.sort_results('modified');self.app.set_view('list');self.root.update()
        self.assertEqual(self.app.sort_column,'title');self.assertIn('masquée',self.app.status.get())

    def test_compact_order_scrolling_bounds_hidden_handles_and_arrow_only(self):
        c=self.config();self.app.apply_columns(c);before=encode(self.cat,self.adapter)
        for width,height,preview in ((1600,900,False),(1000,680,True)):
            self.app.resize(width,height)
            if self.app.inspector_visible!=preview:self.app.toggle_inspector()
            self.root.update();self.assertEqual(self.table.secondary_order,['modified','context','created'])
            self.assertNotIn('tags',self.table.layout());self.assertNotIn('categories',self.table.layout())
            identity=self.visible()[0];ax=self.arrow(identity)[0]
            for fraction in (0,1):
                self.table.xview('moveto',fraction);self.root.update()
                self.assertEqual(self.arrow(identity)[0],ax)
                for key in self.table.secondary_order:
                    x,size=self.table.visible_box(key)
                    if size:self.assertLessEqual(x+size,self.table.winfo_width()-36)
                x,y=self.point(identity,title=True);self.event_click(x,y);self.opener.assert_not_called()
                self.app.last_open=(None,0);self.event_click(*self.arrow(identity));self.opener.assert_called_once();self.opener.reset_mock()
            self.assertEqual(self.app.list_configuration(),validate(c))
        self.assertEqual(encode(self.cat,self.adapter),before)

    def test_reordered_columns_keep_multi_selection_drag_left_right_and_rename(self):
        self.app.apply_columns(self.config());self.scope(self.p.id)
        ids=[r.id for r in self.items[:3]];self.table.selection_set(ids);self.root.update()
        with patch.object(self.store,'save',wraps=self.store.save) as save:
            self.gesture(ids[0],self.q.id);save.assert_called_once()
        self.scope(self.q.id);self.table.selection_set(ids);self.root.update()
        with patch('mon_gpt.atelier.MenuSkin.popup'):
            self.gesture(ids[0],self.twin.id,button=3)
        with patch.object(self.store,'save',wraps=self.store.save) as save:
            self.app.active_menu.invoke(1);self.root.update();save.assert_called_once()
        for identity in ids:self.assertEqual(self.app.cat.records[identity].projects,[self.r.id,self.q.id,self.twin.id])
        self.assertEqual(self.table.secondary_order,['modified','context','created'])
        self.table.selection_set(ids[0]);self.table.focus_force();self.root.update()
        self.table.event_generate('<F2>');self.root.update();self.assertIsNotNone(self.app.inline)
        self.app.escape();self.opener.assert_not_called()

    def test_1429_rows_virtualized_config_sort_filter_and_preferences_write_failure(self):
        from batch_fixtures import fixture
        cat,adapter,projects,items=fixture(1429);self.app.cat,self.app.adapter=cat,adapter;self.app.scope='all'
        before=encode(cat,adapter);self.app.apply_columns(self.config());self.root.update()
        self.table.focus_force();self.table.event_generate('<Control-a>');self.root.update()
        self.assertEqual(len(self.table.selection()),1429);self.assertLess(len(self.table.find_all()),2000)
        self.app.sort_results('created');self.table.yview('moveto',1);self.root.update()
        self.assertLess(len(self.table.find_all()),2000)
        self.app.query.set('0003');self.app.refresh_results();self.root.update()
        self.assertEqual(len(self.table.selection()),1)
        with patch('mon_gpt.ui_state.atomic_write',side_effect=OSError('Panne fictive')):
            self.assertFalse(self.app.apply_columns(defaults()))
        self.assertIn('Préférences non enregistrées',self.app.status.get())
        self.assertEqual(encode(cat,adapter),before)
