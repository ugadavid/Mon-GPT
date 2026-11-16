import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
from mon_gpt.batch import build_batch,common_sources
from mon_gpt.selection import Selection
from mon_gpt.storage import Store,encode,read_backup
from batch_fixtures import fixture


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.cat,self.adapter,self.projects,self.items=fixture()
        self.p,self.q,self.twin,self.r,self.child=self.projects
        self.store=Store(self.temp.name);self.store.save(self.cat,self.adapter)

    def commit(self,plan):return self.store.commit_batch(plan,self.cat,self.adapter,encode(self.cat,self.adapter))

    def test_add_twenty_preserves_every_field_no_clone_and_repeated_no_write(self):
        ids=[r.id for r in self.items[:20]];before=encode(self.cat,self.adapter)
        plan=build_batch(self.cat,ids,'add',destination=self.q.id)
        self.assertEqual(encode(self.cat,self.adapter),before)
        with patch.object(self.store,'save',wraps=self.store.save) as save:
            cat,source=self.commit(plan);save.assert_called_once()
        expected=copy.deepcopy(before)
        for record in expected['records']:
            if record['id'] in ids:
                record['projects'].append(self.q.id)
                record['modified']=cat.records[record['id']].modified
        self.assertEqual(encode(cat,source),expected)
        self.assertEqual(len(source.conversations),22)
        again=build_batch(cat,ids,'add',destination=self.q.id)
        self.assertEqual(again.already,20);self.assertEqual(again.changed,0)
        with patch.object(self.store,'save',side_effect=AssertionError('Écriture inutile')):
            self.store.commit_batch(again,cat,source,encode(cat,source))

    def test_move_retires_only_explicit_source_keeps_other_projects_order(self):
        ids=[r.id for r in self.items[:10]]
        cat,source=self.commit(build_batch(self.cat,ids,'move',self.p.id,self.q.id))
        self.assertTrue(all(cat.records[i].projects==[self.r.id,self.q.id] for i in ids))
        self.assertEqual(source.project_links,self.adapter.project_links)
        for identity in ids:self.assertEqual(cat.records[identity].notes,self.cat.records[identity].notes)
        with self.assertRaises(ValueError):build_batch(cat,ids,'move',self.p.id,self.q.id)

    def test_remove_mixed_remaining_projects_and_unfiled_move(self):
        ids=[self.items[0].id,self.items[15].id]
        plan=build_batch(self.cat,ids,'remove',self.p.id)
        self.assertEqual(plan.unfiled,1)
        cat,_=self.commit(plan)
        self.assertEqual(cat.records[ids[0]].projects,[self.r.id]);self.assertEqual(cat.records[ids[1]].projects,[])
        empty=[r.id for r in self.items[-2:]]
        cat,_=self.commit(build_batch(self.cat,empty,'move',destination=self.q.id))
        self.assertTrue(all(cat.records[i].projects==[self.q.id] for i in empty))

    def test_ambiguous_missing_source_mixed_unfiled_projects_and_same_destination(self):
        mixed=[self.items[0].id,self.items[-1].id]
        self.assertEqual(common_sources(self.cat,mixed),((),False))
        for mode in ('move','remove'):
            with self.assertRaises(ValueError):build_batch(self.cat,mixed,mode,destination=self.q.id if mode=='move' else None)
        ids=[r.id for r in self.items[:10]]
        plan=build_batch(self.cat,ids,'move',self.p.id,self.p.id)
        self.assertEqual(plan.changed,0);self.assertEqual(plan.already,10)
        with self.assertRaises(ValueError):build_batch(self.cat,[ids[0],self.p.id],'add',destination=self.q.id)
        with self.assertRaises(ValueError):build_batch(self.cat,ids,'add',destination='all')
        self.assertNotEqual(self.q.id,self.twin.id)
        self.assertEqual(build_batch(self.cat,ids,'add',destination=self.twin.id).destination,self.twin.id)

    def test_stale_plan_removed_item_source_destination_or_mapping_is_all_or_nothing(self):
        ids=[r.id for r in self.items[:10]]
        for mutation in ('item','source','destination','attachment','mapping','notes'):
            cat,adapter=copy.deepcopy((self.cat,self.adapter));adapter.catalog=cat
            before=encode(cat,adapter);plan=build_batch(cat,ids,'move',self.p.id,self.q.id)
            if mutation=='item':cat.delete(ids[0])
            if mutation=='source':cat.delete(self.p.id)
            if mutation=='destination':cat.delete(self.q.id)
            if mutation=='attachment':cat.attach(ids[0],[self.r.id])
            if mutation=='mapping':adapter.project_links['g-p-autre']=self.q.id
            if mutation=='notes':cat.records[ids[0]].notes='Modification depuis aperçu'
            changed=encode(cat,adapter)
            with self.subTest(mutation=mutation),patch.object(self.store,'save') as save:
                with self.assertRaises(ValueError):self.store.commit_batch(plan,cat,adapter,before)
                save.assert_not_called();self.assertEqual(encode(cat,adapter),changed)

    def test_mid_batch_save_replace_and_size_failures_preserve_original_and_disk(self):
        ids=[r.id for r in self.items[:20]];plan=build_batch(self.cat,ids,'add',destination=self.q.id)
        before=encode(self.cat,self.adapter);disk=self.store.path.read_bytes()
        from mon_gpt.core import Catalog
        attach=Catalog.attach;calls=[]
        def fail(cat,identity,projects):
            calls.append(identity)
            if len(calls)==5:raise ValueError('Erreur fictive en milieu de lot')
            attach(cat,identity,projects)
        scenarios=[patch.object(Catalog,'attach',fail),patch.object(self.store,'save',side_effect=OSError('Disque plein fictif')),patch('mon_gpt.storage.os.replace',side_effect=OSError('Écriture atomique refusée')),patch('mon_gpt.storage.MAX_CATALOG',64)]
        for scenario in scenarios:
            with scenario,self.assertRaises((ValueError,OSError)):self.commit(plan)
            self.assertEqual(encode(self.cat,self.adapter),before);self.assertEqual(self.store.path.read_bytes(),disk)

    def test_personal_image_mapping_backup_restore_and_reimport_still_same_identity(self):
        stream=io.BytesIO();Image.new('RGB',(160,90),'gold').save(stream,'PNG')
        file=Path(self.temp.name)/'fictive.png';file.write_bytes(stream.getvalue())
        ref=self.store.images.import_file(file);self.items[0].visual['image']=ref
        cat,source=self.commit(build_batch(self.cat,[r.id for r in self.items[:20]],'add',destination=self.q.id))
        archive=Path(self.temp.name)/'complet.zip';self.store.export(archive,cat,source)
        bundle=read_backup(archive);self.assertIn(ref,bundle.images)
        other=Store(Path(self.temp.name)/'restaure');empty,adapter=other.load()
        restored,adapter,_=other.restore(bundle,empty,adapter)
        self.assertEqual(encode(restored,adapter),encode(cat,source))
        from collector_fixtures import export_fixture
        from mon_gpt.collector_import import validate_export,initial_decisions,build_plan
        exported=export_fixture(4,22)
        aliases={r['projectKey']:k for r,k in zip(exported['projects'],source.project_links)}
        for row in exported['projects']:row['projectKey']=aliases[row['projectKey']]
        for row,conversation in zip(exported['conversations'],source.conversations.values()):
            old_identity=row['conversationId']
            row['conversationId']=conversation.conversation_id
            row['url']=row['url'].replace(old_identity,conversation.conversation_id)
            for field in ('url',):
                for old,new in aliases.items():row[field]=row[field].replace(old,new)
            row['observedUrls']=[row['url']]
            row['observedProjectKeys']=[aliases[k] for k in row['observedProjectKeys']]
        observations=validate_export(exported)
        reimport=build_plan(observations,initial_decisions(observations,restored,adapter),restored,adapter)
        self.assertFalse(reimport.changed)
        self.assertEqual(len(adapter.conversations),22)

    def test_selection_order_ranges_projects_and_control_shift(self):
        s=Selection();order=['a','folder','b','c','d'];items={'a','b','c','d'}
        s.gesture('a',order,items);s.gesture('c',order,items,control=True)
        self.assertEqual(s.ids,('a','c'))
        s.gesture('b',order,items,shift=True);self.assertEqual(s.ids,('a','b'))
        s.gesture('d',order,items,control=True,shift=True);self.assertEqual(s.ids,('a','b','c','d'))
        s.gesture('folder',order,items,control=True);self.assertEqual(s.ids,('folder',))
        s.set(['a','d'],list(reversed(order)),items,anchor='a',focal='d')
        self.assertEqual(s.ids,('d','a'));self.assertEqual(s.anchor,'a')
        s.set(['a'],order,items)
        s.gesture('folder',order,items,shift=True,project_alone=False)
        self.assertEqual(s.ids,('a',))
