"""MG-004 : rendus interchangeables, images entières et gestes partagés."""
import json
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock,patch
from PIL import Image,ImageDraw
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store,encode
from mon_gpt.ui import App
from mon_gpt import ui_state


class DetailedViewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=Store(Path(self.temp.name));self.cat=Catalog();self.adapter=ChatGPT(self.cat)
        self.a=self.cat.add('Récits fictifs','project');self.b=self.cat.add('Horizons fictifs','project',self.a.id)
        self.a.visual={'image':'pack:ecriture','icon':'book','color':'terracotta'}
        self.b.visual={'image':'pack:montagne','icon':'microscope','color':'petrole'}
        self.items=[]
        for n in range(30):
            r,_=self.adapter.ingest(f'{n:02} Exploration imaginaire '+('très longue '*25 if n==0 else ''),f'https://chatgpt.com/c/00000000-0000-4000-8000-{n+100:012d}')
            r.description='Un résumé fictif assez long pour se répartir sur deux lignes. '*8 if n==0 else 'Quelques idées à explorer.'
            r.notes='Notes communes à préserver';r.tags=['Été','Travaux'];r.categories=['Imaginaire','Écriture']
            if n!=2: self.cat.attach(r.id,[self.a.id,self.b.id] if n==0 else [self.a.id])
            self.items.append(r)
        self.root=tk.Tk();self.addCleanup(self.root.destroy)
        self.opener=Mock(return_value=True)
        self.app=App(self.root,self.store,self.cat,self.adapter,self.opener)
        self.root.update();self.root.focus_force();self.table=self.app.results

    def detail(self):
        self.app.set_view('detail');self.root.update()

    def test_switch_keeps_rows_filters_sort_selection_inspector_and_dirty_editor(self):
        app=self.app;item=self.items[0]
        app.query.set('imaginaire');app.tag.set('Été');app.category.set('Écriture')
        app.scope=self.a.id;app.sort_results('context');app.refresh_results()
        self.table.selection_set(item.id);self.root.update();app.show_record(item.id)
        app.editor_controls['title'].delete(0,'end');app.editor_controls['title'].insert(0,'Brouillon protégé');app.dirty=True
        ids=self.table.get_children();before=encode(self.cat,self.adapter)
        editor=app.editor.winfo_children()[:]
        for mode in ('detail','list','detail'):
            app.set_view(mode);self.root.update()
            self.assertEqual(self.table.get_children(),ids)
            self.assertEqual(self.table.selection(),(item.id,));self.assertEqual(app.current,item.id)
            self.assertEqual((app.query.get(),app.tag.get(),app.category.get(),app.scope),('imaginaire','Été','Écriture',self.a.id))
            self.assertEqual(app.sort_column,'context');self.assertTrue(app.inspector_visible)
            self.assertEqual(app.editor.winfo_children(),editor);self.assertTrue(app.dirty)
            self.assertEqual(app.fields['title'](),'Brouillon protégé')
        self.assertEqual(encode(self.cat,self.adapter),before);self.opener.assert_not_called()

    def test_cover_icon_context_cache_and_complete_portrait(self):
        path=self.store.directory/'portrait.png';im=Image.new('RGB',(90,160),'white');d=ImageDraw.Draw(im)
        d.rectangle((0,0,89,7),fill='red');d.rectangle((0,152,89,159),fill='blue');im.save(path)
        ref=self.store.images.import_file(path);self.b.visual['image']=ref
        self.app.scope=self.b.id;self.app.refresh_results();self.detail()
        data=self.table.item(self.items[0].id)
        self.assertEqual(data['visual'].image,ref);self.assertEqual(data['visual'].icon,'microscope')
        self.assertEqual(data['visual'].color,'petrole')
        from PIL import ImageTk
        photo=self.table.cover(ref,112);pixels=ImageTk.getimage(photo)
        self.assertEqual(photo.width()*9,photo.height()*16)
        self.assertEqual(pixels.getpixel((56,0))[:3],(255,0,0))
        self.assertEqual(pixels.getpixel((56,62))[:3],(0,0,255))
        self.assertEqual(pixels.getpixel((0,30))[:3],(247,243,234))
        with patch.object(self.store.images,'open',wraps=self.store.images.open) as opened:
            self.table.draw();self.table.hover(self.items[0].id);self.table.draw()
            opened.assert_not_called()
        self.assertIs(photo,self.table.cover(ref,112))
        self.app.scope=self.a.id;self.app.refresh_results();self.root.update()
        self.assertEqual(self.table.item(self.items[0].id)['visual'].image,'pack:ecriture')
        self.app.scope='all';self.app.refresh_results();self.root.update()
        self.assertEqual(self.table.item(self.items[0].id)['visual'].image,'pack:ecriture')
        self.assertIsNone(self.table.item(self.items[2].id)['visual'].image)
        self.assertEqual(self.table.get_children().count(self.items[0].id),1)

    def test_hitboxes_thumbnail_badges_blank_select_title_arrow_open_once(self):
        self.detail();r=self.items[0];self.table.focus_set()
        x,y,w,h=self.table.bbox(r.id)
        for px,py in [(30,y+35),(180,y+106),(self.table.winfo_width()-20,y+100)]:
            self.assertFalse(self.table.open_hit(r.id,px,py))
            self.table.event_generate('<ButtonPress-1>',x=px,y=int(py));self.table.event_generate('<ButtonRelease-1>',x=px,y=int(py));self.root.update()
            self.assertEqual(self.app.current,r.id)
        self.opener.assert_not_called()
        tx,ty,_,_=self.table.bbox(r.id,'title')
        self.assertFalse(self.table.open_hit(r.id,tx+4,ty+12))
        self.table.event_generate('<ButtonPress-1>',x=int(tx+4),y=int(ty+12));self.table.event_generate('<ButtonRelease-1>',x=int(tx+4),y=int(ty+12));self.root.update()
        self.opener.assert_not_called()
        self.table.event_generate('<Return>');self.root.update();self.opener.assert_not_called()
        self.table.event_generate('<Alt-Return>');self.root.update();self.opener.assert_called_once()

    def test_geometry_scroll_keyboard_tooltip_empty_and_list_contract(self):
        self.detail()
        for width,height,inspector in [(1360,820,False),(1000,680,True),(1800,950,True)]:
            self.app.resize(width,height)
            if self.app.inspector_visible!=inspector: self.app.toggle_inspector()
            self.root.update();self.table.focus_set();self.table.focus(self.items[0].id)
            self.table.navigate(29);self.root.update()
            last=self.items[-1].id
            self.assertEqual(self.table.selection(),(last,))
            self.assertEqual(self.table.identify_row(self.table.bbox(last)[1]+10),last)
            self.assertGreater(self.table.yview()[0],0)
            self.assertEqual(self.table.xview(),(0,1))
            self.assertTrue(self.table.find_withtag('cover'))
        self.table.see(self.items[0].id);self.table.show_tip(self.items[0].id,40);self.root.update()
        self.assertIn(self.items[0].title,self.table.tip.cget('text'));self.table.hide_tip()
        self.app.query.set('aucunmotcorrespondant');self.app.refresh_results();self.root.update()
        self.assertFalse(self.table.get_children());self.assertFalse(self.table.find_withtag('cover'))
        self.app.set_view('list');self.root.update()
        self.assertEqual((self.table.row_height,self.table.header_height),(42,34))
        self.assertFalse(self.table.find_withtag('cover'))

    def test_projects_context_menus_rename_and_drag_keep_other_links(self):
        self.app.scope=self.a.id;self.app.refresh_results();self.detail()
        self.assertTrue(self.table.exists(self.b.id))
        self.table.see(self.b.id)
        bx,by,bw,bh=self.table.bbox(self.b.id)
        self.assertFalse(self.table.open_hit(self.b.id,bw-15,by+20))
        self.table.focus_set();self.table.focus(self.b.id);self.app.result_enter();self.root.update()
        self.opener.assert_not_called()
        self.app.scope=self.a.id;self.app.refresh_results();self.root.update()
        r=self.items[0];self.table.selection_set(r.id);self.root.update()
        self.app.rename_selected(r.id);self.app.inline.delete(0,'end');self.app.inline.insert(0,'Titre fictif modifié')
        self.app.set_view('list');self.app.set_view('detail');self.root.update()
        self.assertEqual(self.app.inline.get(),'Titre fictif modifié');self.app.commit_inline();self.root.update()
        self.assertEqual(r.title,'Titre fictif modifié')
        with patch('mon_gpt.atelier.MenuSkin.popup'):
            self.app.context_menu(r.id,200,200)
        self.assertIn('Renommer',[self.app.active_menu.entrycget(n,'label') for n in range(self.app.active_menu.index('end')+1) if self.app.active_menu.type(n)!='separator'])
        target=self.cat.add('Cible fictive','project');self.app.refresh_tree();self.root.update()
        self.app.drop_action(r.id,target.id,'move',self.a.id)
        self.assertEqual(self.app.cat.records[r.id].projects,[self.b.id,target.id]);self.assertEqual(self.app.cat.records[r.id].notes,'Notes communes à préserver')

    def test_ui_preferences_old_new_unknown_and_no_catalog_field(self):
        path=self.store.directory/'interface.json';before=encode(self.cat,self.adapter)
        for view in ('list','detail'):
            ui_state.save(path,True,'1000x680',view)
            data,warning=ui_state.load(path);self.assertFalse(warning);self.assertEqual(data['view'],view)
        data['view']='future';path.write_text(json.dumps(data),encoding='utf-8')
        self.assertEqual(ui_state.load(path)[0],{});self.assertTrue(ui_state.load(path)[1])
        self.assertEqual(encode(self.cat,self.adapter),before)
        ui_state.save(path,False,'1360x820','detail')
        other=tk.Toplevel(self.root);app=App(other,self.store,self.cat,self.adapter,self.opener);self.root.update()
        self.assertEqual(app.view.get(),'detail');self.assertEqual(app.results.view,'detail');other.destroy()


if __name__=='__main__': unittest.main()
