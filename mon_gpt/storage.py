"""Stockage versionné, validation et remplacement atomique."""
import json
import os
import tempfile
import shutil
import zipfile
import stat
from pathlib import Path
from datetime import datetime
from uuid import UUID
from .core import Catalog, Record
from dataclasses import fields, dataclass
from .chatgpt import ChatGPT, Conversation, parse_url, PROJECT_KEY
from .identity import validate_visual, image_references, ASSET
from .images import ImageLibrary, check_asset, MAX_BYTES

MAX_CATALOG=10*1024*1024
MAX_ARCHIVE=100*1024*1024
MAX_EXPANDED=200*1024*1024


def encode(catalog, adapter):
    data = {"schema": 3, "records": catalog.to_list(), "chatgpt": adapter.to_list()}
    if adapter.project_links:
        data.update(schema=4, chatgpt_projects=dict(adapter.project_links))
    return data


def decode(data):
    try:
        if type(data) is not dict or type(data.get("schema")) is not int or data["schema"] not in (1,2,3,4):
            raise ValueError("Version de sauvegarde non prise en charge.")
        expected_keys={"schema", "records", "chatgpt"} | ({"chatgpt_projects"} if data["schema"]==4 else set())
        if set(data)!=expected_keys:
            raise ValueError("Champs de catalogue manquants ou inconnus.")
        if not isinstance(data["records"], list) or not isinstance(data["chatgpt"], list):
            raise ValueError("Listes attendues.")
        expected={f.name for f in fields(Record)}-({"visual"} if data["schema"]==1 else set())
        if any(not isinstance(r, dict) or set(r) != expected for r in data["records"]):
            raise ValueError("Champs de fiche manquants ou inconnus.")
        rows = [Record(**r) for r in data["records"]]
        cat = Catalog(rows)
        if len(rows) != len(cat.records):
            raise ValueError("Identifiants dupliqués.")
        for r in rows:
            UUID(r.id)
            validate_visual(r.visual,r.kind)
            if data["schema"]<3 and r.kind=="item" and r.visual:
                raise ValueError("Personnalisation des fils réservée au schéma 3.")
            if r.kind not in ("project", "item") or not isinstance(r.title, str) or not r.title.strip():
                raise ValueError("Fiche invalide.")
            if not all(isinstance(v, str) for v in (r.description, r.notes, r.created, r.modified)):
                raise ValueError("Champs texte invalides.")
            for stamp in (r.created, r.modified):
                if datetime.fromisoformat(stamp).tzinfo is None:
                    raise ValueError("Date sans fuseau.")
            for values in (r.tags, r.categories, r.projects):
                if not isinstance(values, list) or not all(isinstance(v, str) for v in values) or len(values) != len(set(values)):
                    raise ValueError("Liste invalide ou dupliquée.")
            if not isinstance(r.metadata, dict) or not all(isinstance(k, str) and k.strip() and isinstance(v, str) for k, v in r.metadata.items()):
                raise ValueError("Métadonnées invalides.")
            if type(r.order) is not int or r.order < 0:
                raise ValueError("Ordre invalide.")
            if r.kind == "item" and r.parent is not None or r.kind == "project" and r.projects:
                raise ValueError("Relations invalides.")
            for p in ([r.parent] if r.parent is not None else []) + r.projects:
                if p not in cat.records or cat.records[p].kind != "project":
                    raise ValueError("Projet absent.")
            seen, cursor = {r.id}, r.parent
            while cursor is not None:
                if cursor in seen:
                    raise ValueError("Cycle de projets.")
                seen.add(cursor)
                cursor = cat.records[cursor].parent
        conversations = [Conversation(**c) for c in data["chatgpt"]]
        if len({c.record_id for c in conversations}) != len(conversations) or len({c.conversation_id for c in conversations}) != len(conversations):
            raise ValueError("Conversations dupliquées.")
        if {c.record_id for c in conversations} != {r.id for r in rows if r.kind == "item"}:
            raise ValueError("Adaptateur incomplet.")
        for c in conversations:
            if parse_url(c.url)[0] != c.conversation_id:
                raise ValueError("Identité de conversation incohérente.")
        links=data.get("chatgpt_projects",{})
        if type(links) is not dict or len(links)>10000:
            raise ValueError("Correspondances ChatGPT invalides (10 000 maximum).")
        for key,target in links.items():
            if not isinstance(key,str) or not PROJECT_KEY.fullmatch(key) or not isinstance(target,str) or str(UUID(target))!=target:
                raise ValueError("Identité de correspondance ChatGPT invalide.")
            if target in cat.records and cat.records[target].kind!="project":
                raise ValueError("Une correspondance ChatGPT doit viser un projet.")
            # Un projet supprimé garde sa clé comme témoin : l'assistant exigera
            # une résolution explicite au prochain import, sans recréation cachée.
        return cat, ChatGPT(cat, conversations, links)
    except (TypeError, KeyError, AttributeError, ValueError) as exc:
        raise ValueError(f"Catalogue invalide : {exc}") from exc


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            name = stream.name
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


