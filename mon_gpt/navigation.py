"""Habillage local de l'arbre natif, sans règle de classement."""
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from .atelier import shorten, AutoScrollbar
from .theme import COLORS as C


def navigation_icons(root):
    result={}
    for kind in ("project","all","unfiled"):
        icon=tk.PhotoImage(master=root,width=20,height=20)
        def line(x1,y1,x2,y2):
            steps=max(abs(x2-x1),abs(y2-y1),1)
            for n in range(steps+1):
                icon.put(C["pine"],(round(x1+(x2-x1)*n/steps),round(y1+(y2-y1)*n/steps)))
        if kind=="project":
            points=[(2,15),(2,5),(7,5),(10,8),(17,8),(17,15),(2,15)]
        elif kind=="all":
            points=[(2,6),(10,2),(18,6),(10,10),(2,6)]
            line(2,10,10,14);line(10,14,18,10)
            line(2,14,10,18);line(10,18,18,14)
        else:
            points=[(2,12),(5,4),(15,4),(18,12),(18,16),(2,16),(2,12),(7,12),(8,14),(12,14),(13,12),(18,12)]
        for a,b in zip(points,points[1:]): line(*a,*b)
        result[kind]=icon
    return result


class NavigationTree(ttk.Treeview):
    def __init__(self,parent):
        style=ttk.Style(parent)
        style.configure("Nav.Treeview",rowheight=34,indent=18,font=("Segoe UI",10),background=C["paper"],fieldbackground=C["paper"],foreground=C["ink"])
        style.map("Nav.Treeview",background=[("selected","focus","#E0E7D5"),("selected","#E7ECDD")],foreground=[("selected",C["pine"])])
        super().__init__(parent,show="tree",selectmode="browse",style="Nav.Treeview",height=1)
        self.labels={}
        self.font=Font(self,font=("Segoe UI",10))
        self.root_font=Font(self,font=("Segoe UI",10,"bold"))
        self.tip_timer,self.tip=None,None
        self.hovered=None
        self.tag_configure("nav_root",font=("Segoe UI",10,"bold"))
        self.tag_configure("nav_hover",background="#F1F1E8")
        self.bind("<Configure>",lambda e:self.fit())
        self.bind("<<TreeviewOpen>>",lambda e:self.after_idle(self.fit),add="+")
        self.bind("<Motion>",self.motion)
        self.bind("<Leave>",lambda e:self.clear_hover())
        self.bind("<MouseWheel>",lambda e:self.clear_hover(),add="+")
        for event in ("<ButtonPress-1>","<ButtonPress-3>","<B1-Motion>","<B3-Motion>","<FocusOut>","<Destroy>"):
            self.bind(event,lambda e:self.hide_tip(),add="+")

    def insert(self,parent,index,iid=None,**kwargs):
        text=kwargs.get("text","")
        if not parent and iid not in ("all","unfiled"): kwargs["tags"]=tuple(kwargs.get("tags",()))+("nav_root",)
        identity=super().insert(parent,index,iid=iid,**kwargs)
        self.labels[identity]=text
        self.fit()
        return identity

    def delete(self,*items):
        self.hide_tip()
        pending=list(items)
        while pending:
            identity=pending.pop()
            pending.extend(self.get_children(identity))
            self.labels.pop(identity,None)
        super().delete(*items)

    def item(self,item,option=None,**kwargs):
        if "text" in kwargs: self.labels[item]=kwargs["text"]
        if "tags" in kwargs and not self.parent(item) and item not in ("all","unfiled"):
            kwargs["tags"]=tuple(kwargs["tags"])+( "nav_root",)
        result=super().item(item,option,**kwargs)
        if kwargs: self.fit()
        if option=="text": return self.labels.get(item,result)
        if option is None and not kwargs: result["text"]=self.labels.get(item,result.get("text",""))
        return result

    def fit(self):
        for identity,text in self.labels.items():
            depth=0
            parent=self.parent(identity)
            while parent:
                depth+=1
                parent=self.parent(parent)
            available=max(28,self.winfo_width()-(depth+1)*18-32)
            # Les UUID et les libellés exposés à l'application restent complets.
            super().item(identity,text=shorten(self.root_font if not self.parent(identity) and identity not in ("all","unfiled") else self.font,text,available))

    def hide_tip(self):
        if self.tip_timer is not None:
            self.after_cancel(self.tip_timer)
            self.tip_timer=None
        if self.tip is not None:
            self.tip.destroy()
            self.tip=None

    def clear_hover(self):
        self.hide_tip()
        if self.hovered and self.exists(self.hovered):
            tags=tuple(t for t in super().item(self.hovered,"tags") if t!="nav_hover")
            super().item(self.hovered,tags=tags)
        self.hovered=None

    def motion(self,event):
        identity=self.identify_row(event.y)
        if identity==self.hovered: return
        self.clear_hover()
        if identity:
            self.hovered=identity
            tags=super().item(identity,"tags")
            if not {"drop","forbidden"}.intersection(tags): super().item(identity,tags=tuple(tags)+( "nav_hover",))
            self.tip_timer=self.after(550,lambda:self.show_tip(identity,event.y))

    def show_tip(self,identity,y):
        self.tip_timer=None
        if not self.exists(identity): return
        self.tip=tk.Toplevel(self)
        self.tip.overrideredirect(True)
        tk.Label(self.tip,text=self.labels[identity],font=("Segoe UI",10),background=C["ivory"],foreground=C["ink"],wraplength=340,padx=9,pady=6,relief="solid",borderwidth=1).pack()
        self.tip.geometry(f"+{self.winfo_rootx()+12}+{self.winfo_rooty()+y+22}")


class NavigationScrollbar(AutoScrollbar):
    def __init__(self,parent,tree):
        self.tree=tree
        super().__init__(parent,orient="vertical",command=tree.yview)

    def set(self,first,last):
        if float(first)<=0 and float(last)>=1: self.pack_forget()
        elif not self.winfo_manager():
            options={"side":"right","fill":"y"}
            if self.tree.winfo_manager()=="pack": options["before"]=self.tree
            self.pack(**options)
        ttk.Scrollbar.set(self,first,last)
