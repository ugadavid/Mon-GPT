# MG-011 — Finitions fonctionnelles : informations visibles, navigation, éditeur et aide

**Mission Codex — GO utilisateur pour réaliser ce lot ; STOP à la livraison pour recette David/GPT.**  
**Base validée en recette :** Mon GPT<3 **0.9.3 / MG-010c**, commit `189891436c85591a3e0fd5e3973e1e9ee7ffd353`.  
**Version cible indicative : 0.9.4.** Collector Chrome 0.8.2 inchangé.

## 0. Frontière fonctionnel / graphique : PAS de séparation artificielle

David souhaite **achever aujourd'hui les modifications fonctionnelles relevées sur treize captures réelles**, puis réserver **à demain uniquement le travail purement graphique**.

**Précision expresse de l'utilisateur :** la transformation de l'aide / « À propos » en **vraies fenêtres dédiées** est bien **fonctionnelle** (nouvel objet et nouvelle organisation de contenu), même si la présentation change. **Ces deux fenêtres font partie de MG-011.**

Les fonctionnalités demandées ci-dessous peuvent exiger de légers ajustements de place, dimension, alignement ou hauteur pour devenir lisibles : **les effectuer maintenant**. Reporter seulement la direction artistique : refonte de la palette, design des cartes et du bandeau, gestion esthétique des illustrations héritées répétitives, décoration et harmonie fine des composants.

Nous travaillons sur **Mon GPT<3 uniquement**, avec un seul lot coordonné. Pas de nouveau projet, tableau de bord, statistiques, installateur, nouveaux schémas métier, migration Collector ni fonctionnalités non demandées.

**Philosophie :** application personnelle toujours en recette ; simplicité et fluidité, **aucune étape artificielle de confirmation ou surprotection des données de test**. Conserver la logique existante de sauvegarde des fiches quand on en édite les champs.

## 1. Extraits des notes, résumés et métadonnées dans Détaillée et Mosaïque

**Constat source :** dans la capture de 15 h 06 du 16/11, une fiche porte littéralement la note « Rien de cette note ne s'affiche nulle part ailleurs. Voir à l'afficher sur les vues détaillées et mosaïque. » ; elle n'apparaît actuellement que dans l'inspecteur/éditeur. Les cartes Mosaïque affichent surtout l'image et le titre ; dans un même projet les images héritées sont souvent identiques.

**Attendu :**
- Alimenter les données de rendu des deux vues à partir de **`Record.notes`, `description` (résumé), `categories`, `tags`**, en plus des informations existantes. Dans `mon_gpt/ui.py`, `refresh_results()` fournit pour l'instant `summary=r.description`, les catégories et tags, **mais pas les notes**.
- **Détaillée :** montrer clairement et séparément **Résumé** (s'il existe) et **Note** (si elle existe) sous forme d'extraits courts, sans les confondre ; conserver le titre, les emplacements, catégories et tags. Ne pas afficher « Aucune note » sur chaque ligne vide.
- **Mosaïque :** rendre la fiche utile même quand toutes les couvertures héritées sont identiques : au moins un **extrait des notes et/ou du résumé**, et les catégories/tags quand présents. Prévoir une disposition compacte et lisible selon **Cartes normales / grandes**, avec hauteur de carte ajustée si nécessaire ; ne pas couper le titre pour ajouter un extrait. Éviter le pavé documentaire et les pastilles interminables : deux lignes ou quelques mots + « … » / « +N » sont acceptables. S'il n'y a ni résumé ni note ni tag ni catégorie, garder un rendu sobre sans zones vides.
- L'information textuelle complète reste accessible via l'inspecteur et, si utile, une infobulle de la carte. Une note n'est **pas** une description : les deux valeurs restent distinctes.
- Les données peuvent être filtrées/triées comme aujourd'hui ; ne pas ajouter un nouvel éditeur directement dans les cartes.
- **Clic = sélectionner ; ↗ seul = ouvrir** dans les deux vues. Glisser gauche/droit une ou plusieurs fiches, Ctrl/Maj, F2, sélection, clavier, défilement, hit-tests et parcours « 1 429 fils » restent fonctionnels.
- Un **petit changement de géométrie des cartes** nécessaire à l'affichage constitue une exigence fonctionnelle de ce lot, pas une refonte graphique. **La variation esthétique de l'illustration répétée reste pour demain.**

## 2. Bandeau : informations du dossier même sans panneau droit

**Constat utilisateur :** sélectionner un **dossier** dans l'arbre ne donne quasiment aucune information documentaire si l'inspecteur droit est fermé. Le bandeau montre surtout la couverture.

**Attendu :**
- Quand le contexte actif est un **projet sélectionné dans l'arbre**, afficher **à gauche de sa couverture dans le bandeau supérieur** un résumé documentaire compact :
  - **catégorie(s)** du projet, pastilles limitées avec « +N » si nécessaire ;
  - **tag(s)** du projet, idem ;
  - **un extrait de sa description** si disponible et si l'espace le permet (sans pousser l'image hors écran).
