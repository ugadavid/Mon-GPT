# MG-014b — Corrections fines de l’inspecteur droit

**GO réalisation — correction ciblée après MG-014a.**  
Point de départ : `origin/main` après MG-014a, commit `724c321`.  
Référence visuelle principale : [maquette MG-014](MG-014-graphisme/Interface%20GPT%20vert%20sauge%20et%20espace%20d%E2%80%99%C3%A9criture.png).

## Objectif

Corriger quelques écarts visuels restants dans **l’inspecteur droit uniquement**, sans toucher au fonctionnement ni aux autres zones de l’application.

MG-014a a amélioré la direction graphique, mais la recette humaine montre encore quatre points précis à corriger.

## Corrections demandées

### 1. Aligner l’icône du titre

L’icône de type d’élément placée à gauche du titre (par ex. le crayon pour un projet) paraît trop haute.

- La **centrer verticalement par rapport à la ligne du titre**.
- Ne modifier ni la taille du titre ni la logique de choix de l’icône.
- Conserver la fermeture en haut à droite.

### 2. Adoucir l’information contextuelle sous le titre

Le texte `À la racine` (ou l’emplacement affiché pour d’autres objets) est aujourd’hui trop mis en avant et peut donner l’impression d’un second titre.

- **Ne changer aucune logique fonctionnelle** : l’historique a été vérifié, il s’agit bien d’un libellé statique existant, pas d’un menu déroulant supprimé.
- Conserver la valeur réelle calculée par l’application.
- La traiter graphiquement comme une **information secondaire/contextuelle** : plus discrète, mieux intégrée au haut de fiche.
- Ne pas inventer de nouveau contrôle, de nouvelle liste déroulante ni de nouveau parcours.

### 3. Conserver les contrôles visuels séparés

La maquette initiale suggérait un regroupement, mais la recette humaine préfère finalement la solution actuelle.

- **Conserver les contrôles visuels séparés**.
- Ne pas revenir à un groupe forcé.
- Harmoniser seulement leur alignement, leurs espacements et leur cohérence graphique si nécessaire.
- Ne remplacer aucune action par une autre.

### 4. Refaire le traitement des sections — correction principale

Les blocs `Description/Résumé`, `Emplacements`, `Catégories`, `Tags`, `Notes`, `Informations` sont actuellement trop perçus comme des **cartes encadrées**.

La cible est plus subtile, comme dans la maquette :

- sections qui **se succèdent naturellement** ;
- alternance ivoire / sauge **très légère** ;
- **filet fin** ou transition discrète entre les zones ;
- beaucoup moins d’effet « boîte » ;
- pas de contour arrondi marqué autour de chaque rubrique ;
- titres de section et pictogrammes fins conservés ;
- aucune perte de lisibilité, de scroll ou d’accès aux notes longues.

En pratique : réduire fortement la présence des contours et passer d’une logique de cartes séparées à une logique de **panneau éditorial continu**.

## Frontière absolue

**Graphisme seulement.**

Ne pas toucher :
- au modèle métier ;
- aux données ;
- à la logique projet/discussion ;
- aux emplacements/rattachements ;
- à l’édition ;
- au scroll/focus ;
- aux autres colonnes ;
- au bandeau central ;
- à la Liste/Détaillée/Mosaïque ;
- à la barre de création du bas ;
- à la recherche/filtres ;
- au glisser-déposer.

Si une amélioration exige un changement fonctionnel, ne pas la faire et la signaler.

## GitHub — Marcel

Publier cette mission avec **Marcel / `Trucabule-M1`**.

Avant publication :
- vérifier `gh auth status` ;
- vérifier que `Trucabule-M1` est actif ;
- conserver l’identité Git locale du dépôt : `Trucabule-M1 <marcel@trucabule.fr>`.

Si Marcel n’est plus actif, ne pas pousser sous `ugadavid` par défaut.

## Recette et livraison

- Données fictives uniquement.
- Comparer **avant/après du même inspecteur**, idéalement un projet puis une discussion.
- Vérifier seulement les interactions voisines : sélection projet puis discussion, fermeture/réouverture, édition visuelle existante, scroll des notes longues.
- Respecter les obligations actuellement actives de `AGENTS.md`, sans ajouter de campagnes hors sujet.
- Rapport bref : `reports/MG-014b/rapport.md`.
- Commit/push sur `origin/main`, SHA distant vérifié, dépôt propre.
- **STOP** après publication pour validation humaine.

**Critère d’acceptation :** même inspecteur, mêmes informations et mêmes actions, mais un haut de fiche mieux aligné et des sections nettement plus fluides, fines et proches de la maquette.
