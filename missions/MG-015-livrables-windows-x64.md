# MG-015 — Livrables Windows x64 : portable + installateur

**GO réalisation — 19 novembre 2026.**  
Point de départ : `origin/main` après la clôture graphique MG-014.  
Version applicative à empaqueter : **0.9.4**.

## Objectif

Transformer Mon GPT<3 en une vraie application Windows autonome que David puisse :

1. copier depuis CODEX_VM vers Zenith Ice ;
2. lancer sans Python installé séparément ;
3. installer proprement pour son compte Windows ;
4. mettre à jour / désinstaller / réinstaller **sans perdre son catalogue utilisateur**.

Cette mission livre **deux artefacts Windows x64** :
- un **ZIP portable** ;
- un **installateur Inno Setup**.

Nous capitalisons explicitement sur deux précédents Trucabule déjà éprouvés :
- **Ma Médiathèque / ML-020** : PyInstaller + Inno Setup + ZIP portable + SHA-256 ;
- **Mon Bureau / MB-004** : installation par utilisateur sous `%LOCALAPPDATA%\Programs`, raccourci Démarrer, cycle mise à jour/désinstallation/réinstallation en préservant les données.

Ne pas réinventer un nouveau système de packaging si ces solutions conviennent.

## 1. Frontière fonctionnelle

**Aucun changement fonctionnel de Mon GPT<3.**

Ne pas modifier :
- modèle métier ;
- stockage ;
- navigation ;
- import Collector ;
- interface graphique validée MG-014 ;
- règles de données ;
- schéma du catalogue.

Les seuls changements applicatifs acceptables sont ceux strictement nécessaires à :
- afficher les bonnes métadonnées/version dans le binaire ;
- localiser les ressources embarquées sous PyInstaller ;
- afficher une icône Windows cohérente ;
- assurer le fonctionnement autonome du paquet.

Si un problème de packaging révèle un bug applicatif réel, le documenter ; ne pas élargir la mission en silence.

## 2. Données utilisateur : séparation absolue

Le comportement existant est correct et doit rester la règle :

`%LOCALAPPDATA%\MonGPT`

contient les données utilisateur :
- `catalogue.json` ;
- `interface.json` et préférences ;
- ressources personnelles sous `images` ;
- sauvegardes / fichiers de migration / import éventuels.

Les binaires installés doivent vivre séparément, par exemple :

`%LOCALAPPDATA%\Programs\Mon GPT`

### Invariants

- l’installateur **ne doit jamais embarquer ni écraser** un catalogue utilisateur ;
- une mise à jour ne touche pas au dossier `%LOCALAPPDATA%\MonGPT` ;
- la désinstallation supprime l’application et ses raccourcis, **pas les données utilisateur** ;
- la réinstallation retrouve les données précédentes au lancement ;
- le ZIP portable utilise lui aussi par défaut `%LOCALAPPDATA%\MonGPT`, conformément à `__main__.py`.

Les recettes avec données doivent utiliser un catalogue témoin isolé ou, pour la recette de reprise standard, une copie contrôlée. Ne jamais publier de vraies données utilisateur.

## 3. Architecture de build recommandée

Créer un dossier clair, par exemple :

`packaging/windows/`

avec au minimum :
- un fichier PyInstaller `.spec` ;
- `requirements-build.txt` ;
- `build.ps1` ;
- un script Inno Setup `.iss`.

### PyInstaller

Construire une application **Windows x64 autonome, sans console**.

Inclure explicitement :
- package `mon_gpt` ;
- Pillow ;
- runtime Python ;
- Tcl/Tk nécessaires à Tkinter ;
- `mon_gpt/assets/covers/**` ;
- `mon_gpt/notices/**` et tout texte licence consulté hors ligne ;
- autres ressources réellement requises par l’application.

Ne pas inclure :
- tests ;
- rapports ;
- missions ;
- données utilisateur ;
- Collector Chrome sauf si une dépendance applicative réelle l’exige (a priori non).

### Icône Windows

Mon GPT<3 doit avoir une icône Windows cohérente avec son identité actuelle.

- privilégier le **repère plume/feather déjà utilisé dans l’application** ;
- ne pas inventer une nouvelle marque graphique ;
- produire un `.ico` multi-tailles si nécessaire pour l’EXE, l’installateur et les raccourcis ;
- si cela impose de redessiner une nouvelle identité, s’arrêter sur ce point et utiliser une solution neutre plutôt que lancer une mission graphique.

### Métadonnées du binaire

L’exécutable et l’installateur doivent exposer :
- ProductName : `Mon GPT<3` ;
- Publisher / Company : `Trucabule` ;
- ProductVersion : `0.9.4` ;
- FileVersion compatible Windows ;
- description cohérente.

La version applicative et les métadonnées de distribution doivent provenir d’une source commune ou être contrôlées automatiquement pour éviter les divergences.

## 4. Livrables attendus

Structure de sortie recommandée :

`dist/windows/0.9.4/`

### Portable

Un ZIP du type :

`Mon-GPT-0.9.4-windows-x64.zip`

Il contient un dossier autonome avec :
- `Mon-GPT.exe` ;
- son dossier interne / runtime nécessaire ;
- toutes les ressources nécessaires.

Après extraction, l’application doit fonctionner sans installation.

### Installateur

Un installateur du type :

`Mon-GPT-0.9.4-windows-x64-setup.exe`

ou convention équivalente claire.

Installation :
- **par utilisateur**, sans élévation administrative ;
- architecture Windows x64 ;
- dossier fixe sous `%LOCALAPPDATA%\Programs\Mon GPT` ;
- raccourci **Menu Démarrer** ;
- raccourci Bureau proposé mais **décoché par défaut** ;
- entrée de désinstallation Windows ;
- lancement optionnel à la fin de l’installation.

