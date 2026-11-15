"""Produire le seul dossier à charger dans Chrome, sans dépendance Python."""
from pathlib import Path
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "companions" / "chatgpt-collector"
FILES = (
    "manifest.json", "core/observations.js", "adapters/chatgpt.js",
    "browser/background.js", "browser/content.js", "browser/repository.js", "browser/runtime.js",
    "ui/popup.html", "ui/popup.css", "ui/popup.js", "ui/presentation.js",
    "assets/mark.svg", "assets/icon16.png", "assets/icon32.png", "assets/icon48.png", "assets/icon128.png",
)


def package():
    version = json.loads((SOURCE / "manifest.json").read_text(encoding="utf-8"))["version"]
    if not all(part.isdigit() for part in version.split(".")):
        raise ValueError("Version invalide")
    destination = ROOT / "dist" / f"Mon-GPT-Collector-{version}"
    # N’effacer aucun dossier existant. Un livrable pollué est refusé explicitement.
    if destination.is_symlink():
        raise ValueError("Le dossier de distribution ne doit pas être un lien")
    if destination.exists():
        for path in destination.rglob("*"):
            relative = path.relative_to(destination).as_posix()
            if path.is_symlink() or (path.is_file() and relative not in FILES) or (path.is_dir() and not any(f.startswith(relative + "/") for f in FILES)):
                raise ValueError(f"Élément inattendu dans la distribution : {relative}")
    for relative in FILES:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / relative, target)
    archive = destination.parent / (destination.name + ".zip")
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for relative in sorted(FILES):
            info = zipfile.ZipInfo(relative, (2026, 11, 15, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            output.writestr(info, (destination / relative).read_bytes())
    print(json.dumps({"folder": str(destination), "archive": str(archive), "files": len(FILES), "bytes": sum((destination / f).stat().st_size for f in FILES), "zipBytes": archive.stat().st_size}, ensure_ascii=False))


if __name__ == "__main__":
    package()
