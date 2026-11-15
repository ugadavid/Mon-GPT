"""MG-004a : reprise sûre, séparée du métier et sans ouverture de fil."""
import json
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock,patch
from mon_gpt import ui_state
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store
from mon_gpt.ui import App


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=Store(Path(self.temp.name));self.path=self.store.directory/'interface.json'
        self.cat=Catalog();self.adapter=ChatGPT(self.cat)
        self.parent=self.cat.add('Voyages fictifs','project')
        self.child=self.cat.add('Carnet des îles','project',self.parent.id)
        self.child.visual={'image':'pack:voyage','icon':'compass','color':'petrole'}
        self.other=self.cat.add('Branche fermée','project');self.cat.add('Enfant fermé','project',self.other.id)
        self.opened=self.cat.add('Autre branche ouverte','project');self.cat.add('Enfant ouvert','project',self.opened.id)
        self.fils=[]
        for n in range(25):
            r,_=self.adapter.ingest(f'Voyage imaginaire {n:02}',f'https://chatgpt.com/c/00000000-0000-4000-8000-{n+500:012d}')
            r.tags=['Idées'];r.categories=['Imaginaire'];r.notes='Note fictive intacte'
            self.cat.attach(r.id,[self.child.id]);self.fils.append(r)
        self.store.save(self.cat,self.adapter)
        self.before=self.store.path.read_bytes()
        self.root=tk.Tk();self.addCleanup(self.destroy_root)
        self.opener=Mock(return_value=True)

    def destroy_root(self):
        try: self.root.destroy()
        except tk.TclError: pass

    def state(self,**changes):
        data={'version':1,'view':'detail','inspector':True,'geometry':'1000x680',
              'query':'voyage','tag':'Idées','category':'Imaginaire','scope':self.child.id,
              'selected':self.fils[-1].id,'expanded_projects':[self.parent.id,self.opened.id]}
        data.update(changes);return data

    def write(self,data): self.path.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')

    def app(self,data):
        if data is not None: self.write(data)
        app=App(self.root,self.store,self.cat,self.adapter,self.opener)
        self.root.update();return app

    def test_validation_old_optional_fields_bounds_and_invalid_whole_fallback(self):
        old={k:self.state()[k] for k in ('version','view','inspector','geometry')}
        self.write(old);self.assertEqual(ui_state.load(self.path),(old,''))
        self.write(self.state());self.assertEqual(ui_state.load(self.path),(self.state(),''))
        bad=[{'query':[]},{'query':'x'*4097},{'tag':False},{'category':None},{'scope':self.fils[0].id+'x'},
             {'selected':'https://chatgpt.com/c/fictif'},{'expanded_projects':'all'},
             {'expanded_projects':[self.parent.id]*2},{'expanded_projects':[self.parent.id]*4097},
             {'expanded_projects':[False]},{'view':'future'},{'version':True},{'geometry':[]},{'geometry':'99999x99999'}]
        for change in bad:
            with self.subTest(change=str(change)[:60]):
                self.write(self.state(**change));data,warning=ui_state.load(self.path)
                self.assertEqual(data,{});self.assertTrue(warning)
        self.path.write_bytes(b'x'*(ui_state.MAX_BYTES+1));self.assertEqual(ui_state.load(self.path)[0],{})
        self.path.write_bytes(b'\xff');self.assertEqual(ui_state.load(self.path)[0],{})
        self.path.write_bytes(b'['*1200+b']'*1200);self.assertEqual(ui_state.load(self.path)[0],{})
        self.assertEqual(self.store.path.read_bytes(),self.before)

    def test_atomic_write_whitelist_and_failure_preserves_previous_file(self):
        self.write(self.state());previous=self.path.read_bytes()
        with patch('mon_gpt.ui_state.atomic_write',side_effect=OSError('Panne fictive')):
            with self.assertRaises(OSError): ui_state.save(self.path,False,'1360x820')
        self.assertEqual(self.path.read_bytes(),previous)
        data=self.state();data.pop('version')
        ui_state.save(self.path,**data)
        loaded,warning=ui_state.load(self.path);self.assertFalse(warning)
        self.assertEqual(loaded,self.state())
        self.assertFalse({'notes','images','url','schema'} & loaded.keys())

    def test_restore_detail_filters_scope_selection_preview_branches_and_scroll(self):
        app=self.app(self.state())
        self.assertFalse(app.restoring_workspace)
        self.assertEqual((app.query.get(),app.tag.get(),app.category.get()),('voyage','Idées','Imaginaire'))
        self.assertEqual(app.scope,self.child.id);self.assertEqual(app.tree.selection(),(self.child.id,))
        self.assertEqual(app.results.selection(),(self.fils[-1].id,));self.assertEqual(app.current,self.fils[-1].id)
        self.assertTrue(app.inspector_visible);self.assertFalse(app.editing)
        self.assertTrue(hasattr(app,'summary'));self.assertEqual(app.masthead.identity.project,self.child.id)
        self.assertEqual(app.masthead.identity.image,'pack:voyage')
        self.assertTrue(app.tree.item(self.parent.id,'open'));self.assertTrue(app.tree.item(self.opened.id,'open'))
        self.assertFalse(app.tree.item(self.other.id,'open'))
        bbox=app.results.bbox(self.fils[-1].id);self.assertTrue(bbox)
        self.assertLessEqual(bbox[1]+bbox[3],app.results.winfo_height()+1)
        self.opener.assert_not_called();self.assertEqual(self.store.path.read_bytes(),self.before)

    def test_list_hidden_inspector_and_all_closed_survive_refresh(self):
        app=self.app(self.state(view='list',inspector=False,scope='all',expanded_projects=[]))
        self.assertEqual(app.view.get(),'list');self.assertFalse(app.inspector_visible)
        self.assertEqual(app.current,self.fils[-1].id)
        for _ in range(2):
            app.refresh_tree();self.root.update()
            self.assertFalse(any(app.tree.item(r.id,'open') for r in self.cat.records.values() if r.kind=='project'))
        app.toggle_inspector();self.root.update();self.assertFalse(app.editing)
        self.assertEqual(app.current,self.fils[-1].id);self.opener.assert_not_called()

    def test_stale_scope_or_record_falls_back_and_filtered_selection_clears(self):
        unknown='00000000-0000-4000-8000-000000000999'
        for change in ({'scope':unknown},{'scope':self.fils[0].id},{'selected':unknown}):
            with self.subTest(change=change):
                top=tk.Toplevel(self.root);self.write(self.state(**change))
                app=App(top,self.store,self.cat,self.adapter,self.opener);self.root.update()
                self.assertEqual(app.scope,'all');self.assertIsNone(app.current)
                self.assertEqual(app.view.get(),'list');self.assertFalse(app.inspector_visible)
                self.assertTrue('défaut' in app.status.get());top.destroy()
        app=self.app(self.state(query='aucunrésultat',expanded_projects=[unknown,self.parent.id]))
        self.assertFalse(app.results.selection());self.assertIsNone(app.current)
        self.assertTrue(app.inspector_visible);self.assertFalse(app.editing)
        self.assertFalse(app.results.get_children());self.assertIsNone(app.masthead.identity.project)
        self.opener.assert_not_called();self.assertEqual(self.store.path.read_bytes(),self.before)

    def test_corrupt_preferences_default_ui_does_not_replace_any_data(self):
        self.path.write_text('{cassé',encoding='utf-8')
        app=self.app(None)
        self.assertEqual((app.scope,app.current,app.view.get()),('all',None,'list'))
        self.assertFalse(app.inspector_visible);self.assertTrue(app.status.get())
        self.assertEqual(self.path.read_text(encoding='utf-8'),'{cassé')
        self.assertEqual(self.store.path.read_bytes(),self.before);self.opener.assert_not_called()

    def test_close_guard_cancellation_then_full_state_saved_and_read_only_reopened(self):
        app=self.app(self.state());self.root.focus_force();app.show_record(self.fils[-1].id)
        app.editor_controls['title'].insert('end',' — brouillon');self.root.update()
        previous=self.path.read_bytes()
        with patch('mon_gpt.details.messagebox.askyesnocancel',return_value=None): app.close()
        self.assertTrue(self.root.winfo_exists());self.assertEqual(self.path.read_bytes(),previous)
        app.set_view('list');app.tree.item(self.opened.id,open=False)
        with patch('mon_gpt.details.messagebox.askyesnocancel',return_value=False): app.close()
        saved,warning=ui_state.load(self.path);self.assertFalse(warning)
        self.assertEqual(saved['view'],'list');self.assertEqual(saved['scope'],self.child.id)
        self.assertEqual(saved['selected'],self.fils[-1].id)
        self.assertNotIn(self.opened.id,saved['expanded_projects'])
        self.root=tk.Tk();reopened=App(self.root,self.store,self.cat,self.adapter,self.opener);self.root.update()
        self.assertEqual(reopened.current,self.fils[-1].id);self.assertFalse(reopened.editing)
        self.assertTrue(reopened.inspector_visible);self.assertEqual(self.store.path.read_bytes(),self.before)
        self.opener.assert_not_called()

    def test_historical_preferences_default_workspace_and_unfiled_empty(self):
        old={k:self.state()[k] for k in ('version','view','inspector','geometry')}
        app=self.app(old)
        self.assertEqual(app.scope,'all');self.assertIsNone(app.current)
        self.assertEqual(app.query.get(),'');self.assertEqual(app.view.get(),'detail')
        self.assertTrue(app.tree.item(self.other.id,'open'))
        top=tk.Toplevel(self.root);self.write(self.state(scope='unfiled',selected=None))
        other=App(top,self.store,self.cat,self.adapter,self.opener);self.root.update()
        self.assertEqual(other.scope,'unfiled');self.assertEqual(other.tree.selection(),('unfiled',))
        self.assertFalse(other.results.get_children());self.assertIsNone(other.current);top.destroy()
        self.opener.assert_not_called()


if __name__=='__main__': unittest.main()
