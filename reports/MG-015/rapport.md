# MG-015 — Portable et installateur Windows x64

**19 novembre 2026 · Mon GPT<3 0.9.4 · CODEX_VM.**

**Livrables construits et recette VM terminée.** Arrêt pour la recette réelle sur Zenith Ice. Les deux binaires finaux, leurs runtimes et les captures ne sont pas commités.

## Fichiers à copier vers Zenith Ice

Répertoire exact sur CODEX_VM :

```text
C:\Users\codex\Documents\Projets\mon-gpt\dist\windows\0.9.4\
```

| Livrable | Taille exacte | SHA-256 |
|---|---:|---|
| `Mon-GPT-0.9.4-windows-x64.zip` | 30 872 831 octets | `7a7629631ba0bd3343a6f7611d10220e628845c3f2af27be7f463bc9aa27ed0e` |
| `Mon-GPT-0.9.4-windows-x64-setup.exe` | 26 518 619 octets | `9d30ef2d12a0b0f50dfc51158a9bf91163df76877f62629adb75a81b8150cac8` |

Copier aussi **`SHA256SUMS.txt`** depuis ce répertoire. [Copie des empreintes](SHA256SUMS.txt). `Mon-GPT/` est le dossier autonome non compressé ; `verification.json` contient l’inventaire SHA-256 de ses 1 045 fichiers et les contrôles PE. Les empreintes ci-dessus sont celles de la **seconde construction propre**, effectivement utilisée pour toute la recette finale.

Chemins complets des deux livrables :

```text
C:\Users\codex\Documents\Projets\mon-gpt\dist\windows\0.9.4\Mon-GPT-0.9.4-windows-x64.zip
C:\Users\codex\Documents\Projets\mon-gpt\dist\windows\0.9.4\Mon-GPT-0.9.4-windows-x64-setup.exe
```

## Construction et frontière respectée

Base propre sur `main`, synchronisée en avance rapide de `f36f351` à **`6a2e0ce`**, mission et `AGENTS.md` lus. Les scripts et rapports ML-020 de Ma Médiathèque et MB-004 de Mon Bureau ont été examinés en lecture seule : reprise du dossier PyInstaller autonome, du ZIP, du compilateur Inno et de l’installation par utilisateur, avec identité Windows stable et conservation des données.

**Aucun fichier applicatif sous `mon_gpt/` modifié**, aucun changement de modèle, stockage, schéma, navigation, import ou interface MG-014. Le Collector reste inchangé. Le petit `launcher.py` de distribution importe `mon_gpt.__main__.main` et maintient seulement le mutex Windows attendu par Inno. Les ressources sont copiées aux chemins que l’application trouve déjà via `__file__` ; aucune migration ni nouveau système de ressources.

[Commande de construction et guide](../../packaging/windows/README.md) :

```powershell
.\packaging\windows\build.ps1 `
  -PythonExe 'C:\Users\codex\AppData\Local\Programs\Python\Python313\python.exe' `
  -InnoCompiler 'C:\Users\codex\Documents\Projets\mon-gpt\.recette\MG015\tools\InnoSetup\ISCC.exe'
```

