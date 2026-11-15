# MG-004 — Vue Détaillée : des fiches visuelles dans la bibliothèque centrale

**Statut : mission à réaliser, soumise à validation visuelle.**  
**Base :** Mon GPT<3 **0.3.1**, `origin/main` au commit `349a88216da3bc163fda83cd0d79e60fed9d25d1`, MG-003b acceptée par l'utilisateur, **86 tests réussis**.  
**Prochain lot distinct :** vue **Mosaïque**, à entreprendre **seulement après** la recette de MG-004. Pas d'extension Chrome ni de repasse graphique générale.

## 1 — Notre objectif n'est PAS une liste un peu plus grande

Le contrat UX validé dans `missions/MG-002-maquettes/01_specification_UX.md`, section 6 :

> **Liste = efficacité · Détaillée = équilibre · Mosaïque = plaisir visuel.**

| Vue | Ce que l'utilisateur doit reconnaître |
| --- | --- |
| **Liste** — déjà livrée | Icone et lignes compactes, colonnes utiles, ouverture immédiate |
| **Détaillée** — **objet de MG-004** | **Petite couverture illustrée ET icône colorée**, lignes aérées, titre, emplacement, extrait de résumé, catégories/tags |
| **Mosaïque** — plus tard | **Grandes couvertures**, cartes visuelles autonomes, texte bref |

Après plusieurs missions sur les couvertures, **leur présence dans les résultats est désormais obligatoire** en vue Détaillée. La différence doit être immédiate à l'œil, dans l'application réelle. **Ne pas livrer une Treeview standard gonflée ou des rangées sans images.**

## 2 — Conception visuelle de la rangée Détaillée

Dans la zone **centrale existante**, à la place de la Liste lorsque le mode Détaillée est actif, afficher une succession de lignes/cartes légères :

- À gauche, une **vraie vignette** de couverture, par exemple autour de **116×65 px** au format confortable (16:9, sans recadrer ni déformer), avec coins doux/bord fin si possible. S'adapter au format compact sans masquer l'image ; ne pas ajouter une grande colonne vide.
- À proximité de l'image, **l'icône choisie dans la couleur choisie**. Elle doit être reconnaissable, sans masquer le sujet illustré. Dans les fils, icône/couleur et couverture héritées du projet par la fonction commune `identity.resolve_identity`.
- Zone texte : **titre dominant** et lisible, **résumé/description sur 1–2 lignes maximum**, **emplacement(s)** lisibles, catégories et tags en petites pastilles colorées. Des métadonnées utiles (date par ex.) peuvent être discrètes ; **pas un formulaire**, pas des paragraphes interminables.
- Titre très long : coupe propre avec accès au texte entier (info-bulle ou moyen équivalent). Résumé vide : ne pas répéter « Pas de résumé » partout, préserver une rangée soignée.
- Un **petit pictogramme ↗ d'ouverture** clairement disponible à droite pour les discussions. Les projets n'ont **pas** d'action d'ouverture ChatGPT.
- Survol léger, sélection douce, focus clavier visible, séparateurs subtils ; réutiliser la **charte Atelier chaleureux** et les couleurs/icônes/couvertures déjà livrées. **Pas de nouvelles illustrations à générer** ni de nouveau système de thèmes.
- Densité maîtrisée : plusieurs résultats visibles simultanément sur **1360×820** ; ne pas transformer chaque fiche en grande tuile. **La grande image est réservée à Mosaïque.**
- Un fil sans projet prend l'identité générique/solaire. Un fil avec plusieurs rattachements apparaît **une seule fois**, hérite du projet actif si directement rattaché, sinon du premier rattachement comme en MG-003b ; ne pas modifier les relations.

**Exigence de rendu :** vraie vignette 16:9 **entière**. Nous avons précisément corrigé les recadrages de MG-003a ; **ne pas reproduire `ImageOps.fit` dans un cadre incompatible**. En cas d'image personnelle portrait, afficher l'intégralité avec marges élégantes plutôt que tronquer.

