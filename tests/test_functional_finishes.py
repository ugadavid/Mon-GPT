"""MG-011 : contenus distincts et navigation native sur catalogue fictif."""
import unittest
from unittest.mock import patch
import test_natural_gestures as gestures
from mon_gpt.storage import encode
from mon_gpt.information_ui import HELP
from mon_gpt import __version__


class FunctionalFinishesTests(unittest.TestCase):
    setUp=gestures.NaturalGesturesTests.setUp
    destroy=gestures.NaturalGesturesTests.destroy
    point=gestures.NaturalGesturesTests.point
    visible=gestures.NaturalGesturesTests.visible
    scope=gestures.NaturalGesturesTests.scope
    gesture=gestures.NaturalGesturesTests.gesture

    def texts(self,widget):
        return [widget.itemcget(i,'text') for i in widget.find_all() if widget.type(i)=='text']

    def test_distinct_excerpts_optional_fields_sizes_title_and_no_mutation(self):
        for item,summary,note in zip(self.items[:4],('Résumé unique','','Résumé seul',''),('Note longue '*120,'Note seule','','')):
            item.description=summary;item.notes=note;item.tags=[];item.categories=[]
        snapshot=encode(self.app.cat,self.app.adapter)
        for view in ('detail','mosaic'):
            self.app.set_view(view);self.app.refresh_results();self.root.update()
            for size in ('normal','large'):
                self.app.set_mosaic_size(size)
                for item in self.items[:4]:
                    self.table.see(item.id);self.root.update()
                    data=self.table.item(item.id)
                    self.assertEqual(data['notes'],item.notes)
                    labels=[label for _,label,_ in self.table.excerpts(data)]
                    self.assertEqual('Résumé' in labels,bool(item.description))
                    self.assertEqual('Note' in labels,bool(item.notes))
                    self.assertNotIn('Aucune note',' '.join(self.texts(self.table)))
                    if view=='mosaic':
                        box=self.table.bbox(item.id);tx,ty,tw,th=self.table.bbox(item.id,'title')
                        self.assertEqual(th,42)
                        self.assertEqual(self.table.identify_at(box[0]+10,box[1]+box[3]-3),item.id)
                        if not labels:self.assertEqual(box[3],self.table.grid_layout().image_height+76)
        self.assertEqual(encode(self.app.cat,self.app.adapter),snapshot);self.opener.assert_not_called()

    def test_scope_metadata_independent_of_thread_all_empty_and_compact(self):
        self.p.description='Description du dossier fictif';self.p.tags=['Tag dossier'];self.p.categories=['Catégorie dossier']
        self.items[0].tags=['Tag fil'];self.scope(self.p.id)
        snapshot=encode(self.app.cat,self.app.adapter)
        for width in (1000,1600):
            self.app.resize(width,680 if width==1000 else 900);self.root.update()
            for inspector in (False,True):
                if self.app.inspector_visible!=inspector:self.app.toggle_inspector()
                self.app.select_identity(self.items[0].id,checked=True);self.root.update()
                self.assertEqual(self.app.masthead.scope_info,('Description du dossier fictif',('Catégorie dossier',),('Tag dossier',)))
                texts=self.texts(self.app.masthead)
                self.assertIn('Tag dossier',texts);self.assertNotIn('Tag fil',texts)
                x,y,w,h=self.app.masthead.cover_box
                self.assertGreater(w,0);self.assertGreater(h,0)
                self.assertLessEqual(y+h,self.app.masthead.winfo_height())
                self.assertLessEqual(x+w,self.app.masthead.winfo_width())
        for scope in ('all','unfiled',self.q.id):
            self.scope(scope);self.assertEqual(self.app.masthead.scope_info,('',(),()))
        self.assertEqual(encode(self.app.cat,self.app.adapter),snapshot)

    def test_pinned_scrolling_click_keyboard_focus_context_and_single_selection(self):
        projects=[self.app.cat.add(f'Projet fictif {n:02}','project') for n in range(60)]
        self.app.refresh_tree();self.root.update();tree=self.app.tree
        tree.yview('moveto',1);self.root.update()
        self.assertTrue(tree.bbox(projects[-1].id))
        for identity in ('all','unfiled'):
            self.assertTrue(tree.bbox(identity))
            branch=tree.pinned;x,y,w,h=branch.bbox(identity)
            branch.event_generate('<ButtonPress-1>',x=30,y=y+h//2)
            branch.event_generate('<ButtonRelease-1>',x=30,y=y+h//2);self.root.update()
            self.assertEqual(self.app.scope,identity);self.assertEqual(tree.selection(),(identity,))
            self.assertFalse(tree.projects.selection())
        tree.focus_force();tree.pinned.event_generate('<Down>');self.root.update()
        first=tree.projects.get_children()[0]
        self.assertEqual(tree.selection(),(first,));self.assertTrue(tree.owns_focus())
        tree.projects.event_generate('<Up>');self.root.update()
        self.assertEqual(tree.selection(),('unfiled',))
        with patch.object(self.app,'context_menu') as menu:
            tree.pinned.focus_force();self.root.update()
            tree.pinned.event_generate('<KeyPress>',keycode=93);self.root.update();menu.assert_called_once()
        self.assertEqual(len(tree.get_children()),len(tree.projects.get_children())+2)

    def test_direct_differentiated_counts_and_filters(self):
        # Exclude every other direct attachment, leaving exactly three.
        for item in self.items[3:]:self.app.cat.attach(item.id,[])
        self.app.cat.add('Second sous-projet','project',self.p.id)
        indirect=self.app.cat.add('Petit-enfant','project',self.child.id)
        self.app.cat.attach(self.items[-1].id,[indirect.id])
        self.scope(self.p.id)
        self.assertEqual(self.app.results_label.cget('text'),'Contenu du projet')
        self.assertEqual(self.app.result_count.cget('text'),'3 discussions · 2 sous-projets')
        self.assertNotIn(self.items[-1].id,self.table.get_children())
        self.app.query.set('Carnet partagé');self.app.refresh_results();self.root.update()
        self.assertEqual(self.app.result_count.cget('text'),'2 discussions')
        for scope in ('all','unfiled'):
            self.scope(scope);self.assertEqual(self.app.results_label.cget('text'),'Discussions')

    def test_editor_current_locations_first_homonyms_save_and_cancel(self):
        item=self.items[0];self.app.cat.attach(item.id,[self.q.id,self.twin.id])
        snapshot=encode(self.app.cat,self.app.adapter)
        self.app.show_record(item.id);self.root.update()
        self.assertFalse(self.app.dirty);self.assertEqual(encode(self.app.cat,self.app.adapter),snapshot)
        self.assertEqual(self.app.project_ids[:2],[self.q.id,self.twin.id])
        self.assertEqual(self.app.locations.curselection(),(0,1))
        self.assertNotEqual(self.app.locations.get(0),self.app.locations.get(1))
        self.assertNotIn(self.q.id,self.app.current_locations.cget('text'))
        self.assertLess(self.app.locations.winfo_rooty(),self.app.editor_controls['description'].winfo_rooty())
        self.app.locations.selection_clear(1);self.app.dirty=True
        self.assertTrue(self.app.save_record());self.assertEqual(self.app.cat.records[item.id].projects,[self.q.id])
        self.root.update();self.table.selection_set(self.items[-1].id);self.root.update()
        self.app.show_record(self.items[-1].id);self.root.update()
        self.assertEqual(self.app.current_locations.cget('text'),'Actuellement dans : À classer')
        snapshot=encode(self.app.cat,self.app.adapter)
        self.app.locations.selection_set(0);self.app.dirty=True
        with patch('mon_gpt.details.messagebox.askyesnocancel',return_value=False):self.app.show_summary(self.items[-1].id)
        self.assertEqual(encode(self.app.cat,self.app.adapter),snapshot)

    def test_information_windows_sections_version_escape_close_and_focus(self):
        self.table.focus_force();self.root.update()
        with patch('mon_gpt.ui.messagebox.showinfo') as old:
            help_window=self.app.help();self.root.update()
            self.assertEqual(help_window,self.app.help());self.assertEqual(help_window.sections.size(),8)
            for n,title in enumerate(HELP):
                help_window.sections.selection_clear(0,'end');help_window.sections.selection_set(n)
                help_window.sections.event_generate('<<ListboxSelect>>');self.root.update()
                self.assertEqual(help_window.section_title.cget('text'),title)
                self.assertIn(HELP[title],help_window.text.get('1.0','end'))
            help_window.sections.focus_force();help_window.sections.event_generate('<Escape>');self.root.update()
            self.assertFalse(help_window.winfo_exists());self.assertEqual(self.root.focus_get(),self.table)
            about=self.app.about();self.root.update()
            labels=[w.cget('text') for w in about.content.winfo_children() if w.winfo_class()=='TLabel']
            self.assertIn('Version '+__version__,labels)
            with patch('mon_gpt.information_ui.webbrowser.open') as opened:
                about.repository.invoke();opened.assert_called_once_with('https://github.com/ugadavid/Mon-GPT',new=2)
            about.close_button.invoke();self.root.update();old.assert_not_called()
        self.assertEqual(self.root.focus_get(),self.table)

    def test_repeated_covers_keep_identity_metadata_and_bounded_render(self):
        self.scope(self.p.id)
        for r in self.items:r.visual={}
        self.app.set_view('mosaic');self.app.refresh_results();self.root.update()
        for r in self.items[:10]:
            self.assertEqual(self.table.item(r.id)['visual'].image,self.p.visual['image'])
        with patch.object(self.app,'refresh_results',wraps=self.app.refresh_results) as refresh:
            self.table.selection_set([r.id for r in self.items[:3]]);self.root.update()
            self.table.draw();self.root.update();refresh.assert_not_called()
        self.assertLess(len(self.table.find_withtag('cover')),30)
        self.gesture(self.items[0].id,self.q.id,1)
        self.assertEqual([self.app.cat.records[r.id].projects for r in self.items[:3]],[[self.r.id,self.q.id]]*3)
        self.opener.assert_not_called()
