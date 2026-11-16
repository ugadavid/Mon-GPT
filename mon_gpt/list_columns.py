"""Description et validation des colonnes : préférences d'affichage uniquement."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Column:
    key: str
    label: str
    width: int
    minimum: int
    maximum: int
    render: str = 'text'


COLUMNS=(Column('title','Titre',310,180,1200),
         Column('context','Projet',150,65,1000),
         Column('categories','Catégories',150,65,1000,'categories'),
         Column('tags','Tags',150,65,1000,'tags'),
         Column('created','Création',145,90,1000,'date'),
         Column('modified','Modification',145,90,1000,'date'))
BY_KEY={c.key:c for c in COLUMNS}


def defaults():
    return dict(order=list(BY_KEY),visible=[c.key for c in COLUMNS[:4]],
                widths={c.key:c.width for c in COLUMNS},sort='title',reverse=False)


def validate(value):
    if not isinstance(value,dict) or set(value)!={'order','visible','widths','sort','reverse'}:
        raise ValueError('Configuration des colonnes invalide')
    order,visible,widths=value['order'],value['visible'],value['widths']
    if not isinstance(order,list) or len(order)!=len(COLUMNS) or any(not isinstance(k,str) for k in order) or set(order)!=set(BY_KEY) or order[0]!='title':
        raise ValueError('Ordre des colonnes invalide')
    if not isinstance(visible,list) or not 1<=len(visible)<=len(COLUMNS) or any(not isinstance(k,str) for k in visible) or len(set(visible))!=len(visible) or not set(visible)<=set(BY_KEY) or 'title' not in visible:
        raise ValueError('Visibilité des colonnes invalide')
    if not isinstance(widths,dict) or set(widths)!=set(BY_KEY) or any(type(widths[c.key]) is not int or not c.minimum<=widths[c.key]<=c.maximum for c in COLUMNS):
        raise ValueError('Largeur de colonne invalide')
    if not isinstance(value['sort'],str) or value['sort'] not in BY_KEY or type(value['reverse']) is not bool:
        raise ValueError('Tri invalide')
    return dict(order=list(order),visible=[k for k in order if k in visible],widths=dict(widths),sort=value['sort'],reverse=value['reverse'])


def display_date(value,seconds=False):
    return datetime.fromisoformat(value).astimezone().strftime('%d/%m/%Y %H:%M:%S %Z' if seconds else '%d/%m/%Y %H:%M')


def sort_value(cells,key):
    if BY_KEY[key].render=='date':return datetime.fromisoformat(cells[key]).timestamp()
    from .core import fold
    return fold(' · '.join(cells[key]) if isinstance(cells[key],list) else cells[key])
