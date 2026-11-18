# MG-014f — Finaliser la vue Détaillée

**GO réalisation — passe graphique ciblée sur la vue Détaillée uniquement.**  
Point de départ : `origin/main` après MG-014e.

## Objectif

La vue Détaillée doit réellement apporter **davantage d’informations que la Liste**, sinon elle perd son intérêt.

Aujourd’hui, les cartes Détaillées sont trop pauvres alors que les données nécessaires existent déjà dans le modèle de rendu.

Cette mission couvre uniquement :
1. enrichir visuellement chaque cartouche Détaillé avec les informations disponibles ;
2. remplacer le contrôle de tri actuel par un libellé **« Trier par : » + menu déroulant** intégré à la charte graphique.

## 1. Cartouches Détaillés : montrer davantage d’informations

Le rendu actuel dispose déjà de :
- titre ;
- projet/contexte ;
- catégories ;
- tags ;
- résumé ;
- notes ;
- création ;
- modification.

### Attendu

Dans chaque cartouche Détaillé :
- conserver couverture, identité, titre et action d’ouverture ;
- afficher **autant d’informations utiles que possible dans l’espace disponible**, sans créer de surcharge ;
- priorité d’information recommandée :
  1. titre ;
  2. résumé / note (si présents) ;
  3. projet/contexte ;
  4. catégories ;
  5. tags ;
  6. création et modification, si elles tiennent proprement.

Les dates doivent pouvoir apparaître sous une forme compacte et secondaire, par exemple :
- `Créé · 15/11/2026`
- `Modifié · 16/11/2026`

### Règles

- Ne pas masquer une information qui pourrait tenir simplement dans le cartouche.
- Ne pas transformer la carte en tableau administratif.
- Conserver la hiérarchie graphique papier/sauge et les pictogrammes fins.
- Les textes longs restent tronqués intelligemment / limités à quelques lignes.
- Pas de nouveau panneau, popup ou interaction.
- Si le cartouche doit gagner légèrement en hauteur pour accueillir les informations de manière lisible, le faire avec mesure ; ne pas transformer la vue en gigantesques fiches.
- Conserver sélection, clavier, scroll, hit-tests, ouverture ↗ et renommage.

**Principe :** Détaillée doit visiblement contenir plus d’information que Liste au premier coup d’œil.

## 2. Tri de la vue Détaillée

Le bouton actuel `Tri · Titre ↑` est jugé trop compact et peu élégant.

### Cible

Afficher dans la barre de la vue :

**Trier par : [ Titre ▾ ]**

- `Trier par :` = libellé simple, discret, conforme à la charte.
- Le choix de colonne = **menu déroulant**.
- Les choix restent ceux déjà supportés par le code : Titre, Projet, Catégories, Tags, Création, Modification.
- Conserver le sens ascendant/descendant existant.

Pour l’ordre :
- soit afficher une petite flèche ↑/↓ dans le contrôle ;
- soit conserver une action secondaire très discrète à côté.

Choisir la solution la plus naturelle avec Tk, sans inventer une nouvelle logique de tri.

### Important

- Le tri reste partagé avec la logique existante.
- Ne pas modifier les données, le stockage des préférences ni les règles de tri.
- La vue Liste conserve son fonctionnement actuel.
- La vue Mosaïque est hors périmètre pour cette mission.

## Hors périmètre

Ne pas toucher :
- explorateur gauche ;
- bandeau ;
- inspecteur ;
- barre de création ;
- Liste ;
- Mosaïque ;
- glisser-déposer ;
- modèle métier / stockage.

## Tests proportionnés

Mission **L1 UI ciblée** selon `AGENTS.md`.

Attendu :
- tests existants de vue Détaillée, tri et navigation directement concernés ;
- recette Windows courte :
  - plusieurs cartes avec données différentes ;
  - tri par au moins Titre, Catégories et Création ;
  - inversion ascendant/descendant ;
  - sélection + ↗ ;
  - largeur confortable et largeur plus contrainte ;
- contrôle visuel que Détaillée contient réellement plus d’information que Liste ;
- **pas de suite complète des 203 tests**.

Rapporter ce qui a été exécuté et omis.

## GitHub — Marcel

Publier avec **Marcel / `Trucabule-M1`** :
- `gh auth status` : Marcel actif ;
- identité Git locale : `Trucabule-M1 <marcel@trucabule.fr>`.

## Livraison

- Données fictives uniquement.
- Rapport : `reports/MG-014f/rapport.md`.
- Quelques captures avant/après utiles.
- Commit/push `origin/main`, SHA distant vérifié, dépôt propre.
- **STOP pour recette humaine.**

**Critère d’acceptation :** la vue Détaillée montre clairement plus d’informations que la Liste sans devenir lourde, et son tri se présente sous la forme élégante « Trier par : » + menu déroulant.
