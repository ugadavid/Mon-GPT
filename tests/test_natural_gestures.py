"""MG-010b-01 : événements Tk des gestes individuels et groupés."""
import unittest
from unittest.mock import patch
import test_batch_ui as helpers
from mon_gpt.storage import encode,decode
from mon_gpt.project_choices import project_choices


class NaturalGesturesTests(unittest.TestCase):
    setUp=helpers.BatchUITests.setUp
    destroy=helpers.BatchUITests.destroy
    point=helpers.BatchUITests.point
    visible=helpers.BatchUITests.visible
    click=helpers.BatchUITests.click

    def scope(self,identity):
        self.app.scope=identity;self.app.refresh_tree();self.app.refresh_results();self.root.update()

    def gesture(self,identity,target,button=1,state=0):
        x,y=self.point(identity,title=True)
        self.stamp+=2000
        self.table.event_generate(f'<ButtonPress-{button}>',x=x,y=y,state=state,time=self.stamp)
        self.root.update()
        tx,ty,tw,th=self.app.tree.bbox(target)
        rx=self.app.tree.winfo_rootx()+tx+tw//2;ry=self.app.tree.winfo_rooty()+ty+th//2
        ex=rx-self.table.winfo_rootx();ey=ry-self.table.winfo_rooty()
        self.table.event_generate(f'<B{button}-Motion>',x=ex,y=ey,rootx=rx,rooty=ry,state=state|(256 if button==1 else 1024),time=self.stamp+100)
        self.root.update()
        self.table.event_generate(f'<ButtonRelease-{button}>',x=ex,y=ey,rootx=rx,rooty=ry,state=state,time=self.stamp+200)
        self.root.update()

    def reset(self,snapshot):
        self.app.cat,self.app.adapter=decode(snapshot);self.scope(self.p.id)

    def arrow(self,identity):
        self.table.see(identity);self.root.update()
        if self.app.view.get()=='list':
            x,y,w,h=self.table.bbox(identity,'open');return int(x+w/2),int(y+h/2)
        if self.app.view.get()=='detail':
            x,y,w,h=self.table.bbox(identity,'title');return self.table.winfo_width()-18,int(y+12)
        x,y,w,h=self.table.bbox(identity);_,ty,_,_=self.table.bbox(identity,'title')
        return int(x+w-22),int(ty+10)

    def event_click(self,x,y,state=0):
        self.stamp+=2000
        for event,offset in (('ButtonPress-1',0),('ButtonRelease-1',80)):
            self.table.event_generate('<'+event+'>',x=x,y=y,state=state,time=self.stamp+offset)
            self.root.update()

    def test_titles_icons_covers_double_click_and_enter_never_open_arrow_only_all_views(self):
        for view in ('list','detail','mosaic'):
            self.app.set_view(view);self.root.update()
            for width,height in ((1000,680),(1600,900)):
                self.app.resize(width,height);self.root.update()
                identity=self.visible()[0];x,y=self.point(identity,title=True)
                self.assertFalse(self.table.open_hit(identity,x,y))
                self.event_click(x,y);self.event_click(x,y)
                # Double-clic physique simulé avec les horodatages rapprochés.
                for t in (self.stamp+2000,self.stamp+2100):
                    self.table.event_generate('<ButtonPress-1>',x=x,y=y,time=t)
                    self.table.event_generate('<ButtonRelease-1>',x=x,y=y,time=t+30);self.root.update()
                self.stamp+=4000
                bx,by,bw,bh=self.table.bbox(identity)
                self.event_click(int(bx+18),int(by+(bh/2)))
                self.table.focus_force();self.table.event_generate('<Return>');self.root.update()
                self.opener.assert_not_called()
                ax,ay=self.arrow(identity);self.assertTrue(self.table.open_hit(identity,ax,ay))
                self.app.last_open=(None,0);self.event_click(ax,ay)
                self.opener.assert_called_once_with(self.app.adapter.conversations[identity].url,new=2)
                self.opener.reset_mock()

    def test_arrow_on_selected_or_outside_lot_preserves_lot_and_modifiers_never_open(self):
        ids=[r.id for r in self.items[:3]]
        for view in ('list','detail','mosaic'):
            self.app.set_view(view);self.table.selection_set(ids[:2]);self.root.update()
            for identity in (ids[0],ids[2]):
                self.app.last_open=(None,0);self.event_click(*self.arrow(identity))
                self.assertEqual(set(self.table.selection()),set(ids[:2]))
                self.opener.assert_called_once_with(self.app.adapter.conversations[identity].url,new=2)
                self.opener.reset_mock()
            self.event_click(*self.arrow(ids[2]),state=4);self.opener.assert_not_called()
            self.assertEqual(set(self.table.selection()),set(ids))
            self.app.last_open=(None,0);self.table.focus_force();self.table.event_generate('<Alt-Return>');self.root.update()
            self.opener.assert_called_once();self.opener.reset_mock()

    def test_left_drag_one_or_three_same_transaction_and_other_links_all_views(self):
        snapshot=encode(self.app.cat,self.app.adapter)
        for view in ('list','detail','mosaic'):
            for count in (1,3):
                self.reset(snapshot);self.app.set_view(view);self.root.update()
                ids=[r.id for r in self.items[:count]];self.table.selection_set(ids);self.root.update()
                with patch.object(self.store,'save',wraps=self.store.save) as save:
                    self.gesture(ids[0],self.q.id);save.assert_called_once()
                self.assertIsNone(self.app.draft)
                for identity in ids:self.assertEqual(self.app.cat.records[identity].projects,[self.r.id,self.q.id])
                self.assertEqual(len(self.app.adapter.conversations),22)
                self.assertFalse(set(ids).intersection(self.table.selection()))
        self.opener.assert_not_called()

    def test_right_drag_one_or_three_same_menu_add_or_move_single_write(self):
        snapshot=encode(self.app.cat,self.app.adapter)
        for count in (1,3):
            for action in (0,1):
                self.reset(snapshot);ids=[r.id for r in self.items[:count]]
                self.table.selection_set(ids);self.root.update()
                with patch('mon_gpt.atelier.MenuSkin.popup'):
                    self.gesture(ids[0],self.q.id,button=3)
                self.assertEqual(encode(self.app.cat,self.app.adapter),snapshot)
                menu=self.app.active_menu
                self.assertEqual([menu.entrycget(i,'label') for i in range(3)],['Déplacer ici','Ajouter un rattachement ici','Annuler'])
                with patch.object(self.store,'save',wraps=self.store.save) as save:
                    menu.invoke(action);self.root.update();save.assert_called_once()
                expected=[self.r.id,self.q.id] if action==0 else [self.p.id,self.r.id,self.q.id]
                for identity in ids:self.assertEqual(self.app.cat.records[identity].projects,expected)
                self.assertIsNone(self.app.draft)

    def test_drag_outside_lot_moves_only_new_item_modifiers_do_not_drag(self):
        self.scope(self.p.id);ids=[r.id for r in self.items[:3]]
        self.table.selection_set(ids[:2]);self.root.update();self.gesture(ids[2],self.q.id)
        self.assertEqual(self.app.cat.records[ids[2]].projects,[self.r.id,self.q.id])
        self.assertEqual(self.app.cat.records[ids[0]].projects,[self.p.id,self.r.id])
        before=encode(self.app.cat,self.app.adapter)
        self.gesture(ids[0],self.q.id,state=4)
        self.assertEqual(encode(self.app.cat,self.app.adapter),before);self.opener.assert_not_called()

    def test_unique_global_source_unfiled_noop_and_invalid_target(self):
        ids=[self.items[10].id,self.items[11].id];self.scope('all')
        self.table.selection_set(ids);self.root.update();self.gesture(ids[0],self.q.id)
        for identity in ids:self.assertEqual(self.app.cat.records[identity].projects,[self.q.id])
        self.assertIsNone(self.app.draft)
        with patch.object(self.store,'save',side_effect=AssertionError('no-op écrit')):
            self.app.drop_items(ids,self.q.id,'move','all')
        ids=[r.id for r in self.items[-2:]];self.scope('unfiled');self.table.selection_set(ids);self.root.update()
        self.gesture(ids[0],self.twin.id)
        for identity in ids:self.assertEqual(self.app.cat.records[identity].projects,[self.twin.id])
        before=encode(self.app.cat,self.app.adapter);self.scope('all');self.table.selection_set(ids);self.root.update()
        self.gesture(ids[0],'all');self.assertEqual(encode(self.app.cat,self.app.adapter),before)

    def test_ambiguous_global_source_only_choice_then_apply_and_source_subset_labels(self):
        ids=[r.id for r in self.items[:3]];self.table.selection_set(ids);self.root.update()
        before=encode(self.app.cat,self.app.adapter);self.gesture(ids[0],self.q.id)
        self.assertEqual(encode(self.app.cat,self.app.adapter),before)
        self.assertEqual(self.app.draft['kind'],'source');self.assertEqual(self.app.source_box.current(),-1)
        self.app.source_box.set('Autre carnet')
        with patch.object(self.store,'save',wraps=self.store.save) as save:
            self.app.apply_transfer();self.root.update();save.assert_called_once()
        self.assertIsNone(self.app.draft)
        for identity in ids:self.assertEqual(self.app.cat.records[identity].projects,[self.p.id,self.q.id])

    def test_readable_choices_stable_homonyms_distinct_paths_and_literal_number_collision(self):
        cat=self.app.cat;ian=cat.add('Ian','project');a=cat.add('Cours M2','project');b=cat.add('Cours M2','project')
        cat.add('Cours M2 · 1','project');cat.add('Réflexion','project',a.id);cat.add('Réflexion','project',ian.id)
        choices=project_choices(cat)
        self.assertEqual(choices['Ian'],ian.id)
        self.assertNotIn(a.id,choices);self.assertEqual(len(set(choices.values())),len(choices))
        self.assertIn('Ian / Réflexion',choices);self.assertIn('Cours M2 / Réflexion',choices)
        self.assertEqual(project_choices(cat,[a.id]),{'Cours M2':a.id})
        self.assertEqual(project_choices(cat,[a.id,b.id]),project_choices(cat,[b.id,a.id]))
        self.table.selection_set([r.id for r in self.items[:3]]);self.root.update();self.app.open_batch('add')
        d=self.app.batch_dialog;self.assertEqual(d.projects['Ian'],ian.id)
        label=next(k for k,v in d.projects.items() if v==b.id);d.destination.set(label)
        d.confirm();self.root.update()
        for r in self.items[:3]:self.assertIn(b.id,self.app.cat.records[r.id].projects)
        d.cancel();self.assertFalse(hasattr(self.app,'group_buttons'))

    def test_source_choice_cannot_apply_an_invisible_or_replaced_lot(self):
        ids=[r.id for r in self.items[:3]];self.table.selection_set(ids);self.root.update()
        self.gesture(ids[0],self.q.id);self.app.source_box.set('Autre carnet')
        before=encode(self.app.cat,self.app.adapter)
        self.table.selection_set(ids[:1]);self.root.update();self.app.apply_transfer()
        self.assertEqual(encode(self.app.cat,self.app.adapter),before)
        self.assertIn('sélection a changé',self.app.work_error.get())
        self.app.escape();self.assertIsNone(self.app.draft)

    def test_subproject_origin_and_failed_drag_leave_original_intact(self):
        ids=[r.id for r in self.items[:3]]
        for identity in ids:self.app.cat.attach(identity,[self.child.id,self.r.id])
        self.scope(self.child.id);self.table.selection_set(ids);self.root.update()
        before=encode(self.app.cat,self.app.adapter);disk=self.store.path.read_bytes()
        with patch.object(self.store,'save',side_effect=OSError('Panne fictive')),patch('mon_gpt.details.messagebox.showerror'):
            self.gesture(ids[0],self.q.id)
        self.assertEqual(encode(self.app.cat,self.app.adapter),before);self.assertEqual(self.store.path.read_bytes(),disk)
        self.gesture(ids[0],self.q.id)
        for identity in ids:self.assertEqual(self.app.cat.records[identity].projects,[self.r.id,self.q.id])

    def test_individual_selector_same_engine_noop_and_readable_homonyms(self):
        identity=self.items[0].id;self.scope(self.p.id)
        self.table.selection_set(identity);self.root.update()
        before=encode(self.app.cat,self.app.adapter)
        self.app.transfer_panel(identity,'move',self.p.id)
        self.assertIn('Atelier des idées',self.app.source_box.cget('values'))
        with patch.object(self.store,'save',side_effect=AssertionError('no-op écrit')):
            self.app.apply_transfer()
        self.assertEqual(encode(self.app.cat,self.app.adapter),before)
        self.app.show_record(identity);self.root.update()
        self.app.transfer_panel(identity,'add',self.twin.id)
        labels=self.app.destination_box.cget('values')
        self.assertTrue(any(str(label).startswith('Voyages imaginaires · ') for label in labels))
        with patch.object(self.store,'save',wraps=self.store.save) as save:
            self.app.apply_transfer();save.assert_called_once()
        self.assertEqual(self.app.cat.records[identity].projects,[self.p.id,self.r.id,self.twin.id])
        self.assertFalse(self.app.editing)
        self.assertIn('Discussion · 3 emplacement(s)',[label.cget('text') for label in self.app.summary.labels])
        self.scope('all');self.table.selection_set(identity);self.root.update()
        self.app.drop_action(identity,self.q.id,'move',self.p.id)
        self.assertNotIn('▱  Atelier des idées',[label.cget('text') for label in self.app.summary.labels])