### Empreintes

Générer :

`SHA256SUMS.txt`

pour au minimum le ZIP et l’installateur final.

## 5. Inno Setup

Capitaliser sur les scripts ML-020 / MB-004 :

- Inno Setup 7.1.1 x64 si disponible sur CODEX_VM ;
- `PrivilegesRequired=lowest` ;
- installation sous `{localappdata}\Programs\Mon GPT` ;
- architecture x64 ;
- Wizard moderne ;
- compression LZMA2 ;
- raccourci Démarrer ;
- Bureau optionnel ;
- désinstallation propre.

Prévoir un comportement raisonnable si Mon GPT<3 est ouvert pendant une mise à jour :
- éviter d’écraser des binaires en cours d’utilisation ;
- demander une fermeture normale plutôt que forcer le processus.

Pas de suppression du dossier de données utilisateur lors de la désinstallation.

## 6. Signature / SmartScreen

Aucun certificat de signature de code n’est prévu dans cette mission.

- vérifier et documenter `Get-AuthenticodeSignature` ;
- accepter un résultat `NotSigned` ;
- ne pas acheter/configurer de certificat ;
- ne pas prétendre que SmartScreen ne réagira pas.

La signature pourra faire l’objet d’une décision séparée plus tard.

## 7. Recette Windows — cette fois une vraie recette de distribution

Cette mission est un **jalon de distribution majeur** : elle relève du niveau **L3** de `AGENTS.md`.

### 7.1 Suite applicative

Lancer la suite complète :
`python -m unittest discover -s tests -v`

Une seule fois sur l’état final à empaqueter, sauf correction ultérieure touchant le code.

### 7.2 ZIP portable

Depuis un dossier de recette distinct :
- extraire le ZIP dans un chemin contenant espaces et accents ;
- lancer `Mon-GPT.exe` ;
- vérifier que Python/py ne sont pas nécessaires au lancement ;
- vérifier les trois vues, inspecteur, recherche, création, sauvegarde, illustrations, licences/crédits ;
- vérifier la version affichée ;
- fermer et relancer ;
- vérifier persistance dans le dossier de données témoin.

### 7.3 Installateur

Installer sous un compte standard :
- vérifier absence d’élévation ;
- vérifier dossier d’installation ;
- raccourci Démarrer ;
- raccourci Bureau seulement si demandé ;
- entrée de désinstallation ;
- lancement par le raccourci.

### 7.4 Mise à jour / désinstallation / réinstallation

Effectuer un cycle témoin inspiré de MB-004 / ML-020 :
1. installation ;
2. création ou modification de données fictives ;
3. réinstallation / mise à jour du même numéro ou build de recette si nécessaire ;
4. vérification que les données restent intactes ;
5. désinstallation ;
6. vérifier que les binaires/raccourcis sont retirés mais que `%LOCALAPPDATA%\MonGPT` (ou son équivalent de recette) est conservé ;
7. réinstallation ;
8. vérifier reprise des mêmes données.

Utiliser des empreintes SHA-256 du catalogue / ressources témoins pour prouver qu’une désinstallation n’a pas supprimé ou altéré les données.

### 7.5 Ressources / licences

Vérifier dans le binaire final :
- couvertures intégrées ;
- images personnelles de recette ;
- fenêtre Aide → Licences et crédits ;
- notices locales réellement consultables hors connexion ;
- Pillow / Tcl / Tk / Python correctement inclus.

## 8. Build reproductible et propre

Le script de build doit :
- construire depuis un environnement propre / venv temporaire ;
- épingler les dépendances de build réellement nécessaires ;
- vérifier Windows x64 ;
- vérifier la version d’Inno Setup utilisée ;
- créer ses dossiers temporaires sous un chemin dédié et les supprimer en fin de build ;
- ne pas dépendre d’artefacts oubliés d’un précédent build ;
- pouvoir être relancé avec une commande documentée dans le README.

Les artefacts lourds générés peuvent être ignorés par Git si approprié ; ne pas versionner inutilement le runtime PyInstaller complet.

## 9. README et rapport

Mettre à jour le README avec :
- comment construire ;
- où trouver les artefacts ;
- distinction ZIP portable / installateur ;
- emplacement des données utilisateur ;
- statut non signé.

Créer :
`reports/MG-015/rapport.md`

Le rapport doit fournir :
- environnement exact de build ;
- versions Python / PyInstaller / Pillow / Inno Setup ;
- noms, tailles et SHA-256 des livrables ;
- métadonnées Windows vérifiées ;
- résultats de la recette portable ;
- résultats installation / désinstallation / réinstallation ;
- persistance des données ;
- signature ;
- limites éventuelles.

Quelques captures utiles suffisent.

## 10. Publication GitHub — Marcel

Publier code, scripts et rapport avec **Marcel / `Trucabule-M1`**.

Avant publication :
- `gh auth status` : Marcel actif ;
- identité Git locale : `Trucabule-M1 <marcel@trucabule.fr>`.

Les binaires finaux ne doivent pas être commités dans le dépôt sauf décision explicite déjà prévue par le projet. Donner dans le rapport **leur chemin local exact sur CODEX_VM** pour que David puisse les copier vers Zenith Ice.

Commit/push `origin/main`, SHA distant vérifié, dépôt propre.

**STOP après livraison pour recette réelle sur Zenith Ice.**

## Critère d’acceptation

David doit pouvoir prendre le ZIP ou l’installateur depuis CODEX_VM, le copier sur Zenith Ice, lancer/installer Mon GPT<3 0.9.4 sans environnement Python, retrouver ses données dans `%LOCALAPPDATA%\MonGPT`, puis mettre à jour ou désinstaller l’application sans perdre ce catalogue.
