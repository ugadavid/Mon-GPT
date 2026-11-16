# Sélectionner et classer plusieurs discussions

Mon GPT<3 **0.9.2** propose les mêmes gestes dans **Liste, Détaillée et Mosaïque**.

| Geste dans les résultats | Effet |
| --- | --- |
| Clic simple | Sélectionne une seule fiche. Le titre et ↗ conservent l’ouverture directe individuelle. |
| Ctrl+clic | Ajoute ou retire une discussion, sans ouvrir son lien. |
| Maj+clic | Sélectionne la plage depuis l’ancre, dans l’ordre visible après tri et filtres. |
| Ctrl+Maj+clic | Ajoute cette plage au lot courant. |
| Ctrl+A, résultats focalisés | Sélectionne toutes les discussions des résultats, même hors écran ; les projets sont exclus. |
| Flèches | Déplace la sélection simple ; en Mosaïque, navigation selon les colonnes de la grille. |
| Maj+flèches | Étend la plage vers la nouvelle focale ; les projets ne sont pas ajoutés. |
| Échap | Après les traitements d’édition/popup/drag existants, réduit un lot à une seule fiche sans fermer l’aperçu. |
| Clic droit sur le lot ou touche Menu | Affiche les commandes groupées et conserve la sélection. |

Ctrl+A dans la recherche et les champs continue de sélectionner **le texte**. Un projet peut être sélectionné seul ; cliquer un projet quitte le lot de discussions. Le passage entre vues conserve le lot. Un tri ou filtre conserve seulement les identifiants encore visibles ; changer de projet vide la sélection. Rien d’invisible ne reçoit une opération groupée.

À partir de deux discussions, un bandeau affiche le nombre de **fiches distinctes**, les trois actions et **Désélectionner**. Dans un centre étroit, les boutons deviennent Déplacer / Ajouter / Retirer ; leur nom complet reste accessible au survol et dans le menu. L’aperçu droit devient neutre : aucun titre, note ou éditeur d’une fiche isolée ne représente le lot.

Entrée, F2, Ctrl+S et les commandes d’édition individuelles sont bloqués tant qu’un lot reste actif. Un clic simple sur une fiche revient à une sélection unique ; l’ouverture directe redevient alors disponible pour cette fiche seulement. Le glisser d’un **lot** est explicitement désactivé : utiliser les commandes ci-dessous. Le glisser gauche/droit d’une **seule** fiche conserve son fonctionnement habituel. Aucun Ctrl+X / Ctrl+V ajouté.

## Ajouter, déplacer, retirer

- **Ajouter un rattachement…** : choisir un projet local. Les autres emplacements restent présents. Un lien déjà présent est compté comme inchangé. **Copier signifie ajouter un emplacement, jamais cloner une fiche.**
- **Déplacer des rattachements…** : choisir une destination et une source commune à tout le lot. Seule cette source sera retirée ; les autres emplacements restent présents. Le projet courant est prérempli seulement si tous les fils y sont directement rattachés. Depuis Tous les fils, choisir explicitement la source, même s’il n’y en a qu’une possible. Source = destination ne change rien.
- **Retirer un rattachement…** : choisir une source commune. Elle seule est retirée ; les fiches sans autre emplacement deviennent À classer. Aucune fiche supprimée.

Si tout le lot est À classer, Déplacer permet son premier classement sans source à retirer. Un lot mélangé classé/non classé, ou sans source commune, ne peut pas être déplacé silencieusement : choisir un lot homogène ou utiliser Ajouter. La racine n’est pas une destination de rattachement.

Les projets homonymes sont distingués par leur chemin **et leur UUID local intégral** dans les sélecteurs. La clé de décision est cet identifiant, jamais le nom.

## Vérifier puis confirmer

Le dialogue présente l’action, la source, la destination, les nombres de discussions modifiées, inchangées, déjà dans la destination et devenant À classer, puis quelques titres et classements résultants. **Annuler** ou Échap ne modifie rien. Les notes, descriptions, tags, catégories, métadonnées, autres emplacements, couvertures, UUID et URL sont préservés. La date de modification évolue uniquement pour les fiches effectivement reclassées.

**Confirmer** revérifie le plan et la sélection visible, puis enregistre le lot en **une seule écriture atomique**. Changement inattendu, projet supprimé, fiche périmée ou panne : refus complet, sans résultat partiel. Actualiser l’aperçu pour revoir le plan. Un lot inchangé ne provoque aucune écriture inutile.

Après réussite, l’arbre, les trois vues et l’aperçu sont rafraîchis. Une fiche déplacée hors du périmètre disparaît normalement des résultats et du lot. Les mappings ChatGPT, le schéma 4, les images et les sauvegardes restent inchangés. La sélection multiple n’est pas mémorisée au redémarrage ; aucun lot caché ne reprend une action.

[Rapport et captures fictives de la recette Windows](../reports/MG-010b/rapport.md).
