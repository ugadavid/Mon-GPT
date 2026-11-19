"""Application en dossier, comme ML-020 ; ressources à leurs chemins existants."""
import json
import platform
import sys
from importlib.metadata import distribution,version as package_version
from pathlib import Path
from runpy import run_path
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.config import CONF
from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo,StringFileInfo,StringStruct,StringTable,VarFileInfo,VarStruct,VSVersionInfo,
)

root=Path(SPECPATH).resolve().parents[1]
package=root/'mon_gpt'
version=run_path(str(package/'__init__.py'))['__version__']
numeric=tuple(int(n) for n in version.split('.'))+(0,)
icon=root/'missions/MG-015-exe/Mon-GPT-robot.ico'
runtime=Path(sys.base_prefix)
metadata=VSVersionInfo(
    ffi=FixedFileInfo(filevers=numeric,prodvers=numeric,fileType=1),
    kids=[StringFileInfo([StringTable('040c04b0',[
        StringStruct('CompanyName','Trucabule'),
        StringStruct('FileDescription','Mon GPT<3 — Organisation locale des discussions'),
        StringStruct('FileVersion','.'.join(map(str,numeric))),
        StringStruct('InternalName','Mon-GPT'),
        StringStruct('OriginalFilename','Mon-GPT.exe'),
        StringStruct('ProductName','Mon GPT<3'),
        StringStruct('ProductVersion',version),
    ])]),VarFileInfo([VarStruct('Translation',[0x040C,1200])])],
)
notices=[(str(runtime/'LICENSE.txt'),'licenses/CPython')]
for terms in (runtime/'tcl').rglob('license.terms'):
    if 'demos' not in terms.parts:
        notices.append((str(terms),'licenses/'+str(terms.parent.relative_to(runtime/'tcl'))))
for name in ('Pillow','PyInstaller'):
    dist=distribution(name)
    for path in dist.files or []:
        if path.name.lower().startswith(('license','copying','notice')):
            # Le COPYING de PyInstaller conserve l'exception du bootloader.
            notices.append((str(dist.locate_file(path)),f'licenses/{name}'))
datas=[(str(package/'assets/covers'),'mon_gpt/assets/covers')]
datas.extend((str(p),'mon_gpt/notices') for p in (package/'notices').iterdir() if p.suffix in ('.txt','.json','.md'))
datas.extend(notices)
datas.extend([(str(icon),'distribution'),(str(Path(SPECPATH)/'DISTRIBUTION.txt'),'distribution')])
build_info=Path(CONF['workpath'])/'distribution-build.json'
build_info.parent.mkdir(parents=True,exist_ok=True)
build_info.write_text(json.dumps({
    'product':'Mon GPT<3','version':version,'python':platform.python_version(),
    'machine':platform.machine(),'packages':{n:package_version(n) for n in ('Pillow','PyInstaller','pyinstaller-hooks-contrib')},
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
datas.append((str(build_info),'distribution'))
a=Analysis([str(Path(SPECPATH)/'launcher.py')],pathex=[str(root)],datas=datas,
           hiddenimports=collect_submodules('mon_gpt'),
           excludes=['unittest','pytest','tkinter.test'],noarchive=False)
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='Mon-GPT',console=False,
        icon=str(icon),version=metadata,upx=False)
coll=COLLECT(exe,a.binaries,a.datas,name='Mon-GPT',upx=False)
