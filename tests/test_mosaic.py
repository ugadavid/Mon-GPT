"""MG-005 : grille, actions partagées et reprise sans ouverture automatique."""
from pathlib import Path
import tempfile
import tkinter as tk
from types import SimpleNamespace
import unittest
from unittest.mock import Mock,patch
from PIL import Image,ImageDraw,ImageTk
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store,encode
from mon_gpt.identity import resolve_identity
from mon_gpt.mosaic import GridLayout
from mon_gpt.ui import App
from mon_gpt import ui_state


class GridTests(unittest.TestCase):
    def test_responsive_geometry_sizes_gaps_and_partial_last_row(self):
        for width,normal,large in ((1010,4,2),(650,2,1),(280,1,1),(1580,6,4)):
            for size,cols in (('normal',normal),('large',large)):
                grid=GridLayout(width,size);self.assertEqual(grid.columns,cols)
                self.assertEqual(grid.image_width*9,grid.image_height*16)
                for index in range(13):
                    x,y,w,h=grid.box(index,37)
                    self.assertGreaterEqual(x,0);self.assertLessEqual(x+w,width)
                    self.assertEqual(grid.hit(x+w/2,y+h/2,37,13),index)
                    self.assertIsNone(grid.hit(x+w+2,y+h/2,37,13))
                    self.assertIsNone(grid.hit(x+w/2,y+h+2,37,13))
                self.assertLess(len(grid.visible(500,400,10000)),40)
        self.assertGreater(GridLayout(1010,'large').image_width,GridLayout(1010).image_width)
        grid=GridLayout(1010);x,y,w,h=grid.box(5)
        self.assertIsNone(grid.hit(x+5,y+5,0,5))


class MosaicTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=Store(Path(self.temp.name));self.cat=Catalog();self.adapter=ChatGPT(self.cat)
        self.a=self.cat.add('Récits fictifs','project');self.b=self.cat.add('Horizons fictifs','project')
        self.child=self.cat.add('Couleurs fictives','project',self.a.id)
        self.a.visual={'image':'pack:ecriture','icon':'book','color':'terracotta'}
        self.b.visual={'image':'pack:montagne','icon':'compass','color':'petrole'}
        self.child.visual={'image':'pack:creation','icon':'palette','color':'prune'}
        self.items=[]
        for n in range(72):
            r,_=self.adapter.ingest(f'{n:02} Voyage imaginaire '+('entre les îles et les montagnes '*9 if n==0 else ''),f'https://chatgpt.com/c/00000000-0000-4000-8000-{n+700:012d}')
            r.tags=['Idées','Été'];r.categories=['Imaginaire'];r.description='Résumé fictif à garder dans l’inspecteur.';r.notes='Note partagée intacte'
            if n!=2: self.cat.attach(r.id,[self.a.id,self.b.id] if n==0 else [[self.a.id],[self.b.id],[self.child.id]][n%3])
            self.items.append(r)
        self.root=tk.Tk();self.addCleanup(self.destroy_root)
        self.opener=Mock(return_value=True);self.app=App(self.root,self.store,self.cat,self.adapter,self.opener)
        self.root.update();self.root.focus_force();self.table=self.app.results
        self.app.set_view('mosaic');self.root.update()

    def destroy_root(self):
        try: self.root.destroy()
        except tk.TclError: pass

    def point(self,record):
        self.table.see(record.id);self.root.update()
        x,y,w,h=self.table.bbox(record.id)
        return int(x+w/2),int(y+30)

    def click(self,x,y):
        self.table.event_generate('<ButtonPress-1>',x=int(x),y=int(y))
        self.table.event_generate('<ButtonRelease-1>',x=int(x),y=int(y));self.root.update()

    def test_hit_test_columns_gaps_title_arrow_double_enter_and_project(self):
        r=self.items[1];x,y=self.point(r)
        self.click(x,y);self.assertEqual(self.app.current,r.id);self.opener.assert_not_called()
        tx,ty,tw,th=self.table.bbox(r.id,'title')
        self.assertFalse(self.table.open_hit(r.id,tx+tw-2,ty+38))
        self.click(tx+3,ty+8);self.opener.assert_not_called()
        self.opener.reset_mock();self.app.last_open=(None,0)
        bx,by,bw,bh=self.table.bbox(r.id);self.click(bx+bw-22,ty+10);self.opener.assert_called_once()
        self.opener.reset_mock();self.table.event_generate('<Return>');self.root.update();self.opener.assert_not_called()
        self.opener.reset_mock();self.app.last_open=(None,0)
        self.app.result_double(SimpleNamespace(x=x,y=y));self.opener.assert_not_called()
        self.app.scope=self.a.id;self.app.refresh_results();self.root.update();self.table.see(self.child.id)
        x,y,w,h=self.table.bbox(self.child.id)
        self.assertFalse(self.table.open_hit(self.child.id,x+w-22,y+h-40))
        self.opener.reset_mock();self.table.focus(self.child.id);self.table.focus_set();self.app.result_enter();self.root.update()
        self.opener.assert_not_called()

    def test_keyboard_four_directions_scroll_resize_and_size_controls(self):
        self.table.focus_set();self.table.focus(self.items[0].id);self.table.selection_set(self.items[0].id)
        self.table.event_generate('<Right>');self.root.update();self.assertEqual(self.table.focus(),self.items[1].id)
        cols=self.table.grid_layout().columns
        self.table.event_generate('<Down>');self.root.update();self.assertEqual(self.table.focus(),self.items[1+cols].id)
        self.table.event_generate('<Left>');self.root.update();self.assertEqual(self.table.focus(),self.items[cols].id)
        self.table.event_generate('<Up>');self.root.update();self.assertEqual(self.table.focus(),self.items[0].id)
        for width,height,preview in ((1360,820,False),(1360,820,True),(1000,680,True),(1000,680,False),(1900,1000,True)):
            self.app.resize(width,height)
            if self.app.inspector_visible!=preview: self.app.toggle_inspector()
            self.root.update()
            for size in ('normal','large'):
                self.app.set_mosaic_size(size);self.root.update();self.table.focus(self.items[-1].id);self.table.selection_set(self.items[-1].id);self.table.see(self.items[-1].id)
                box=self.table.bbox(self.items[-1].id);self.assertTrue(box)
                self.assertLessEqual(box[1]+box[3],self.table.winfo_height()+1)
                self.assertEqual(self.table.xview(),(0,1))
                for key,button in self.app.mosaic_size_buttons.items():
                    self.assertTrue(button.winfo_viewable())
                    self.assertEqual(button.tone=="chip",key==size)
                self.assertLessEqual(self.app.mosaic_tools.winfo_x()+self.app.mosaic_tools.winfo_width(),self.app.viewbar.winfo_width())
        self.opener.assert_not_called()

    def test_images_whole_portrait_cache_visible_only_and_metadata_without_repeated_path(self):
        path=self.store.directory/'portrait.png';im=Image.new('RGB',(90,160),'white');d=ImageDraw.Draw(im)
        d.rectangle((0,0,89,8),fill='red');d.rectangle((0,151,89,159),fill='blue');im.save(path)
        ref=self.store.images.import_file(path);self.a.visual['image']=ref;self.app.refresh_results();self.root.update()
        grid=self.table.grid_layout();photo=self.table.cover(ref,grid.image_width);pixels=ImageTk.getimage(photo)
        self.assertEqual(photo.width()*9,photo.height()*16)
        for y,expected in ((0,(255,0,0)),(photo.height()-1,(0,0,255))):
            pixel=pixels.getpixel((photo.width()//2,y))[:3]
            self.assertLessEqual(max(abs(channel-target) for channel,target in zip(pixel,expected)),5)
        texts=[self.table.itemcget(i,'text') for i in self.table.find_all() if self.table.type(i)=='text']
        self.assertTrue(any('Récits fictifs' in t for t in texts))
        self.assertTrue(any('Résumé' in t for t in texts))
        self.assertIn('Idées',texts)
        self.assertLess(len(self.table.find_withtag('cover')),len(self.items))
        with patch.object(self.store.images,'open',wraps=self.store.images.open) as opened:
            self.table.draw();self.table.hover(self.items[0].id);self.table.draw();opened.assert_not_called()
        for n in range(2000):
            self.table.insert('', 'end',iid=f'fictif-widget-{n}',values=(f'Carte fictive {n}','Chemin caché','',''),tags=('item',),visual=resolve_identity(self.cat,self.items[0].id))
        self.root.update();self.table.yview('moveto',1);self.root.update()
        self.assertLess(len(self.table.find_withtag('cover')),40);self.assertLessEqual(len(self.table.covers),192)
        self.app.query.set('zzintrouvable');self.app.refresh_results();self.root.update()
        self.assertFalse(self.table.get_children());self.assertFalse(self.table.find_withtag('cover'))

    def test_switch_three_views_keeps_shared_results_context_dirty_and_inheritance(self):
        self.app.scope=self.a.id;self.app.query.set('Voyage');self.app.tag.set('Idées');self.app.category.set('Imaginaire');self.app.refresh_results()
        self.table.selection_set(self.items[0].id);self.root.update();self.app.show_record(self.items[0].id)
        self.app.editor_controls['title'].insert('end',' — brouillon');self.app.dirty=True
        before=encode(self.cat,self.adapter);ids=self.table.get_children();editor=self.app.editor.winfo_children()
        self.app.sort_results('tags')
        ids=self.table.get_children()
        for view in ('list','detail','mosaic','list','mosaic'):
            self.app.set_view(view);self.root.update()
            self.assertEqual(self.table.get_children(),ids);self.assertEqual(self.table.selection(),(self.items[0].id,))
            self.assertEqual(self.app.editor.winfo_children(),editor);self.assertTrue(self.app.dirty)
            self.assertEqual((self.app.query.get(),self.app.tag.get(),self.app.category.get(),self.app.scope),('Voyage','Idées','Imaginaire',self.a.id))
            self.assertEqual(self.app.sort_column,'tags')
        self.assertEqual(encode(self.cat,self.adapter),before);self.opener.assert_not_called()
        self.app.dirty=False;self.app.scope=self.b.id;self.app.refresh_results();self.root.update()
        self.assertEqual(self.table.item(self.items[0].id)['visual'].image,'pack:montagne')
        self.assertEqual(self.table.get_children().count(self.items[0].id),1)
        self.app.scope='all';self.app.refresh_results();self.root.update()
        self.assertEqual(self.table.item(self.items[0].id)['visual'].image,'pack:ecriture')

    def test_drag_from_second_column_preserves_other_links_and_forbidden_target(self):
        self.app.scope=self.a.id;self.app.refresh_results();self.root.update()
        r=self.items[0];x,y=self.point(r)
        event=SimpleNamespace(x=x,y=y,x_root=self.table.winfo_rootx()+x,y_root=self.table.winfo_rooty()+y)
        self.app.drag_press(event,self.table,1)
        self.assertEqual(self.app.drag['id'],r.id)
        tx,ty,tw,th=self.app.tree.bbox(self.child.id)
        drop=SimpleNamespace(x=-100,y=100,x_root=self.app.tree.winfo_rootx()+tx+tw/2,y_root=self.app.tree.winfo_rooty()+ty+th/2)
        self.app.drag_motion(drop);self.app.drag_release(drop,self.table,1)
        r=self.app.cat.records[r.id]
        self.assertEqual(r.projects,[self.b.id,self.child.id]);self.assertEqual(r.notes,'Note partagée intacte')
        # Navigation réelle : synchroniser l'arbre et le périmètre, y compris
        # les événements de sélection laissés en file par le déplacement.
        self.app.tree.selection_set(self.child.id);self.app.select_scope();self.root.update();x,y=self.point(r)
        event=SimpleNamespace(x=x,y=y,x_root=self.table.winfo_rootx()+x,y_root=self.table.winfo_rooty()+y)
        before=encode(self.app.cat,self.app.adapter);self.app.drag_press(event,self.table,1)
        tx,ty,tw,th=self.app.tree.bbox('all');drop.x_root=self.app.tree.winfo_rootx()+tx+20;drop.y_root=self.app.tree.winfo_rooty()+ty+th/2
        self.app.drag_motion(drop);self.app.drag_release(drop,self.table,1)
        self.assertEqual(encode(self.app.cat,self.app.adapter),before)

    def test_f2_menu_title_tooltip_and_cancel_without_mutation(self):
        r=self.items[0];x,y=self.point(r);self.click(x,y)
        self.app.ensure_inspector();self.app.show_summary(r.id,checked=True);self.root.update()
        with patch('mon_gpt.atelier.MenuSkin.popup'):
            self.app.results_context_menu()
        labels=[self.app.active_menu.entrycget(i,'label') for i in range(self.app.active_menu.index('end')+1) if self.app.active_menu.type(i)!='separator']
        self.assertIn('Renommer',labels);self.assertIn('Déplacer…',labels)
        self.table.event_generate('<F2>');self.root.update();self.assertIsNotNone(self.app.inline)
        self.assertTrue(self.app.inline.winfo_viewable());self.assertLessEqual(self.app.inline.winfo_x()+self.app.inline.winfo_width(),self.table.winfo_width())
        self.app.inline.delete(0,'end');self.app.inline.insert(0,'Brouillon fictif');self.app.escape()
        self.assertNotEqual(r.title,'Brouillon fictif')
        self.root.update();self.table.focus_set();self.root.update()
        self.table.show_tip(r.id,y);self.root.update();self.assertIn(r.title,self.table.tip.cget('text'));self.table.hide_tip()
        self.app.rename_selected(r.id);self.app.inline.delete(0,'end');self.app.inline.insert(0,'Titre fictif modifié');self.app.commit_inline();self.root.update()
        self.assertEqual(r.title,'Titre fictif modifié')
        self.assertEqual(self.app.summary.title.cget('text'),r.title)

    def test_preferences_mosaic_large_old_defaults_invalid_sizes_and_real_reopen(self):
        path=self.store.directory/'interface.json'
        for view in ('list','detail','mosaic'):
            ui_state.save(path,False,'1360x820',view)
            data,warning=ui_state.load(path);self.assertFalse(warning);self.assertEqual(data.get('mosaic_size','normal'),'normal')
        previous=path.read_bytes()
        for bad in ('huge',42,[],False):
            with self.assertRaises(ValueError): ui_state.save(path,False,'1360x820','mosaic',mosaic_size=bad)
            self.assertEqual(path.read_bytes(),previous)
        self.app.scope=self.a.id;self.app.query.set('Voyage');self.app.tag.set('Idées');self.app.category.set('Imaginaire');self.app.refresh_results()
        r=self.items[-3];self.table.selection_set(r.id);self.root.update();self.app.toggle_inspector();self.app.set_mosaic_size('large')
        self.app.tree.item(self.b.id,open=False);self.app.close()
        self.root=tk.Tk();self.app=App(self.root,self.store,self.cat,self.adapter,self.opener);self.root.update()
        self.assertEqual(self.app.view.get(),'mosaic');self.assertEqual(self.app.mosaic_size.get(),'large')
        self.assertEqual(self.app.current,r.id);self.assertEqual(self.app.results.selection(),(r.id,));self.assertTrue(self.app.inspector_visible);self.assertFalse(self.app.editing)
        self.assertEqual(self.app.scope,self.a.id);self.assertEqual(self.app.query.get(),'Voyage')
        self.opener.assert_not_called()


if __name__=='__main__': unittest.main()
