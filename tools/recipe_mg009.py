"""Recette Windows de l'assistant réel. Ne produit que des compteurs anonymes.

Deux processus séparés (first puis second) vérifient le redémarrage.
Les catalogues de recette et résultats doivent rester hors des livrables publics.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import tkinter as tk
from unittest.mock import Mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store,encode,decode,read_backup
from mon_gpt.ui import App
from mon_gpt.import_ui import ImportWizard


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--data-dir',type=Path,required=True)
    parser.add_argument('--phase',choices=('first','second'),required=True)
    args=parser.parse_args()
    # La recette ne doit jamais viser le catalogue Windows habituel.
    import os
    default=Path(os.environ.get('LOCALAPPDATA',Path.home()))/'MonGPT'
    if args.data_dir.resolve()==default.resolve():
        parser.error('Utiliser un catalogue isolé.')
    digest=hashlib.sha256(args.source.read_bytes()).hexdigest()
    store=Store(args.data_dir);store.acquire()
    cat,adapter=store.load()
    if args.phase=='first': assert not cat.records
    else: assert len(cat.records)==173 and len(adapter.project_links)==58
    root=tk.Tk();opener=Mock(return_value=True)
    app=App(root,store,cat,adapter,opener=opener)
    root.update();app.place_initial_sash(force=True)
    result={'phase':args.phase,'windowsTkExecuted':True,'restart':args.phase=='second'}
    started=time.monotonic()

    def fail(exc):
        result.update(success=False,errorType=type(exc).__name__)
        (store.directory/f'resultat-{args.phase}.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        root.destroy();store.lock.close()

    def safe(action):
        try: action()
        except Exception as exc: fail(exc)

    def wait(wizard,callback):
        if time.monotonic()-started>90:
            return fail(TimeoutError())
        if wizard.busy:
            root.after(80,lambda:safe(lambda:wait(wizard,callback)))
        else:
            root.after(120,lambda:safe(callback))

    def start():
        wizard=ImportWizard(app)
        before=encode(app.cat,app.adapter)
        wizard.load_path(args.source)
        def preview():
            assert wizard.plan is not None
            assert encode(app.cat,app.adapter)==before
            result['previewNoMutation']=True
            counts=wizard.plan.counts
            result['counts']=counts
            expected=(58,115,59) if args.phase=='first' else (0,0,0)
            assert (counts['created_projects'],counts['created_threads'],counts['unfiled_threads'])==expected
            # Annulation réelle du premier aperçu, puis analyse identique.
            wizard.cancel()
            assert encode(app.cat,app.adapter)==before
            result['cancelNoMutation']=True
            root.after(200,lambda:safe(confirm))
        wait(wizard,preview)

    def confirm():
        wizard=ImportWizard(app);wizard.load_path(args.source)
        def apply():
            assert wizard.plan is not None
            wizard.accept_separate.set(True)
            wizard.next();assert wizard.confirming
            wizard.next()
            wait(wizard,lambda:finish(wizard))
        wait(wizard,apply)

    def finish(wizard):
        assert wizard.finished
        cat,adapter=app.cat,app.adapter
        assert len(adapter.project_links)==58 and len(set(adapter.project_links.values()))==58
        assert len(adapter.conversations)==115
        items=[r for r in cat.records.values() if r.kind=='item']
        attached=sum(bool(r.projects) for r in items)
        assert attached==56
        result.update(projects=58,distinctLocalProjects=58,threads=115,attached=attached,unfiled=115-attached)
        backups=list(store.directory.glob('avant-import-*.zip'))
        assert len(backups)==1
        result['importBackupCount']=len(backups)
        assert not decode(read_backup(backups[0]).data)[0].records
        result['beforeBackupReadable']=True
        if args.phase=='second':
            snapshot=encode(cat,adapter)
            archive=store.directory/'verification-complete.zip'
            store.export(archive,cat,adapter)
            restored,source,_=store.restore(read_backup(archive),cat,adapter)
            assert encode(restored,source)==snapshot
            app.cat,app.adapter=restored,source
            from mon_gpt.collector_import import read_export,initial_decisions,build_plan
            observations=read_export(args.source)
            plan=build_plan(observations,initial_decisions(observations,restored,source),restored,source)
            assert not plan.changed
            result['backupRestoreThenReimportUnchanged']=True
        opener.assert_not_called()
        assert hashlib.sha256(args.source.read_bytes()).hexdigest()==digest
        result.update(noAutomaticOpen=True,sourceIntact=True,success=True)
        (store.directory/f'resultat-{args.phase}.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(json.dumps(result,ensure_ascii=True))
        wizard.cancel()
        app.close()

    root.after(800,lambda:safe(start))
    root.mainloop()
    return 0 if result.get('success') else 1


if __name__=='__main__':
    raise SystemExit(main())
