# MG-014d — Bandeau responsive, groupe des vues et création rapide

**GO réalisation — étape suivante de finition graphique.**  
Point de départ : `origin/main` après MG-014c, commit `788997a`.

## Objectif

Terminer trois zones visuelles encore perfectibles, **sans ouvrir d’autre chantier** :

1. rendre le bandeau supérieur plus intelligent selon la largeur disponible ;
2. mieux regrouper les trois commandes Liste / Détaillée / Mosaïque ;
3. alléger la barre de création rapide du bas.

La direction MG-014 est validée. Il s’agit d’une passe de finition, pas d’une refonte.

## 1. Bandeau supérieur responsive

### Problème observé

À largeur moyenne ou grande, le bandeau paraît dispersé : logo/signature à gauche, grande illustration au centre, informations projet très loin à droite, alors que certaines informations restent malgré tout tronquées.

Sur un écran très large (jusqu’à 3840 × 2160 sur Zenith Ice), il faut au contraire **profiter de la place disponible**.

### Attendu

Conserver la structure actuelle :
- identité Mon GPT<3 à gauche ;
- illustration au centre ;
- informations du projet courant à droite.

Mais rendre leur mise en page **fluide selon la largeur** :

- ne pas tronquer artificiellement description, catégories, tags ou autres informations lorsque la fenêtre dispose de suffisamment de place ;
- afficher **davantage de contenu sur les grandes largeurs** ;
- conserver le comportement compact actuel sur petites largeurs ;
- l’illustration peut profiter raisonnablement de l’espace supplémentaire, sans écraser les informations projet ;
- conserver exactement les règles existantes projet courant / couverture / sélection de fil.

**Important :** ne pas transformer le bandeau en ligne pleine largeur au-dessus des trois colonnes. Le squelette validé reste intact.

### Recette visuelle

Comparer au minimum :
- ~1000 px de large ;
- largeur confortable CODEX_VM ;
- largeur très large simulée/observable si possible.

Le contenu doit être plus complet quand la largeur augmente, pas simplement plus espacé.

## 2. Regrouper les trois commandes de vues

Les trois commandes Liste / Détaillée / Mosaïque doivent être perçues comme **une seule famille**.

- Les décaler visuellement d’environ **30 px vers la droite** par rapport aux commandes filtre / effacer.
- Les regrouper dans un ensemble léger commun : contour discret ou surface commune.
- Conserver trois icônes distinctes, état actif sauge, infobulles/noms accessibles.
- Ne changer ni `set_view`, ni les valeurs/persistances/raccourcis des trois modes.

Le but est seulement de clarifier visuellement : **filtres d’un côté, choix de vue de l’autre**.

## 3. Barre de création rapide du bas

Rester simple et conserver **strictement le parcours de création existant**.

### 3.1 Message d’erreur

- Ne plus utiliser une alerte rouge agressive pour les erreurs de saisie.
- Employer une nuance chaude/terracotta douce et discrète, lisible mais non alarmiste.
- Ne pas changer les validations ni les messages métier.

### 3.2 Action principale

Le bouton actuel `Ajouter le fil` est trop lourd visuellement.

- Utiliser un vert plus pâle / sauge compatible avec la charte.
- Remplacer le libellé par une formulation plus légère, par exemple **`→ Ajouter`** ou une icône d’ajout + `Ajouter`.
- Conserver exactement la même action, validation et raccourci.

### 3.3 Annuler

- Placer `Annuler · Échap` **à gauche** de l’action principale.
- Laisser une respiration réelle entre les deux commandes, environ **20 px visuels**, pas des boutons collés.
- Conserver Échap.

### 3.4 Clic hors du formulaire

Ajouter un comportement local :
- lorsqu’un brouillon de création est ouvert, **cliquer clairement en dehors du cadre de création ferme/annule le brouillon**, comme Échap/Annuler ;
- ne pas déclencher cette annulation si le clic appartient à un contrôle, popup, menu ou sélecteur faisant partie du formulaire ;
- ne jamais enregistrer implicitement ;
- préserver la protection contre les pertes involontaires si une logique équivalente existe déjà.

Ce point est le seul changement comportemental de la mission ; il doit rester strictement local.

## Hors périmètre

Ne pas toucher :
- à l’inspecteur droit validé en MG-014c ;
- à l’explorateur gauche ;
- à la Liste elle-même ;
- au glisser-déposer ;
- aux modèles métier, stockage, imports, sauvegardes ;
- aux données ou schémas.

Ne pas ajouter d’autres idées graphiques dans cette mission.

## Tests proportionnés

Cette mission reste une modification UI ciblée. Appliquer `AGENTS.md` :

- L0 statique ;
- tests existants ciblant bandeau/layout, vues et création intégrée ;
- recette Windows courte couvrant les trois largeurs du bandeau, les trois vues, erreur de saisie, Annuler/Échap, clic hors formulaire et création réussie ;
- **pas de suite complète des 203 tests** sauf découverte d’un impact transversal ou d’une régression non localisée.

Rapporter explicitement les tests exécutés et non exécutés.

## GitHub — Marcel

Publier avec **Marcel / `Trucabule-M1`**.

Avant publication :
- `gh auth status` : `Trucabule-M1` actif ;
- identité Git locale : `Trucabule-M1 <marcel@trucabule.fr>`.

Ne pas publier sous `ugadavid` par défaut.

## Livraison

- Données fictives uniquement.
- Rapport bref : `reports/MG-014d/rapport.md`.
- Captures utiles, sans collection redondante.
- Commit/push `origin/main`, SHA distant vérifié, dépôt propre.
- **STOP pour recette humaine.**

**Critère d’acceptation :** sur grand écran le bandeau exploite réellement l’espace au lieu de l’étirer ; les trois vues forment un groupe visuel clair ; la création rapide reste la même fonction mais devient plus discrète, plus agréable et plus naturelle à quitter.
