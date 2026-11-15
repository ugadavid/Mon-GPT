"""Trois sélecteurs de projet et illustration contextuelle, sans règle métier."""
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageDraw, ImageOps, ImageTk
from .identity import COVERS, ICONS, PALETTE, DEFAULTS
from .images import IMPORT_HINT
from .atelier import Masthead, rounded, AutoScrollbar
from .inspector import InspectorScrollbar
from .theme import COLORS as C


def icon_picture(key,color,size=28):
    scale=4
    image=Image.new("RGBA",(24*scale,24*scale))
    draw=ImageDraw.Draw(image)
    def line(points): draw.line([(x*scale,y*scale) for x,y in points],fill=color,width=scale,joint="curve")
    def oval(box): draw.ellipse(tuple(v*scale for v in box),outline=color,width=scale)
    if key=="folder": line([(3,19),(3,6),(9,6),(12,9),(21,9),(21,19),(3,19)])
    elif key=="book":
        line([(12,6),(7,4),(3,5),(3,19),(7,18),(12,20),(17,18),(21,19),(21,5),(17,4),(12,6),(12,20)])
    elif key=="leaf":
        line([(5,20),(12,12),(20,4)])
        draw.arc((4*scale,4*scale,21*scale,21*scale),0,180,fill=color,width=scale)
        draw.arc((4*scale,3*scale,21*scale,20*scale),180,360,fill=color,width=scale)
    elif key=="compass":
        oval((3,3,21,21));line([(16,7),(14,14),(7,17),(10,10),(16,7)]);line([(10,10),(14,14)])
    elif key=="mountain":
        line([(2,20),(10,5),(15,13),(18,9),(23,20),(2,20)]);line([(7,10),(10,12),(12,9)])
    elif key=="flask":
        line([(8,3),(16,3),(14,3),(14,10),(21,20),(3,20),(10,10),(10,3)]);line([(7,15),(17,15)])
    elif key=="palette":
        oval((3,3,21,21));oval((7,7,9,9));oval((13,6,15,8));oval((16,11,18,13));oval((7,13,9,15));line([(14,20),(12,17),(15,15),(18,17)])
    else:
        line([(7,7),(17,7),(17,17),(7,17),(7,7)])
        for n in (9,12,15):
            line([(n,3),(n,7)]);line([(n,17),(n,21)]);line([(3,n),(7,n)]);line([(17,n),(21,n)])
    return image.resize((size,size),Image.Resampling.LANCZOS)


def thumbnail(library,reference,width,height,radius=7):
    image=ImageOps.fit(library.open(reference),(width,height),method=Image.Resampling.LANCZOS)
    mask=Image.new("L",image.size,0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,width-1,height-1),radius=radius,fill=255)
    image.putalpha(mask)
    return image


def choice_name(kind,value):
    if kind=="image": return COVERS.get(value.removeprefix("pack:"),"Image personnelle")
    if kind=="icon": return ICONS[value]
    return PALETTE[value][0]


class ContextMasthead(Masthead):
    def __init__(self,parent,library):
        self.library,self.identity=library,None
        self.photo_key,self.photo=None,None
        super().__init__(parent)

    def set_identity(self,identity):
        if identity!=self.identity:
            self.identity=identity
            self.draw()

    def draw(self,event=None):
        super().draw(event)
        visual=self.identity
        if visual is None or not visual.image: return
        width=self.winfo_width()
        scale=.45 if width>=560 else .25 if width>=420 else .15
        w,h=round(500*scale),round(114*scale)
        key=(visual.image,visual.icon,visual.color,w,h)
        if key!=self.photo_key:
            try:
                image=thumbnail(self.library,visual.image,w,h,5)
                draw=ImageDraw.Draw(image)
                draw.rectangle((3,h-3,w-4,h-1),fill=PALETTE[visual.color][1])
                if h>=28:
                    draw.rounded_rectangle((4,4,26,26),radius=5,fill=C["paper"])
                    image.alpha_composite(icon_picture(visual.icon,PALETTE[visual.color][1],20),(5,5))
                self.photo=ImageTk.PhotoImage(image,master=self)
                self.photo_key=key
            except (ValueError,OSError):
                # Une ressource endommagée après chargement ne détruit pas le bandeau neutre.
                return
        self.delete("landscape")
        self.create_image(width-w-8,78-h,image=self.photo,anchor="nw",tags="context_cover")


