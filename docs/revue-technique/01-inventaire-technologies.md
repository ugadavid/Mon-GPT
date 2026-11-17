# 01 — Inventaire initial des technologies et bibliothèques

**Mon GPT<3 0.9.4 / Collector 0.8.2 — relevé du 17 novembre 2026.**

**Méthode :** faits relevés dans `requirements.txt`, `package.json`, `manifest.json` et le code ; les justifications comparatives sont **nos hypothèses d'analyse**, non des motivations historiques vérifiées. Ce tableau est volontairement simple et sera complété par une étude des API réellement appelées.

**Portée de ce chapitre : Mon GPT<3 seulement.** L'étude Trucabule porte désormais sur **six produits** : Mon GPT<3, Ma Médiathèque, Mon Bureau, Chrome Organizer, Mon Aise et Ma Capture (en conception). Voir la [vision du portefeuille](02-vision-trucabule-et-mutualisation.md) et la [matrice fonctionnelle des six produits](03-cartographie-fonctionnelle-trucabule.md). Les dépendances des autres applications ne sont pas confondues avec celles de Mon GPT<3.

## Vue d'ensemble

| Technologie | Usage constaté dans Mon GPT<3 | Pourquoi ce choix peut être pertinent plutôt que son voisin (à confirmer) | Alternative / question à examiner | Documentation officielle |
| --- | --- | --- | --- | --- |
| **Python** (3.13 utilisé en recette Windows ; version non figée dans `requirements.txt`) | Moteur local, fiches et projets, recherche, import, opérations groupées, lancement | Lisibilité, rapidité d'itération, riche bibliothèque standard ; pas besoin du runtime .NET pour ce projet | C#, Go ou autre ne sont pas justifiés à ce stade : quel bénéfice mesurable ? | [Python](https://docs.python.org/3/) |
| **Tkinter + ttk / Tk** (standard Python) | Fenêtres Windows, menus, champs, Treeview de navigation, boîtes de dialogue, événements | Déjà disponible avec l'environnement Python/Tk ; intégration sans framework graphique tiers supplémentaire | PySide6/Qt ou autre apporteraient-ils quelque chose que nos composants maison ne peuvent pas faire simplement ? | [tkinter](https://docs.python.org/3/library/tkinter.html) · [ttk](https://docs.python.org/3/library/tkinter.ttk.html) |
| **Tkinter Canvas et composants maison** | Liste, Détaillée, Mosaïque, en-têtes de colonnes, cartes, icônes et interactions | Contrôle précis du rendu et des gestes ; peu de dépendances mais davantage de code d'interface | Étudier une **petite bibliothèque commune de widgets maison** issue de `atelier.py`, `results.py`, `mosaic.py`, `navigation.py` | [Tkinter](https://docs.python.org/3/library/tkinter.html) · [Tk Canvas](https://www.tcl-lang.org/man/tcl9.0/TkCmd/canvas.html) |
| **Pillow 13.0.0** (tiers, **dépendance d'exécution**) | Ouvrir, vérifier, réorienter, convertir et redimensionner des PNG/JPEG/WebP, gérer les couvertures | Beaucoup plus spécialisé dans l'image que Tk.PhotoImage seul ; plus léger conceptuellement qu'OpenCV pour notre besoin | **Candidat à mesurer**, pas à retirer d'office : quelle part des API est utilisée ? Coût de décodage/EXIF/erreurs si réécrits ? | [Pillow](https://pillow.readthedocs.io/en/stable/) |
| **JSON** (`json` standard Python) | Catalogue local versionné, préférences `interface.json`, contrats d'import/export | Lisible, inspectable, partageable, adapté au catalogue et au workflow actuels | SQLite serait à étudier seulement si taille, requêtes ou concurrence le nécessitent ; **pas de parseur JSON maison** sans raison | [json](https://docs.python.org/3/library/json.html) |
| **ZIP** (`zipfile` standard Python) | Sauvegarde/restauration du catalogue et des images | Format connu et disponible sans paquet externe | Un format propriétaire n'apporterait pas de valeur évidente ; une **surcouche métier maison** existe déjà dans `storage.py` | [zipfile](https://docs.python.org/3/library/zipfile.html) |
| **JavaScript natif + HTML/CSS** | Popup et logique de l'extension Chrome Collector | Extension de faible taille, sans dépendance React/Vue ; contrôle direct du DOM | Si les interactions se complexifient : maintenir le natif ou créer des petits composants maison, plutôt que prendre un framework par réflexe | [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript) · [HTML](https://developer.mozilla.org/en-US/docs/Web/HTML) · [CSS](https://developer.mozilla.org/en-US/docs/Web/CSS) |
| **Chrome Extensions Manifest V3** | Déclaration du popup, service worker, content scripts, permissions | Modèle prévu par Chrome pour construire l'extension | Pas directement remplaçable par une bibliothèque maison : c'est le **contrat de la plateforme** | [Manifest](https://developer.chrome.com/docs/extensions/reference/manifest) · [MV3](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3) |
| **`chrome.storage.local`** | Conservation des observations locales du Collector, côté navigateur | API native d'extension, sans serveur ou base externe | Conserver ; un module **repository maison** encapsule déjà son usage | [Storage API](https://developer.chrome.com/docs/extensions/reference/api/storage) |
| **`MutationObserver`** | Suivi des changements utiles du DOM visible de ChatGPT | Mécanisme standard du navigateur ; évite un framework d'observation supplémentaire | Nos **règles de filtrage et d'adaptation** sont maison ; observer leur robustesse lors de changements du DOM | [MutationObserver](https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver) |
| **`unittest` (Python)** | Tests de l'application Tk, du cœur et des imports | Inclus avec Python, couverture existante importante | `pytest` n'est pas nécessaire sans bénéfice identifié | [unittest](https://docs.python.org/3/library/unittest.html) |
| **`node:test` (Node.js)** | Tests automatiques JS du collecteur | Outil de tests fourni par Node ; pas de Jest/Vitest à installer | Conserver tant que la suite reste claire | [Node test runner](https://nodejs.org/api/test.html) |
| **`puppeteer-core` 25.17.0** (**dépendance de développement uniquement**) | Pilotage de Chrome lors de recettes de l'extension | Peut utiliser le Chrome installé, sans embarquer son propre navigateur ; **pas livré comme dépendance d'exécution du Collector** | Évaluer son coût pour les tests, pas pour le poids de l'extension | [Puppeteer](https://pptr.dev/) |

**Remarques :**
- `requirements.txt` déclare **une seule dépendance Python tierce**, exactement **`Pillow==13.0.0`**.
- `package.json` déclare **`puppeteer-core==25.17.0` au sens npm `"25.17.0"`**, dans `devDependencies`. Le manifeste Chrome ne déclare aucun paquet npm à installer chez l'utilisateur.
- `tkinter`, `ttk` et les modules standards sont fournis par l'environnement Python/Tk ; ils ne sont pas des packages PyPI à ajouter au projet.
- Cette liste décrit les **dépendances directes déclarées et les composants principaux**, pas l'ensemble des bibliothèques ou sous-dépendances de l'environnement Windows.

## Modules de la bibliothèque standard Python repérés

| Modules | Rôle dans le projet |
| --- | --- |
| `tkinter`, `tkinter.ttk`, `tkinter.font` | Fenêtres, styles, Canvas, contrôles |
| `json`, `zipfile` | Catalogue, préférences, sauvegardes et échanges |
| `dataclasses` | Modèles de projets, fiches et plans |
| `pathlib`, `os`, `shutil`, `tempfile` | Chemins, fichiers et écriture temporaire |
| `uuid`, `hashlib` | Identités des fiches et empreintes d'images |
| `datetime` | Horodatages, création et modification des fiches |
| `argparse` | Options de lancement (notamment répertoire de recette) |
| `unittest` | Tests de régression |

**Liens vers les fichiers :** [requirements](../../requirements.txt) · [application](../../mon_gpt/__main__.py) · [modèles](../../mon_gpt/core.py) · [stockage](../../mon_gpt/storage.py) · [images](../../mon_gpt/images.py) · [tests](../../tests) · [package Collector](../../companions/chatgpt-collector/package.json) · [manifeste Collector](../../companions/chatgpt-collector/manifest.json).

## Ce qui relève déjà de bibliothèques maison

Le dépôt a déjà produit plusieurs briques réutilisables ou isolables :
- `core.py` : modèles et classement **sans dépendance ChatGPT** ;
- `selection.py`, `batch.py`, `project_choices.py` : logique de sélection et de classement indépendante de l'interface ;
- `atelier.py`, `widgets.py`, `theme.py`, `navigation.py`, `information_ui.py` : composants d'interface construits localement ;
- `images.py`, `identity.py` : gestion des ressources visuelles et résolution de l'héritage ;
- `companions/chatgpt-collector/core/observations.js` : modèle/agrégation d'observations ;
- `companions/chatgpt-collector/adapters/chatgpt.js` : extraction liée au DOM de ChatGPT.

**Piste de travail :** inventorier les **importations/API réellement utilisées** pour chaque dépendance. Si une bibliothèque externe n'apporte que deux ou trois fonctions simples, comparer sérieusement une petite implémentation maison **mais** distinguer la petitesse d'une API de la complexité cachée de son comportement (ex. codecs d'images et cas EXIF). À l'inverse, **réemployer/extraire les briques déjà maison** peut être plus rentable que les réécrire.

## Grille de décision — à remplir après mesure, pas au jugé

| Composant | Surface réelle utilisée | Complexité d'une alternative maison | Coût de maintenance | Décision |
| --- | --- | --- | --- | --- |
| Pillow | **À mesurer** | **À analyser** | **À analyser** | **Ouvert** |
| Tkinter/ttk + Canvas | **À mesurer par widget** | **À analyser** | **À analyser** | **Ouvert** |
| Briques d'interface déjà maison | **À cartographier** | Extraction/factorisation à évaluer | **À analyser** | **Ouvert** |
| Collector natif Chrome | **À cartographier** | Pas d'alternative de plateforme à réécrire | **À analyser** | **Ouvert** |
| Outils de tests | **À vérifier** | **À comparer si nécessaire** | **À analyser** | **Ouvert** |

**Aucune décision de suppression, migration ou refonte n'a été prise.**

Cette première étape répond à **« qu'utilisons-nous et pour quoi faire ? »** ; l'étape suivante sera **« combien de ses fonctionnalités utilisons-nous réellement, et qu'est-ce qui mériterait une bibliothèque maison ? »**.
