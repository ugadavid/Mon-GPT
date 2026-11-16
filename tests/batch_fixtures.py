"""Catalogue fictif pour les tests et la recette MG-010b."""
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT


def fixture(count=22):
    cat=Catalog();adapter=ChatGPT(cat)
    p=cat.add('Atelier des idées','project');q=cat.add('Voyages imaginaires','project')
    twin=cat.add('Voyages imaginaires','project');r=cat.add('Autre carnet','project')
    child=cat.add('Sous-projet fictif','project',p.id)
    p.visual={'image':'pack:creation','icon':'palette','color':'terracotta'}
    q.visual={'image':'pack:voyage','icon':'compass','color':'petrole'}
    items=[]
    for i in range(count):
        item,_=adapter.ingest('Carnet partagé' if i<2 else f'Idée imaginaire {i+1:04}',f'https://chatgpt.com/c/00000000-0000-4000-8000-{i+1:012}')
        item.notes='Notes fictives à conserver';item.description='Une idée à explorer.';item.tags=['Fiction'];item.categories=['Atelier'];item.metadata={'Repère':'Fictif'}
        projects=[] if i>=count-2 else ([p.id,r.id] if i<10 else [p.id])
        cat.attach(item.id,projects)
        if i<2:item.visual={'image':'pack:ecriture' if i==0 else 'pack:voyage','icon':'book','color':'sauge'}
        items.append(item)
    adapter.project_links={f'g-p-fictif-{i}':record.id for i,record in enumerate((p,q,twin,r),1)}
    return cat,adapter,(p,q,twin,r,child),items
