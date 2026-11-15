"""Catalogue MG-004 exclusivement fictif ; refuse tout remplacement."""
import sys
from pathlib import Path
from PIL import Image,ImageDraw
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT
from mon_gpt.storage import Store


def create(directory):
    store=Store(directory);store.acquire()
    try:
        if store.path.exists(): raise ValueError("Catalogue existant : aucune donnée remplacée.")
        cat=Catalog();adapter=ChatGPT(cat)
        writing=cat.add("Le jardin des récits","project")
        writing.visual={"image":"pack:ecriture","icon":"book","color":"terracotta"}
        travel=cat.add("Les grands horizons","project")
        travel.visual={"image":"pack:montagne","icon":"compass","color":"petrole"}
        child=cat.add("Carnet de lumière","project",writing.id)
        child.visual={"image":"pack:creation","icon":"palette","color":"prune"}
        cat.add("Une nouvelle prairie","project")
        portrait=cat.add("Portrait imaginaire","project")
        image=Image.new("RGB",(450,800),"#E7D9C5");d=ImageDraw.Draw(image)
        d.rectangle((0,0,449,50),fill="#BD7658");d.rectangle((0,749,449,799),fill="#447984")
        d.ellipse((85,175,365,455),fill="#D9B75D");d.polygon([(0,680),(140,490),(270,600),(450,460),(450,748),(0,748)],fill="#8FA98B")
        path=store.directory/'portrait-fictif.png';image.save(path)
        portrait.visual={"image":store.images.import_file(path),"icon":"camera","color":"brume"}
        titles=["01 · Un jardin sur la Lune","02 · Préparer une échappée imaginaire","03 · La couleur des souvenirs",
                "04 · Carnet de route : traverser les montagnes et inventer un voyage au fil des saisons, des rencontres et des chemins oubliés",
                "05 · Des idées à garder pour demain","06 · Lumière sur un monde inventé"]
        descriptions=["Faire pousser un jardin entre les étoiles. Des pistes pour un récit tendre, lumineux et un peu surprenant.",
                      "Un même fil, deux univers : préparer les étapes d’un voyage et en faire une belle histoire.",
                      "Composer une palette douce, choisir les matières et donner une atmosphère au carnet.",
                      "Imaginer une traversée des Alpes, des sentiers au bord des lacs et des haltes dans les villages. "*7,
                      "", "Une étude de lumière dans un portrait fictif : garder le haut et le bas de l’image visibles."]
        for n,title in enumerate(titles):
            r,_=adapter.ingest(title,f"https://chatgpt.com/c/00000000-0000-4000-8000-{n+401:012d}")
            r.description=descriptions[n];r.notes="Note fictive partagée, à conserver dans tous les emplacements."
            r.categories=["Imaginaire","Écriture"] if n<3 else ["Exploration"]
            r.tags=["Idées","À explorer","Été"] if n!=4 else ["Plus tard"]
            links=[[writing.id],[writing.id,travel.id],[child.id],[travel.id],[],[portrait.id]][n]
            if links: cat.attach(r.id,links)
        for n in range(18):
            r,_=adapter.ingest(f"{n+7:02} · Fragments d’un atelier imaginaire — carnet {n+1}",f"https://chatgpt.com/c/00000000-0000-4000-8000-{n+410:012d}")
            r.description="Une collection de petites idées, de paysages inventés et de mots à retrouver."
            r.tags=["Carnet"];r.categories=["Imaginaire"]
            cat.attach(r.id,[writing.id,travel.id,child.id][n%3:n%3+1])
        store.save(cat,adapter)
    finally: store.lock.close()


if __name__=="__main__": create(Path(sys.argv[1]))