class Store:
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        self.path = self.directory / "catalogue.json"
        self.lock = None
        self.images = ImageLibrary(self.directory/"images")

    def acquire(self):
        # Verrou OS libéré aussi en cas d'arrêt brutal ; aucun verrou périmé.
        import msvcrt
        self.directory.mkdir(parents=True, exist_ok=True)
        self.lock = open(self.directory / "catalogue.lock", "a+b")
        try:
            if os.fstat(self.lock.fileno()).st_size == 0:
                self.lock.write(b"0")
                self.lock.flush()
            self.lock.seek(0)
            msvcrt.locking(self.lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            self.lock.close()
            raise ValueError("Ce catalogue est déjà ouvert dans une autre instance.") from None

    def load(self):
        if not self.path.exists():
            cat = Catalog()
            return cat, ChatGPT(cat)
        data=read_json(self.path)
        cat,adapter=decode(data)
        self.validate_images(cat)
        if data["schema"]<3:
            # Copie exacte avant la première écriture du format 3.
            self.save(cat,adapter)
        return cat,adapter

    @staticmethod
    def read(path):
        if zipfile.is_zipfile(path): return decode(read_backup(path).data)
        return decode(read_json(path))

    @staticmethod
    def prepare_restore(path):
        return read_backup(path)

    def validate_images(self,cat,images=None):
        for reference in image_references(cat):
            if images is not None:
                if reference not in images: raise ValueError("Sauvegarde incomplète : une image personnelle manque.")
                check_asset(reference,images[reference])
            else: self.images.read(reference)

    def save(self, cat, adapter):
        data = encode(cat, adapter)
        decode(data)
        catalog_bytes(data)
        self.validate_images(cat)
        if self.path.exists():
            old=read_json(self.path)
            if not isinstance(old,dict) or type(old.get("schema")) is not int or old["schema"] not in (1,2,3,4):
                raise ValueError("Version du catalogue existant non prise en charge ; fichier conservé.")
            if old["schema"]<data["schema"]:
                decode(old)
                backup=self.directory/(f"avant-migration-v{old['schema']}-"+datetime.now().strftime("%Y%m%d-%H%M%S-%f")+".json")
                shutil.copy2(self.path,backup)
        atomic_write(self.path, data)

    def commit_import(self, plan, cat, adapter):
        """Sauvegarde complète puis un seul remplacement ; objets actifs intacts."""
        if encode(cat,adapter)!=plan.before:
            raise ValueError("Le catalogue a changé : analysez à nouveau l’import.")
        new_cat,new_adapter=decode(plan.data)
        catalog_bytes(plan.data)
        self.validate_images(new_cat)
        if plan.data==plan.before:
            return cat,adapter,None
        backup=self.directory/("avant-import-"+datetime.now().strftime("%Y%m%d-%H%M%S-%f")+".zip")
        self.export(backup,cat,adapter)
        # La sauvegarde ZIP contient déjà l'état antérieur et les ressources.
        # save() conserve aussi la copie exacte d'un ancien schéma si nécessaire.
        self.save(new_cat,new_adapter)
        return new_cat,new_adapter,backup

    def commit_batch(self,plan,cat,adapter,expected):
        from .batch import build_batch
        if encode(cat,adapter)!=expected or cat.to_list()!=plan.before:
            raise ValueError("Le catalogue a changé depuis l’aperçu. Actualisez le plan ; aucun rattachement modifié.")
        checked=build_batch(cat,plan.ids,plan.action,plan.source,plan.destination)
        if checked!=plan: raise ValueError("Plan périmé ou incohérent : actualisez l’aperçu.")
        candidate,source=decode(expected)
        for identity,projects in checked.changes.items(): candidate.attach(identity,projects)
        data=encode(candidate,source)
        decode(data);catalog_bytes(data);self.validate_images(candidate)
        if not checked.changed: return cat,adapter
        # Un seul remplacement atomique ; aucun objet actif muté en cas d’échec.
        self.save(candidate,source)
        return candidate,source

    def export(self, destination, cat, adapter):
        destination=Path(destination).resolve()
        if destination == self.path or destination.is_relative_to(self.images.directory.resolve()):
            raise ValueError("Choisissez un autre fichier que le catalogue actif.")
        data = encode(cat, adapter)
        decode(data)
        catalog_bytes(data)
        self.validate_images(cat)
        references=image_references(cat)
        if destination.suffix.lower()!=".zip":
            if references: raise ValueError("Des images personnelles sont présentes : choisissez une sauvegarde complète ZIP.")
            atomic_write(destination, data)
            return
        images={ref:self.images.read(ref) for ref in references}
        write_backup(destination,data,images)

    def restore(self, candidate, cat, adapter):
        # Revalidation avant toute écriture, même si l'interface a déjà validé.
        bundle=isinstance(candidate,Backup)
        images=candidate.images if bundle else None
        new_cat, new_adapter = decode(candidate.data if bundle else candidate)
        self.validate_images(new_cat,images)
        # Vérifier les collisions avant de toucher au catalogue ou à ses ressources.
        for ref,data in (images or {}).items():
            target=self.images.path(ref)
            if target.exists() and target.read_bytes()!=data:
                raise ValueError("Une ressource existante est incohérente ; restauration annulée.")
        extension=".zip" if image_references(cat) else ".json"
        backup = self.directory / ("avant-restauration-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f") + extension)
        self.export(backup, cat, adapter)
        # Ressources immuables d’abord, catalogue atomique en dernier. Aucun nettoyage
        # destructif : un échec laisse les anciennes références utilisables.
        for reference,data in (images or {}).items(): self.images.put(reference,data)
        self.save(new_cat, new_adapter)
        return new_cat, new_adapter, backup


