# MG-014c — Contexte de l’inspecteur et re-sélection du projet courant

**GO réalisation — correction ciblée après MG-014b.**  
Point de départ : `origin/main` après MG-014b, commit `ae18877`.

## Objectif

Corriger deux écarts très localisés dans l’inspecteur droit :

1. améliorer l’affichage du contexte sous le titre ;
2. corriger le comportement lorsqu’on reclique dans l’explorateur gauche sur le projet déjà courant alors qu’un fil est affiché dans l’inspecteur.

Cette mission reste petite. Ne pas ouvrir un nouveau chantier graphique.

## 1. Alignement du pictogramme du titre

La recette humaine montre que le pictogramme placé à gauche du titre paraît encore trop haut.

- Centrer réellement le pictogramme verticalement sur la première ligne du titre.
- Vérifier le rendu sur un titre court et sur un titre qui passe sur deux lignes.
- Ne modifier ni la taille du titre ni sa logique.

## 2. Contexte sous le titre — règles exactes

Le libellé actuel `À la racine` est jugé inutile et trop mécanique.

Appliquer les règles suivantes :

- **Projet racine** : n’afficher **aucune ligne de contexte** sous le titre.
- **Projet dans un dossier/projet parent** : afficher le nom du parent.
- **Discussion dans un projet** : afficher le nom du projet ou le contexte déjà calculé par l’application, sans changer la logique des rattachements.

Pour un contexte affiché :
- traitement visuel plus élégant et secondaire ;
- pictogramme du projet/dossier juste avant le nom ;
- reprendre sa couleur/identité visuelle si l’information est déjà disponible sans nouvelle logique métier ;
- léger retrait horizontal (environ 10 px visuels) pour casser l’effet trop carré ;
- pas de nouveau menu déroulant, pas de nouveau contrôle fonctionnel.

Le but est d’améliorer l’information existante, pas de créer un nouveau système de navigation.

## 3. Bug de re-sélection du projet courant

### Comportement observé

- Le projet `Écriture` est le scope courant.
- L’utilisateur clique sur un fil dans la Liste : l’inspecteur affiche correctement la fiche du fil.
- L’utilisateur reclique ensuite sur **Écriture** dans l’explorateur gauche.
- Le scope ne change pas, donc le code sort actuellement trop tôt de `select_scope()`.
- Résultat : l’inspecteur reste sur le fil au lieu de revenir à la fiche du projet sur lequel l’utilisateur vient explicitement de cliquer.

### Comportement attendu

**Cliquer sur un projet dans l’explorateur doit toujours afficher sa fiche dans l’inspecteur**, même si ce projet est déjà le scope courant.

Conserver :
- le scope courant ;
- les résultats affichés ;
- la recherche/filtres ;
- l’état de l’arbre ;
- les rattachements ;
- tout le reste du comportement actuel.

Corriger uniquement l’intention de sélection : un clic explicite sur le projet courant doit remettre ce projet comme identité courante de l’inspecteur.

## 4. Ne pas revenir sur MG-014b

Les sections successives ivoire/sauge et les filets fins livrés dans MG-014b sont conservés.

Ne pas refaire :
- la structure des sections ;
- la Liste ;
- le bandeau ;
- la barre du bas ;
- les vues Détaillée/Mosaïque ;
- les contrôles visuels de l’inspecteur.

## 5. Tests proportionnés

`AGENTS.md` définit désormais les vérifications proportionnées.

Cette mission relève de **L1 — domaine ciblé**.

Attendu :
- tests existants ciblant navigation/sélection/inspecteur et tout test directement modifié ;
- courte recette Windows : projet → fil → re-clic sur le même projet → inspecteur revenu au projet ;
- contrôle visuel du contexte racine / parent et de l’alignement du pictogramme ;
- **ne pas relancer automatiquement les 203 tests** sauf découverte d’un impact transversal ou régression non localisée.

Le rapport doit préciser ce qui a été lancé et ce qui ne l’a pas été.

## 6. GitHub — Marcel

Publier avec **Marcel / `Trucabule-M1`**.

Avant publication :
- vérifier `gh auth status` ;
- vérifier que `Trucabule-M1` est actif ;
- conserver l’identité Git locale : `Trucabule-M1 <marcel@trucabule.fr>`.

## 7. Livraison

- Données fictives uniquement.
- Rapport bref : `reports/MG-014c/rapport.md`.
- Une ou deux captures utiles suffisent.
- Commit/push sur `origin/main`, SHA distant vérifié, dépôt propre.
- **STOP** après publication pour validation humaine.

**Critère d’acceptation :** le haut de fiche est visuellement propre, un projet racine n’affiche plus « À la racine », un projet enfant affiche élégamment son parent, et recliquer sur le projet courant dans l’explorateur ramène toujours sa fiche dans l’inspecteur.
