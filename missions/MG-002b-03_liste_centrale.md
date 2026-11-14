# MG-002b-03 — La Liste centrale : élégante, compacte, immédiatement utilisable

**Statut : à réaliser — UNE micro-mission graphique.**  
**Base de travail :** `origin/main`, dernière livraison `384496d899dbd828fc0a364e15ea79253ae0249a` (MG-002b-02), application Mon GPT<3 0.2.1.  
**Décision utilisateur :** MG-002b-01 (menu) et MG-002b-02 (disposition des colonnes) sont **acceptées et figées**. **Ne pas les améliorer, corriger esthétiquement ou déplacer.** Nous connaissons les réserves de marges extérieures, mais nous les laissons **expressément hors de cette mission**.

## 1 — LA référence graphique de ce lot

**Référence principale et quasi exclusive pour la zone centrale :**
`missions/MG-002-maquettes/Image ChatGPT 14 nov. 2026, 11_51_55-3.png`

C'est la maquette « gestionnaire fluide » avec **une vraie Liste de discussions** : titre **« Discussions — 4 résultat(s) »**, tri à droite, **en-tête de colonnes horizontal**, **une ligne compacte par discussion**, **icône non encadrée**, titre prioritaire, colonne projet, **pastilles différenciées** catégories et tags, petite **icône de lien à l'extrémité droite** ; sélection vert pâle, survol discret. La maquette présente aussi un glisser-déposer/contextuel et une création intégrée, déjà fonctionnels dans notre application.

Les deux autres PNG restent des références d'ambiance, **mais cette troisième image est le contrat de composition pour la Liste**. Codex doit la consulter **localement** sur CODEX-VM sans la modifier, re-uploader, dupliquer ou utiliser comme capture de résultat. Ne pas tenter de reproduire les colonnes gauche/droite de cette image : **elles ont été validées dans notre application autrement et restent inchangées**.

### Pourquoi cette mission ?

La 0.2.1 a introduit une liste Canvas avec des lignes d'environ 54–62 px, des pictogrammes parfois encadrés et le texte **« ↗ Ouvrir la discussion » répété sous chaque titre**. L'utilisateur l'a explicitement refusé. Le cœur de l'application est de **trouver un fil et l'ouvrir immédiatement**, et non d'afficher un gros bouton ou un deuxième libellé sous tous les titres.

**Mot d'ordre : la finesse de la maquette, pas une nouvelle interprétation libre.** Cette fois, la fidélité de la composition prime sur la quantité de décor.

## 2 — Travail graphique demandé, ciblé au CENTRE

### 2.1 Lignes compactes, une discussion = une ligne

- Passer à une **vraie ligne compacte et unique** par fil, avec hauteur homogène, alignements fins et rythme vertical maîtrisé. **Supprimer complètement le sous-texte répétitif `Ouvrir la discussion`**. Ne pas remplacer ce texte par un autre sous-titre redondant.
- Mettre en avant **titre** avec bonne graisse et lecture immédiate. Rendre lisible un titre long par troncature élégante et moyen natif de connaître sa totalité (survol, info locale ou inspecteur facultatif), sans élargir démesurément la fenêtre.
- **Icône du fil** : petite, harmonieuse, **sans encadré systématique**. Icône distincte pour un projet ; ne pas montrer un bouton d'ouverture pour un projet.
- **Ouvrir** : petite icône `↗` ou lien externe **tout à droite de la ligne**, discrète mais cliquable/focalisable ; pas de grand bouton, pas de texte récurrent. **Conserver également le clic sur le titre pour ouvrir immédiatement**, plus double-clic et Entrée sur le résultat sélectionné.
- Les clics sur les colonnes, les pastilles et l'espace libre continuent de **sélectionner sans ouvrir**. L'action de fin de ligne **ne doit jamais ouvrir une autre fiche que celle de sa ligne**.

### 2.2 En-tête et colonnes

- Un petit en-tête « **Discussions** » et le **nombre de résultats**, avec tri accessible discrètement ; pas de grande bannière ni nouveau bloc recherche.
- Une table simple, à proportions adaptées : **type/icône | titre local | projet/emplacements | catégories | tags | ouverture**. Une information n'est montrée **qu'une fois**. On peut garder « modifié » si l'espace le permet, mais ne pas écraser titre/ouverture pour conserver cette colonne.
- **Catégories et tags visuellement distincts**, avec pastilles colorées de façon cohérente et lisible ; la palette peut décliner vert/sable/terracotta **sans attribuer une même couleur arbitraire à toutes les valeurs**. Ne pas imposer des couleurs persistantes personnalisées dans ce lot ; ce sera étudié plus tard avec les couvertures.
- Dépassement : `+N` ou équivalent pour les valeurs cachées, avec détail accessible ; pas de texte coupé par des colonnes étroites. Le tri par en-tête, le resize des colonnes et le défilement horizontal doivent toujours fonctionner.
- En **fenêtre compacte** ou aperçu ouvert : choisir une hiérarchie de colonnes raisonnable, garder **titre et icône d'ouverture** visibles sans chercher constamment le lien à l'extrême droite d'une zone hors écran. Si nécessaire, masquer/replier les colonnes secondaires de façon explicite, **sans supprimer les données ou modifier le filtrage**.

