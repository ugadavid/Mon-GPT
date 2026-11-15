"""MG-006 : surcharges indépendantes, anciens formats et contrôles partagés."""
import copy
import json
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock, patch
import zipfile
from PIL import Image
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.identity import resolve_identity, image_references, DEFAULTS
from mon_gpt.identity_ui import ProjectVisualFields, ProjectVisualStrip
from mon_gpt.storage import Store, encode, decode, read_backup
from mon_gpt.ui import App


class ThreadFixture:
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.store=Store(self.base/'data')
        self.cat=Catalog();self.a=self.cat.add('Montagne fictive','project');self.b=self.cat.add('Atelier fictif','project')
        self.a.visual={'image':'pack:montagne','icon':'compass','color':'petrole'}
        self.b.visual={'image':'pack:creation','icon':'palette','color':'prune'}
        self.adapter=ChatGPT(self.cat)
        self.f,_=self.adapter.ingest('Fil fictif partagé','https://chatgpt.com/c/00000000-0000-4000-8000-000000000601')
        self.cat.attach(self.f.id,[self.a.id,self.b.id]);self.f.notes='Notes conservées'
        self.f.tags=['Idées'];self.f.categories=['Imaginaire'];self.f.metadata={'État':'Fictif'}

    def asset(self,fmt='PNG'):
        path=self.base/('source.'+fmt.lower());Image.new('RGB',(128,72),'#aabbcc').save(path,fmt)
        return self.store.images.import_file(path),path


