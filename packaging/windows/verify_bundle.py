"""Contrôle des vrais fichiers produits, pas des constantes du script de build."""
import hashlib
import json
from pathlib import Path
from runpy import run_path
import struct
import sys
import zipfile
import pefile


ROOT=Path(__file__).resolve().parents[2]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def icon_hashes(path):
    data=path.read_bytes();reserved,kind,count=struct.unpack_from('<HHH',data)
    assert reserved==0 and kind==1 and count>0
    return {hashlib.sha256(data[offset:offset+size]).hexdigest()
            for size,offset in (struct.unpack_from('<II',data,6+n*16+8) for n in range(count))}


def inspect_pe(path,expected_icons,version):
    with pefile.PE(str(path)) as pe:
        assert pe.FILE_HEADER.Machine==0x8664,f'PE non AMD64 : {path}'
        assert pe.OPTIONAL_HEADER.Subsystem==2,f'Console inattendue : {path}'
        fields={}
        for group in pe.FileInfo:
            for entry in group:
                for table in getattr(entry,'StringTable',[]):
                    fields.update({k.decode():v.decode().strip('\0 ') for k,v in table.entries.items()})
        for key,value in {'CompanyName':'Trucabule','ProductName':'Mon GPT<3','ProductVersion':version,'FileVersion':version+'.0'}.items():
            assert fields.get(key)==value,(str(path),key,fields.get(key),value)
        frames=set()
        for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries:
            if entry.id==pefile.RESOURCE_TYPE['RT_ICON']:
                for item in entry.directory.entries:
                    for language in item.directory.entries:
                        record=language.data.struct
                        frames.add(hashlib.sha256(pe.get_data(record.OffsetToData,record.Size)).hexdigest())
        assert expected_icons.issubset(frames),f'Images ICO absentes de {path}'
        return {'file':path.name,'machine':'AMD64','subsystem':'Windows GUI','metadata':fields,'reference_icon_frames':len(expected_icons)}


def verify(application,setup,archive):
    version=run_path(str(ROOT/'mon_gpt/__init__.py'))['__version__']
    reference=ROOT/'missions/MG-015-exe/Mon-GPT-robot.ico'
    expected_icons=icon_hashes(reference)
    binaries=[inspect_pe(p,expected_icons,version) for p in (application/'Mon-GPT.exe',setup)]
    internal=application/'_internal'
    assert sha(internal/'distribution/Mon-GPT-robot.ico')==sha(reference)
    for directory in ('assets/covers','notices'):
        for path in (ROOT/'mon_gpt'/directory).iterdir():
            if path.suffix in ('.jpg','.txt','.json','.md'):
                assert sha(path)==sha(internal/'mon_gpt'/directory/path.name),str(path)
    names=[str(p.relative_to(application)).replace('\\','/') for p in application.rglob('*') if p.is_file()]
    for marker in ('python313.dll','_tkinter.pyd','tcl86t.dll','tk86t.dll','base_library.zip'):
        assert any(Path(n).name.lower()==marker for n in names),f'Runtime absent : {marker}'
    assert any(Path(n).name.startswith('_imaging.') for n in names),'Pillow absent'
    for forbidden in ('catalogue.json','interface.json'):
        assert not any(Path(n).name==forbidden for n in names),f'Donnée embarquée : {forbidden}'
    assert not any(set(n.split('/')) & {'missions','reports','companions','tests','node_modules'} for n in names)
    copying=list((internal/'licenses/PyInstaller').glob('*'))
    assert copying and any('exception' in p.read_text(encoding='utf-8',errors='replace').lower() for p in copying)
    assert (internal/'licenses/CPython/LICENSE.txt').is_file()
    assert (internal/'licenses/Pillow/LICENSE').is_file()
    for bundled,reference_notice in (('CPython/LICENSE.txt','python-3.13.17-windows.txt'),('Pillow/LICENSE','pillow-13.0.0-windows.txt')):
        original=(internal/'licenses'/bundled).read_text(encoding='utf-8').rstrip('\n')+'\n'
        assert original==(internal/'mon_gpt/notices'/reference_notice).read_text(encoding='utf-8'),f'Notice de référence divergente : {bundled}'
    with zipfile.ZipFile(archive) as z:
        expected={'Mon-GPT/'+n for n in names}
        assert {n for n in z.namelist() if not n.endswith('/')}==expected,'Contenu ZIP divergent'
        for name in names:
            assert hashlib.sha256(z.read('Mon-GPT/'+name)).hexdigest()==sha(application/name),name
    inventory=[{'path':n,'size':(application/n).stat().st_size,'sha256':sha(application/n)} for n in sorted(names)]
    return {'version':version,'binaries':binaries,'covers':len(list((internal/'mon_gpt/assets/covers').glob('*.jpg'))),
            'icon_sha256':sha(reference),'archive':{'file':archive.name,'size':archive.stat().st_size,'sha256':sha(archive)},
            'setup':{'file':setup.name,'size':setup.stat().st_size,'sha256':sha(setup)},'files':inventory}


if __name__=='__main__':
    application,setup,archive=map(lambda value:Path(value).resolve(),sys.argv[1:])
    result=verify(application,setup,archive)
    (setup.parent/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"Paquet vérifié : {result['version']}, {result['covers']} couvertures, {len(result['files'])} fichiers.")