@dataclass
class Backup:
    data: dict
    images: dict[str,bytes]


def read_json(path):
    with open(path,"rb") as f: data=f.read(MAX_CATALOG+1)
    if len(data)>MAX_CATALOG: raise ValueError("Catalogue trop volumineux : 10 Mo maximum.")
    try: return json.loads(data.decode("utf-8"))
    except (UnicodeError,json.JSONDecodeError) as exc: raise ValueError("Catalogue JSON illisible.") from exc


def read_backup(path):
    if not zipfile.is_zipfile(path):
        data=read_json(path)
        cat,_=decode(data)
        if image_references(cat): raise ValueError("Sauvegarde JSON incomplète pour les images : utilisez l’archive ZIP complète.")
        return Backup(data,{})
    if Path(path).stat().st_size>MAX_ARCHIVE: raise ValueError("Archive trop volumineuse : 100 Mo maximum.")
    try:
        with zipfile.ZipFile(path) as archive:
            infos=archive.infolist()
            names=[i.filename for i in infos]
            if len(infos)>513 or len({name.casefold() for name in names})!=len(names):
                raise ValueError("Archive : trop de fichiers ou noms dupliqués.")
            if sum(i.file_size for i in infos)>MAX_EXPANDED: raise ValueError("Archive décompressée trop volumineuse : 200 Mo maximum.")
            for info in infos:
                name=info.filename
                allowed=name=="catalogue.json" or (name.startswith("images/") and ASSET.fullmatch("asset:"+name[7:-4]) and name.endswith(".png"))
                if not allowed or info.is_dir() or stat.S_ISLNK(info.external_attr>>16) or info.flag_bits&1:
                    raise ValueError("Nom, chemin ou type de fichier non autorisé dans l’archive.")
                if info.compress_type not in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED): raise ValueError("Compression d’archive non prise en charge.")
                limit=MAX_CATALOG if name=="catalogue.json" else MAX_BYTES
                if info.file_size>limit: raise ValueError("Fichier de sauvegarde trop volumineux.")
            if "catalogue.json" not in names: raise ValueError("Catalogue absent de l’archive.")
            data=json.loads(archive.read("catalogue.json").decode("utf-8"))
            cat,_=decode(data)
            references=image_references(cat)
            if set(names)!={"catalogue.json",*("images/"+r[6:]+".png" for r in references)}:
                raise ValueError("Images manquantes ou fichiers supplémentaires dans la sauvegarde.")
            images={ref:archive.read("images/"+ref[6:]+".png") for ref in references}
            for ref,content in images.items(): check_asset(ref,content)
            return Backup(data,images)
    except (zipfile.BadZipFile,UnicodeError,RuntimeError,EOFError) as exc:
        raise ValueError("Archive endommagée ou illisible.") from exc


def write_backup(destination,data,images):
    encoded=catalog_bytes(data)
    if len(encoded)>MAX_CATALOG or len(images)>512 or len(encoded)+sum(map(len,images.values()))>MAX_EXPANDED:
        raise ValueError("Sauvegarde trop volumineuse : 10 Mo de catalogue, 512 images et 200 Mo au total maximum.")
    destination=Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    name=None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent,delete=False) as f:
            name=f.name
            with zipfile.ZipFile(f,"w",compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("catalogue.json",encoded)
                for ref,content in sorted(images.items()): archive.writestr("images/"+ref[6:]+".png",content)
            f.flush();os.fsync(f.fileno())
        if Path(name).stat().st_size>MAX_ARCHIVE: raise ValueError("Archive trop volumineuse : 100 Mo maximum.")
        os.replace(name,destination)
    finally:
        if name and os.path.exists(name): os.unlink(name)


def catalog_bytes(data):
    encoded=json.dumps(data,ensure_ascii=False,indent=2).encode("utf-8")
    if len(encoded)>MAX_CATALOG: raise ValueError("Catalogue trop volumineux : 10 Mo maximum, aucune écriture effectuée.")
    return encoded
