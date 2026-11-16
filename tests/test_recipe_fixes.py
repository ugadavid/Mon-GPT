"""MG-010a : périmètre de vue et événements Tk réels, données fictives."""
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock,patch
from PIL import Image

from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store,encode,read_backup
from mon_gpt.ui import App


class RecipeFixTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=tk.Tk();self.addCleanup(self.root.destroy)
        self.cat=Catalog();self.parent=self.cat.add('Atelier fictif','project')
        self.child=self.cat.add('Carnet fictif','project',self.parent.id)
        self.grandchild=self.cat.add('Études fictives','project',self.child.id)
        self.adapter=ChatGPT(self.cat)
        self.items=[]
        for index,(title,projects) in enumerate((('Fil du parent',[self.parent.id]),('Fil enfant',[self.child.id]),('Fil profond',[self.grandchild.id]),('Fil partagé',[self.parent.id,self.child.id]),('Fil à classer',[])),1):
            r,_=self.adapter.ingest(title,f'https://chatgpt.com/c/00000000-0000-4000-8000-{index:012}')
            self.cat.attach(r.id,projects);r.tags=['Repère'];r.categories=['Fiction'];r.notes='Note fictive conservée'
            self.items.append(r)
        self.adapter.project_links={'g-p-atelier-fictif':self.parent.id}
        self.store=Store(self.temp.name);self.store.save(self.cat,self.adapter)
        self.opener=Mock(return_value=True)
        self.app=App(self.root,self.store,self.cat,self.adapter,self.opener)
        self.root.update();self.app.place_initial_sash(force=True);self.root.update()
        self.table=self.app.results

    def scope(self,identity):
        self.app.scope=identity;self.app.refresh_results();self.root.update()
        return set(self.table.get_children())

    def click(self,widget,x=14,y=14,stamp=10000):
        widget.event_generate('<ButtonPress-1>',x=x,y=y,time=stamp)
        if widget.winfo_exists():widget.event_generate('<ButtonRelease-1>',x=x,y=y,time=stamp+20)
        self.root.update()

    def double(self,tile):
        self.click(tile,stamp=20000)
        tile.event_generate('<ButtonPress-1>',x=14,y=14,time=20100)
        self.root.event_generate('<ButtonRelease-1>',x=14,y=14,time=20120)
        self.root.update()

    def gallery(self,record=None,width=340,kind='image'):
        self.app.show_record((record or self.parent).id);self.root.update()
        self.app.panes.sashpos(1,self.app.panes.winfo_width()-width);self.root.update()
        self.app.project_visual.open(kind);self.root.update()
        return self.app.visual_layer

    def button(self,layer,text):
        def children(widget):
            for w in widget.winfo_children():
                yield w;yield from children(w)
        return next(w for w in children(layer) if getattr(w,'text',None)==text)

    def drag(self,key,delta):
        start,width=self.table.layout()[key];x=round(start+width)
        self.table.event_generate('<Motion>',x=x,y=15);self.root.update()
        self.assertEqual(self.table.cget('cursor'),'sb_h_double_arrow')
        self.assertTrue(self.table.find_withtag('column_grip'))
        self.table.event_generate('<ButtonPress-1>',x=x,y=15,time=30000)
        self.table.event_generate('<B1-Motion>',x=x+delta,y=15,state=256,time=30100)
        self.table.event_generate('<ButtonRelease-1>',x=x+delta,y=15,time=30200)
        self.root.update()

    def test_direct_scope_all_three_views_and_generic_search_unchanged(self):
        before=encode(self.cat,self.adapter)
        self.assertIn(self.items[2],self.cat.search(project=self.parent.id))
        expected=((self.parent.id,{self.items[0].id,self.items[3].id,self.child.id}),
                  (self.child.id,{self.items[1].id,self.items[3].id,self.grandchild.id}),
                  (self.grandchild.id,{self.items[2].id}))
        for scope,identities in expected:
            for view in ('list','detail','mosaic'):
                self.app.set_view(view)
                self.assertEqual(self.scope(scope),identities)
                self.assertEqual(self.app.results_label.cget('text'),'Contenu du projet')
                count=sum(self.cat.records[i].kind=='item' for i in identities)
                self.assertIn(f'{count} discussion',self.app.result_count.cget('text'))
        self.assertEqual(encode(self.cat,self.adapter),before)
        self.opener.assert_not_called()

    def test_search_filters_multi_attachment_and_global_unfiled(self):
        self.app.query.set('profond');self.assertEqual(self.scope(self.parent.id),set())
        self.assertEqual(self.scope('all'),{self.items[2].id})
        self.app.query.set('');self.app.tag.set('repere');self.app.category.set('fiction')
        self.assertEqual(self.scope(self.parent.id),{self.items[0].id,self.items[3].id})
        self.app.tag.set('');self.app.category.set('')
        self.assertEqual(self.scope('all'),{r.id for r in self.items})
        self.assertEqual(self.scope('unfiled'),{self.items[4].id})
        self.assertEqual(self.items[3].projects,[self.parent.id,self.child.id])

    def test_four_columns_mouse_resize_sort_no_open_and_session_widths(self):
        self.app.resize(1600,900);self.root.update()
        self.assertEqual(self.table.headings['title']['text'],'Titre')
        self.assertEqual(self.table.headings['context']['text'],'Projet')
        self.assertIn('Carnet fictif',self.table.item(self.items[3].id,'values')[1])
        before=encode(self.cat,self.adapter);order=self.table.get_children()
        initial=self.table.layout()['title'][1]
        self.drag('title',-100)
        self.assertEqual(self.table.layout()['title'][1],initial-100)
        for key in ('context','categories','tags'):
            width=self.table.column(key,'width');self.drag(key,20)
            self.assertEqual(self.table.column(key,'width'),width+20)
            self.assertEqual(self.table.visible_box(key)[1],width+20)
        self.assertEqual(self.table.get_children(),order);self.assertFalse(self.app.sort_reverse)
        widths={k:self.table.column(k,'width') for k in ('title','context','categories','tags')}
        for view in ('detail','mosaic','list'):self.app.set_view(view);self.root.update()
        self.assertEqual(widths,{k:self.table.column(k,'width') for k in widths})
        x=self.table.layout()['title'][0]+20
        self.click(self.table,x,15,40000)
        self.assertTrue(self.app.sort_reverse)
        self.opener.assert_not_called();self.assertEqual(encode(self.cat,self.adapter),before)

    def test_scrolled_handles_minimums_compact_and_pinned_action(self):
        self.app.resize(1000,680);self.root.update()
        self.drag('title',-15)
        for key in ('context','categories','tags'):self.table.column(key,width=360)
        self.table.draw();self.table.xview('moveto',1);self.root.update()
        self.drag(self.table.secondary_order[-1],-30)
        self.assertTrue(self.table.xview()[0]>0)
        for key in self.table.secondary_order:
            x,size=self.table.visible_box(key)
            if size:self.assertLessEqual(x+size,self.table.winfo_width()-36)
        self.table.xview('moveto',0);self.drag('title',-1000)
        self.assertEqual(self.table.column('title','width'),180)
        self.app.toggle_inspector();self.root.update()
        self.assertGreater(self.table.layout()['title'][1],0)
        self.assertEqual(sum(self.table.layout()['open']),self.table.winfo_width())
        self.opener.assert_not_called()

    def test_cover_cards_responsive_for_projects_and_threads(self):
        self.app.resize(1600,950);self.root.update()
        for record in (self.parent,self.items[0]):
            layer=self.gallery(record,width=340)
            tile=layer.tiles[0];narrow=(tile.winfo_width(),tile.winfo_height())
            self.assertAlmostEqual(tile.photo.width()/tile.photo.height(),16/9,delta=.04)
            self.app.panes.sashpos(1,self.app.panes.winfo_width()-650);self.root.update()
            self.assertGreater(tile.winfo_width(),narrow[0]);self.assertGreater(tile.winfo_height(),narrow[1])
            self.assertAlmostEqual(tile.photo.width()/tile.photo.height(),16/9,delta=.02)
            self.assertLess(tile.photo.height()+6,tile.winfo_height()-25)
            layer.canvas.yview_moveto(1);self.root.update();self.assertGreater(layer.canvas.yview()[0],0)
            layer.cancel()

    def test_image_single_click_cancel_keyboard_and_use_do_not_save(self):
        before=encode(self.cat,self.adapter);disk=self.store.path.read_bytes()
        layer=self.gallery();tile=next(t for t in layer.tiles if t.value=='pack:voyage')
        self.click(tile)
        self.assertEqual(layer.selected,'pack:voyage');self.assertFalse(self.app.dirty)
        self.assertEqual(self.app.project_visual.get()['image'],'pack:soleil')
        layer.cancel();self.assertEqual(encode(self.cat,self.adapter),before)
        layer=self.gallery();tile=next(t for t in layer.tiles if t.value=='pack:montagne')
        tile.focus_force();self.root.update();tile.event_generate('<space>');self.root.update()
        self.assertEqual(layer.selected,'pack:montagne');self.assertIs(self.app.visual_layer,layer)
        tile.event_generate('<Return>');self.root.update()
        self.click(self.button(layer,'Utiliser'),stamp=50000)
        self.assertIsNone(self.app.visual_layer);self.assertTrue(self.app.dirty)
        self.assertEqual(self.store.path.read_bytes(),disk)
        with patch('mon_gpt.details.messagebox.askyesnocancel',return_value=False):self.assertTrue(self.app.can_leave())
        self.app.show_record(self.parent.id);self.root.update()
        self.assertEqual(self.app.project_visual.get()['image'],'pack:soleil')

    def test_image_double_click_applies_once_returns_focus_without_saving(self):
        before=encode(self.cat,self.adapter);disk=self.store.path.read_bytes()
        self.root.focus_force();self.root.update()
        layer=self.gallery();fields=self.app.project_visual
        tile=next(t for t in layer.tiles if t.value=='pack:voyage')
        with patch.object(fields,'set_choice',wraps=fields.set_choice) as choose:
            self.double(tile);layer.accept()
            choose.assert_called_once_with('image','pack:voyage')
        self.assertIsNone(self.app.visual_layer)
        self.assertEqual(self.root.focus_get(),fields.buttons['image'])
        self.assertEqual(fields.get()['image'],'pack:voyage');self.assertTrue(self.app.dirty)
        self.assertEqual(encode(self.cat,self.adapter),before);self.assertEqual(self.store.path.read_bytes(),disk)

    def test_personal_image_double_click_thread_save_backup_and_mapping(self):
        path=Path(self.temp.name)/'portrait-fictif.png';Image.new('RGB',(90,160),'gold').save(path)
        before=encode(self.cat,self.adapter);layer=self.gallery(self.items[0])
        with patch('mon_gpt.identity_ui.filedialog.askopenfilename',return_value=str(path)):layer.import_image()
        ref=layer.selected
        tile=next(t for t in layer.tiles if t.value==ref);layer.canvas.yview_moveto(1);self.root.update()
        self.double(tile)
        self.assertTrue(self.app.dirty);self.assertEqual(encode(self.cat,self.adapter),before)
        self.assertEqual(self.app.project_visual.get()['image'],ref)
        self.assertTrue(self.app.save_record());self.root.update()
        target=Path(self.temp.name)/'complet.zip';self.store.export(target,self.app.cat,self.app.adapter)
        bundle=read_backup(target);self.assertIn(ref,bundle.images)
        self.assertEqual(bundle.data['schema'],4)
        self.assertEqual(bundle.data['chatgpt_projects'],self.adapter.project_links)
        self.assertEqual(self.items[0].projects,[self.parent.id])

    def test_icon_and_color_tiles_unchanged_no_double_accept(self):
        for kind,height in (('icon',68),('color',54)):
            layer=self.gallery(kind=kind)
            tile=layer.tiles[1]
            self.assertEqual(int(tile.cget('height')),height)
            self.assertFalse(tile.bind('<Double-Button-1>'))
            self.double(tile)
            self.assertIs(self.app.visual_layer,layer);self.assertFalse(self.app.dirty)
            layer.cancel()
