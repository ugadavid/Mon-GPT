"""Sélection ordonnée de résultats, indépendante des rendus et de Tk."""
class Selection:
    def __init__(self):
        self.ids=()
        self.anchor=None
        self.focal=None

    def set(self,ids,order,items,anchor=None,focal=None):
        wanted=set(ids)
        chosen=tuple(i for i in order if i in wanted)
        # Un projet peut être sélectionné seul, jamais mélangé aux discussions.
        if len(chosen)>1: chosen=tuple(i for i in chosen if i in items)
        self.ids=chosen
        self.focal=focal if focal in order else (chosen[0] if chosen else None)
        self.anchor=anchor if anchor in order else (chosen[0] if chosen else None)
        return chosen

    def gesture(self,identity,order,items,control=False,shift=False,project_alone=True):
        if identity not in order: return
        if identity not in items and (not shift or project_alone):
            return self.set([identity],order,items)
        if shift:
            anchor=self.anchor if self.anchor in order and self.anchor in items else identity
            a,b=sorted((order.index(anchor),order.index(identity)))
            wanted=set(self.ids if control else ()) | {i for i in order[a:b+1] if i in items}
            return self.set(wanted,order,items,anchor,identity)
        if control:
            wanted=set(self.ids).intersection(items)
            if identity in wanted: wanted.remove(identity)
            else: wanted.add(identity)
            return self.set(wanted,order,items,self.anchor or identity,identity)
        return self.set([identity],order,items,identity,identity)
