# MG-014g — Tri cohérent de la vue Détaillée

**GO réalisation — micro-correction après MG-014f.**  
Point de départ : `origin/main` après MG-014f.

## Objectif unique

Corriger la présentation du tri dans la vue Détaillée pour qu’elle soit **alignée avec le cartouche** et visuellement cohérente avec les autres menus de Mon GPT<3.

Le contenu des cartes Détaillées est validé. **Ne pas y retoucher.**

## 1. Positionnement du contrôle de tri

Le bloc actuel `Trier par : [ ... ]` est trop collé au bord droit de la colonne centrale et paraît découplé du cartouche.

### Attendu

- Aligner le bloc de tri avec le **bord droit utile du cartouche Détaillé**.
- Éviter l’effet « contrôle perdu à l’extrême droite » lorsque l’inspecteur est fermé.
- Conserver une petite respiration verticale/horizontale cohérente avec la carte située en dessous.
- Avec l’inspecteur ouvert ou fermé, le tri doit rester visuellement attaché à la zone de résultats.

## 2. Menu de choix : une seule famille visuelle

Le menu actuel réutilise le `MenuSkin` générique destiné aux menus d’actions. Cela produit pour les choix de tri :
- un petit carré arrondi avec le symbole de fallback `·` ;
- une présentation adaptée à « Nouveau / Renommer / Déplacer », mais pas à une simple liste de choix.

### Attendu

Créer ou réutiliser une **présentation de menu de choix** cohérente avec la charte papier/sauge :

- options : `Titre`, `Projet`, `Catégories`, `Tags`, `Création`, `Modification` ;
- **aucun petit carré avec point** ;
- pas d’icône décorative si elle n’apporte rien ;
- état survolé / sélectionné léger en sauge ;
- filet, fond et typographie cohérents avec les autres menus de l’application ;
- clavier et focus conservés.

Ne pas modifier le `MenuSkin` d’action existant si cela risque de changer les menus Nouveau/Renommer/Déplacer. Préférer une variante dédiée aux **menus de choix** si nécessaire.

## 3. Contrôle fermé

Le contrôle fermé doit rester simple :

**Trier par : [ Catégories ]**

- **Ne pas ajouter de caractère `▾` dans le libellé.**
- Le contrôle lui-même doit faire comprendre qu’il est déroulant.
- Ne pas ajouter d’ornement redondant.

## 4. Sens du tri

Le sens ascendant / descendant reste une information utile, mais il ne doit plus polluer le libellé de l’option.

### Attendu

- garder le choix de colonne dans le menu déroulant ;
- afficher le sens du tri via une **petite commande séparée ↑ / ↓** ou un pictogramme fin adjacent ;
- cette commande inverse le sens du tri actuel ;
- conserver exactement la logique existante de `sort_results`, `sort_column`, `sort_reverse` et persistance.

Pas de flèche descendante ajoutée après `Catégories` dans le menu de choix.

## Hors périmètre

Ne pas toucher :
- aux informations des cartes Détaillées validées ;
- à la Liste ;
- à la Mosaïque ;
- au bandeau ;
- à l’inspecteur ;
- à l’explorateur ;
- à la création rapide ;
- aux données et règles métier.

## Tests proportionnés

Mission **L1 UI locale**.

Attendu :
- tests ciblés du tri et de la vue Détaillée ;
- recette Windows courte :
  - ouvrir le menu ;
  - choisir au moins Titre, Catégories, Création ;
  - inverser ↑ / ↓ ;
  - inspecteur ouvert puis fermé ;
  - vérifier l’alignement au cartouche ;
  - clavier/focus du menu ;
- pas de suite complète.

## GitHub — Marcel

Publier avec **Marcel / `Trucabule-M1`** :
- `gh auth status` : Marcel actif ;
- identité Git locale : `Trucabule-M1 <marcel@trucabule.fr>`.

## Livraison

- Rapport bref : `reports/MG-014g/rapport.md`.
- Une ou deux captures utiles.
- Commit/push `origin/main`, SHA distant vérifié, dépôt propre.
- **STOP pour validation humaine.**

**Critère d’acceptation :** le tri de la vue Détaillée semble appartenir naturellement à la carte, le menu ne ressemble plus à un menu d’actions, et colonne + sens de tri restent immédiatement compréhensibles sans symboles redondants.