| Élément | Version / état constaté |
|---|---|
| Hôte | Windows 11 x64, build 26300 ; PowerShell 7.6.9 |
| Python embarqué | CPython 3.13.17 AMD64, 64 bits |
| Pillow | 13.0.0, wheel `cp313-cp313-win_amd64` |
| Tcl / Tk exécutés | 8.6.15 / 8.6.15 |
| PyInstaller | 6.22.3 |
| Hooks | pyinstaller-hooks-contrib 2026.10 |
| Autres dépendances de build | altgraph 0.17.5, packaging 26.3, pefile 2024.8.26, pywin32-ctypes 0.2.3, setuptools 84.2.1 |
| Inno Setup | 7.1.1 x64 ; compilateur officiel téléchargé depuis [la version amont](https://github.com/jrsoftware/issrc/releases/tag/is-7_1_1), signature `Valid`, signataire Pyrsys B.V. avant exécution |

Chaque construction a créé un venv, un cache PyInstaller et un staging uniques sous `build/windows/<GUID>`, installé les dépendances binaires épinglées avec `--no-deps`, exécuté `pip check`, puis assemblé et vérifié les artefacts. **Deux constructions propres réussies** ; aucun dossier temporaire de build ne reste après le `finally`. Les dossiers `dist/` et `.recette/` sont ignorés. La procédure est relançable ; les horodatages ne permettent pas de promettre des octets identiques entre deux builds.

La version vient de `mon_gpt/__init__.py` pour PyInstaller et Inno. Le build refuse un Python, compilateur ou Pillow inattendu. `verify_bundle.py` contrôle les vrais artefacts, leurs fichiers et l’archive finale avant publication locale.

## Métadonnées, icône et ressources

Les PE applicatif et installateur exposent **AMD64 / sous-système Windows GUI**, `ProductName=Mon GPT<3`, `CompanyName=Trucabule`, `ProductVersion=0.9.4`, `FileVersion=0.9.4.0`. La description est « Mon GPT<3 — Organisation locale des discussions » pour l’application, « Mon GPT<3 Setup » pour l’installateur.

L’ICO fourni a été utilisé **tel quel** :

```text
missions/MG-015-exe/Mon-GPT-robot.ico
SHA-256 : 038a2835eeefbecee5d859cabf2da24fb36cd3c124c9da7dbdb6255c9bdf8670
```

Ses **dix images d’icône** ont été retrouvées dans les ressources PE de l’EXE et du Setup, puis du désinstalleur installé, lui aussi x64. La copie ICO dans le paquet a la même empreinte. Les raccourcis et `UninstallDisplayIcon` visent l’EXE qui porte cette icône. La plume interne des fenêtres est conservée comme demandé. Aucun nouveau blob graphique versionné ; les deux références de David ne sont pas modifiées.

Le paquet contient **31 couvertures**, les notices locales MG-012, les avis effectifs CPython et Pillow, ainsi que le COPYING de PyInstaller avec son exception du bootloader. Les textes Python/Pillow effectivement embarqués correspondent intégralement aux références de MG-012 après normalisation des fins de ligne. Les ressources Tcl/Tk et les DLL Python/Pillow sont incluses ; `VCRUNTIME140.dll` et `VCRUNTIME140_1.dll` sont présents. Les fichiers, tailles et SHA-256 du ZIP correspondent au dossier produit. Aucun catalogue, préférences, image personnelle, test, rapport, mission, Collector ou `node_modules` dans la distribution.

**Note documentaire préservée :** le texte historique de l’onglet Périmètre MG-012 parle encore du lancement depuis les sources et d’un futur packaging. L’interface validée n’est pas remaniée ici ; `_internal/distribution/DISTRIBUTION.txt` explique la réalité du paquet autonome et `_internal/distribution/distribution-build.json` indique ses versions. Les versions réellement exécutées restent correctes dans l’écran. Aucune licence générale du code Trucabule n’est choisie ; cette livraison ne constitue pas un nouvel audit juridique des illustrations.

## Recette du ZIP final

ZIP final extrait dans :

```text
C:\Users\codex\Documents\Projets\mon-gpt\.recette\MG015\Portable espace et accents é\Mon-GPT\
```

Lancement réel de `Mon-GPT.exe` avec le témoin isolé `--data-dir "…\.recette\MG015\données témoin" --simulate-open`. Le processus reçoit un **PATH réduit à System32**, `PYTHONHOME` et `PYTHONPATH` volontairement inexistants. `where python.exe` et `where py.exe` échouent sur ce PATH. Les modules chargés `python313.dll`, `_tkinter.pyd`, `tcl86t.dll`, `tk86t.dll`, `_imaging`, `_imagingft` et `_imagingtk` proviennent tous du dossier `_internal` extrait, et non de l’installation Python du poste.

Contrôles dans la vraie interface, via le pilote Windows :

- Liste, Détaillée et Mosaïque ; recherche « Carnet personnel » ; sélection et inspecteur.
- Couvertures intégrées et image personnelle fictive, importée depuis une illustration locale déjà existante, sans création artistique.
- Création effective de **Projet portable MG-015**, retrouvée dans le catalogue.
- Sauvegarde complète depuis Fichier et le vrai dialogue Windows : `mon-gpt-sauvegarde.zip`, relue et validée ensuite avec **36 fiches et l’image personnelle**.
- Fenêtre Licences et crédits : versions Python/Tcl/Tk/Pillow et notice locale consultable sans lien externe. Aucun navigateur ni fil réel ouvert.
- Fermeture normale puis relance réelle : Mosaïque, recherche, scope, branche, fiche et aperçu retrouvés.

Les premières captures du pilote ont expiré ; une activation explicite de la fenêtre a rétabli le pilotage. La recette visuelle complète a ensuite été effectuée dans ce même exécutable du chemin accentué, sans contournement ni remplacement de pilote.

## Installation, mise à jour, désinstallation, réinstallation

L’installation réelle utilise le dossier fixe **`C:\Users\codex\AppData\Local\Programs\Mon GPT`**. Les journaux Inno indiquent **`User privileges: None`**, **`Administrative install mode: No`**, **`HKEY_CURRENT_USER`**, **64-bit install mode: Yes** ; le processus de recette n’est pas administrateur. Aucune élévation.

Le dossier standard `%LOCALAPPDATA%\MonGPT` était préexistant dans la VM : il n’a pas été utilisé pour la recette ni ouvert dans l’interface. Son catalogue et ses préférences sont restés identiques par contrôle privé d’empreinte ; **aucune empreinte ni donnée de cette bibliothèque réelle n’est publiée**. Le cycle utilise l’équivalent autorisé :

```text
C:\Users\codex\Documents\Projets\mon-gpt\.recette\MG015\profil témoin\MonGPT
```

Le raccourci Démarrer créé par Inno a été copié dans `.recette/`, en conservant cible, dossier de travail et icône, puis doté des seuls arguments `--data-dir` du témoin et `--simulate-open`. **Cette copie du vrai raccourci** a lancé le programme installé, sans risquer d’ouvrir le catalogue réel. L’utilisation du dossier standard par défaut est conservée dans l’entrée applicative inchangée ; le lancement sans arguments sur la bibliothèque réelle est réservé à David/ZI.

| Étape réelle | Résultat |
|---|---|
| Installation pendant que le portable est ouvert | Inno détecte le mutex, demande une fermeture normale, puis abandonne sur Annuler en mode silencieux. L’application reste active. Aucun arrêt forcé. |
| Première installation fermée | Code 0 ; raccourci Démarrer présent, Bureau absent. Entrée Windows unique : Mon GPT<3, Trucabule, 0.9.4, commande de désinstallation valide. |
| Lancement installé | Via la copie isolée du raccourci ; reprise du témoin et création effective de **Projet installé MG-015**. Puis fermeture normale. |
| Mise à jour / réinstallation du même paquet | Code 0. L’option Bureau a été explicitement sélectionnée pour cet essai ; raccourci Bureau créé. Les cinq fichiers témoins conservent tous leur SHA-256. |
| Désinstallation | Code 0 ; dossier applicatif, deux raccourcis et entrée de désinstallation retirés. Témoin, image, préférences et sauvegardes conservés, mêmes cinq empreintes. |
| Nouvelle installation | Code 0 ; seul raccourci Démarrer, Bureau de nouveau absent par défaut. Les données gardent leurs empreintes. |
| Reprise finale | Lancement réel par la copie du raccourci : deux projets créés durant la recette, recherche, Mosaïque, sélection, aperçu et image personnelle retrouvés. Après fermeture, les cinq fichiers sont toujours identiques. |

Les cinq fichiers suivis sont catalogue, préférences, image personnelle et deux sauvegardes. Le fichier de verrouillage est exclu des empreintes documentaires. Le témoin final compte **37 fiches : 30 discussions et 7 projets**. Les **1 045 fichiers installés correspondent tous** à l’inventaire du ZIP final. Le désinstalleur ne contient aucune instruction de suppression des données, et aucun fichier de données n’est installé sous le dossier applicatif.

État laissé sur la VM : application réinstallée et fermée, raccourci Démarrer présent, Bureau absent ; données standard intactes, témoin et preuves conservés sous `.recette/MG015/`.

## Tests et preuves

- **L3 : `python -m unittest discover -s tests -v` exécuté une seule fois, 205 tests réussis en 157,027 s**, sur le code applicatif final inchangé. [Journal intégral](tests-python.txt).
- Syntaxe Python des scripts de packaging, analyse du script PowerShell, compilation Inno, `pip check`, vérification des PE, des dix images ICO, du ZIP et des ressources, comparaison complète de l’installation et contrôle des empreintes du témoin.
- [Bilan machine lisible](bilan-verifications.json) : artefacts, versions PE, signatures, runtime chargé, cycle et empreintes **exclusivement fictives**.
- Les tests JS du Collector ne sont **pas rejoués** : aucun de ses fichiers, dépendances ou frontières n’est touché. Pas de nouveau test recopiant des constantes de présentation ; le contrôle ajouté lit les vrais artefacts produits.
- Le cycle Inno est une **installation Windows réelle en ligne de commande silencieuse**, pas une simulation de fichiers. Les applications lancées ont ensuite été contrôlées dans leur vraie interface. Les interfaces Paramètres et recherche du menu Démarrer ne sont pas déclarées testées ; l’inscription HKCU et les fichiers `.lnk` ont été vérifiés.

Captures Windows natives **locales, non versionnées**, conformément à l’interdiction de nouveaux blobs :

```text
C:\Users\codex\Documents\Projets\mon-gpt\.recette\MG015\captures\
01-portable-liste.png
02-portable-detaillee.png
03-portable-mosaique-inspecteur.png
04-portable-runtimes.png
05-portable-notices.png
06-portable-reprise.png
07-installe-temoin.png
08-installe-reprise-apres-reinstallation.png
```

Les journaux détaillés de build et Inno restent aussi sous `.recette/MG015/`. Les données réelles et contrôles privés n’en sortent pas. Les deux builds et la recette n’ont produit aucune modification des dépôts sources de référence.

## Signature, limites et STOP

`Get-AuthenticodeSignature` retourne **NotSigned** pour l’EXE et le Setup finaux. Aucun certificat acheté, configuré ou ajouté. Aucun test ne permet d’affirmer que SmartScreen ne réagira pas à une copie ou à un téléchargement marqué Internet.

La VM possède Python : son exclusion du PATH et les DLL effectivement chargées démontrent l’autonomie de ce paquet, mais **un poste réellement dépourvu de Python n’a pas été utilisé ici**. Le test Windows 10, l’absence de tout prérequis externe sur un poste propre, le cycle interactif complet de l’assistant et le comportement SmartScreen restent à confirmer sur la cible. **La recette Zenith Ice demandée est la prochaine validation humaine**, pas une validation annoncée à distance.

Scripts, documentation, résultats et rapport sont publiés avec **Trucabule-M1 / Marcel**, identité Git **`Trucabule-M1 <marcel@trucabule.fr>`**. Les binaires finaux ne sont pas commités, aucune Release ni diffusion publique des exécutables créée. **STOP après MG-015 pour recette sur ZI.**
