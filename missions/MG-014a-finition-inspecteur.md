# MG-014a — Finition graphique de l’inspecteur droit

**GO réalisation — étape 1 de finition après MG-014.**  
Point de départ : `origin/main` au commit MG-014 `7afb316`.  
Référence visuelle : [maquette MG-014](MG-014-graphisme/Interface%20GPT%20vert%20sauge%20et%20espace%20d%E2%80%99%C3%A9criture.png).

## Objectif unique

Faire franchir un cap graphique au **volet inspecteur de droite**, sans toucher au reste de l’application.

La recette humaine de MG-014 est positive : bandeau, explorateur, recherche et Liste sont désormais suffisamment proches de la direction souhaitée. **Ne les retravaille pas dans cette mission.**

L’inspecteur reste en revanche trop proche de l’ancienne interface. Nous voulons le rapprocher de la maquette : plus doux, plus composé, moins administratif.

## Travail demandé

1. **Sections de l’inspecteur**
   - Conserver exactement les sections et leurs données : Description/Résumé selon l’objet, Emplacements, Catégories, Tags, Notes, Informations.
   - Leur donner une vraie structure visuelle par **petits blocs très légers**, avec alternance ivoire/sauge extrêmement douce, filets fins et espacements cohérents.
   - Pas de gros bandeaux ni de blanc absolu `#FFFFFF`.
   - Les titres de section restent immédiatement lisibles, avec pictogrammes fins et cohérents.

2. **Zone identité / visuels**
   - Conserver la vignette et les **trois contrôles visuels existants** avec exactement leurs fonctions actuelles.
   - Les **regrouper graphiquement en un petit groupe cohérent**, dans l’esprit du groupe des icônes de vues.
   - Ne pas remplacer ces contrôles par d’autres actions (ouvrir/copier/etc.).

3. **Titre et fermeture**
   - Garder le titre réel de l’élément sélectionné comme tête de fiche et la fermeture en haut à droite.
   - Préserver projet vs discussion, sélection multiple, absence de sélection, focus, scroll et édition tels qu’ils fonctionnent aujourd’hui.

## Frontière

**Peinture et composition interne de l’inspecteur uniquement.**  
Aucun changement métier, aucune modification de données, aucun nouveau comportement, aucun déplacement de fonctions hors du volet droit.

**Hors périmètre de cette étape :**
- barre de création rapide du bas ;
- bandeau central ;
- Liste/Détaillée/Mosaïque ;
- explorateur gauche ;
- recherche et filtres ;
- glisser-déposer.

Si une idée exige une refonte du fonctionnement, ne pas la faire.

## GitHub — utiliser Marcel

Cette mission doit être publiée par notre compte technique partagé **Marcel / `Trucabule-M1`**, pas par `ugadavid`.

Avant toute publication :
- vérifier `gh auth status` ;
- si `Trucabule-M1` est disponible sur CODEX_VM, sélectionner explicitement ce compte (par exemple `gh auth switch -u Trucabule-M1`) puis vérifier l’accès au dépôt ;
- vérifier aussi l’auteur Git local (`git config user.name` / `git config user.email`). Pour cette mission, utiliser en configuration **locale au dépôt** `Trucabule-M1` / `marcel@trucabule.fr` si cette identité est acceptée par GitHub ;
- si Marcel n’est pas réellement disponible/autorisé sur la VM, **ne pas publier silencieusement sous ugadavid** : signaler clairement le blocage et s’arrêter avant le push.

Dans le rapport, distinguer **compte utilisé pour pousser** et **auteur du commit**.

## Recette et livraison

- Travail sur données fictives.
- Capturer **avant/après du même inspecteur**, idéalement un projet puis une discussion, sans multiplier les preuves.
- Vérifier les interactions immédiatement voisines : sélectionner projet puis fil, fermer/réouvrir l’inspecteur, édition visuelle existante, scroll/focus.
- Respecter les vérifications actuellement exigées par `AGENTS.md`, sans inventer de campagne supplémentaire hors sujet.
- Rapport bref : `reports/MG-014a/rapport.md`.
- Commit/push sur `origin/main`, SHA distant vérifié, dépôt propre.
- **STOP** après cette étape pour validation humaine. Ne pas commencer la barre du bas ni une autre finition.

**Critère d’acceptation : même inspecteur, mêmes informations et mêmes actions, mais une présentation nettement plus proche de la maquette MG-014.**
