"""MG-007 : intégrité du pack et intégration dans les sélecteurs existants."""
import hashlib
import json
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock
from PIL import Image
from mon_gpt.identity import COVERS, resolve_identity
from mon_gpt.images import PACK, ImageLibrary
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store, encode, read_backup
from mon_gpt.ui import App

ROOT=Path(__file__).resolve().parents[1]


class CoverAssetsTests(unittest.TestCase):
    def test_twenty_four_sources_jpegs_dimensions_and_historical_bytes(self):
        manifest=json.loads((ROOT/'reports/MG-007/inventaire.json').read_text(encoding='utf-8'))
        rows=manifest['covers'];self.assertEqual(len(rows),24)
        self.assertEqual(len(COVERS),31)
        self.assertEqual(set(COVERS),set(manifest['historical_sha256'])|{r['key'][5:] for r in rows})
        self.assertEqual(len({r['source'] for r in rows}),24)
        self.assertEqual(set(PACK.glob('*.jpg')),{PACK/(k+'.jpg') for k in COVERS})
        for key,digest in manifest['historical_sha256'].items():
            self.assertEqual(hashlib.sha256((PACK/(key+'.jpg')).read_bytes()).hexdigest(),digest)
        for row in rows:
            with self.subTest(key=row['key']):
                source=ROOT/'missions/MG-007-illustrations'/row['source']
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),row['source_sha256'])
                self.assertEqual(COVERS[row['key'][5:]],row['theme'])
                with Image.open(PACK/row['jpeg']) as image:
                    self.assertEqual(image.format,'JPEG');self.assertEqual(image.size,(1200,675));image.verify()
                self.assertLess(row['jpeg_bytes'],row['source_bytes']//4)

    def test_all_thirty_one_load_locally_with_distinct_old_new_writing(self):
        library=ImageLibrary(ROOT/'inexistant-recette')
        for key in COVERS:
            with self.subTest(key=key): self.assertEqual(library.open('pack:'+key).size,(1200,675))
        self.assertNotEqual(library.open('pack:ecriture').tobytes(),library.open('pack:ecriture_carnet').tobytes())


class CoverGalleryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=Store(self.temp.name);self.cat=Catalog();self.a=self.cat.add('Atelier fictif','project')
        self.a.visual={'image':'pack:ecriture','icon':'book','color':'terracotta'}
        self.adapter=ChatGPT(self.cat)
        self.f,_=self.adapter.ingest('Carnet fictif','https://chatgpt.com/c/00000000-0000-4000-8000-000000000701')
        self.cat.attach(self.f.id,[self.a.id]);self.f.visual={'icon':'star','color':'ocre'}
        self.root=tk.Tk();self.addCleanup(self.root.destroy)
        self.app=App(self.root,self.store,self.cat,self.adapter,Mock());self.root.update()
        self.app.scope=self.a.id

    def test_existing_gallery_reaches_last_choice_keyboard_wheel_normal_compact(self):
        self.app.show_record(self.a.id)
        for size in ((1360,820),(1000,680)):
            self.app.resize(*size);self.app.project_visual.open('image');self.root.update()
            layer=self.app.visual_layer;self.assertEqual(len(layer.tiles),31)
            self.root.focus_force();self.root.update()
            layer.tiles[0].focus_set();self.root.update()
            for tile in layer.tiles[:-1]: tile.neighbor(1);self.root.update()
            last=layer.tiles[-1];self.assertIs(self.root.focus_get(),last)
            self.assertEqual(last.value,'pack:animaux')
            self.assertGreater(layer.canvas.yview()[0],0)
            self.assertLessEqual(last.winfo_rooty()+last.winfo_height(),layer.canvas.winfo_rooty()+layer.canvas.winfo_height()+2)
            layer.canvas.yview_moveto(0)
            for _ in range(40): last.event_generate('<MouseWheel>',delta=-120)
            self.root.update();self.assertEqual(layer.canvas.yview()[1],1)
            last.choose();layer.accept();self.assertTrue(self.app.save_record());self.root.update()
        self.assertEqual(self.a.visual['image'],'pack:animaux')
        self.app.project_visual.open('image');self.app.visual_layer.defaults();self.app.visual_layer.accept()
        self.assertEqual(self.app.project_visual.get()['image'],'pack:soleil')

    def test_shared_project_thread_choices_inheritance_views_save_zip_and_reload(self):
        before=encode(self.cat,self.adapter)
        self.app.show_record(self.f.id);self.app.project_visual.open('image');self.root.update()
        layer=self.app.visual_layer
        next(t for t in layer.tiles if t.value=='pack:ecriture_carnet').choose();layer.accept()
        self.assertTrue(self.app.save_record());self.root.update()
        self.assertEqual(self.f.visual,{'image':'pack:ecriture_carnet','icon':'star','color':'ocre'})
        for view in ('list','detail','mosaic'):
            self.app.set_view(view);self.root.update()
            self.assertEqual(self.app.results.item(self.f.id)['visual'].image,'pack:ecriture_carnet')
            self.assertEqual(self.app.masthead.identity.image,'pack:ecriture_carnet')
        self.assertEqual(resolve_identity(self.cat,self.a.id).image,'pack:ecriture')
        archive=Path(self.temp.name)/'pack.zip';self.store.export(archive,self.cat,self.adapter)
        other=Store(Path(self.temp.name)/'restaure');empty=Catalog()
        loaded,source,_=other.restore(read_backup(archive),empty,ChatGPT(empty))
        self.assertEqual(encode(loaded,source),encode(self.cat,self.adapter))
        self.assertEqual(resolve_identity(loaded,self.f.id).image,'pack:ecriture_carnet')
        self.app.show_record(self.f.id);self.app.project_visual.open('image')
        self.app.visual_layer.defaults();self.app.visual_layer.accept();self.assertTrue(self.app.save_record())
        self.assertEqual(self.f.visual,{'icon':'star','color':'ocre'})
        self.assertEqual(resolve_identity(self.cat,self.f.id).image,'pack:ecriture')
        after=encode(*self.store.load())
        for doc in (before,after):
            for r in doc['records']: r.pop('modified');r.pop('visual')
        self.assertEqual(before,after)


if __name__=='__main__': unittest.main()
