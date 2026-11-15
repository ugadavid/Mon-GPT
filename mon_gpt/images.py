"""Copies locales d’images vérifiées ; noms immuables dérivés du contenu."""
import hashlib
import io
import os
from pathlib import Path
import tempfile
import warnings
from PIL import Image, ImageOps, UnidentifiedImageError
from .identity import ASSET, COVERS

MAX_BYTES=20*1024*1024
MAX_EDGE=8192
MAX_PIXELS=24_000_000
IMPORT_HINT="PNG, JPG/JPEG, WebP · conseillé 1200 × 675 · 20 Mo max., côté ≤ 8192 px, 24 Mpx max."
PACK=Path(__file__).parent/"assets"/"covers"


def checked_image(data):
    if not data or len(data)>MAX_BYTES:
        raise ValueError("Image vide ou trop volumineuse : 20 Mo maximum.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error",Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as probe:
                if probe.format not in {"PNG","JPEG","WEBP"}:
                    raise ValueError("Format réel non pris en charge : PNG, JPG/JPEG ou WebP attendu.")
                w,h=probe.size
                if min(w,h)<16 or max(w,h)>MAX_EDGE or w*h>MAX_PIXELS:
                    raise ValueError("Dimensions refusées : 16 px minimum, 8192 px par côté et 24 Mpx maximum.")
                if getattr(probe,"n_frames",1)!=1:
                    raise ValueError("Choisissez une image fixe, sans animation.")
                probe.verify()
            with Image.open(io.BytesIO(data)) as image:
                image.load()
                return ImageOps.exif_transpose(image).convert("RGBA")
    except (UnidentifiedImageError,OSError,SyntaxError,Image.DecompressionBombError,Image.DecompressionBombWarning) as exc:
        raise ValueError("Image illisible, endommagée ou dimensions excessives.") from exc


def check_asset(reference,data):
    match=ASSET.fullmatch(reference)
    if not match or hashlib.sha256(data).hexdigest()!=match[1]:
        raise ValueError("Image de sauvegarde incohérente : empreinte incorrecte.")
    image=checked_image(data)
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Une ressource interne doit être au format PNG.")
    return image


class ImageLibrary:
    def __init__(self,directory):
        self.directory=Path(directory)

    def path(self,reference):
        match=ASSET.fullmatch(reference)
        if not match: raise ValueError("Référence d’image personnelle invalide.")
        path=self.directory/(match[1]+".png")
        if self.directory.is_symlink() or path.is_symlink():
            raise ValueError("Dossier ou ressource symbolique refusé.")
        return path

    def put(self,reference,data):
        check_asset(reference,data)
        path=self.path(reference)
        self.directory.mkdir(parents=True,exist_ok=True)
        if path.exists():
            if path.read_bytes()!=data: raise ValueError("Ressource existante incohérente, conservée sans écrasement.")
            return
        name=None
        try:
            with tempfile.NamedTemporaryFile(dir=self.directory,delete=False) as f:
                name=f.name;f.write(data);f.flush();os.fsync(f.fileno())
            os.replace(name,path)
        finally:
            if name and os.path.exists(name): os.unlink(name)

    def import_file(self,path):
        with open(path,"rb") as f: data=f.read(MAX_BYTES+1)
        image=checked_image(data)
        image.thumbnail((2400,2400),Image.Resampling.LANCZOS)
        stream=io.BytesIO()
        image.save(stream,format="PNG")
        data=stream.getvalue()
        if len(data)>MAX_BYTES: raise ValueError("Image normalisée trop volumineuse : 20 Mo maximum.")
        reference="asset:"+hashlib.sha256(data).hexdigest()
        self.put(reference,data)
        return reference

    def read(self,reference):
        with self.path(reference).open("rb") as f: data=f.read(MAX_BYTES+1)
        check_asset(reference,data)
        return data

    def open(self,reference):
        if reference.startswith("pack:") and reference[5:] in COVERS:
            with Image.open(PACK/(reference[5:]+".jpg")) as image: return image.convert("RGBA")
        return check_asset(reference,self.read(reference))