## 3 — Changement de mode visible et naturel

- Proposer **Liste | Détaillée** dans un **petit commutateur explicite** près de l'en-tête `Discussions` (ou à un emplacement discret équivalent **dans la zone centrale**, pas dans la barre de menus principale). La vue active est immédiatement identifiable. Éviter de surcharger la recherche ou les boutons `+ Fil` et `Aperçu`.
- Ajouter également les deux choix dans le menu existant **Affichage**. Ne pas redessiner le menu « Windows plus plus » validé.
- **Un clic change le mode sans recréer de données**. La recherche, le périmètre de projet, les tags/catégories filtrés, l'ordre de tri et la **fiche sélectionnée** restent identiques ; si la sélection devient invisible parce que les filtres changent, suivre le comportement existant.
- L'inspecteur droit conserve son état et sa fiche. Le même titre, la même discussion, les mêmes tags/notes et les mêmes URL se retrouvent dans les deux vues.
- **Mémoriser la vue choisie** dans `interface.json` (préférences d'interface), **sans ajouter de champ au catalogue `schema: 2`**. `ui_state.py` valide aujourd'hui uniquement `view: "list"` : accepter `list` et `detail` avec lecture rétrocompatible de l'ancien fichier et repli sûr pour valeur inconnue. Préparer proprement l'ajout futur de `mosaic`, sans afficher aujourd'hui une commande inactive encombrante.
- Conserver `Ctrl+K`, `F2`, `Ctrl+N`, `Ctrl+Maj+P`, `Ctrl+S` et les autres raccourcis ; **ne pas inventer des raccourcis conflictuels**. Si un raccourci de vue est ajouté, l'indiquer honnêtement.

## 4 — Fonctionnalités : la vue change, pas les gestes

**Une seule collection de fiches et de projets.** Le moteur `Catalog.search`, les identifiants stables, la recherche et les règles de déduplication restent les mêmes.

- **Clic sur le titre** (ou sur ↗) d'un fil : **ouvrir directement son URL** ; **clic sur l'image, sur l'espace de la ligne ou sur les pastilles** : sélectionner sans ouvrir ChatGPT. Double-clic sur le résultat et Entrée quand le résultat est focalisé : comportement de la Liste actuel. Le clic sur un projet sélectionne/navigue, sans ouverture ChatGPT.
- Menus contextuels (renommer, modifier, rattacher/déplacer, supprimer selon l'objet), édition via l'inspecteur, et parcours clavier doivent rester disponibles.
- Préserver autant que possible le **glisser-déposer d'un fil vers un projet** dans la colonne de gauche (et ses limites connues : glisser droit physique non garanti). Ne pas perdre les autres rattachements. **Si une interaction ne peut pas être maintenue**, la rétablir dans le périmètre de cette mission ou signaler **PARTIEL** : le simple fait de changer de vue ne doit pas supprimer une capacité existante.
- Défilement vertical fluide de la vue détaillée, plus scrollbar visible si nécessaire ; suivi de la sélection, du focus et du survol même après scrolling et changement de vue. Le déplacement entre les modes ne doit pas déclencher un clic d'ouverture involontaire.
- Les **projets apparaissant dans les résultats d'un périmètre** doivent bénéficier de leur propre illustration et icône ; en `Tous les fils` conserver le périmètre d'affichage actuel (pas introduire des projets supplémentaires dans la liste globale par surprise).
- Zéro résultat et absence de sélection : état vide propre et utile, sans fantômes de l'autre vue.

## 5 — Architecture : réutiliser ce que nous avons payé en missions précédentes

L'application utilise `CatalogList` (`mon_gpt/atelier.py`) comme widget Canvas avec une API exploité par `ui.py` (`insert`, `delete`, `exists`, `selection`, `selection_set`, `focus`, `identify_row`, `bbox`, `open_hit`, scroll, menus, DnD, etc.).

- **Ne pas dupliquer la recherche, les mutations, la gestion des liens ou le stockage** pour cette nouvelle vue. Privilégier **un composant de résultats partagé** ou deux rendus interchangeables derrière **une interface commune explicite**.
- Conserver la vue Liste **à l'identique** lorsqu'elle est active. Aucun ajustement de ses alignements, ses colonnes, ses hitboxes ou de son tri n'est permis pour « arranger » Détaillée.
- Utiliser `resolve_identity(catalog, record_id, scope)`, `ImageLibrary` et les petits pictogrammes existants pour les vignettes. Réutiliser/cache des `PhotoImage` à la bonne taille ; pas de chargements d'images en boucle à chaque événement souris/redessin.
- S'assurer que les actions contextuelles et le DnD peuvent identifier correctement la ligne sous le pointeur **dans les deux vues** ; ne pas laisser un faux `is self.results` ou des coordonnées supposées casser la navigation.
- Respecter tailles minimales, fenêtres de **1000×680**, **1360×820** et maximisée, avec **inspecteur affiché et masqué**.
- Aucune migration métier, modification d'images, ZIP, catalogue, extension Chrome ni nouveau framework UI.

## 6 — Recette réelle, pas uniquement tests abstraits

Codex doit utiliser la **vraie application Tk** sur CODEX-VM et un catalogue de développement **entièrement fictif** (comme les recettes précédentes). Aucune demande de sauvegarder les données fictives de l'utilisateur.

**Parcours obligatoire :**
1. Créer 3 projets fictifs avec **3 couvertures et icônes/couleurs différentes**, dont un sous-projet ; 6 fils dont 1 non classé, 1 multirattaché, 1 titre très long, 1 résumé long et des tags/catégories multiples.
2. Afficher **Liste**, puis **Détaillée**, puis **Liste**, sans modifier recherche, filtres, projet actif ni fiche sélectionnée. Montrer les deux **côtes à côtes par captures distinctes**, mêmes données, pour prouver une vraie différence de densité et de richesse visuelle.
3. En Détaillée, cliquer sur une **vignette** → sélection seule ; puis **titre/↗** → une ouverture simulée (pas de navigateur réel) ; vérifier le focus et Entrée. Double-clic cohérent. Les projets ne déclenchent jamais d'ouverture ChatGPT.
4. Fil lié à deux projets, navigation via ses deux périmètres et depuis `Tous les fils` : **une fiche**, la couverture héritée correcte pour chaque contexte, relations inchangées.
5. Filtres/tag/catégorie/recherche et tri, changement de vue, ouvrir/fermer l'inspecteur, renommer F2, menu droit, glisser gauche vers le projet et annulation d'édition non enregistrée.
6. Fermer/reouvrir l'application avec `Détaillée` sélectionnée : elle est restaurée depuis `interface.json` ; JSON de préférences plus ancien `view:list` accepté.
7. **Petites et grandes fenêtres**, scroll et hover ; portrait personnel et couverture solaire par défaut visibles sans recadrage ; beaucoup de résultats et zéro résultat.

**Tests :** conserver les **86 tests existants**, ajouter tests ciblés rendu des vignettes, sélection/gestes, cohérence des données entre vues, bascule/recherche/filtre/tri, persistance UI et non-régression de la Liste, des DnD et menus.

**Livrables :** `reports/MG-004/rapport.md`, code, tests et **3 à 5 captures natives** : Liste avant, Détaillée au même contexte (vue suffisamment remplie !), Détaillée avec inspecteur, version compacte, éventuellement sélection/hover. README et version ajustés sobrement ; commit et push sur `origin/main`, SHA distant vérifié, dépôt propre.

**Pas de validation graphique par Codex seul.** La réussite est jugée par David : **Détaillée doit donner envie de parcourir les fiches et faire enfin apparaître les couvertures, sans perdre l'efficacité de la Liste**.

**Stop après MG-004.** La **Mosaïque** sera une mission distincte, une fois cette première vue examinée ensemble.
