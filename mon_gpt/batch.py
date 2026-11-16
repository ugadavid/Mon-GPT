"""Plans génériques de rattachements : aucune UI, source ou persistance."""
from dataclasses import dataclass


@dataclass(frozen=True)
class BatchPlan:
    ids: tuple
    action: str
    source: str | None
    destination: str | None
    before: list
    changes: dict
    already: int
    unfiled: int

    @property
    def changed(self): return len(self.changes)

    @property
    def unchanged(self): return len(self.ids)-self.changed


def common_sources(catalog,ids):
    rows=[]
    for identity in dict.fromkeys(ids):
        r=catalog.records.get(identity)
        if r is None or r.kind!="item": raise ValueError("Sélection périmée ou contenant un projet : actualisez le lot.")
        rows.append(r)
    if not rows: raise ValueError("Sélectionnez des discussions.")
    common=set(rows[0].projects)
    for r in rows[1:]: common.intersection_update(r.projects)
    return tuple(p for p in rows[0].projects if p in common),all(not r.projects for r in rows)


def build_batch(catalog,ids,action,source=None,destination=None):
    ids=tuple(dict.fromkeys(ids))
    common,unfiled=common_sources(catalog,ids)
    if action not in ("add","move","remove"): raise ValueError("Action groupée inconnue.")
    if action in ("add","move"):
        target=catalog.records.get(destination)
        if target is None or target.kind!="project": raise ValueError("Choisissez un projet destination existant.")
    elif destination is not None: raise ValueError("Le retrait n’a pas de destination.")
    if action in ("move","remove"):
        if not (action=="move" and unfiled and source is None):
            if source not in common: raise ValueError("Choisissez un rattachement source commun à toutes les discussions. Sinon, utilisez Ajouter un rattachement.")
            if source not in catalog.records or catalog.records[source].kind!="project": raise ValueError("La source a disparu : actualisez l’aperçu.")
    elif source is not None: raise ValueError("L’ajout ne retire aucune source.")
    changes={};already=0;new_unfiled=0
    for identity in ids:
        old=catalog.records[identity].projects
        new=list(old)
        if destination in old: already+=1
        if action=="move" and source==destination:
            pass
        else:
            if action in ("move","remove") and source is not None: new.remove(source)
            if action in ("move","add") and destination not in new: new.append(destination)
        if new!=old:
            changes[identity]=new
            if old and not new: new_unfiled+=1
    return BatchPlan(ids,action,source,destination,catalog.to_list(),changes,already,new_unfiled)
