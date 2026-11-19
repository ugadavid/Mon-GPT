# Construire et utiliser Mon GPT<3 sous Windows x64

## Utiliser les livrables

- **Portable** : extraire entièrement `Mon-GPT-0.9.4-windows-x64.zip`, puis ouvrir `Mon-GPT\Mon-GPT.exe`. Conserver `_internal` à côté de l’EXE. Aucun Python, pip ou environnement virtuel externe n’est nécessaire.
- **Installateur** : exécuter `Mon-GPT-0.9.4-windows-x64-setup.exe`. Installation pour le compte courant, sans droits administrateur, dans `%LOCALAPPDATA%\Programs\Mon GPT`. Le raccourci **Mon GPT** est créé dans le menu Démarrer ; celui du Bureau est facultatif, décoché initialement. Le lancement final est optionnel. Les caractères `<` et `>` du nom du produit ne sont pas permis dans un nom de fichier Windows : les raccourcis utilisent donc « Mon GPT ».

« Portable » désigne les binaires transportables : les données restent **`%LOCALAPPDATA%\MonGPT`**, même avec le ZIP. Les deux formes partagent donc le même catalogue et les mêmes préférences. L’option existante `--data-dir "C:\chemin\témoin"` permet une recette isolée. Ne pas placer un catalogue dans le dossier des binaires. Sauvegarder depuis **Fichier → Sauvegarder le catalogue…** produit une archive complète avec les images personnelles.

Fermer Mon GPT normalement avant mise à jour, désinstallation ou changement de forme. Le binaire maintient un mutex ; Inno demande sa fermeture tant qu’il existe. L’installateur ne force pas l’arrêt et ne redémarre pas automatiquement l’application pendant une mise à jour. Réinstaller une version conserve l’identité Windows de l’application. **Ne pas changer l’AppId stable de `setup.iss`** pour les versions suivantes.

La désinstallation retire les fichiers installés, ses raccourcis et l’entrée Windows, **sans supprimer `%LOCALAPPDATA%\MonGPT`**. Une réinstallation retrouve ce dossier au prochain lancement. L’installateur refuse un dossier différent du dossier applicatif fixé ; aucun fichier ni script de suppression ne cible les données utilisateur.

Les binaires ne sont **pas signés**. SmartScreen peut réagir selon le poste et la provenance ; aucune absence d’avertissement n’est garantie. Les empreintes sont fournies dans `SHA256SUMS.txt`. La recette sur Zenith Ice reste à effectuer avant diffusion.

## Construire depuis les sources

Prérequis de fabrication, uniquement sur le poste de build : **Windows x64**, **CPython 3.13.17 x64 avec Tcl/Tk**, **PowerShell 7** et **Inno Setup 7.1.1 x64**. Les versions sont vérifiées avant assemblage. Installer le compilateur officiel selon ses conditions ; aucun téléchargement ni installation d’Inno n’est effectué par le script de build.

Depuis la racine du dépôt :

```powershell
.\packaging\windows\build.ps1 `
  -PythonExe 'C:\Users\codex\AppData\Local\Programs\Python\Python313\python.exe' `
  -InnoCompiler 'C:\chemin\Inno Setup 7\ISCC.exe'
```

Remplacer le chemin du compilateur par celui de l’installation locale. Pour reproduire la recette sur **CODEX_VM**, ce chemin est :

```text
C:\Users\codex\Documents\Projets\mon-gpt\.recette\MG015\tools\InnoSetup\ISCC.exe
```

Le script crée un venv unique sous `build/windows/<GUID>`, installe exclusivement les versions binaires épinglées de `requirements-build.txt`, sans dépendances implicites non épinglées, puis exécute `pip check`. Un cache PyInstaller propre est utilisé à chaque construction. La version vient de `mon_gpt/__init__.py` pour PyInstaller et Inno ; la version numérique Windows est `0.9.4.0`. Le Pillow installé doit correspondre exactement au manifeste applicatif. Le script ne réutilise pas un ancien dossier de travail et supprime son venv/cache/intermédiaires dans `finally`, après contrôle des chemins absolus.

PyInstaller construit un dossier autonome, suivant ML-020. `launcher.py` importe l’entrée de package existante pour préserver les imports relatifs et crée seulement le mutex de distribution utilisé par Inno, suivant le principe MB-004. Il ne modifie ni stockage, ni données, ni logique métier. Les chemins `__file__` existants de l’application trouvent les ressources placées à leur emplacement habituel dans `_internal` : aucune adaptation des modèles ou de l’interface n’est nécessaire.

Sorties dans `dist/windows/0.9.4/` :

```text
Mon-GPT/                                  Dossier autonome complet
Mon-GPT-0.9.4-windows-x64.zip               Livrable portable
Mon-GPT-0.9.4-windows-x64-setup.exe         Livrable installateur
SHA256SUMS.txt                             Empreintes des deux livrables
verification.json                         Contrôles PE et inventaire des fichiers
```

Le contrôle final lit les vrais PE, leurs versions et leurs ressources d’icônes ; compare les couvertures et notices aux sources ; refuse les données utilisateur, tests, missions, rapports et Collector dans le paquet ; vérifie le contenu et les empreintes de chaque fichier du ZIP. Les fichiers installés peuvent ensuite être comparés à cet inventaire. Les sorties ne sont publiées qu’après réussite de ces contrôles. Une reconstruction est reproductible en procédure, **pas promise identique octet pour octet** : horodatages et outils peuvent changer les empreintes.

L’ICO fourni `missions/MG-015-exe/Mon-GPT-robot.ico` est utilisé tel quel pour EXE, Setup et raccourcis. Une copie exacte n’existe que dans les artefacts ignorés. Aucun nouveau visuel n’est créé ou versionné. La plume interne de l’interface est conservée, conformément au périmètre MG-015.

## Notices et inventaire

Le paquet inclut les notices de CPython, de la wheel Pillow et du bootloader PyInstaller, dont son exception de redistribution. Les textes MG-012 restent disponibles dans **Aide → Licences et crédits** et dans `_internal/mon_gpt/notices`. Les notices effectives de fabrication sont sous `_internal/licenses`, les versions sous `_internal/distribution/distribution-build.json`.

L’écran MG-012 garde son texte historique décrivant le lancement depuis les sources ; **pour le paquet autonome, Python et Tcl/Tk sont embarqués**. `_internal/distribution/DISTRIBUTION.txt` explique cette différence, sans modifier l’interface validée. Le script vérifie aussi que les textes complets Python/Pillow embarqués correspondent aux références locales. Aucune licence générale du code Trucabule n’est ajoutée, ni aucun droit supposé sur les illustrations.

Ne pas committer `dist/`, `build/`, `.recette/`, les exécutables, archives, runtimes ou captures de MG-015. Les seules ressources graphiques de référence de cette mission sont les fichiers déjà déposés par David. [Rapport de recette](../../reports/MG-015/rapport.md).
