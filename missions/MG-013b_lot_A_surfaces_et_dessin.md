# MG-013b — Lot A : surfaces et dessin (peinture uniquement)

**17 novembre 2026 — GO explicite de David pour le LOT A seulement.**  
**Produit : Mon GPT<3 0.9.4 — dépôt `ugadavid/Mon-GPT`.**  
**Mission de RÉALISATION GRAPHique ciblée, à publier sur `origin/main`.**  
**STOP impératif après lot A et rapport, en attente de recette humaine.**

> Coucou, Codex artiste ! ❤️🎨 Nous validons le **cadrage corrigé MG-013a-01**, pas l'ancien programme de refonte MG-013a. Ta tâche est de donner une vraie qualité de finition graphique aux composants actuels, à leur emplacement actuel. **Des pinceaux, pas une pelleteuse.** Aucun fonctionnement ne doit changer.

## 1. Autorités et état au départ

Avant modification, lire et appliquer :
- `AGENTS.md` et les instructions des sous-dossiers applicables ;
- [addendum MG-013a-01](../reports/MG-013a-01/rapport.md), **source de référence prioritaire** pour le périmètre esthétique ;
- [rapport MG-013a et captures d'état initial](../reports/MG-013a/rapport.md), pour les comparaisons visuelles, en excluant ses quatre lots structurels retirés ;
- [spécification UX et trois maquettes historiques](MG-002-maquettes/01_specification_UX.md), déjà dans `missions/MG-002-maquettes/` : inspiration esthétique, **pas** une autorisation de copier leurs gestes ou de faire réapparaître des fonctions fictives ;
- [MG-011 — navigation et informations](../docs/MG-011-navigation-et-informations.md), [MG-012 — licences](../reports/MG-012/rapport.md), et les derniers contrats fonctionnels réellement présents dans le code.

Vérifier état Git initial, branche, remotes, SHA, travaux concurrents avant d'écrire. Synchroniser seulement sans écraser. Si un problème préexistant bloque, qualifier précisément et ne pas nettoyer pour forcer un état artificiellement propre.

## 2. Périmètre EXACT du lot A : couleur, trait, matière

**Autorisé :** des changements visuels modestes et localisés via `mon_gpt/theme.py`, styles ttk existants, et fonctions de dessin des widgets existants (`Surface`, `PillButton`, cartes, titres, pastilles, menus), seulement lorsque le changement ne déplace aucune fonctionnalité ni ne modifie sa zone interactive.

Intention graphique :
- Papier/ivoire/sable plus cohérents, sans masse grise ou bordures multiples inutiles ;
- contours/filets plus fins, séparations plus discrètes et hiérarchie typographique plus évidente ;
- sélection sauge, hover discret, focus visible, contraste suffisant ;
- pictogrammes et pastilles harmonisés **sans** changer leur signification ;
- menus et fenêtres d'aide/crédits raccordés par **quelques styles** si cela ne perturbe pas leur comportement ;
- conserver palette d'identité : ivoire `#F7F3EA`, sable `#E7D9C5`, sapin `#315E4F`, terracotta `#C87A50`, encre `#292D30` (nuances compatibles autorisées). Utiliser Segoe UI et les polices déjà présentes, pas de police téléchargée/embarquée.

**Nous voulons un avant/après visible, sans effets gadgets**, mais pas une grande opération de nettoyage CSS/Tk ni une nouvelle abstraction de styles. Privilégier les modifications minimales, réversibles et cohérentes.

## 3. HORS LOT : limites non négociables

**Pas de changement fonctionnel, pas de réorganisation des zones.**

- Ne toucher ni au modèle métier, ni aux adaptateurs ChatGPT, ni au stockage, schémas, données, import/export, Collector ou ressources utilisateur.
- Aucune modification des comportements de sélection, recherche, tri, filtres, raccourcis, ouverture explicite ↗, glisser-déposer, rattachements, création, édition, focus et navigation clavier.
- Ne pas changer les positions relatives, hauteurs, largeurs automatiques, seuils de repli, Panedwindow, modes Liste/Détaillée/Mosaïque, ratios et hauteurs de cartes, hit-tests, scroll, répartition des colonnes, tailles des cibles cliquables, géométrie de grille, proportions de l'aperçu ou persistance UI.
- **Bandeau actuel** : ne modifier ni sa hauteur (80 ou 112 selon l'état), ni les informations présentées, ni leur source. Les informations du projet courant restent distinctes de l'objet sélectionné. La couverture peut suivre la sélection selon les règles existantes.
- **Inspecteur droit** : affiche l'élément sélectionné (projet ou fil), tandis que le bandeau renseigne le projet courant ; préserver totalement cette distinction.
- **Réserver au lot B**, NON autorisé ici : suppression du titre « Aperçu », éventuelle substitution des boutons textuels Liste/Détaillée/Mosaïque par des pictogrammes, nouveau rendu des informations de bandeau.
- **Réserver au lot C**, NON autorisé ici : habillage des états de glisser-déposer, du menu de dépôt et des signaux de classement.
- Ne pas ajouter de nouvelle dépendance, de nouvelle couche UI, de framework ou de technologie Web/CSS (la « peinture/CSS » est une analogie pour l'interface Tk).
- L'ancien plan MG-013a (recomposition du centre, titres sur deux lignes par recalcul, nouveau rythme géométrique des cartes, redimensionnement automatique des volets) demeure **NO-GO**.

Si une amélioration esthétique nécessite de modifier le comportement ou le squelette, **renoncer à cette amélioration** et l'indiquer parmi les idées écartées. Aucun arbitrage fonctionnel implicite.

## 4. Preuve graphique courte, et tests proportionnés au périmètre

- Réutiliser le **même jeu fictif et des cadrages comparables** aux neuf captures MG-013a ; ouvrir Liste, Détaillée et Mosaïque. Comparer au moins un cas avec aperçu et une fenêtre secondaire si elle est touchée.
- Montrer des **avant/après honnêtes** de la vraie application Windows, sur données fictives, sans retoucher les captures. Le rapport donne les couleurs/styles réellement changés et les surfaces touchées. **Maximum 3 à 5 captures utiles**, pas une collection d'images redondantes.
- Contrôles fonctionnels voisins limités à ce que la peinture pourrait affecter : sélection et focus visible, ouverture simulée par ↗, choix d'une autre vue, fonctionnement d'une fenêtre d'information si stylisée. Pas de test de migrations, sauvegardes, Collector JS, ni campagne multi-DPI par simple réflexe.
- **Attention à la règle active `AGENTS.md` : elle demande actuellement `python -m unittest discover -s tests -v` et une recette Windows avant publication. Ne la contourne pas silencieusement.** Fais les vérifications qui restent obligatoires en l'état et signale leur coût ; limite tout test additionnel aux composants touchés. **Ne lance pas de tests JavaScript Collector** sauf lien causal explicité. Notre future politique de tests par domaines est un chantier séparé, important mais non urgent ; ne réécris pas `AGENTS.md` dans MG-013b.
- Distinguer tests automatisés, vérifications de widgets Tk, pilotage Windows et recette humaine de David. Ne pas qualifier l'ergonomie finale sans sa validation.

## 5. Livrables et STOP

- Retouches exclusivement graphiques, bornées au lot A.
- Rapport concis : `reports/MG-013b/rapport.md`, liste des fichiers/styles modifiés, captures avant/après, contrôles exécutés, non exécutés et limites, choix volontairement écartés.
- Mise à jour README minimale uniquement si utile.
- Commit et push dans **Mon-GPT seulement** sur `origin/main`, contrôle `git diff --check`, SHA distant, état propre. Préserver le travail concurrent ; jamais de push forcé.
- **Ne pas commencer les lots B ou C, ni une nouvelle mission, ni la préparation de l'installateur.** Après livraison : STOP et attendre l'appréciation graphique de David.

**Critère d'acceptation :** les mêmes écrans, les mêmes objets, la même ergonomie, avec une présentation sensiblement plus soignée — sans réécriture fonctionnelle.