class ThreadDataTests(ThreadFixture,unittest.TestCase):
    def test_partial_overrides_dynamic_context_and_purity(self):
        for visual in ({},{'image':'pack:voyage'},{'icon':'star'},{'color':'ocre'},
                       {'image':'pack:voyage','icon':'star','color':'ocre'}):
            self.f.visual=visual;before=encode(self.cat,self.adapter)
            for scope,base in ((self.a.id,self.a),(self.b.id,self.b),('all',self.a)):
                actual=resolve_identity(self.cat,self.f.id,scope)
                for key in DEFAULTS: self.assertEqual(getattr(actual,key),visual.get(key,base.visual[key]))
            self.assertEqual(encode(self.cat,self.adapter),before)
        self.f.visual={'icon':'star'};self.a.visual['image']='pack:soleil';self.a.visual['color']='sauge'
        actual=resolve_identity(self.cat,self.f.id);self.assertEqual((actual.image,actual.icon,actual.color),('pack:soleil','star','sauge'))
        self.cat.attach(self.f.id,[self.b.id]);self.assertEqual(resolve_identity(self.cat,self.f.id).color,'prune')
        self.assertEqual(self.f.visual,{'icon':'star'})

    def test_unfiled_and_explicit_choice_equal_to_current_inheritance(self):
        self.f.visual={'color':'petrole'};self.a.visual['color']='rose'
        self.assertEqual(resolve_identity(self.cat,self.f.id).color,'petrole')
        self.cat.attach(self.f.id,[]);self.f.visual={'image':'pack:voyage','icon':'sun'}
        actual=resolve_identity(self.cat,self.f.id);self.assertEqual((actual.image,actual.icon,actual.color),('pack:voyage','sun','atelier'))
        self.f.visual={};self.assertIn(resolve_identity(self.cat,self.f.id).image,(None,'pack:soleil'))

    def test_schema_three_strict_and_old_schema_cannot_hide_overrides(self):
        for bad in ({'unknown':'x'},{'image':'../photo.png'},{'icon':'unknown'},{'color':'#123456'}, {'image':None}, [], {'image':'asset:'+'A'*64}):
            self.f.visual=bad
            with self.subTest(bad=bad),self.assertRaises(ValueError): decode(encode(self.cat,self.adapter))
        self.f.visual={'icon':'book'};data=encode(self.cat,self.adapter);self.assertEqual(data['schema'],3)
        for version in (1,2,4):
            old=copy.deepcopy(data);old['schema']=version
            with self.assertRaises(ValueError): decode(old)

    def test_v1_v2_migration_exact_backup_and_failure_safe(self):
        self.store.directory.mkdir()
        for version in (1,2):
            data=encode(self.cat,self.adapter);data['schema']=version
            if version==1:
                for row in data['records']: row.pop('visual')
            raw=json.dumps(data,ensure_ascii=False).encode('utf-8');self.store.path.write_bytes(raw)
            with patch('mon_gpt.storage.shutil.copy2',side_effect=OSError('Refus fictif')):
                with self.assertRaises(OSError): self.store.load()
            self.assertEqual(self.store.path.read_bytes(),raw)
            cat,adapter=self.store.load()
            self.assertEqual(json.loads(self.store.path.read_bytes())['schema'],3)
            self.assertEqual(list(self.store.directory.glob(f'avant-migration-v{version}-*.json'))[0].read_bytes(),raw)
            expected=copy.deepcopy(data);expected['schema']=3
            if version==1:
                for row in expected['records']: row['visual']={}
            self.assertEqual(encode(cat,adapter),expected)
            self.assertEqual(cat.records[self.f.id].visual,{})

    def test_thread_only_images_zip_all_formats_and_shared_resource_survives(self):
        for fmt in ('PNG','JPEG','WEBP'):
            ref,path=self.asset(fmt);self.f.visual={'image':ref,'color':'rose'}
            self.store.save(self.cat,self.adapter);path.unlink()
            self.assertEqual(image_references(self.cat),{ref})
            archive=self.base/(fmt+'.zip');self.store.export(archive,self.cat,self.adapter)
            with self.assertRaisesRegex(ValueError,'ZIP'): self.store.export(self.base/'incomplet.json',self.cat,self.adapter)
            other=Store(self.base/fmt);empty=Catalog()
            loaded,source,_=other.restore(read_backup(archive),empty,ChatGPT(empty))
            self.assertEqual(encode(loaded,source),encode(self.cat,self.adapter))
            self.assertEqual(other.images.read(ref),self.store.images.read(ref))
            self.a.visual['image']=ref;self.f.visual={};self.store.save(self.cat,self.adapter)
            self.assertTrue(self.store.images.path(ref).exists())
            self.a.visual['image']='pack:montagne'

    def test_old_zip_two_restore_and_missing_corrupt_thread_image_no_loss(self):
        data=encode(self.cat,self.adapter);data['schema']=2
        old=self.base/'ancien.zip'
        with zipfile.ZipFile(old,'w') as z: z.writestr('catalogue.json',json.dumps(data))
        cat,adapter,_=self.store.restore(read_backup(old),self.cat,self.adapter)
        self.assertEqual(cat.records[self.a.id].visual,self.a.visual)
        ref,_=self.asset();self.f.visual={'image':ref};self.store.save(self.cat,self.adapter)
        before=self.store.path.read_bytes();archive=self.base/'fil.zip';self.store.export(archive,self.cat,self.adapter)
        for raw in (None,b'corrompu'):
            broken=self.base/'invalide.zip'
            with zipfile.ZipFile(broken,'w') as z:
                z.writestr('catalogue.json',json.dumps(encode(self.cat,self.adapter)))
                if raw is not None: z.writestr('images/'+ref[6:]+'.png',raw)
            with self.assertRaises(ValueError): read_backup(broken)
            self.assertEqual(self.store.path.read_bytes(),before)


