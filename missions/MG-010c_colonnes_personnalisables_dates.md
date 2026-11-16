# MG-010c — Administration des colonnes de la Liste, dates et préférences persistantes

**Mission Codex prête à réaliser ; STOP à la livraison pour validation David/GPT.**  
**Base validée en recette utilisateur :** Mon GPT<3 **0.9.2a**, commit `49caa287469ef98ab53b70a4dc169ad857aa1ac5`, et les lots MG-010a / MG-010b / MG-010b-01.  
**Version cible suggérée : 0.9.3.** Le Collector Chrome 0.8.2 est inchangé.

## 0. Intention : une administration SIMPLE, pas une usine à gaz

Dans sa première vraie recette avec environ **1 429 conversations**, David a demandé :

> « Le top du top serait même d'avoir une partie administration de tout ça où l'on puisse faire ce genre de choses, choisir les colonnes visibles dans la liste. »

Il a aussi explicitement souhaité pouvoir afficher **les dates de création et de modification** et régler les colonnes. MG-010a a déjà livré les en-têtes « Titre / Projet / Catégories / Tags » et leur redimensionnement **pendant une session** ; MG-010c termine cette idée en offrant une **configuration mémorisée**, sans modifier les données métier.

**Priorité absolue : simplicité des gestes et fluidité.** Pas de confirmations inutiles, ni de sauvegarde de catalogue pour modifier une préférence de vue ; le catalogue utilisé est encore en développement/recette. Ne pas créer un framework générique de dashboards, un « administrateur » séparé ou une nouvelle application.

**Périmètre strict : vue Liste et ses préférences**, plus tri commun lorsque nécessaire. L'ordre et les colonnes ne doivent pas s'imposer aux vues Détaillée et Mosaïque ; elles doivent continuer à fonctionner normalement.

## 1. Comprendre l'existant avant de modifier

Inspecter au minimum :

- `mon_gpt/atelier.py` : `CatalogList(tk.Canvas)`, **pas** un `ttk.Treeview`; `keys`, `layout()`, `visible_box()`, `separator_at()`, `resize_motion()`, `xview()`, `draw()`, `heading()`, `column()`. **Attention :** l'ordre actuel des trois colonnes secondaires change automatiquement selon la largeur du widget ; cela doit être concilié avec l'ordre **choisi par l'utilisateur**.
- `mon_gpt/ui.py` : `build_menus()`, `build_shell()`, `refresh_results()`, `sort_results()`, `detail_sort_popup()`, `restore_workspace()`, `close()` et gestion du passage entre les trois vues. Attention au tri `values(r)[self.sort_column]`, aux valeurs de ligne codées en position, aux sélections multiples et à la conservation du focus.
- `mon_gpt/ui_state.py` : préférences locales **`interface.json` version 1**, `FIELDS` stricts, `validate/load/save`. Les préférences de colonne doivent vivre **ici** et non dans `catalogue.json` ni dans les backups métier.
- `mon_gpt/core.py` : `Record.created` et `Record.modified` existent déjà, au format de dates interne ; aucun nouveau champ métier nécessaire.
- `mon_gpt/details.py` : l'éditeur affiche déjà les deux dates.
- `mon_gpt/results.py`, `mon_gpt/mosaic.py` : autres rendus et interactions ↗, sélection multiple, drag, zones de clic.
- Tests MG-010a (redimensionnement) et MG-010b-01 (gestes de sélection, ouverture sur ↗ exclusivement) à préserver.
- `docs/idees-et-finitions.md` : parking de sujets différés ; **aucune autre idée à développer**.

**Important :** les colonnes actuelles sont visibles sous les noms **« Titre »**, **« Projet »**, **« Catégories »**, **« Tags »**. Ne jamais restaurer « Titre local » / « Projet / emplacements ».

## 2. Menu « Colonnes de la liste… » et panneau de configuration