- **Utiliser les métadonnées du projet courant (scope)**, pas celles de la conversation sélectionnée qui pourrait changer l'identité visuelle au même moment. L'objectif est de renseigner sur le *dossier* sans afficher l'inspecteur.
- État « Tous les fils » / « À classer », projet sans métadonnées, espace étroit, panneau droit ouvert/fermé : **aucune pastille factice, aucun chevauchement avec logo, titre ou couverture**. Le bandeau garde une hauteur raisonnable et une information intelligible. Le détail complet reste accessible dans l'inspecteur.
- Réutiliser les composants ou logique de pastilles et le `ContextMasthead` existants, sans inventer de nouveau thème. Éviter les redraws coûteux ou les confusions lorsque la sélection d'un fil change sans changement de projet.
- Le bandeau ne doit pas enregistrer de données : il est **lecture seule**.

**Points de code :** `mon_gpt/identity_ui.py` `ContextMasthead`, `mon_gpt/ui.py` `update_identity`, `select_scope`, `toggle_inspector`, `refresh_results`; `mon_gpt/core.py` `Record.description/categories/tags`.

## 3. Navigation gauche : épingler « Tous les fils » et « À classer »

**Constat sur les captures :** dès que l'arbre descend parmi les dizaines de projets, les deux entrées générales quittent l'écran. Elles doivent toujours être accessibles.

**Attendu :**
- Épingler **« Tous les fils » et « À classer » au-dessus de la zone défilante de projets**, sous le titre et le tri. **Seuls les projets et sous-projets défilent** verticalement.
- Une seule navigation logique : le projet sélectionné, le pseudo-périmètre sélectionné, le filtre en cours et l'inspecteur doivent rester cohérents, sans double sélection visuelle contradictoire.
- Si l'on garde un seul `NavigationTree` sous-jacent, utiliser une solution réellement fixe/épinglée et non deux fausses entrées supplémentaires qui détournent les événements. Si l'on scinde en contrôles fixes + arbre projets, **adapter explicitement** `refresh_tree`, `select_scope`, la restauration de session, raccourcis, navigation clavier, focus, clic droit, accessibilité et les appels à `tree.exists/selection_set/identify_row/see`.
- **Important :** les cibles de **glisser-déposer** continuent à fonctionner sur les projets. La sémantique actuelle d'un dépôt sur « Tous les fils » ou « À classer », lorsqu'elle existe, ne doit pas être silencieusement modifiée. Ne pas transformer « À classer » en dossier réel.
- Le **tri manuel / alphabétique**, la hiérarchie parents/enfants, l'ouverture des branches et les déplacements de projets restent identiques. Panneau gauche utilisable à 1000×680.

## 4. Titre et décompte du centre : « Contenu du projet » quand nécessaire

**Constat :** dans un projet parent, la zone centrale contient **sous-projets immédiats et fils directement rattachés**, mais le titre demeure « Discussions ».

**Attendu :**
- Lorsque l'on affiche un projet, utiliser un intitulé **« Contenu du projet »** (ou « Contenu de [nom] » si cela reste lisible).
- Quand sous-projets et fils sont mélangés, afficher **un décompte différencié**, par exemple « 4 discussions · 2 sous-projets », cohérent avec les filtres et le périmètre **direct** validé MG-010a. Si un seul type est présent, un compteur adapté suffit.
- Dans « Tous les fils » et « À classer », **« Discussions »** reste approprié.
- Aucun changement au modèle métier ni à la logique de recherche ; respecter la hiérarchie directe (ne pas revenir au mélange récursif).
- Les boutons « + Fil », « Aperçu », Liste/Détaillée/Mosaïque et les tris conservent leur place et leur sens.

## 5. Éditeur : rendre les emplacements pertinents avant le reste du long formulaire

**Constat :** dans l'éditeur d'une discussion (capture du 16/11 à 15 h 06), « Emplacements » est tout au bout après Notes, Tags, Catégories et Informations. Sa Listbox montre les premiers projets alphabétiques même lorsque l'on est dans « BHE / Réflexion », et oblige à défiler sans voir immédiatement les rattachements actuels.

