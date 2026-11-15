import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image

from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.collector_import import (read_export,validate_export,initial_decisions,build_plan,Decision,ImportProblem,MAX_EXPORT)
from mon_gpt.storage import Store,encode,decode,read_backup
from collector_fixtures import export_fixture


class CollectorImportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store=Store(self.temp.name)
        self.cat=Catalog();self.adapter=ChatGPT(self.cat)
        self.data=export_fixture()

    def plan(self,data=None,decisions=None,cat=None,adapter=None):
        cat=self.cat if cat is None else cat
        adapter=self.adapter if adapter is None else adapter
        obs=validate_export(self.data if data is None else data)
        return build_plan(obs,initial_decisions(obs,cat,adapter) if decisions is None else decisions,cat,adapter)

    def test_default_separate_homonyms_no_mutation_or_title_matching(self):
        local=self.cat.add("Développement","project")
        before=encode(self.cat,self.adapter)
        p=self.plan()
        self.assertEqual(encode(self.cat,self.adapter),before)
        self.assertEqual(p.counts['created_projects'],3)
        links=p.data['chatgpt_projects'];self.assertEqual(len(set(links.values())),3)
        self.assertNotIn(local.id,links.values())
        self.assertTrue(all(key!=value for key,value in links.items()))
        self.assertEqual(p.counts['created_threads'],4)
        self.assertEqual(p.counts['unfiled_threads'],1)

    def test_fusion_and_existing_keep_individual_source_keys(self):
        folder=self.cat.add("Dossier personnel","project")
        obs=validate_export(self.data);choices=initial_decisions(obs,self.cat,self.adapter)
        a,b,c=choices
        choices[a]=Decision("existing",folder.id)
        choices[b]=Decision("merge",a)
        choices[c]=Decision("ignore")
        p=self.plan(decisions=choices)
        self.assertEqual(p.data['chatgpt_projects'],{a:folder.id,b:folder.id})
        self.assertEqual(p.counts['created_projects'],0)
        self.assertEqual(p.counts['associated_projects'],2)
        self.assertEqual(p.counts['unfiled_threads'],2)

    def test_multi_projects_one_thread_unique_attachment_after_merge(self):
        row=self.data['conversations'][0];b=self.data['projects'][1]['projectKey']
        row['observedProjectKeys'].append(b)
        row['observedUrls'].append(f"https://chatgpt.com/g/{b}/c/{row['conversationId']}")
        p=self.plan();cat,adapter=decode(p.data)
        r=cat.records[next(c.record_id for c in adapter.conversations.values() if c.conversation_id==row['conversationId'])]
        self.assertEqual(len(r.projects),2)
        choices=initial_decisions(validate_export(self.data),self.cat,self.adapter)
        choices[b]=Decision('merge',self.data['projects'][0]['projectKey'])
        cat,adapter=decode(self.plan(decisions=choices).data)
        r=cat.records[next(c.record_id for c in adapter.conversations.values() if c.conversation_id==row['conversationId'])]
        self.assertEqual(len(r.projects),1)

    def test_unknown_name_requires_decision_empty_project_and_provisional_title(self):
        row=self.data['projects'][2]
        row.update(observedName=None,nameObservedAt=None,evidence={'kind':'key-only','url':None})
        self.data['conversations'][0]['observedTitle']=None
        with self.assertRaisesRegex(ValueError,'Décision requise'):self.plan()
        choices=initial_decisions(validate_export(self.data),self.cat,self.adapter)
        choices[row['projectKey']]=Decision('create',title='Mon atelier')
        p=self.plan(decisions=choices)
        self.assertTrue(p.conversations[0]['provisional'])
        self.assertEqual(p.counts['created_projects'],3)
        empty=export_fixture(2,0)
        self.assertEqual(self.plan(empty).counts['created_projects'],2)

    def test_existing_all_fields_and_url_unchanged_renamed_remote_ignored(self):
        p=self.plan();cat,adapter=decode(p.data)
        record=next(r for r in cat.records.values() if r.kind=='item')
        record.title='Titre local';record.description='Résumé';record.notes='Notes privées fictives'
        record.tags=['Tag'];record.categories=['Catégorie'];record.metadata={'clé':'valeur'}
        record.visual={'image':'builtin:jardin','icon':'book','color':'sauge'}
        # Use actual valid visual tokens from resolver rather than assuming a cover.
        from mon_gpt.identity import DEFAULTS
        record.visual=dict(DEFAULTS)
        folder=cat.add('Classement local','project')
        cat.attach(record.id,[folder.id])
        adapter.change_url(record.id,f'https://chatgpt.com/c/{adapter.conversations[record.id].conversation_id}?local=1')
        for r in cat.records.values():
            if r.kind=='project':r.title='Personnalisé'
        before=encode(cat,adapter)
        for row in self.data['projects']:row['observedName']='Renommé à distance'
        q=self.plan(cat=cat,adapter=adapter)
        self.assertEqual(q.data,before)
        self.assertFalse(q.changed)

    def test_atomic_commit_idempotence_restart_backup_restore_and_enrichment(self):
        self.store.acquire();self.addCleanup(self.store.lock.close)
        p=self.plan()
        cat,adapter,backup=self.store.commit_import(p,self.cat,self.adapter)
        self.assertTrue(backup.exists());self.assertEqual(read_backup(backup).data,p.before)
        cat,adapter=self.store.load()
        q=self.plan(cat=cat,adapter=adapter)
        _,_,second=self.store.commit_import(q,cat,adapter)
        self.assertIsNone(second);self.assertEqual(len(list(Path(self.temp.name).glob('avant-import-*.zip'))),1)
        dest=Path(self.temp.name)/'complet.zip';self.store.export(dest,cat,adapter)
        cat,adapter,_=self.store.restore(read_backup(dest),cat,adapter)
        self.assertFalse(self.plan(cat=cat,adapter=adapter).changed)
        enriched=export_fixture(3,7)
        q=self.plan(enriched,cat=cat,adapter=adapter)
        self.assertEqual(q.counts['created_threads'],3)
        self.assertEqual(q.counts['created_projects'],0)
        self.assertEqual(q.data['chatgpt_projects'],p.data['chatgpt_projects'])

    def test_personal_image_backup_before_commit(self):
        b=io.BytesIO();Image.new('RGB',(100,100),'gold').save(b,'PNG')
        # ImageLibrary.import_file performs the normal immutable import.
        image=Path(self.temp.name)/'fictive.png';image.write_bytes(b.getvalue())
        ref=self.store.images.import_file(image)
        r=self.cat.add('Local illustré','project');r.visual={'image':ref}
        self.store.save(self.cat,self.adapter)
        p=self.plan();_,_,backup=self.store.commit_import(p,self.cat,self.adapter)
        bundle=read_backup(backup)
        self.assertIn(ref,bundle.images)
        self.assertEqual(bundle.data,p.before)

    def test_backup_and_atomic_write_failure_leave_disk_and_objects_unchanged(self):
        self.store.save(self.cat,self.adapter)
        before=self.store.path.read_bytes();p=self.plan()
        for target in ('export','save'):
            with self.subTest(target=target),patch.object(self.store,target,side_effect=OSError('disque fictif plein')):
                with self.assertRaises(OSError):self.store.commit_import(p,self.cat,self.adapter)
            self.assertEqual(self.store.path.read_bytes(),before)
            self.assertEqual(encode(self.cat,self.adapter),p.before)
        from mon_gpt.storage import os
        replace=os.replace
        def refuse_catalogue(source,destination):
            if Path(destination)==self.store.path:
                raise OSError('remplacement fictif du catalogue refusé')
            return replace(source,destination)
        with patch('mon_gpt.storage.os.replace',side_effect=refuse_catalogue):
            with self.assertRaises(OSError):self.store.commit_import(p,self.cat,self.adapter)
        self.assertEqual(self.store.path.read_bytes(),before)
        self.assertTrue(any(read_backup(path).data==p.before for path in Path(self.temp.name).glob('avant-import-*.zip')))

    def test_catalog_limit_and_stale_candidate_fail_before_backup(self):
        p=self.plan()
        with patch('mon_gpt.storage.MAX_CATALOG',32):
            with self.assertRaises(ValueError):self.store.commit_import(p,self.cat,self.adapter)
        self.assertFalse(list(Path(self.temp.name).glob('avant-import-*')))
        self.cat.add('Nouveau dossier','project')
        with self.assertRaisesRegex(ValueError,'a changé'):self.store.commit_import(p,self.cat,self.adapter)

    def test_deleted_project_mapping_requires_visible_resolution(self):
        cat,adapter=decode(self.plan().data)
        key=next(iter(adapter.project_links));cat.delete(adapter.project_links[key])
        obs=validate_export(self.data)
        choices=initial_decisions(obs,cat,adapter)
        self.assertEqual(choices[key].action,'resolve')
        # Persisted tombstone remains valid, but may never target an item.
        decode(encode(cat,adapter))
        with self.assertRaises(ValueError):build_plan(obs,choices,cat,adapter)
        choices[key]=Decision('create')
        self.assertEqual(build_plan(obs,choices,cat,adapter).counts['created_projects'],1)

    def test_strict_mapping_and_minimal_schema_evolution(self):
        self.assertEqual(encode(self.cat,self.adapter)['schema'],3)
        data=self.plan().data;self.assertEqual(data['schema'],4)
        for target in ('invalid',self.data['conversations'][0]['conversationId']):
            bad=copy.deepcopy(data)
            if target=='invalid':bad['chatgpt_projects'][next(iter(bad['chatgpt_projects']))]=target
            else:bad['chatgpt_projects'][next(iter(bad['chatgpt_projects']))]=bad['chatgpt'][0]['record_id']
            with self.assertRaises(ValueError):decode(bad)
        legacy=encode(self.cat,self.adapter);self.store.path.write_text(json.dumps(legacy))
        self.store.commit_import(self.plan(),self.cat,self.adapter)
        copies=list(Path(self.temp.name).glob('avant-migration-v3-*.json'))
        self.assertEqual(len(copies),1);self.assertEqual(json.loads(copies[0].read_bytes()),legacy)

    def test_cycles_missing_choices_and_merge_to_ignored_rejected(self):
        obs=validate_export(self.data);choices=initial_decisions(obs,self.cat,self.adapter)
        a,b,c=choices
        for edits in ({a:Decision('merge',b),b:Decision('merge',a)},{a:Decision('merge',b),b:Decision('ignore')}):
            invalid={**choices,**edits}
            with self.assertRaises(ValueError):self.plan(decisions=invalid)
        with self.assertRaises(ValueError):self.plan(decisions={})

    def test_invalid_envelopes_strict_types_v1_future_and_unknown_fields(self):
        for key,value in [('schemaVersion',1),('schemaVersion',3),('schemaVersion',True),('source','other'),('projects',{}),('exportedAt','2026-02-30T12:00:00.000Z'),('extra',0)]:
            data=copy.deepcopy(self.data);data[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ImportProblem):validate_export(data)
        for key in self.data:
            data=copy.deepcopy(self.data);del data[key]
            with self.assertRaises(ImportProblem):validate_export(data)

    def test_invalid_individual_rows_never_silently_skipped(self):
        cases=[('projects','observedName','x'*257),('projects','seenCount',True),('projects','nameObservedAt',None),('projects','projectKey','not-a-key'),('projects','extra',1),('conversations','observedTitle','x'*513),('conversations','conversationId','invalid'),('conversations','url','https://chatgpt.com.evil/c/00000000-0000-0000-0000-000000000001'),('conversations','observedProjectKeys',['g-p-missing']),('conversations','lastObservedActive',1),('conversations','extra',None)]
        for group,key,value in cases:
            data=copy.deepcopy(self.data);data[group][0][key]=value
            with self.subTest(group=group,key=key),self.assertRaises(ImportProblem):validate_export(data)
        self.assertEqual(len(self.cat.records),0)

    def test_evidence_wrong_project_uuid_url_duplicates_and_date_order(self):
        variants=[]
        d=copy.deepcopy(self.data);d['projects'][0]['evidence']={'kind':'direct-link','url':'https://chatgpt.com/g/g-p-wrong/project'};variants.append(d)
        d=copy.deepcopy(self.data);d['conversations'][0]['observedUrls']=[d['conversations'][1]['url']];variants.append(d)
        d=copy.deepcopy(self.data);d['conversations'].append(copy.deepcopy(d['conversations'][0]));variants.append(d)
        d=copy.deepcopy(self.data);d['projects'].append(copy.deepcopy(d['projects'][0]));variants.append(d)
        d=copy.deepcopy(self.data);d['projects'][0]['firstSeenAt']='2027-01-01T00:00:00.000Z';variants.append(d)
        for d in variants:
            with self.assertRaises(ImportProblem):validate_export(d)

    def test_reader_bounded_json_duplicates_unicode_and_special_characters(self):
        path=Path(self.temp.name)/'export.json'
        self.data['projects'][0]['observedName']='Été & recherches — <sans HTML>'
        path.write_text(json.dumps(self.data,ensure_ascii=False),encoding='utf-8')
        self.assertEqual(read_export(path).projects[0]['observedName'],self.data['projects'][0]['observedName'])
        for content in ('{','{"source":1,"source":2}','NaN','[]'):
            path.write_text(content)
            with self.assertRaises(ImportProblem):read_export(path)
        path.write_text('[] ')
        with patch('mon_gpt.collector_import.MAX_EXPORT',2):
            with self.assertRaisesRegex(ImportProblem,'volumineux'):read_export(path)

    def test_large_fixture_limits_and_idempotence(self):
        p=self.plan(export_fixture(1000,5000))
        self.assertEqual(p.counts['created_threads'],5000)
        cat,adapter=decode(p.data)
        self.assertFalse(self.plan(export_fixture(1000,5000),cat=cat,adapter=adapter).changed)
        data=export_fixture(1001,0)
        with self.assertRaises(ImportProblem):validate_export(data)