class ProjectVisualFields(ttk.Frame):
    def __init__(self,parent,app,value):
        super().__init__(parent,style="Paper.TFrame")
        self.app=app
        self.value={**DEFAULTS,**value}
        self.previews={}
        self.names={}
        self.buttons={}
        for kind,title in (("image","Image"),("icon","Icône"),("color","Couleur")):
            ttk.Label(self,text=title,style="Paper.TLabel",font=("Segoe UI",10,"bold")).pack(anchor="w",pady=(9,4))
            row=ttk.Frame(self,style="Paper.TFrame")
            row.pack(fill="x")
            picture=tk.Label(row,background=C["paper"],borderwidth=0)
            picture.pack(side="left",padx=(0,8))
            button=small_button(app,row,"Choisir",lambda k=kind:self.open(k),74)
            button.pack(side="right",padx=(6,0))
            name=ttk.Label(row,style="PaperMuted.TLabel",font=("Segoe UI",9),wraplength=100)
            name.pack(side="left",fill="x",expand=True)
            self.previews[kind],self.names[kind],self.buttons[kind]=picture,name,button
        self.refresh()

    def get(self): return dict(self.value)

    def refresh(self):
        for kind,value in self.value.items():
            if kind=="image": image=thumbnail(self.app.store.images,value,90,51)
            elif kind=="icon": image=icon_picture(value,PALETTE[self.value["color"]][1],28)
            else:
                image=Image.new("RGBA",(28,28))
                ImageDraw.Draw(image).ellipse((2,2,25,25),fill=PALETTE[value][1])
            photo=ImageTk.PhotoImage(image,master=self)
            self.previews[kind].configure(image=photo)
            self.previews[kind].image=photo
            self.names[kind].configure(text=choice_name(kind,value))

    def open(self,kind):
        if getattr(self.app,"visual_layer",None): self.app.visual_layer.cancel()
        self.app.visual_layer=VisualLayer(self.app,self,kind)


def small_button(app,parent,text,command,width):
    button=app.button(parent,text=text,command=command,width=width,height=29)
    button.font=("Segoe UI",9)
    return button


class ChoiceTile(tk.Canvas):
    def __init__(self,parent,layer,value):
        self.layer,self.value=layer,value
        self.photo=None
        super().__init__(parent,height=94 if layer.kind=="image" else 72,width=1,
                         background=C["paper"],highlightthickness=0,takefocus=1)
        self.bind("<Configure>",self.draw)
        self.bind("<FocusIn>",self.focused);self.bind("<FocusOut>",self.draw)
        self.bind("<Button-1>",lambda e:self.choose())
        self.bind("<Return>",lambda e:self.choose());self.bind("<space>",lambda e:self.choose())
        for key,step in (("Left",-1),("Right",1),("Up",-layer.columns),("Down",layer.columns)):
            self.bind("<"+key+">",lambda e,s=step:self.neighbor(s))

    def choose(self):
        self.focus_set()
        self.layer.selected=self.value
        self.layer.refresh()
        return "break"

    def neighbor(self,step):
        self.layer.tiles[(self.layer.tiles.index(self)+step)%len(self.layer.tiles)].focus_set()
        return "break"

    def focused(self,event=None):
        canvas=self.layer.canvas
        top=self.winfo_rooty()-canvas.winfo_rooty()
        if top<0 or top+self.winfo_height()>canvas.winfo_height():
            content_height=max(1,self.layer.content.winfo_height())
            offset=self.winfo_rooty()-self.layer.content.winfo_rooty()
            canvas.yview_moveto(max(0,(offset-6)/content_height))
        self.draw()

    def draw(self,event=None):
        self.delete("all")
        w,h=self.winfo_width(),self.winfo_height()
        selected=self.layer.selected==self.value
        focused=self.focus_get()==self
        rounded(self,2,2,w-2,h-2,9,fill=C["selection"] if selected else C["paper"],
                outline=C["pine"] if selected or focused else C["line"],width=2 if selected or focused else 1)
        kind=self.layer.kind
        if kind=="image":
            image=thumbnail(self.layer.app.store.images,self.value,max(2,w-12),60,5)
            self.photo=ImageTk.PhotoImage(image,master=self)
            self.create_image(w/2,6,image=self.photo,anchor="n")
        elif kind=="icon":
            self.photo=ImageTk.PhotoImage(icon_picture(self.value,C["pine"],28),master=self)
            self.create_image(w/2,22,image=self.photo)
        else:
            color=PALETTE[self.value][1]
            self.create_oval(w/2-12,9,w/2+12,33,fill=color,outline="")
        self.create_text(w/2,h-17,text=choice_name(kind,self.value),font=("Segoe UI",8),fill=C["ink"],width=max(10,w-9),justify="center")
        if selected: self.create_text(w-10,10,text="✓",fill=C["pine"],font=("Segoe UI",9,"bold"))


