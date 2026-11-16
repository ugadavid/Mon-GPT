"""Libellés de projets : chemins lisibles, homonymes numérotés localement."""
from collections import Counter


def project_choices(catalog, ids=None):
    ids={r.id for r in catalog.records.values() if r.kind=='project'} if ids is None else set(ids)
    paths={}
    for identity in sorted(ids):
        parts=[];current=identity
        while current:
            row=catalog.records[current];parts.append(row.title);current=row.parent
        paths[identity]=' / '.join(reversed(parts))
    counts=Counter(paths.values());numbers=Counter();result={}
    # Réserver aussi les vrais noms pour ne pas heurter un projet nommé « X · 1 ».
    reserved=set(paths.values())
    for identity,path in paths.items():
        label=path
        if counts[path]>1:
            while True:
                numbers[path]+=1;label=f'{path} · {numbers[path]}'
                if label not in reserved and label not in result:break
        result[label]=identity
    return dict(sorted(result.items()))