class ThreadUITests(ThreadFixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.root=tk.Tk();self.addCleanup(lambda:self.root.destroy())
        self.opener=Mock();self.app=App(self.root,self.store,self.cat,self.adapter,self.opener);self.root.update()
        self.app.scope=self.a.id;self.app.show_record(self.f.id);self.root.update()

    def choose(self,kind,value=None,inherit=False):
        fields=self.app.project_visual;fields.open(kind);self.root.update();layer=self.app.visual_layer
        if inherit: layer.defaults()
        else: next(tile for tile in layer.tiles if tile.value==value).choose()
        layer.accept();self.root.update()

    def test_shared_controls_independent_inheritance_cancel_and_explicit_equal(self):
        fields=self.app.project_visual;self.assertIsInstance(fields,ProjectVisualFields)
        self.assertEqual(fields.get(),{})
        for size in ((1360,820),(1000,680)):
            self.app.resize(*size);self.root.update()
            self.assertEqual(len({b.winfo_y() for b in fields.buttons.values()}),1)
            self.assertLessEqual(fields.winfo_height(),58)
        self.choose('image','pack:voyage');self.choose('icon','star');self.choose('color','ocre')
        self.assertEqual(fields.get(),{'image':'pack:voyage','icon':'star','color':'ocre'})
        self.choose('image',inherit=True);self.assertEqual(fields.get(),{'icon':'star','color':'ocre'})
        self.assertEqual(fields.value['image'],'pack:montagne')
        self.assertIn('Héritée',fields.control_name('image'));self.assertIn('Personnalisée',fields.control_name('icon'))
        fields.open('color');self.app.visual_layer.defaults();self.app.visual_layer.cancel()
        self.assertEqual(fields.get()['color'],'ocre')
        self.choose('color',inherit=True);self.choose('icon',inherit=True)
        self.assertEqual(fields.get(),{})
        self.choose('image','pack:montagne')
        self.assertEqual(fields.get(),{'image':'pack:montagne'})
        self.assertTrue(self.app.dirty);self.assertEqual(self.f.visual,{})

    def test_save_summary_views_banner_and_reopen(self):
        self.choose('image','pack:voyage');self.choose('icon','star')
        before=(self.f.notes,list(self.f.projects),list(self.f.tags),self.adapter.to_list())
        self.assertTrue(self.app.save_record());self.root.update()
        self.assertEqual(self.f.visual,{'image':'pack:voyage','icon':'star'})
        self.app.show_summary(self.f.id);self.root.update()
        strip=self.app.summary.visual_strip;self.assertIsInstance(strip,ProjectVisualStrip);self.assertIsNone(strip.choose)
        for view in ('list','detail','mosaic'):
            self.app.set_view(view);self.root.update()
            visual=self.app.results.item(self.f.id)['visual']
            self.assertEqual((visual.image,visual.icon,visual.color),('pack:voyage','star','petrole'))
            self.assertEqual(self.app.masthead.identity,visual)
            self.assertEqual(strip.value['image'],visual.image)
            if view=='list':
                drawn=self.app.results.find_withtag('effective_icon')
                self.assertTrue(drawn)
                self.assertIn(str(self.app.project_icons.get('star','petrole',20)),[self.app.results.itemcget(i,'image') for i in drawn])
            self.assertIs(self.app.results.item(self.f.id)['image'],self.app.project_icons.get('star','petrole',20))
        self.app.results.selection_set(self.f.id);self.app.set_mosaic_size('large');self.app.close()
        self.root=tk.Tk();self.app=App(self.root,self.store,*self.store.load(),self.opener);self.root.update()
        self.assertEqual(self.app.masthead.identity.image,'pack:voyage');self.assertEqual(self.app.mosaic_size.get(),'large')
        self.assertEqual((self.f.notes,self.f.projects,self.f.tags,self.adapter.to_list()),before)
        self.opener.assert_not_called()

    def test_abandon_draft_and_import_existing_layer(self):
        before=encode(self.cat,self.adapter);self.choose('color','ocre')
        with patch('mon_gpt.details.messagebox.askyesnocancel',return_value=None):
            self.assertFalse(self.app.can_leave())
        self.assertTrue(self.app.dirty)
        with patch('mon_gpt.details.messagebox.askyesnocancel',return_value=False):
            self.assertTrue(self.app.select_identity(self.b.id))
        self.assertEqual(encode(self.cat,self.adapter),before)
        self.app.show_record(self.f.id);ref,path=self.asset('JPEG')
        self.app.project_visual.open('image');layer=self.app.visual_layer
        with patch('mon_gpt.identity_ui.filedialog.askopenfilename',return_value=str(path)): layer.import_image()
        layer.accept();self.assertEqual(self.app.project_visual.get(),{'image':ref})


if __name__=='__main__': unittest.main()
