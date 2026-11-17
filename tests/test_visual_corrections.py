"""Contrats MG-003b : repères visibles, scène entière et commandes compactes."""
import gc
import hashlib
import json
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock,patch
from PIL import Image,ImageDraw,ImageTk,ImageColor
from mon_gpt.theme import COLORS
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.core import Catalog
from mon_gpt.identity import COVERS,ICONS,PALETTE,DEFAULTS,resolve_identity
from mon_gpt.identity_ui import contained_picture
from mon_gpt.project_icons import icon_picture
from mon_gpt.storage import Store,encode,decode,read_backup
from mon_gpt.ui import App


class VisualCorrectionsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)
        self.root=tk.Tk();self.addCleanup(self.root.destroy)
        self.cat=Catalog();self.a=self.cat.add('Projet avec un titre fictif suffisamment long pour son infobulle','project')
        self.b=self.cat.add('Sous-projet explicite','project',self.a.id)
        self.b.visual={'image':'pack:ecriture','icon':'book','color':'terracotta'}
        self.adapter=ChatGPT(self.cat)
        self.item,_=self.adapter.ingest('Fil fictif','https://chatgpt.com/c/00000000-0000-4000-8000-000000000023')
        self.cat.attach(self.item.id,[self.a.id,self.b.id])
        self.item.notes='Notes communes à conserver'
        self.store=Store(self.directory)
        self.app=App(self.root,self.store,self.cat,self.adapter,Mock(return_value=True))
        self.root.update();self.root.focus_force()

    def test_thirty_six_distinct_icons_preserve_old_ids_and_exact_palette(self):
        self.assertTrue({'folder','book','leaf','compass','mountain','flask','palette','circuit'}<=ICONS.keys())
        self.assertEqual(len(ICONS),36)
        signatures=set()
        for name in ICONS:
            picture=icon_picture(name,'#447984',20)
            self.assertTrue(picture.getbbox(),name)
            signatures.add(hashlib.sha256(picture.tobytes()).hexdigest())
        self.assertEqual(len(signatures),36)
        self.assertEqual([c[1] for c in PALETTE.values()],['#315E4F','#8FA98B','#6D7C52','#6A9990','#BD7658','#D6A18B','#C69B9F','#916A80','#D3BD92','#BE944C','#D9B75D','#92715E','#91A8BD','#447984','#AB9BBE','#6E7D94'])

    def test_tree_uses_colored_icons_cache_survives_refresh_reorder_move_and_inline(self):
        self.a.visual={'icon':'microscope','color':'petrole'}
        self.app.refresh_tree();self.root.update()
        cache=self.app.project_icons
        photo=cache.get('microscope','petrole')
        self.assertEqual(self.app.tree.item(self.a.id,'image'),(str(photo),))
        self.assertEqual(self.app.tree.item(self.b.id,'image'),(str(cache.get('book','terracotta')),))
        pixels=ImageTk.getimage(photo)
        self.assertTrue(any(pixels.getpixel((x,y))[:3]==(68,121,132) and pixels.getpixel((x,y))[3]>180
                            for y in range(20) for x in range(20)))
        self.cat.move(self.b.id,None);self.cat.reorder(self.b.id,-1)
        self.app.sort.set('Alphabétique français');self.app.refresh_tree()
        gc.collect();self.root.update()
        self.assertIs(photo,cache.get('microscope','petrole'))
        self.assertEqual(int(self.root.tk.call('image','width',str(photo))),20)
        self.assertEqual(self.app.tree.item(self.a.id,'text'),self.a.title)
        self.assertEqual(self.app.tree.parent(self.b.id),'')
        self.app.scope='all';self.app.new('project');self.root.update()
        self.assertEqual(self.app.tree.item('__draft__','image'),(str(cache.get()),))
        self.assertNotIn(str(self.app.icons['project']),self.app.tree.item('__draft__','image'))
        self.app.cancel_inline();self.assertFalse(self.app.tree.exists('__draft__'))
        self.app.scope=self.a.id;self.app.new('project');self.root.update()
        _,y,_,height=self.app.tree.bbox('__draft__')
        image_pixels=[x for x in range(self.app.tree.winfo_width())
                      if self.app.tree.identify_element(x,y+height//2).endswith('image')]
        self.assertTrue(image_pixels)
        self.assertGreater(self.app.inline.winfo_x(),max(image_pixels))
        self.app.cancel_inline()

    def test_editor_row_three_independent_controls_and_summary_is_read_only(self):
        before=encode(self.cat,self.adapter)
        for size in ((1360,820),(1000,680)):
            self.app.resize(*size);self.app.show_record(self.a.id);self.root.update()
            fields=self.app.project_visual
            buttons=list(fields.buttons.values())
            self.assertEqual(len({b.winfo_y() for b in buttons}),1)
            self.assertLessEqual(fields.winfo_height(),58)
            for b in buttons:
                self.assertLessEqual(b.winfo_x()+b.winfo_width(),fields.winfo_width())
                self.assertTrue(b.cget('takefocus'))
                self.assertFalse(any(b.type(item)=='text' for item in b.find_all()))
            for kind in ('image','icon','color'):
                button=fields.buttons[kind];button.focus_set()
                button.event_generate('<Return>');self.root.update()
                self.assertEqual(self.app.visual_layer.kind,kind)
                self.app.escape();self.root.update()
                self.assertIs(self.root.focus_get(),button)
            self.assertEqual(encode(self.cat,self.adapter),before)
        self.app.show_summary(self.b.id);self.root.update()
        strip=self.app.summary.visual_strip
        self.assertEqual(strip.value['image'],'pack:ecriture')
        for button in strip.buttons.values(): button.activate()
        self.assertFalse(self.app.editing)
        self.assertIsNone(getattr(self.app,'visual_layer',None))
        self.app.show_summary(self.item.id);self.root.update()
        self.assertTrue(hasattr(self.app.summary,'visual_strip'))
        self.assertIsNone(self.app.summary.visual_strip.choose)

    def test_round_swatches_names_keyboard_focus_and_grid_of_icons(self):
        self.app.show_record(self.a.id);self.root.update()
        self.app.project_visual.open('color');self.root.update()
        layer=self.app.visual_layer
        self.assertEqual(len(layer.tiles),16)
        for tile in layer.tiles:
            self.assertFalse(any(tile.type(item) in ('polygon','rectangle') for item in tile.find_all()))
            self.assertEqual(tile.accessible_name,PALETTE[tile.value][0])
        layer.tiles[0].neighbor(1);self.root.update()
        focused=layer.tiles[1]
        self.assertIsNotNone(focused.tip.timer)
        focused.tip.hide();focused.tip.show();self.root.update()
        self.assertEqual(focused.tip.window.winfo_children()[0].cget('text'),'Sauge')
        self.app.escape()
        self.app.project_visual.open('icon');self.root.update()
        layer=self.app.visual_layer
        self.assertEqual(len(layer.tiles),36)
        layer.tiles[-1].focus_set();self.root.update()
        self.assertLessEqual(layer.tiles[-1].winfo_rooty()+layer.tiles[-1].winfo_height(),layer.canvas.winfo_rooty()+layer.canvas.winfo_height()+1)
        layer.cancel()

    def test_header_contains_whole_landscape_portrait_and_never_changes_shell(self):
        # Les bandes aux quatre bords rendent un recadrage détectable.
        refs=[]
        for size in ((160,90),(90,160)):
            im=Image.new('RGB',size,'#ffffff');d=ImageDraw.Draw(im);w,h=size
            d.rectangle((0,0,w-1,7),fill='#ff0000');d.rectangle((0,h-8,w-1,h-1),fill='#0000ff')
            d.rectangle((0,8,7,h-9),fill='#00ff00');d.rectangle((w-8,8,w-1,h-9),fill='#ffff00')
            path=self.directory/f'{w}.png';im.save(path)
            refs.append(self.store.images.import_file(path))
        landscape=contained_picture(self.store.images,refs[0],128,72)
        self.assertEqual(landscape.getpixel((64,0)),(255,0,0,255))
        self.assertEqual(landscape.getpixel((64,71)),(0,0,255,255))
        portrait=contained_picture(self.store.images,refs[1],128,72)
        self.assertEqual(portrait.getpixel((64,0)),(255,0,0,255))
        self.assertEqual(portrait.getpixel((64,71)),(0,0,255,255))
        self.assertEqual(portrait.getpixel((0,36)),ImageColor.getcolor(COLORS["ivory"],"RGBA"))
        for dimensions in ((1360,820),(1000,680),(1800,900)):
            self.app.resize(*dimensions);self.app.ensure_inspector();self.root.update()
            header=self.app.masthead
            height=header.winfo_height()
            menu_height=self.app.main_menu.winfo_height()
            search_y=self.app.search_line.winfo_rooty()
            for ref in ['pack:montagne',*refs]:
                self.a.visual={'image':ref,'icon':'microscope','color':'petrole'}
                self.app.update_identity() if self.app.current==self.a.id else self.app.select_identity(self.a.id)
                self.root.update()
                self.assertEqual(header.winfo_height(),height)
                self.assertEqual(self.app.main_menu.winfo_height(),menu_height)
                self.assertEqual(self.app.search_line.winfo_rooty(),search_y)
                self.assertEqual(len(header.find_withtag('context_cover')),1)
                self.assertFalse(header.find_withtag('landscape'))
                x,y,w,h=header.cover_box
                self.assertGreater(w,0)
                self.assertGreaterEqual(y,0);self.assertLessEqual(y+h,height)
                if ref in refs:
                    pixels=ImageTk.getimage(header.photo)
                    # La réduction Lanczos peut mélanger quelques pixels voisins.
                    for pos,expected in [((w//2,0),(255,0,0)),((w//2,h-1),(0,0,255))]:
                        actual=pixels.getpixel(pos)[:3]
                        self.assertLess(max(abs(a-b) for a,b in zip(actual,expected)),16)
                for item in header.find_all():
                    if header.type(item)=="text":
                        l,t,r,b=header.bbox(item)
                        self.assertTrue(r<=x or l>=x+w or b<=y or t>=y+h)

    def test_solar_default_old_choices_migration_reopen_and_portable_images(self):
        self.assertEqual(DEFAULTS['image'],'pack:soleil')
        self.assertTrue({'ecriture','voyage','montagne','laboratoire','creation','technique'}<=COVERS.keys())
        legacy=encode(self.cat,self.adapter);legacy['schema']=1
        for row in legacy['records']: row.pop('visual')
        self.store.path.write_text(json.dumps(legacy),encoding='utf-8')
        migrated,source=self.store.load()
        self.assertEqual(resolve_identity(migrated,self.a.id).image,'pack:soleil')
        self.assertEqual(migrated.records[self.a.id].visual,{})
        self.assertEqual(migrated.records[self.item.id].projects,self.item.projects)
        self.store.save(self.cat,self.adapter)
        loaded,_=self.store.load()
        self.assertEqual(loaded.records[self.b.id].visual,self.b.visual)
        self.assertEqual(resolve_identity(loaded,self.b.id).image,'pack:ecriture')
        self.app.show_record(self.b.id);self.root.update()
        self.app.project_visual.open('image');self.root.update()
        self.app.visual_layer.defaults();self.app.visual_layer.accept()
        self.assertEqual(self.app.project_visual.get()['image'],'pack:soleil')
        self.assertEqual(self.b.visual['image'],'pack:ecriture')
        self.app.dirty=False;self.app.show_summary(None,checked=True);self.root.update()
        self.assertEqual(self.app.masthead.photo_key[0],'pack:soleil')
        path=self.directory/'portrait.png';Image.new('RGB',(90,160),'#bb7733').save(path)
        ref=self.store.images.import_file(path)
        self.a.visual={'image':ref,'icon':'microscope','color':'petrole'}
        self.store.export(self.directory/'reference.zip',self.cat,self.adapter)
        fresh=Store(self.directory/'restaure')
        empty=Catalog()
        c,a,_=fresh.restore(read_backup(self.directory/'reference.zip'),empty,ChatGPT(empty))
        self.assertEqual(encode(c,a),encode(self.cat,self.adapter))
        self.assertEqual(fresh.images.read(ref),self.store.images.read(ref))


if __name__=='__main__': unittest.main()