class VisualLayer(ttk.Frame):
    def __init__(self,app,fields,kind):
        super().__init__(app.canvas,style="Paper.TFrame",padding=12)
        self.app,self.fields,self.kind=app,fields,kind
        self.selected=fields.value[kind]
        self.columns=2 if kind=="image" else 4
        self.place(x=0,y=0,relwidth=1,relheight=1)
        self.lift()
        header=ttk.Frame(self,style="Paper.TFrame")
        header.pack(fill="x",pady=(0,8))
        ttk.Label(header,text={"image":"Une image pour ce projet","icon":"Un repère au trait","color":"La couleur du projet"}[kind],style="Paper.TLabel",foreground=C["pine"],font=("Segoe UI",11,"bold"),wraplength=220).pack(side="left")
        small_button(app,header,"×",self.cancel,28).pack(side="right")
        footer=ttk.Frame(self,style="Paper.TFrame")
        footer.pack(side="bottom",fill="x",pady=(8,0))
        small_button(app,footer,"Par défaut",self.defaults,85).pack(side="left")
        small_button(app,footer,"Utiliser",self.accept,69).pack(side="right")
        small_button(app,footer,"Annuler",self.cancel,69).pack(side="right",padx=4)
        self.error=ttk.Label(self,text="",background="#F7E6DF",foreground="#8C4F38",font=("Segoe UI",9),wraplength=270,justify="left")
        body=ttk.Frame(self,style="Paper.TFrame")
        self.body=body
        body.pack(fill="both",expand=True)
        self.canvas=tk.Canvas(body,background=C["paper"],highlightthickness=0,width=1,height=1)
        scrollbar=InspectorScrollbar(body,self.canvas)
        scrollbar.pack(side="right",fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left",fill="both",expand=True)
        self.content=ttk.Frame(self.canvas,style="Paper.TFrame")
        window=self.canvas.create_window(0,0,window=self.content,anchor="nw")
        self.canvas.bind("<Configure>",lambda e:self.canvas.itemconfigure(window,width=e.width))
        self.content.bind("<Configure>",lambda e:self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.preview=tk.Label(self.content,background=C["paper"],borderwidth=0)
        self.preview.pack(anchor="w",pady=(2,5))
        self.name=ttk.Label(self.content,style="Paper.TLabel",font=("Segoe UI",10,"bold"),wraplength=260)
        self.name.pack(anchor="w",pady=(0,10))
        if kind=="image":
            ttk.Label(self.content,text=IMPORT_HINT,style="PaperMuted.TLabel",font=("Segoe UI",8),wraplength=264,justify="left").pack(fill="x",pady=(0,5))
            small_button(app,self.content,"Importer mon image…",self.import_image,170).pack(anchor="w",pady=(0,12))
        grid=ttk.Frame(self.content,style="Paper.TFrame")
        grid.pack(fill="x")
        values=["pack:"+key for key in COVERS] if kind=="image" else list(ICONS if kind=="icon" else PALETTE)
        self.tiles=[]
        for index,value in enumerate(values):
            tile=ChoiceTile(grid,self,value)
            tile.grid(row=index//self.columns,column=index%self.columns,sticky="nsew",padx=2,pady=3)
            grid.columnconfigure(index%self.columns,weight=1,uniform="tiles")
            self.tiles.append(tile)
        def wheel(event):
            self.canvas.yview_scroll(-1 if event.delta>0 else 1,"units")
            return "break"
        def bindings(widget):
            widget.bind("<MouseWheel>",wheel)
            widget.bind("<Escape>",lambda e:(self.cancel(),"break")[1])
            for child in widget.winfo_children(): bindings(child)
        bindings(self)
        self.refresh()
        self.update_idletasks()
        next((t for t in self.tiles if t.value==self.selected),self.tiles[0]).focus_set()

    def refresh(self):
        if self.kind=="image": image=thumbnail(self.app.store.images,self.selected,264,148)
        elif self.kind=="icon": image=icon_picture(self.selected,PALETTE[self.fields.value["color"]][1],42)
        else:
            image=Image.new("RGBA",(48,48))
            ImageDraw.Draw(image).ellipse((2,2,45,45),fill=PALETTE[self.selected][1])
        self.photo=ImageTk.PhotoImage(image,master=self)
        self.preview.configure(image=self.photo)
        self.name.configure(text=choice_name(self.kind,self.selected))
        for tile in self.tiles: tile.draw()

    def defaults(self):
        self.selected=DEFAULTS[self.kind]
        self.refresh()

    def import_image(self):
        path=filedialog.askopenfilename(parent=self.app.root,title="Importer mon image",filetypes=[("Images PNG, JPG/JPEG, WebP","*.png *.jpg *.jpeg *.webp"),("Tous les fichiers","*.*")])
        if not path: return
        try:
            reference=self.app.store.images.import_file(path)
            self.selected=reference
            self.error.configure(text="")
            self.error.pack_forget()
            self.refresh()
            self.canvas.yview_moveto(0)
        except (OSError,ValueError) as exc:
            self.error.configure(text=str(exc))
            self.error.pack(side="bottom",fill="x",before=self.body,pady=(4,0))

    def accept(self):
        if self.selected!=self.fields.value[self.kind]:
            self.fields.value[self.kind]=self.selected
            self.app.dirty=True
            self.fields.refresh()
        self.cancel()

    def cancel(self):
        self.app.visual_layer=None
        self.destroy()
        button=self.fields.buttons[self.kind]
        if button.winfo_exists(): button.focus_set()
