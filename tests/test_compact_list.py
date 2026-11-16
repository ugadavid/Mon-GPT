"""Hitboxes, colonnes épinglées et clavier de la Liste MG-002b-03."""
import tempfile
import tkinter as tk
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store
from mon_gpt.ui import App


class CompactListTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.cat=Catalog()
        self.project=self.cat.add("Projet fictif","project")
        self.child=self.cat.add("Sous-projet fictif","project",self.project.id)
        self.adapter=ChatGPT(self.cat)
        self.items=[]
        for n in range(15):
            item,_=self.adapter.ingest(f"Fil {n:02} — un titre fictif très long à lire intégralement",f"https://chatgpt.com/c/00000000-0000-4000-8000-{n+1:012}")
            item.categories=["Écriture","Imaginaire"]
            item.tags=["Travaux","Créativité","Été"]
            self.cat.attach(item.id,[self.project.id])
            self.items.append(item)
        self.opener=Mock(return_value=True)
        self.app=App(self.root,Store(self.temp.name),self.cat,self.adapter,self.opener)
        self.root.deiconify()
        self.root.update()
        self.app.place_initial_sash(force=True)
        self.root.update()
        self.root.focus_force()
        self.table=self.app.results

    def point(self,identity,column,dx=10):
        x,y,w,h=self.table.bbox(identity,column)
        return SimpleNamespace(x=x+min(dx,w/2),y=y+h/2,x_root=self.table.winfo_rootx()+x+min(dx,w/2),y_root=self.table.winfo_rooty()+y+h/2)

    def click(self,event):
        self.table.select_click(event)
        self.app.drag_press(event,self.table,1)
        self.app.drag_release(event,self.table,1)
        self.root.update()

    def test_end_link_always_opens_its_row_in_all_widths_and_scroll_positions(self):
        for width,preview in [(1360,False),(1360,True),(1000,True),(1000,False)]:
            self.app.resize(width,680)
            if self.app.inspector_visible!=preview: self.app.toggle_inspector()
            self.root.update()
            for scroll in (0,1):
                self.table.xview("moveto",scroll)
                self.table.yview("moveto",1)
                identity=self.items[-1].id
                event=self.point(identity,"open")
                self.assertLess(event.x,self.table.winfo_width())
                self.assertGreaterEqual(self.table.bbox(identity,"title")[0],0)
                self.app.last_open=(None,0)
                self.opener.reset_mock()
                self.click(event)
                self.opener.assert_called_once_with(self.adapter.conversations[identity].url,new=2)

    def test_badges_and_blank_title_select_without_open_and_details_are_complete(self):
        item=self.items[0]
        self.click(self.point(item.id,"categories"))
        self.opener.assert_not_called()
        self.assertEqual(self.app.current,item.id)
        self.table.show_tip(item.id,60)
        self.assertIn(item.title,self.table.tip.cget("text"))
        self.assertIn("Écriture · Imaginaire",self.table.tip.cget("text"))
        self.assertIn("Travaux · Créativité · Été",self.table.tip.cget("text"))
        self.table.hide_tip()
        self.cat.records[item.id].title="Court"
        self.app.refresh_results()
        event=self.point(item.id,"title",dx=self.table.bbox(item.id,"title")[2]-10)
        self.assertFalse(self.app.title_hit(event,item.id))

    def test_header_sort_resize_and_horizontal_scroll_preserve_pinned_action(self):
        self.app.resize(1000,680)
        self.root.update()
        identity=self.items[0].id
        original=self.table.bbox(identity,"open")[0]
        self.table.xview("moveto",1)
        self.assertEqual(self.table.bbox(identity,"open")[0],original)
        self.assertGreater(self.table.xview()[0],0)
        self.table.xview("moveto",0)
        x,y,w,h=self.table.bbox(identity,"title")
        self.table.select_click(SimpleNamespace(x=x+w,y=10))
        self.table.resize_motion(SimpleNamespace(x=x+w-35))
        self.assertEqual(self.table.column("title","width"),w-35)
        self.table.resize_column=None
        self.table.select_click(SimpleNamespace(x=x+20,y=10))
        self.assertTrue(self.app.sort_reverse)
        self.assertEqual(self.table.get_children()[0],self.items[-1].id)

    def test_keyboard_end_action_and_projects_never_open_external_link(self):
        identity=self.items[0].id
        self.table.focus(identity)
        self.table.selection_set(identity)
        self.table.focus_set()
        self.root.update()
        self.table.event_generate("<Right>")
        self.table.event_generate("<Return>")
        self.root.update()
        self.opener.assert_called_once_with(self.adapter.conversations[identity].url,new=2)
        self.app.scope=self.project.id
        self.app.refresh_results()
        self.root.update()
        self.table.see(self.child.id)
        self.assertFalse(self.app.title_hit(self.point(self.child.id,"open"),self.child.id))
        self.opener.reset_mock()
        self.click(self.point(self.child.id,"open"))
        self.opener.assert_not_called()

    def test_release_over_neighbour_link_does_not_open_wrong_conversation(self):
        start=self.point(self.items[0].id,"open")
        end=self.point(self.items[1].id,"open")
        self.app.drag_press(start,self.table,1)
        self.app.drag_release(end,self.table,1)
        self.opener.assert_not_called()


if __name__=="__main__": unittest.main()