**Attendu :**
- Pour une **discussion**, placer **« Emplacements » près du haut de l'éditeur**, juste après le titre/identité (et éventuellement le lien), avant les longs champs Résumé, Notes et Informations.
- Montrer **sans défilement** le ou les **projets actuellement rattachés**, via une petite zone « Actuellement dans : BHE / Réflexion, … ». Un fil à classer affiche clairement « À classer ». Aucune perte d'identité lors de projets homonymes (utiliser la logique de libellés lisibles validée MG-010b-01, sans GUID inutile).
- Conserver un moyen **simple et explicite** d'ajouter / retirer des rattachements dans l'éditeur, par la liste multi-sélection actuelle améliorée ou un sélecteur compact. Si la liste de tous les projets subsiste, **mettre les projets déjà sélectionnés en évidence ET visibles en premier / accessibles**, plutôt que de laisser l'utilisateur regarder les premiers projets alphabétiques qui n'ont aucun rapport avec le fil. Éviter de dupliquer les champs ou de demander une seconde confirmation.
- Garder la règle actuelle de l'éditeur : **Enregistrer** applique les changements ; quitter sans enregistrer respecte les gestes existants. Les opérations de drag et menu du centre restent directes comme MG-010b-01.
- Pour une **fiche projet**, garder « Projet parent » intelligible dans la même logique, sans ajouter les emplacements multiples qui ne concernent que les fils.
- Aucune mutation des emplacements/tags/notes simplement en ouvrant l'éditeur, et les saisies existantes, F2, Enregistrer, Annuler, sélection multiple, sauvegardes et import restent compatibles.

**Points de code :** `mon_gpt/details.py` `render_editor`, `self.project_ids`, `self.locations`, `clear_locations`, `save_record`, `can_leave`.

## 6. Aide et À propos : de VRAIES fenêtres fonctionnelles (MAINTENANT)

**Correction explicite du périmètre par David :** ce n'est **pas** un chantier graphique « demain ». Remplacer les boîtes Windows `messagebox.showinfo` par de **vraies fenêtres dédiées et structurées**, dès MG-011.

**Aide — « Gestes et raccourcis » :**
- Fenêtre propre à l'application, lisible, avec **rubriques distinctes** (navigation, sélection simple/multiple, glisser gauche/droit, classement, ouvrir ↗, édition, colonnes/recherche, raccourcis) ; défilement si nécessaire.
- Le contenu doit refléter **exactement le comportement actuel de 0.9.3**, notamment **titre ne fait que sélectionner, ↗ seul ouvre**, Alt+Entrée pour l'action focalisée, Ctrl/Maj, drag multiple et colonnes administrables. Plus de phrase périmée « Un clic sur le titre ouvre ».
- Fenêtre redimensionnable si utile, fermeture visible, **Échap / bouton Fermer**, accès clavier, focus rendu à la fenêtre principale. Pas de pavé de texte tout tassé dans une messagebox.
- Rester dans les composants visuels *actuels* de l'Atelier chaleureux sans refonte de thème.

**À propos :**
- Fenêtre dédiée, affichant **Mon GPT<3**, sa **version exacte**, le rôle de gestion locale, l'information que les actions de classement sont **locales** (pas de modification du compte ChatGPT), et éventuellement **le site Trucabule** ou **le dépôt GitHub** avec liens ouverts explicitement dans le navigateur.
- Ne pas inventer de licence, d'auteur, de copyright ou de contacts. Pas de données personnelles ajoutées au dépôt.
- Même conventions de fermeture, focus et accessibilité que l'Aide. Possibilité d'utiliser un composant commun léger pour les fenêtres d'information, mais pas de création de framework générique.

**Demain uniquement :** une éventuelle passe de direction artistique approfondie sur ces fenêtres (typographie décorative, illustration, palette), si besoin.

## 7. Menu Affichage : retirer les deux tailles de fenêtre imposées

Les commandes actuelles :
- « Fenêtre compacte · 1000 × 680 »
- « Fenêtre confortable · 1360 × 820 »

