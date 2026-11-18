"""Trois sélecteurs partagés et illustration contextuelle, sans règle métier."""
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageTk
from math import sin, pi
from datetime import datetime
from .identity import COVERS, ICONS, PALETTE, DEFAULTS
from .images import IMPORT_HINT
from .atelier import Masthead, rounded, CatalogList, shorten
from tkinter.font import Font
from .inspector import InspectorScrollbar
from .theme import COLORS as C
from .project_icons import icon_picture


def thumbnail(library,reference,width,height,radius=7):
    image=ImageOps.fit(library.open(reference),(width,height),method=Image.Resampling.LANCZOS)
    mask=Image.new("L",image.size,0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,width-1,height-1),radius=radius,fill=255)
    image.putalpha(mask)
    return image


def contained_picture(library,reference,width,height):
    """Toute l’image, y compris un portrait, dans un cadre 16:9 sans masque."""
    image=ImageOps.contain(library.open(reference),(width,height),method=Image.Resampling.LANCZOS)
    frame=Image.new("RGBA",(width,height),C["ivory"])
    frame.alpha_composite(image,((width-image.width)//2,(height-image.height)//2))
    return frame


def swatch_picture(color,size=30):
    image=Image.new("RGBA",(size*4,size*4))
    ImageDraw.Draw(image).ellipse((8,8,size*4-9,size*4-9),fill=color)
    return image.resize((size,size),Image.Resampling.LANCZOS)


def choice_name(kind,value):
    if kind=="image": return COVERS.get(value.removeprefix("pack:"),"Image personnelle")
    if kind=="icon": return ICONS[value]
    return PALETTE[value][0]


class ContextMasthead(Masthead):
    def __init__(self,parent,library):
        self.library,self.identity=library,None
        self.photo_key,self.photo=None,None
        self.scope_info=("",(),())
        super().__init__(parent)
        self.small_font=Font(self,font=("Segoe UI",10))
        self.context_font=Font(self,font=("Segoe UI",12,"bold"))

    def set_identity(self,identity):
        if identity!=self.identity:
            self.identity=identity
            self.draw()

    def set_context(self,identity,project=None,count=0,scope_label="Tous les fils"):
        info=(project.description,tuple(project.categories),tuple(project.tags)) if project else ('',(),())
        title=project.title if project else scope_label
        date=datetime.fromisoformat(project.created).strftime("%d/%m/%Y") if project else ""
        caption=f"{count} discussion{'s' if count!=1 else ''}  ·  Créé le {date}" if date else ""
        context=(title,caption)
        if identity!=self.identity or info!=self.scope_info or context!=getattr(self,"context",None):
            self.identity,self.scope_info,self.context=identity,info,context
            self.draw()

    def draw(self,event=None):
        super().draw(event)
        width=self.winfo_width()
        compact=width<590
        height=104 if compact else 132
        if int(self.cget("height"))!=height:
            self.configure(height=height)
        description,categories,tags=self.scope_info
        title,caption=getattr(self,"context",("", ""))
        info_width=min(202,max(134,width//4)) if not compact else max(80,width-235)
        text_x=width-info_width+4
        # La couverture occupe l’espace entre la signature et la fiche projet.
        left=222
        right=text_x-12 if not compact else width-5
        art_height=height-4 if not compact else 51
        art_width=min(520,max(0,right-left))
        left+=max(0,(right-left-art_width)//2)
        self.draw_cover(left,art_width,art_height)
        if compact:
            y=63
        else:
            y=24
        self.create_line(text_x,y+6,text_x,y-7,text_x+7,y-7,text_x+10,y-4,
                         text_x+20,y-4,text_x+20,y+6,text_x,y+6,
                         fill=C["pine"],width=1.5,joinstyle="round")
        self.create_text(text_x+27,y,text=shorten(self.context_font,title,info_width-36),
                         font=self.context_font,fill=C["pine"],anchor="w")
        if not compact and caption:
            if self.small_font.measure(caption)>info_width-10:
                caption=caption.replace("Créé le ","")
            self.create_text(text_x,y+25,text=shorten(self.small_font,caption,info_width-10),
                             font=self.small_font,fill=C["muted"],anchor="w")
        if compact:
            if tags or categories:
                CatalogList.draw_badges(self,[*tags,*categories],text_x,88,info_width,False)
            elif description:
                self.create_text(text_x,88,text=shorten(self.small_font,description,info_width-10),
                                 font=self.small_font,fill=C["muted"],anchor="w")
        else:
            y+=49
            if description:
                self.create_text(text_x,y,text=shorten(self.small_font,' '.join(description.split()),info_width-12),
                                 font=self.small_font,fill=C["muted"],anchor="w",tags="scope_description")
                y+=23
            if categories:
                CatalogList.draw_badges(self,categories,text_x,y,info_width,True)
                y+=24
            CatalogList.draw_badges(self,tags,text_x,y,info_width,False)

    def draw_cover(self,left,art_width,art_height):
        self.cover_box=(0,0,0,0)
        if art_width<16:
            return
        visual=self.identity
        reference=visual.image if visual and visual.image else DEFAULTS["image"]
        key=(reference,art_width,art_height)
        if self.photo_key!=key:
            try:
                source=self.library.open(reference)
            except (ValueError,OSError):
                self.photo_key=None
                return
            if reference.startswith("asset:"):
                picture=ImageOps.contain(source,(art_width,art_height),Image.Resampling.LANCZOS)
            else:
                picture=ImageOps.fit(source,(art_width,art_height),Image.Resampling.LANCZOS,centering=(.5,.64))
                w,h=picture.size
                mask=Image.new("L",(w,h))
                edge=min(w*.16,48)
                points=[]
                for y in range(h):
                    t=y/max(1,h-1)
                    points.append((edge*(1-t)**2+edge*.18*sin(3*pi*t)+edge*.42*t**10,y))
                for y in reversed(range(h)):
                    t=y/max(1,h-1)
                    points.append((w-1-edge*(1-t)**2-edge*.32*sin(pi*t)**2-edge*.48*t**10,y))
                ImageDraw.Draw(mask).polygon(points,fill=255)
                picture.putalpha(mask.filter(ImageFilter.GaussianBlur(3)))
            self.photo=ImageTk.PhotoImage(picture,master=self)
            self.photo_key=key
        w,h=self.photo.width(),self.photo.height()
        x=left+(art_width-w)//2
        y=(art_height-h)//2+1
        self.cover_box=(x,y,w,h)
        self.create_image(x,y,image=self.photo,anchor="nw",tags="context_cover")


class ControlTip:
    """Nom visible au survol et au focus, sans consommer de ligne de formulaire."""
    def __init__(self,widget,text):
        self.widget,self.text=widget,text
        self.timer,self.window=None,None
        for event in ("<Enter>","<FocusIn>"): widget.bind(event,lambda e:self.schedule(),add="+")
        for event in ("<Leave>","<FocusOut>","<ButtonPress-1>","<KeyPress>","<Destroy>"):
            widget.bind(event,lambda e:self.hide(),add="+")

    def schedule(self):
        self.hide()
        self.timer=self.widget.after(450,self.show)

    def show(self):
        self.timer=None
        self.window=tk.Toplevel(self.widget)
        self.window.overrideredirect(True)
        text=self.text() if callable(self.text) else self.text
        tk.Label(self.window,text=text,font=("Segoe UI",9),background=C["ivory"],foreground=C["ink"],padx=8,pady=5,wraplength=250,relief="solid",borderwidth=1).pack()
        self.window.update_idletasks()
        x=min(self.widget.winfo_rootx(),self.widget.winfo_screenwidth()-self.window.winfo_reqwidth()-8)
        y=min(self.widget.winfo_rooty()+self.widget.winfo_height()+5,self.widget.winfo_screenheight()-self.window.winfo_reqheight()-8)
        self.window.geometry(f"+{max(0,x)}+{max(0,y)}")

    def hide(self):
        if self.timer is not None:
            self.widget.after_cancel(self.timer);self.timer=None
        if self.window is not None:
            self.window.destroy();self.window=None


class IdentityControl(tk.Canvas):
    def __init__(self,parent,kind,command=None):
        self.kind,self.command=kind,command
        self.picture=None
        super().__init__(parent,width=94 if kind=="image" else 46,height=56,background=C["paper"],highlightthickness=0,takefocus=bool(command),cursor="hand2" if command else "")
        self.bind("<Configure>",self.draw)
        self.bind("<FocusIn>",self.draw);self.bind("<FocusOut>",self.draw)
        self.bind("<Button-1>",lambda e:self.activate())
        self.bind("<Return>",lambda e:self.activate());self.bind("<space>",lambda e:self.activate())

    def activate(self):
        if self.command:
            self.focus_set();self.command()
        return "break"

    def draw(self,event=None):
        self.delete("all")
        w,h=self.winfo_width(),self.winfo_height()
        # Les trois segments partagent un contour continu, avec un filet intérieur.
        left=1 if self.kind=="image" else -9
        right=w-1 if self.kind=="color" else w+9
        rounded(self,left,1,right,h-1,9,fill=C["inspector_ivory"],outline=C["line"])
        if self.kind!="image":
            self.create_line(0,8,0,h-8,fill=C["line"])
        if self.command and self.focus_get()==self:
            rounded(self,1,1,w-1,h-1,8,fill="",outline=C["pine"],width=2)
        if self.picture: self.create_image(w/2,h/2,image=self.picture)


class ProjectVisualStrip(ttk.Frame):
    def __init__(self,parent,library,value,choose=None,*,inherited=None,origin=None):
        super().__init__(parent,style="Paper.TFrame")
        self.library,self.choose=library,choose
        self.inherited=inherited
        self.origin=origin
        self.overrides=dict(value)
        self.value={**DEFAULTS,**(inherited or {}),**value}
        self.buttons={}
        for kind in ("image","icon","color"):
            button=IdentityControl(self,kind,(lambda k=kind:choose(k)) if choose else None)
            if not choose:
                button.configure(width=88 if kind=="image" else 34,height=51)
            button.pack(side="left")
            self.buttons[kind]=button
            button.tip=ControlTip(button,lambda k=kind:self.control_name(k))
        self.refresh()

    def control_name(self,kind):
        label={"image":"Image","icon":"Icône","color":"Couleur"}[kind]
        status="" if self.inherited is None else (" · Personnalisée" if kind in self.overrides else " · Héritée "+(f"de « {self.origin} »" if self.origin else "du défaut"))
        return f"{label} · {choice_name(kind,self.value[kind])}"+status+(" — choisir" if self.choose else "")

    def refresh(self):
        for kind,value in self.value.items():
            if kind=="image": image=contained_picture(self.library,value,80,45)
            elif kind=="icon": image=icon_picture(value,PALETTE[self.value["color"]][1],28)
            else: image=swatch_picture(PALETTE[value][1])
            button=self.buttons[kind]
            button.picture=ImageTk.PhotoImage(image,master=self)
            button.draw()


class ProjectVisualFields(ProjectVisualStrip):
    def __init__(self,parent,app,value,*,inherited=None,origin=None):
        self.app=app
        super().__init__(parent,app.store.images,value,self.open,inherited=inherited,origin=origin)

    def get(self): return dict(self.overrides if self.inherited is not None else self.value)

    def set_choice(self,kind,value):
        previous=self.get()
        if value is None and self.inherited is not None:
            self.overrides.pop(kind,None)
            self.value[kind]=self.inherited[kind]
        else:
            self.overrides[kind]=value
            self.value[kind]=value
        if self.get()!=previous: self.app.dirty=True
        self.refresh()

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
        super().__init__(parent,height=94 if layer.kind=="image" else 54 if layer.kind=="color" else 68,width=1,
                         background=C["paper"],highlightthickness=0,takefocus=1)
        self.accessible_name=choice_name(layer.kind,value)
        self.bind("<Configure>",self.draw)
        self.bind("<FocusIn>",self.focused);self.bind("<FocusOut>",self.draw)
        self.bind("<Button-1>",lambda e:self.choose())
        if layer.kind=="image": self.bind("<Double-Button-1>",self.double_choose)
        self.bind("<Return>",lambda e:self.choose());self.bind("<space>",lambda e:self.choose())
        for key,step,vertical in (("Left",-1,False),("Right",1,False),("Up",-1,True),("Down",1,True)):
            self.bind("<"+key+">",lambda e,s=step,v=vertical:self.neighbor(s*self.layer.columns if v else s))
        if layer.kind in ("color","icon"): self.tip=ControlTip(self,self.accessible_name)

    def choose(self):
        self.focus_set()
        self.layer.selected=self.value
        self.layer.inheriting=False
        self.layer.refresh()
        return "break"

    def double_choose(self,event=None):
        if not self.layer.closed:
            self.choose()
            self.layer.accept()
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
        if self.layer.kind=="image":
            image_width=max(2,w-12)
            image_height=max(1,round(image_width*9/16))
            target_height=image_height+42
            if int(self.cget("height"))!=target_height:
                self.configure(height=target_height)
        selected=self.layer.selected==self.value
        focused=self.focus_get()==self
        if self.layer.kind=="color":
            x,y=w/2,h/2
            self.photo=ImageTk.PhotoImage(swatch_picture(PALETTE[self.value][1],36),master=self)
            self.create_image(x,y,image=self.photo)
            if selected or focused:
                self.create_oval(x-21,y-21,x+21,y+21,outline=C["pine"],width=2 if selected else 1,dash=() if selected else (2,2))
            if selected:
                rgb=PALETTE[self.value][1]
                light=sum(int(rgb[n:n+2],16)*k for n,k in ((1,.299),(3,.587),(5,.114)))>155
                self.create_text(x,y,text="✓",fill=C["ink"] if light else C["paper"],font=("Segoe UI",10,"bold"))
            return
        rounded(self,2,2,w-2,h-2,9,fill=C["selection"] if selected else C["paper"],
                outline=C["pine"] if selected or focused else C["line"],width=2 if selected or focused else 1)
        kind=self.layer.kind
        if kind=="image":
            key=(self.value,image_width,image_height)
            if getattr(self,"photo_key",None)!=key:
                image=contained_picture(self.layer.app.store.images,self.value,image_width,image_height)
                self.photo=ImageTk.PhotoImage(image,master=self)
                self.photo_key=key
            self.create_image(w/2,6,image=self.photo,anchor="n")
        elif kind=="icon":
            self.photo=ImageTk.PhotoImage(icon_picture(self.value,C["pine"],28),master=self)
            self.create_image(w/2,22,image=self.photo)
        label=choice_name(kind,self.value)
        self.create_text(w/2,h-17,text=label,font=("Segoe UI",7 if kind=="icon" and len(label)>11 else 8),fill=C["ink"],width=max(10,w-9),justify="center")
        if selected: self.create_text(w-10,10,text="✓",fill=C["pine"],font=("Segoe UI",9,"bold"))


class VisualLayer(ttk.Frame):
    def __init__(self,app,fields,kind):
        super().__init__(app.canvas,style="Paper.TFrame",padding=12)
        self.app,self.fields,self.kind=app,fields,kind
        self.closed=False
        self.selected=fields.value[kind]
        self.inheriting=fields.inherited is not None and kind not in fields.overrides
        self.columns=2 if kind=="image" else 4
        self.place(x=0,y=0,relwidth=1,relheight=1)
        self.lift()
        header=ttk.Frame(self,style="Paper.TFrame")
        header.pack(fill="x",pady=(0,8))
        ttk.Label(header,text={"image":"Une image pour ce fil" if fields.inherited is not None else "Une image pour ce projet","icon":"Un repère au trait","color":"La couleur du fil" if fields.inherited is not None else "La couleur du projet"}[kind],style="Paper.TLabel",foreground=C["pine"],font=("Segoe UI",11,"bold"),wraplength=220).pack(side="left")
        small_button(app,header,"×",self.cancel,28).pack(side="right")
        footer=ttk.Frame(self,style="Paper.TFrame")
        footer.pack(side="bottom",fill="x",pady=(8,0))
        if fields.inherited is not None:
            small_button(app,footer,"Revenir à l’héritage",self.defaults,165).pack(anchor="w",pady=(0,5))
        else:
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
        intro=self.content
        if kind=="color":
            intro=ttk.Frame(self.content,style="Paper.TFrame")
            intro.pack(fill="x",pady=(3,12))
        self.preview=tk.Label(intro,background=C["paper"],borderwidth=0)
        if kind=="image": self.preview.bind("<Double-Button-1>",lambda e:self.accept())
        self.name=ttk.Label(intro,style="Paper.TLabel",font=("Segoe UI",10,"bold"),wraplength=240)
        if kind=="color":
            self.preview.pack(side="left")
            self.name.pack(side="left",padx=8)
        else:
            self.preview.pack(anchor="w",pady=(2,5))
            self.name.pack(anchor="w",pady=(0,10))
        if kind=="image":
            ttk.Label(self.content,text=IMPORT_HINT,style="PaperMuted.TLabel",font=("Segoe UI",8),wraplength=264,justify="left").pack(fill="x",pady=(0,5))
            small_button(app,self.content,"Importer mon image…",self.import_image,170).pack(anchor="w",pady=(0,12))
        grid=self.grid_frame=ttk.Frame(self.content,style="Paper.TFrame")
        grid.pack(fill="x")
        values=["pack:"+key for key in COVERS] if kind=="image" else list(ICONS if kind=="icon" else PALETTE)
        if kind=="image" and self.selected not in values: values.insert(0,self.selected)
        self.tiles=[]
        for index,value in enumerate(values):
            tile=ChoiceTile(grid,self,value)
            tile.grid(row=index//self.columns,column=index%self.columns,sticky="nsew",padx=2,pady=3)
            grid.columnconfigure(index%self.columns,weight=1,uniform="tiles")
            self.tiles.append(tile)
        if kind=="icon": grid.bind("<Configure>",self.layout_icons)
        if kind=="image": self.canvas.bind("<Configure>",lambda e:self.refresh(),add=True)
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
        if self.kind=="image":
            width=max(64,min(512,self.canvas.winfo_width()-8))
            image=contained_picture(self.app.store.images,self.selected,width,round(width*9/16))
        elif self.kind=="icon": image=icon_picture(self.selected,PALETTE[self.fields.value["color"]][1],42)
        else:
            image=swatch_picture(PALETTE[self.selected][1],30)
        self.photo=ImageTk.PhotoImage(image,master=self)
        self.preview.configure(image=self.photo)
        status="" if self.fields.inherited is None else (" · Héritée" if self.inheriting else " · Personnalisée")
        self.name.configure(text=choice_name(self.kind,self.selected)+status)
        for tile in self.tiles: tile.draw()

    def layout_icons(self,event):
        columns=max(4,min(6,event.width//68))
        if columns==self.columns: return
        for index in range(max(columns,self.columns)):
            self.grid_frame.columnconfigure(index,weight=1 if index<columns else 0,uniform="tiles" if index<columns else "")
        self.columns=columns
        for index,tile in enumerate(self.tiles): tile.grid(row=index//columns,column=index%columns)

    def defaults(self):
        self.inheriting=self.fields.inherited is not None
        self.selected=self.fields.inherited[self.kind] if self.inheriting else DEFAULTS[self.kind]
        self.refresh()

    def import_image(self):
        path=filedialog.askopenfilename(parent=self.app.root,title="Importer mon image",filetypes=[("Images PNG, JPG/JPEG, WebP","*.png *.jpg *.jpeg *.webp"),("Tous les fichiers","*.*")])
        if not path: return
        try:
            reference=self.app.store.images.import_file(path)
            self.selected=reference
            self.inheriting=False
            self.error.configure(text="")
            self.error.pack_forget()
            if not any(t.value==reference for t in self.tiles):
                tile=ChoiceTile(self.grid_frame,self,reference)
                index=len(self.tiles)
                tile.grid(row=index//self.columns,column=index%self.columns,sticky="nsew",padx=2,pady=3)
                self.tiles.append(tile)
            self.refresh()
            self.canvas.yview_moveto(0)
        except (OSError,ValueError) as exc:
            self.error.configure(text=str(exc))
            self.error.pack(side="bottom",fill="x",before=self.body,pady=(4,0))

    def accept(self):
        if self.closed: return "break"
        self.fields.set_choice(self.kind,None if self.inheriting else self.selected)
        self.cancel()
        return "break"

    def cancel(self):
        if self.closed: return
        self.closed=True
        self.app.visual_layer=None
        self.destroy()
        button=self.fields.buttons[self.kind]
        if button.winfo_exists(): button.focus_set()