### 2.3 Interaction et petits états

- Une sélection **vert sauge très pâle**, hover discret, une seule ligne active bien visible, focus clavier distinct et contraste correct ; pas de gros encadrements d'icône ou grands rectangles « boutons » sur chaque ligne.
- Le drag-and-drop gauche, le menu contextuel de rattachement, les cibles interdites, l'ordre/tri, les raccourcis existants et la sélection doivent être **intégralement conservés**. Les hitboxes de la nouvelle icône de fin, du titre et du reste de la ligne doivent être testées : une migration de colonnes peut casser `title_hit`, `identify_column`, les coordonnées de drag ou le clic/double-clic.
- Lors d'un déplacement, conserver le feedback de destination, sans transformer une opération existante en formulaire. Ne pas développer dans ce lot de fonction « copie de fiche », ni nouvelle sélection multiple.
- États vides et lignes de projets dans les résultats : distinction lisible, pas de fausse action de lien externe.

## 3 — Où travailler et que préserver

Le code actuel place la table centrale dans `CatalogList`, classe de `mon_gpt/atelier.py` (dessin Canvas, `draw()`, `row_height`, `bbox`, colonnes, souris, défilement). `mon_gpt/ui.py` adapte les données à la table (`refresh_results`) et détermine l'ouverture par `title_hit` / `open_click`. **Limiter les changements à ces composants et aux tests ciblés** ; ne pas toucher aux modules métier.

**Figés :**
- **Menu principal** « Windows plus plus » (MG-002b-01) **à préserver strictement**, dont `main_menu.py` et `build_menus()`.
- **Implantation verticale des trois colonnes**, recherche compacte, Masthead, ordre des panneaux, largeur/espacement extérieurs et aperçu (MG-002b-02). **Ne pas retoucher les marges, même si tu penses pouvoir les améliorer.**
- **Arborescence gauche et son habillage**, inspecteur droit, créations intégrées, suggestions globales, autres menus, tags/catégories en mode édition et les modalités de sauvegarde/restauration.
- **MG-001** `core.py`, `chatgpt.py`, `storage.py`, schéma `1` et archives ; aucune mutation du catalogue utilisateur réel.
- **Les trois maquettes** PNG d'origine, inchangées.

**Attention :** les « trois vues » (Liste/Détaillée/Mosaïque), images de couvertures et personnalisation persistante sont **toujours hors lot**. MG-002b-03 concerne uniquement **le rendu de la vue Liste existante** ; ne pas inventer les autres vues ni de nouvelles opérations.

## 4 — Recette et preuves indispensables

Travailler sur **CODEX-VM**, sous le compte `codex` avec une copie **strictement fictive** `--data-dir` et `--simulate-open`, pas le catalogue normal.

**Scénarios ciblés :**
1. **1360×820 aperçu masqué :** comparer la Liste exécutée à la maquette principale. Lignes compactes, titre une seule fois, petites icônes, badges catégorie/tag distincts, petit lien à droite, sans sous-texte d'ouverture.
2. **1360×820 aperçu visible :** les mêmes qualités, en largeur moindre ; clic sur le titre et sur l'icône de fin → **exactement la bonne conversation** (simulation). Clic dans catégorie/tag/autre colonne → sélection seule, aucune ouverture.
3. **1000×680 aperçu visible/masqué :** colonne titre utilisable, icône d'ouverture accessible, badges gérés proprement, pas de chevauchement ni coupure fonctionnelle.
4. **Navigation clavier** : flèches, Entrée, focus, F2, menu contextuel ; distinguer projet et fil.
5. **Classement** : drag gauche vers l'arbre, clic droit, ajout/réaffectation sans duplication ; pas de perte de rattachement. Tri, scrolling, resizing de colonnes.
6. **Création inline**, recherche unique et bascule aperçu : pas de casse des autres zones. La nouvelle ligne doit rejoindre la Liste avec le même rendu.

**Preuves à publier :** trois ou quatre captures de la **vraie application** :
- Liste centrale sans aperçu ;
- Liste centrale avec aperçu ;
- format compact ;
- sélection/hover ou menu contextuel si utile.

Les comparaisons sont orientées **zone centrale**, pas réouverture du chantier des panneaux latéraux. **Conserver tous les 48 tests** existants ; ajouter seulement les tests de régression nécessaires. Publier les captures uniquement avec des liens/UUID de conversation **fictifs**.

## 5 — Livrables

- `reports/MG-002b-03/rapport.md` court : comparaison **concrète** entre la Liste produite et le tableau de la maquette, constat des écarts résiduels, tests, captures, éventuel PARTIEL.
- Mise à jour courte du README/version uniquement si nécessaire ; code et tests ; commit/push `origin/main`, SHA distant vérifié, dépôt propre.
- **Aucune mission suivante lancée.** Aucune proclamation de « GO graphique général » : le verdict sur cette Liste appartient à l'utilisateur après recette.

**Critère de passage :** à première vue, le centre doit être une **vraie liste élégante et fonctionnelle**, qui se rapproche de notre maquette « gestionnaire fluide ». Une ligne par discussion, un titre clair, des repères colorés et une discrète icône d'ouverture. Le reste de l'interface est **inchangé**.