Ce sont des **raccourcis de recette**, non des changements de résolution écran. **Les supprimer du menu Affichage** (et de l'aide si elles y figurent). La fenêtre reste **redimensionnable librement** par les contrôles Windows et sa taille reste mémorisée dans `interface.json`.

Ne pas supprimer les capacités internes/tests `resize()` ou les tests de dimensions compactes. **Ne pas introduire d'autres tailles prédéfinies.**

## 8. Vérifications de régression et recette Windows

Base : **192 tests Python + 43 JS** validés en MG-010c. Ajouter des tests fonctionnels et événements Tk, sans réduire la couverture historique.

### Contrôles incontournables
1. **Note distincte du résumé** : un fil contenant un résumé et une note très longue, un autre uniquement une note, un autre uniquement un résumé, un autre aucun champ ; Détaillée et Mosaïque affichent des extraits corrects, sans zones vides, en cartes normales/grandes et fenêtres compactes. Aucune mutation des notes au changement de vue.
2. **Mosaïque de 10 fils héritant de la même couverture** : cartes distinctes par titre et métadonnées, zéro relance de recherche/rendu superflu, ↗ uniquement pour ouvrir ; sélection Ctrl/Maj et drag d'un lot restent corrects.
3. **Bandeau scope projet**, panneau droit fermé : catégories, tags et éventuelle description visibles ; projet vide / Tous / À classer n'affichent pas de faux badges ; sélection d'un fil ne remplace pas silencieusement les tags du dossier dans cette zone. Test sur largeur 1000 et 1600.
4. **Épinglage** : scroller jusqu'au 58e projet ; « Tous les fils » et « À classer » restent visibles et cliquables, sélection et périmètre corrects, retour sur projet ; tri et expansion préservés ; glisser un fil/lot sur un projet continue à fonctionner. Tester événements Tk et accès clavier.
5. **Contenu du projet** : dossier parent avec deux enfants et trois fils directs : titre et compte « 3 discussions · 2 sous-projets », descendant indirect absent ; « Tous » et « À classer » affichent « Discussions » ; filtre modifie les comptes de façon cohérente.
6. **Éditeur** : une fiche dans 2 projets avec homonyme de nom, une à classer, une avec note ; emplacements actuels visibles au début, modifications par utilisateur puis Enregistrer, annulation sans effet ; notes/tags/identités intactes.
7. **Vraies fenêtres Aide et À propos** : fenêtres dédiées avec rubriques/texte véridique, fermeture Échap et bouton, focus, version, pas de mention erronée du clic sur titre. Vérifier 1000×680 et texte français.
8. **Menu Affichage** : les deux commandes de tailles prédéfinies absentes ; reste des fonctions Liste/Détaillée/Mosaïque/Colonnes/recherche/filtres conservé ; dimensionnement libre et persistance valides.
9. **Régressions** MG-010a/b/b-01/c : clic titre sélectionne sans ouvrir, ↗ seul ouvre, drag gauche/droit un/lot, colonnes configurables et dates triées, sélection Ctrl/Maj/Ctrl+A, recherche, dossiers directs, image picker, sauvegarde/restauration, import Collector v2 idempotent ; catalogue schéma 4 et mappings inchangés.
10. **Charge** : catalogue isolé de **1 429 conversations entièrement fictives**, fenêtre 1000×680 et 1600×900 ; défilement, grandes cartes, sélection rapide, transitions de vues ; ne pas publier les captures du catalogue réel.

**Recette Windows sur CODEX-VM** : `python -m mon_gpt --data-dir .recette/MG011 --simulate-open`, avec projets parents/enfants, homonymes, métadonnées, notes/résumés non vides, couvertures identiques héritées et lots. Puis **David valide sur sa propre bibliothèque**.

## 9. Livrables et STOP

- Code Python maintenable, tests nouveaux + historiques, actualisation du guide d'aide et de `README.md`.
- `reports/MG-011/rapport.md` : contrôle par section (1 à 7), nombre de tests, bilan Windows, limites.
- **Six à huit captures Windows natives** sur données fictives : Détaillée avec note, Mosaïque enrichie, bandeau projet avec inspecteur fermé, navigation épinglée en bas d'arbre, éditeur/rattachements, fenêtres Aide et À propos ; captures sans données personnelles.
- Commit/push `origin/main`, SHA distant vérifié, dépôt propre.
- **STOP après MG-011** ; ne pas lancer spontanément demain la passe graphique, les statistiques, le tableau de bord ou la distribution.

### Critère GO

Sur la même version, David peut **lire une note courte et ses catégories/tags sans ouvrir l'éditeur**, connaître rapidement la nature d'un dossier même **inspecteur fermé**, retrouver **Tous les fils / À classer** même avec l'arbre tout en bas, distinguer **discussions et sous-projets**, voir **ses rattachements actuels en haut de l'éditeur**, consulter de **vraies fenêtres Aide / À propos**, et ne plus voir les deux tailles de fenêtre de recette dans Affichage.

**Ne différer que l'esthétique de fond : pas les objets et interactions fonctionnels ci-dessus.**
