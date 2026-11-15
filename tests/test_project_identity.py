"""Identité des projets : migration, images portables, héritage et brouillons."""
import copy
import hashlib
import io
import json
from pathlib import Path
import struct
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch, Mock
import zipfile
import zlib
from PIL import Image
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store,encode,decode,read_backup,Backup
from mon_gpt.identity import resolve_identity,DEFAULTS,PALETTE,COVERS
from mon_gpt.images import checked_image,MAX_BYTES,ImageLibrary
from mon_gpt.ui import App


class IdentityDataTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.store=Store(self.base/'catalogue')
        self.cat=Catalog()
        self.a=self.cat.add('Écriture fictive','project')
        self.b=self.cat.add('Montagne fictive','project',self.a.id)
        self.adapter=ChatGPT(self.cat)
        self.item,_=self.adapter.ingest('Fil partagé fictif','https://chatgpt.com/c/00000000-0000-4000-8000-000000000003')
        self.cat.attach(self.item.id,[self.a.id,self.b.id])
        self.item.notes='Notes fictives conservées'
        self.item.tags=['Été'];self.item.categories=['Création'];self.item.metadata={'État':'Fictif'}

    def image_file(self,kind='PNG',color='#a8b98c'):
        path=self.base/('original.'+kind.lower())
        Image.new('RGB',(320,180),color).save(path,format=kind)
        return path

    def legacy(self):
        data=encode(self.cat,self.adapter)
        data['schema']=1
        for row in data['records']: row.pop('visual')
        return data

    def test_schema_one_migration_exact_backup_and_no_loss(self):
        self.store.directory.mkdir()
        raw=json.dumps(self.legacy(),ensure_ascii=False).encode('utf-8')
        self.store.path.write_bytes(raw)
        before=encode(self.cat,self.adapter)
        actual=encode(*self.store.load())
        self.assertEqual(actual,before)
        self.assertEqual(json.loads(self.store.path.read_bytes())['schema'],2)
        backups=list(self.store.directory.glob('avant-migration-v1-*.json'))
        self.assertEqual(len(backups),1);self.assertEqual(backups[0].read_bytes(),raw)
        self.store.load()
        self.assertEqual(len(list(self.store.directory.glob('avant-migration*'))),1)

    def test_migration_backup_failure_and_future_schema_never_replace(self):
        self.store.directory.mkdir()
        self.store.path.write_text(json.dumps(self.legacy()),encoding='utf-8')
        before=self.store.path.read_bytes()
        with patch('mon_gpt.storage.shutil.copy2',side_effect=OSError('Copie refusée')):
            with self.assertRaises(OSError): self.store.load()
        self.assertEqual(self.store.path.read_bytes(),before)
        future=self.legacy();future['schema']=99
        self.store.path.write_text(json.dumps(future),encoding='utf-8')
        before=self.store.path.read_bytes()
        with self.assertRaises(ValueError): self.store.load()
        self.assertEqual(self.store.path.read_bytes(),before)

    def test_identity_resolution_is_stable_and_does_not_rewrite_links(self):
        self.a.visual={'image':'pack:voyage','icon':'compass','color':'petrole'}
        self.b.visual={'image':'pack:montagne','icon':'mountain','color':'ocre'}
        links=list(self.item.projects)
        self.assertEqual(resolve_identity(self.cat,self.item.id).project,self.a.id)
        self.assertEqual(resolve_identity(self.cat,self.item.id,self.b.id).image,'pack:montagne')
        self.assertEqual(resolve_identity(self.cat,self.a.id,self.b.id).icon,'compass')
        self.assertEqual(self.item.projects,links)
        orphan=self.cat.add('Sans projet')
        self.assertIsNone(resolve_identity(self.cat,orphan.id).image)
        self.assertIsNone(resolve_identity(self.cat).image)
        self.assertEqual(resolve_identity(self.cat,self.b.id).color,'ocre')

    def test_visual_validation_rejects_paths_unknown_values_and_item_overrides(self):
        for kind,key,value in [('project','image','../photo.png'),('project','image','asset:'+'A'*64),
                               ('project','icon','unknown'),('project','color','#123456'),('item','icon','book')]:
            data=encode(self.cat,self.adapter)
            row=next(r for r in data['records'] if r['kind']==kind)
            row['visual']={key:value}
            with self.subTest(kind=kind,key=key),self.assertRaises(ValueError): decode(data)
        data=encode(self.cat,self.adapter);data['records'][0]['visual']={'x':'y'}
        with self.assertRaises(ValueError): decode(data)

    def test_png_jpeg_webp_import_survive_original_removal_and_shared_replacement(self):
        for kind,color in [('PNG','#a8b98c'),('JPEG','#c98163'),('WEBP','#75a2bb')]:
            with self.subTest(kind=kind):
                original=self.image_file(kind,color)
                ref=self.store.images.import_file(original)
                self.a.visual={'image':ref};self.b.visual={'image':ref}
                self.store.save(self.cat,self.adapter)
                original.unlink()
                loaded,_=self.store.load()
                self.assertEqual(loaded.records[self.b.id].visual['image'],ref)
                self.assertEqual(self.store.images.open(ref).size,(320,180))
                self.a.visual={'image':'pack:creation'}
                self.cat.delete(self.a.id)
                self.store.save(self.cat,self.adapter)
                self.assertTrue(self.store.images.path(ref).exists())
                self.assertEqual(self.store.images.open(ref).size,(320,180))
                # Rétablir le projet du sous-test sans toucher à la copie partagée.
                self.cat.records[self.a.id]=self.a

    def test_real_content_size_dimensions_animation_and_corruption_are_checked(self):
        raw=self.image_file().read_bytes()
        disguised=self.base/'photo.jpg';disguised.write_bytes(raw)
        self.assertTrue(self.store.images.import_file(disguised).startswith('asset:'))
        for data in (b'pas une image',raw[:42],b'x'*(MAX_BYTES+1)):
            with self.assertRaises(ValueError): checked_image(data)
        # Entêtes PNG valides : limites vérifiées avant toute allocation du bitmap.
        for w,h in [(9000,16),(6000,5000),(1,1)]:
            ihdr=struct.pack('>IIBBBBB',w,h,8,2,0,0,0)
            data=raw[:8]+struct.pack('>I',13)+b'IHDR'+ihdr+struct.pack('>I',zlib.crc32(b'IHDR'+ihdr))+raw[33:]
            with self.assertRaises(ValueError): checked_image(data)
        stream=io.BytesIO()
        Image.new('RGB',(32,32),'red').save(stream,format='WEBP',save_all=True,append_images=[Image.new('RGB',(32,32),'blue')])
        with self.assertRaises(ValueError): checked_image(stream.getvalue())

    def test_complete_zip_roundtrip_fresh_directory_and_prebackup_with_images(self):
        ref=self.store.images.import_file(self.image_file())
        self.a.visual={'image':ref,'icon':'book','color':'lavande'}
        self.b.visual={'image':ref}
        original=encode(self.cat,self.adapter)
        destination=self.base/'complete.zip'
        self.store.export(destination,self.cat,self.adapter)
        other=Store(self.base/'neuf')
        empty=Catalog();adapter=ChatGPT(empty)
        cat,source,_=other.restore(read_backup(destination),empty,adapter)
        self.assertEqual(encode(cat,source),original)
        self.assertEqual(other.images.read(ref),self.store.images.read(ref))
        self.assertEqual(encode(*other.load()),original)
        replacement=encode(Catalog(),ChatGPT(Catalog()))
        _,_,backup=other.restore(replacement,cat,source)
        self.assertEqual(backup.suffix,'.zip')
        self.assertEqual(read_backup(backup).images[ref],self.store.images.read(ref))
        with self.assertRaisesRegex(ValueError,'ZIP'): self.store.export(self.base/'incomplet.json',self.cat,self.adapter)

    def test_historical_json_restore_remains_available(self):
        path=self.base/'historique.json';path.write_text(json.dumps(self.legacy()),encoding='utf-8')
        restored,source,_=self.store.restore(read_backup(path),self.cat,self.adapter)
        self.assertEqual(encode(restored,source),encode(self.cat,self.adapter))

    def test_archive_rejects_paths_duplicates_missing_extra_corrupt_and_future(self):
        self.store.save(self.cat,self.adapter)
        before=self.store.path.read_bytes()
        data=encode(self.cat,self.adapter)
        variants=[('..\\evil.png',b'x'),('../evil.png',b'x'),('/evil.png',b'x'),('C:/evil.png',b'x'),('extra.txt',b'x')]
        for name,content in variants:
            path=self.base/'hostile.zip'
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('catalogue.json',json.dumps(data));z.writestr(name,content)
            with self.subTest(name=name),self.assertRaises(ValueError): read_backup(path)
            self.assertEqual(self.store.path.read_bytes(),before)
        for variation in ('duplicate','missing','hash','future','catalogue'):
            current=copy.deepcopy(data)
            ref='asset:'+'0'*64
            if variation in ('missing','hash'): current['records'][0]['visual']={'image':ref}
            if variation=='future': current['schema']=17
            path=self.base/'bad.zip'
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('catalogue.json','cassé' if variation=='catalogue' else json.dumps(current))
                if variation=='duplicate': z.writestr('CATALOGUE.JSON',json.dumps(current))
                if variation=='hash': z.writestr('images/'+'0'*64+'.png',self.image_file().read_bytes())
            with self.subTest(variation=variation),self.assertRaises(ValueError): read_backup(path)
            self.assertEqual(self.store.path.read_bytes(),before)

    def test_restore_failed_catalog_commit_preserves_old_assets_and_catalog(self):
        ref=self.store.images.import_file(self.image_file())
        self.a.visual={'image':ref}
        self.store.save(self.cat,self.adapter)
        before=self.store.path.read_bytes();asset=self.store.images.read(ref)
        newref=self.store.images.import_file(self.image_file('JPEG','#aabbcc'))
        candidate=encode(self.cat,self.adapter);candidate['records'][0]['visual']={'image':newref}
        incoming=Backup(candidate,{newref:self.store.images.read(newref)})
        with patch('mon_gpt.storage.atomic_write',side_effect=OSError('Panne fictive')):
            with self.assertRaises(OSError): self.store.restore(incoming,self.cat,self.adapter)
        self.assertEqual(self.store.path.read_bytes(),before)
        self.assertEqual(self.store.images.read(ref),asset)
        self.assertEqual(len(list(self.store.directory.glob('avant-restauration-*.zip'))),1)

    def test_pack_is_local_complete_landscape_and_palette_has_sixteen(self):
        self.assertEqual(len(PALETTE),16)
        library=ImageLibrary(self.base/'absent')
        for key in COVERS:
            with self.subTest(key=key): self.assertEqual(library.open('pack:'+key).size,(1200,675))

    def test_archive_limits_and_catalog_write_limits_are_consistent(self):
        self.store.save(self.cat,self.adapter)
        before=self.store.path.read_bytes()
        path=self.base/'limits.zip'
        self.store.export(path,self.cat,self.adapter)
        with patch('mon_gpt.storage.MAX_ARCHIVE',1),self.assertRaises(ValueError): read_backup(path)
        with patch('mon_gpt.storage.MAX_EXPANDED',1),self.assertRaises(ValueError): read_backup(path)
        with patch('mon_gpt.storage.MAX_CATALOG',1),self.assertRaises(ValueError): self.store.save(self.cat,self.adapter)
        self.assertEqual(self.store.path.read_bytes(),before)
        # Pas de ressource partagée écrasée par une restauration incohérente.
        ref=self.store.images.import_file(self.image_file())
        self.a.visual={'image':ref};self.store.save(self.cat,self.adapter)
        archive=self.base/'resource.zip';self.store.export(archive,self.cat,self.adapter)
        self.store.images.path(ref).write_bytes(b'copie locale endommagee fictive')
        before=self.store.path.read_bytes()
        with self.assertRaises(ValueError): self.store.restore(read_backup(archive),self.cat,self.adapter)
        self.assertEqual(self.store.path.read_bytes(),before)
        self.assertEqual(self.store.images.path(ref).read_bytes(),b'copie locale endommagee fictive')


