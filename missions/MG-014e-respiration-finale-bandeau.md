# MG-014e — Respiration finale du bandeau supérieur

**GO réalisation — micro-correction après MG-014d.**  
Point de départ : `origin/main` au commit MG-014d `0cd306a`.

## Constat de recette

MG-014d est validée sur ses autres points : groupe des vues, création rapide et comportement responsive général.

Il reste **un seul défaut graphique** : lorsque l’inspecteur droit est fermé, la colonne centrale devient très large et le bandeau paraît trop étiré / dispersé. Les trois sous-ensembles existent bien, mais ils ne composent pas encore un ensemble assez cohérent :

1. logo + nom + signature ;
2. illustration ;
3. informations du projet.

Avec l’inspecteur ouvert, le rendu est déjà satisfaisant. **Ne dégrade pas ce cas pour corriger l’autre.**

## Objectif unique

Améliorer la **respiration horizontale** du bandeau, en particulier quand l’inspecteur est fermé et que la largeur centrale augmente fortement.

### Attendu

- Conserver strictement les trois zones actuelles et leur ordre.
- Ajouter un **espace visuel plus généreux** entre :
  - le bloc identité/logo et le début de l’illustration ;
  - la fin de l’illustration et le bloc d’informations du projet.
- Éviter l’effet « trois îlots perdus sur une immense ligne » : les trois blocs doivent rester perçus comme **une composition commune**, même sur grande largeur.
- Le contenu projet doit continuer à profiter de la largeur disponible : ne pas réintroduire de troncature inutile.
- L’illustration peut garder son plafond actuel ; l’objectif n’est pas de la faire grossir indéfiniment.
- Conserver la silhouette organique, les informations projet, catégories/tags, slogan et comportement compact actuels.
- Ne pas modifier la hauteur du bandeau ni le squelette des trois colonnes.

### Intention de mise en page

Sur les largeurs normales et grandes, prévoir des **gouttières explicites et stables** entre les trois sous-blocs plutôt que de laisser la géométrie dépendre seulement de la largeur restante. Une respiration de l’ordre de quelques dizaines de pixels est attendue ; choisir la valeur réelle d’après le rendu, pas au pixel près.

Le résultat doit rester équilibré :
- inspecteur ouvert : proche du rendu actuel déjà validé ;
- inspecteur fermé : davantage d’air entre logo ↔ image ↔ informations, sans grand vide absurde ni contenus repoussés aux extrêmes.

## Hors périmètre

**Ne toucher à rien d’autre.**

Sont déjà validés et hors mission :
- inspecteur droit ;
- explorateur gauche ;
- Liste / Détaillée / Mosaïque ;
- groupe des trois vues ;
- recherche/filtres ;
- barre de création rapide ;
- glisser-déposer ;
- données et logique métier.

## Tests proportionnés

Mission **L1 UI locale** selon `AGENTS.md`.

- contrôle statique du module modifié ;
- recette visuelle ciblée du bandeau avec inspecteur ouvert puis fermé ;
- vérifier au minimum une largeur CODEX_VM confortable et une très grande largeur ;
- vérifier qu’aucune information qui tenait auparavant n’est artificiellement tronquée ;
- **pas de suite complète**.

Une ou deux captures comparables suffisent.

## GitHub — Marcel

Publier avec **Marcel / `Trucabule-M1`** :
- vérifier `gh auth status` ;
- identité Git locale `Trucabule-M1 <marcel@trucabule.fr>`.

## Livraison

- Rapport bref : `reports/MG-014e/rapport.md`.
- Commit/push sur `origin/main`.
- SHA distant vérifié, dépôt propre.
- **STOP pour validation humaine.**

**Critère d’acceptation :** avec ou sans inspecteur, le bandeau reste aéré et composé ; fermer l’inspecteur ne transforme plus logo, illustration et informations projet en trois éléments trop éloignés ou trop collés.