Ajouter sous **Affichage → Colonnes de la liste…** (accessible même lorsqu'on est momentanément en Détaillée ou Mosaïque, mais les effets concernent la Liste).

Ouvrir un **petit panneau/dialogue Atelier chaleureux**, lisible et utilisable au clavier. Il contient une **liste des colonnes configurables** avec, pour chacune :

- sa **visibilité** (case à cocher, sauf colonnes obligatoires) ;
- sa **position** (commandes **Monter / Descendre**, simples et accessibles, plutôt qu'un drag fragile obligatoire) ;
- sa **largeur** actuelle en pixels, ajustable **à la souris depuis l'en-tête**, éventuellement éditable dans ce panneau si cela reste simple ;
- des boutons **Rétablir les valeurs par défaut**, **Appliquer** et **Fermer/Annuler** avec comportement clair.

**Colonnes disponibles :**
1. **Titre** — toujours visible, première colonne textuelle, épinglée à gauche. Largeur ajustable.
2. **Projet** — libellé des emplacements locaux d'une discussion (plusieurs rattachements possibles).
3. **Catégories**.
4. **Tags**.
5. **Création** — date de création de la fiche dans **Mon GPT<3**, `Record.created`.
6. **Modification** — date de dernière modification de la fiche locale, `Record.modified`.

L'icône d'identité à gauche et **↗** à droite sont des **éléments structurels fixes**, non des colonnes que l'utilisateur peut masquer ou déplacer. Il faut préserver la sélection par clic et l'ouverture **↗ uniquement**.

**Configuration initiale** sans préférences : **Titre / Projet / Catégories / Tags**, dans cet ordre ; les colonnes **Création et Modification** sont facultatives et **masquées au départ**, pour ne pas bouleverser la version que David a validée. Les cinq colonnes secondaires doivent pouvoir être **montrées, masquées et réordonnées** librement ; le Titre reste épinglé.

**Gestion d'un panneau très étroit :** pas de réorganisation automatique contraire au choix de l'utilisateur. Garder Titre et ↗ accessibles ; les colonnes secondaires restent dans **l'ordre choisi**, avec défilement horizontal si nécessaire. Ne pas masquer silencieusement une colonne cochée ; seules les contraintes du mode compact déjà existantes peuvent déclencher un affichage de secours clairement explicable. Les largeurs minimum/maximum doivent rendre le tableau manipulable.

**Ne pas développer** une administration des champs métier ou un éditeur de métadonnées supplémentaires : cette mission ne concerne que les colonnes existantes + deux dates.

## 3. Dates : affichage clair et tri chronologique véritable

Les deux dates ne sont **pas** les dates originales de la conversation dans ChatGPT (le Collector ne les fournit pas). Ce sont bien les timestamps de la **fiche locale**.

- Affichage français lisible dans les cellules, par exemple `16/11/2026 14:45` si la largeur le permet, ou date seule `16/11/2026` en colonne étroite avec infobulle/accès à la valeur complète. **Ne jamais tronquer de façon ambiguë l'année.**
- **Tri chronologique sur les vraies dates/horodatages**, ascendant et descendant — **pas de tri alphabétique des chaînes `JJ/MM/AAAA` affichées**. Une fiche créée en décembre 2025 doit correctement se comparer à une fiche créée en janvier 2026.
- `Record.created` demeure inchangé lors d'un renommage, reclassement ou édition normale ; `Record.modified` reflète seulement les mises à jour métier déjà produites par les fonctions existantes. **Ne pas modifier les dates en ouvrant ou réorganisant les colonnes.**
- Pour les projets éventuellement affichés comme lignes au milieu de la Liste, utiliser leurs propres dates de `Record`. Les fiches importées utilisent leur date locale, sans fabriquer de date source historique.
- Les commandes de tri des vues Détaillée/Mosaïque peuvent inclure Création et Modification pour cohérence si un tri commun est conservé. Si l'utilisateur masque la colonne servant au tri, afficher néanmoins un état de tri compréhensible ou revenir clairement à Titre ; aucun tri silencieux incompréhensible.

## 4. Largeurs persistantes, ordre stable, préférences locales

Actuellement les quatre largeurs changent à la souris **uniquement pour la session**. Après MG-010c :

- Mémoriser **colonnes visibles**, **ordre**, **largeurs**, et éventuellement **tri/direction** dans `interface.json` via `ui_state.py`, pas dans le catalogue ni son ZIP métier.
- Enregistrer les choix **après l'action terminée** / à la fermeture, jamais une écriture sur **chaque pixel** d'un glisser. La préférences choisie doit être **restaurée au redémarrage**, ainsi qu'après passage Liste → Détaillée → Mosaïque → Liste et redimensionnement de la fenêtre.
- Étendre prudemment le **format existant `interface.json` v1** avec un champ optionnel validé (ex. `list_columns`), **sans rendre invalides les fichiers v1 actuels** qui n'ont pas ce champ. Pour un fichier actuel, appliquer les valeurs par défaut de colonne et conserver recherche, filtre, taille, projet ouvert, inspection, etc.
- Valider type, ensemble de clés autorisées, valeurs de largeur bornées, ordre sans doublons, présence obligatoire du titre, visibilité et tri ; les préférences incorrectes doivent produire un retour aux choix par défaut **sans altérer le catalogue**. Si possible ne rejeter que la configuration de colonne et conserver le reste des préférences valides.
- Attention à `ui_state.save()` qui reconstruit un objet plutôt que de fusionner les préférences existantes : ne pas perdre les champs existants. Ne pas créer un **deuxième fichier de préférences concurrent** pour les colonnes.
- Le clic sur un séparateur de colonne garde son effet **glisser largeur** et ne lance ni tri, ni sélection, ni ouverture. Les colonnes cachées ne doivent pas réserver de largeur ou laisser des poignées invisibles.

## 5. Implémentation : réduire les cas spéciaux dans le Canvas

- Créer une **description de colonnes** centralisée (`key, libellé, largeur par défaut, largeur min, type de rendu, tri`) réutilisée entre l'en-tête, la mise en page, les cellules, le sélecteur, les préférences et les tests. Éviter six listes incohérentes dans plusieurs fichiers.
- Ne plus supposer que la valeur de colonne `context` est toujours `values[1]` ou que les badges et dates occupent une position fixe. **Dissocier les données de ligne (`title, context, categories, tags, created, modified`) de leur ordre d'affichage**.
- Garder un chemin de rendu simple et performant (Canvas **virtuel**, pas six widgets par conversation), avec 1 429 fils, zéro ralentissement perceptible au tri/défilement.
- **Conserver les sélections multiples**, plages Shift, Ctrl+A, menus contextuels, glisser multiple gauche/droit, renommer F2, action ↗, focus, en-têtes et zones de redimensionnement : ne jamais réintroduire l'ouverture par clic sur le titre.
- Le changement de colonnes **ne modifie ni les emplacements, ni les notes/tags/catégories**, ni les identités visuelles, ni le stockage ni les mappings de projets ChatGPT. Zéro nécessité de nouveau schéma catalogue, de migration Collector ou de modification du moteur d'import.

## 6. Tests / recette et livraison

**Tests Python** : conserver les **184 tests** MG-010b-01 et les **43 JS** du Collector inchangé ; ajouter des tests de configuration et événements Tk :

1. Version de départ sans `list_columns` dans `interface.json` : interface 0.9.2a préservée (4 colonnes par défaut) et autres préférences intactes ; avec `list_columns` valide : restauration complète.
2. Activer Création / Modification, masquer Catégories / Tags, réordonner Projet/Modification/Création, changer quatre largeurs ; vérifier rendu, en-têtes, séparateurs, scroll, tri et état après fermeture/reprise.
3. **Tri vrai des dates** par exemple 31/12/2025, 01/01/2026, 16/11/2026, ascendant/descendant ; dates à la minute ; valeur affichée ≠ clé de tri, pas de changement dans les timestamps du catalogue.
4. Configuration erronée : colonne inconnue, doublon, valeur non numérique, taille absurde, Titre masqué, nombre de colonnes non permis ; défaut lisible et **catalogue inchangé**.
5. Fenêtre **1000×680** et **1600×900**, inspecteur ouvert/fermé, largeur modifiée par véritable `ButtonPress`/`B1-Motion`/`ButtonRelease`, et conservation en repassant par les trois vues.
6. Sélection multiple et glisser gauche/droit (un/plusieurs) après réordonnancement ; clic sur cellule/titre ne déclenche pas ChatGPT ; ↗ ouvre un seul fil. Tri d'une colonne masquée traité clairement.
7. Charge et réactivité sur **1 429 discussions fictives**, recherche/filtres/sous-projets, visuel sans chevauchement ni disparition de colonnes choisies.
8. Sauvegarde/restauration et import Collector v2 toujours fonctionnels ; préférences séparées du catalogue ; tests du reste du dépôt verts.

**Recette Windows réelle sur CODEX-VM**, données fictives isolées (`--data-dir .recette/MG010c --simulate-open`) : interface initiale à quatre colonnes, ouvrir administration, configurer plusieurs colonnes, voir dates, tri, enregistrer, relancer, retrouver réglages et glisser un lot à travers les vues. Pas besoin d'utiliser les données personnelles de la bibliothèque pour réaliser les tests Codex.

**Livrables** :
- code et tests ; mise à jour du guide/raccourcis et `README.md` ;
- `reports/MG-010c/rapport.md` (diagnostic du Canvas et `interface.json`, décisions de présentation, bilans, limites) et **4 à 6 captures natives Windows sur données fictives** (réglages, liste avec dates, tri, configuration après relance, fenêtre étroite) ;
- commit/push `ugadavid/Mon-GPT` `main`, SHA distant vérifié, dépôt propre ;
- **STOP pour recette David/GPT**. Ne pas démarrer le tableau de bord, les statistiques, l'installateur, un nouvel outil graphique ou une nouvelle application.

### Critère GO

David peut choisir quelles colonnes afficher, les réordonner, les redimensionner et **retrouver exactement ses réglages en relançant Mon GPT<3**. Il peut montrer **Création** et **Modification** avec des dates lisibles et triées chronologiquement. L'interface reste naturelle et tous les gestes validés en 0.9.2a fonctionnent.