class IdentityUITests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=tk.Tk();self.addCleanup(self.root.destroy)
        self.cat=Catalog();self.project=self.cat.add('Projet fictif','project')
        self.adapter=ChatGPT(self.cat)
        self.item,_=self.adapter.ingest('Fil fictif','https://chatgpt.com/c/00000000-0000-4000-8000-000000000015')
        self.cat.attach(self.item.id,[self.project.id])
        self.app=App(self.root,Store(self.temp.name),self.cat,self.adapter,Mock(return_value=True))
        self.root.update();self.root.focus_force()
        self.app.show_record(self.project.id);self.root.update()

    def test_three_layers_cancel_apply_default_ctrl_s_and_reload(self):
        before=encode(self.cat,self.adapter)
        for kind,value in [('image','pack:montagne'),('icon','compass'),('color','terracotta')]:
            fields=self.app.project_visual
            fields.open(kind);self.root.update()
            layer=self.app.visual_layer
            layer.selected=value;layer.refresh();layer.cancel();self.root.update()
            self.assertEqual(fields.get()[kind],DEFAULTS[kind])
            self.assertEqual(encode(self.cat,self.adapter),before)
            fields.open(kind);self.root.update()
            layer=self.app.visual_layer;layer.selected=value;layer.refresh();layer.accept()
            self.assertTrue(self.app.dirty)
            self.assertEqual(encode(self.cat,self.adapter),before)
        self.root.event_generate('<Control-s>');self.root.update()
        self.assertEqual(self.project.visual,{'image':'pack:montagne','icon':'compass','color':'terracotta'})
        loaded,_=self.app.store.load()
        self.assertEqual(loaded.records[self.project.id].visual,self.project.visual)
        self.app.project_visual.open('image');self.root.update()
        self.app.visual_layer.defaults();self.app.visual_layer.accept()
        self.assertEqual(self.app.project_visual.get()['image'],DEFAULTS['image'])
        with patch('mon_gpt.ui.messagebox.askyesnocancel',return_value=None):
            self.assertFalse(self.app.can_leave())
        self.assertTrue(self.app.dirty)

    def test_layer_escape_keyboard_focus_compact_and_invalid_import_preserve_choice(self):
        self.app.resize(1000,680);self.root.update()
        fields=self.app.project_visual;fields.open('color');self.root.update()
        layer=self.app.visual_layer
        self.assertEqual(len(layer.tiles),16)
        layer.tiles[0].neighbor(1);self.root.update()
        self.assertIs(self.root.focus_get(),layer.tiles[1])
        layer.tiles[1].choose();self.root.update()
        self.assertEqual(layer.selected,'sauge')
        self.app.escape();self.root.update()
        self.assertIsNone(self.app.visual_layer)
        self.assertTrue(self.app.inspector_visible)
        self.assertIs(self.root.focus_get(),fields.buttons['color'])
        fields.open('image');self.root.update();layer=self.app.visual_layer
        with patch('mon_gpt.identity_ui.filedialog.askopenfilename',return_value='inexistant.png'):
            layer.import_image()
        self.assertEqual(layer.selected,DEFAULTS['image'])
        self.assertTrue(layer.error.cget('text'))
        layer.cancel()

    def test_context_changes_immediately_and_fil_editor_stays_unchanged(self):
        self.project.visual={'image':'pack:montagne','icon':'mountain','color':'petrole'}
        self.app.show_record(self.project.id);self.root.update()
        self.assertEqual(self.app.masthead.identity.image,'pack:montagne')
        self.app.select_identity(self.item.id);self.root.update()
        self.assertEqual(self.app.masthead.identity.project,self.project.id)
        self.app.show_record(self.item.id);self.root.update()
        self.assertIsNone(self.app.project_visual)
        self.assertNotIn('image',self.app.fields)
        self.app.select_identity(None);self.root.update()
        self.assertIsNone(self.app.masthead.identity.image)


if __name__=='__main__': unittest.main()
