# MG-005 — Vue Mosaïque : la bibliothèque d'images, enfin !

**Statut : mission à réaliser, puis recette de David.**  
**Base vérifiée :** `origin/main` au commit `64638d51b0b2a9c9d4d599e28d2e5091889e31b1`, **Mon GPT<3 v0.4.1**, **100 tests réussis**. MG-004a, reprise de l'espace de travail, est **validée**.  
**Périmètre :** construire **seulement** la troisième vue centrale, **Mosaïque**. Ne pas relancer une refonte graphique globale, ne pas modifier le catalogue des projets et ne pas commencer l'extension Chrome.

## 1. L'intention utilisateur et l'enseignement des recettes précédentes

Référence : `missions/MG-002-maquettes/01_specification_UX.md`, section « Trois modes de présentation » :

> **Liste = efficacité · Détaillée = équilibre · Mosaïque = plaisir visuel.**

Les trois vues explorent **le même catalogue, les mêmes résultats, les mêmes sélections et filtres**. Leur présentation seule diffère.

**Mosaïque doit donner toute sa place aux couvertures déjà créées** : un ensemble de cartes illustrées disposées en grille adaptative. Le visuel doit dominer ; le texte sert à identifier l'objet, et non à répéter les métadonnées.

**Retour utilisateur impératif après MG-004 :** éviter de répéter `Le jardin des récits / Carnet de lumière` sur **chaque carte**, alors que le périmètre apparaît déjà à gauche et dans les pastilles au-dessus des résultats. Cette répétition a été explicitement jugée lourde.

**Surtout ne pas reproduire une vue Détaillée avec des lignes plus hautes.** Nous voulons une véritable **grille de tuiles**, avec plusieurs colonnes et de grandes images.

## 2. Composition d'une mosaïque — simple, soignée, utile

Chaque tuile comporte :

1. **Grande couverture** du projet, ou du projet dont hérite le fil, en format **16:9 intégral** ; pas de recadrage massif, ni d'étirement. Pour une image personnelle portrait, voir toute la scène avec marges harmonisées.
2. **Titre** clairement lisible sous l'image, limité à ~2 lignes ; accès au titre complet par infobulle/focus quand nécessaire.
3. **Petite icône** personnalisée dans sa **couleur** ; visible mais non dominante, idéalement près du titre ou dans un coin discret hors du sujet important de l'image.
4. **Au plus une information secondaire contextuelle, uniquement si elle est utile** : par exemple une catégorie OU une pastille de tag, pas une série de colonnes, ni les chemins complets, ni toutes les notes. Si toutes les cartes partagent le même projet, **ne pas répéter son nom**. L'inspecteur est là pour le détail.
5. Pour une discussion, un **petit signe ↗** facilement discernable et cliquable pour ouvrir ChatGPT. Pour un projet, **aucun signe d'ouverture de fil** ; cliquer/naviguer dans le projet plutôt que lancer un navigateur.

**Sont exclus de la face visible des cartes :** longue description, notes, date de création/modification, URL, chemin complet, liste de tous les rattachements, badges à répétition, slogans. Ces informations restent dans l'inspecteur ; un survol peut les rendre consultables sans surcharger la grille.

**Règle d'or :** on doit reconnaître une conversation ou un projet par **son illustration**, comprendre son titre et agir en un geste.

## 3. Densité, tailles et adaptation

- Grille adaptative avec marges régulières, alignements propres, largeur des cartes calculée selon **la largeur réelle du panneau central**.
- Par défaut, cartes **normales**, suffisamment généreuses pour montrer les images : viser environ **220–280 px** de largeur en fenêtre confortable **1360×820** avec inspecteur fermé ; adapter automatiquement le nombre de colonnes (pas une grille rigide de quatre). **Au moins deux colonnes lorsque la largeur utile le permet**.
- Proposer un sélecteur discret **Normal / Grand** dans l'en-tête des résultats, **uniquement en Mosaïque**, avec deux tailles réellement différentes. Une carte « Grand » augmente principalement l'image et l'espace entre cartes, pas le texte. En étroit, tomber gracieusement sur **une colonne** si besoin. Ne jamais rogner la Liste ou la vue Détaillée pour rendre ce sélecteur visible.
- En bandeau, recherche, menu, colonne gauche et inspecteur : **aucune modification de géométrie**. La Mosaïque se place **uniquement dans la zone centrale existante**.
- Défilement vertical avec scrollbar discrète et visible quand nécessaire, molette ; pas de barre horizontale permanente en Mosaïque.
- États vides sobres : **zéro résultat** ou catalogue sans fiche ; afficher un message au lieu de cartes fantômes. Une grande quantité de résultats doit rester navigable et redimensionnable sans blocage perceptible.

**Pas de nouvelles images** à créer/télécharger. Réutiliser `identity.resolve_identity`, `ImageLibrary`, couvertures intégrées et importées, `project_icons.py` et les ressources actuelles. Prévoir du cache d'images redimensionnées et un rendu limité aux éléments visibles pour garder la navigation fluide.

## 4. Navigation et gestes : mêmes fiches, mêmes conséquences

Le widget `mon_gpt/results.py:ResultsView` est actuellement un rendu partagé Liste/Détaillée dérivé de `CatalogList`. **Étendre proprement son contrat à Mosaïque**, ou isoler un renderer de grille, sans dupliquer la recherche ni la logique métier. Garder une seule collection d'identités `rows`.

- **Clic simple sur la couverture, le fond de carte ou un badge** : sélectionner l'objet et afficher son aperçu si l'inspecteur est ouvert, **sans ouvrir ChatGPT**.
- **Clic sur le texte du titre** ou sur **↗** d'un fil : ouvrir directement l'URL comme dans Liste/Détaillée ; une seule ouverture par geste. **Double-clic** sur une carte de fil et **Entrée** quand focalisée : même ouverture. Un projet navigue dans son périmètre sans ouvrir ChatGPT.
- **Clavier adapté à la grille** : gauche/droite changent de colonne ; haut/bas changent de rangée, sans perdre le focus, avec défilement de la sélection quand elle sort de la zone visible. L'action « ouvrir » au clavier reste utilisable sans conflit avec les flèches de grille. Aucun raccourci supprimé.
- Clic droit/touche Menu : conserver menu contextuel **Renommer / Modifier / Déplacer / Ajouter un rattachement / Supprimer** selon le contexte, identique aux deux vues existantes.
- **F2** renomme dans le contexte de la carte sélectionnée, de façon visible et sans masquer la saisie ; `Échap` annule sans toucher au catalogue. **Ctrl+N** / nouveau projet conservent leurs créations intégrées accessibles (sans popup non demandée).
- **Glisser gauche** d'une tuile de fil/projet vers un projet de l'arbre gauche conserve les règles existantes (pas de duplication, pas de suppression involontaire des autres rattachements, détection des cycles). Menu équivalent pour les opérations non garanties au glisser droit physique. Vérifier les coordonnées des cartes après redimensionnement/scroll.
- Un changement de vue **n'autorise jamais** une modification ou une ouverture de chat par accident. Respecter `can_leave()`, les brouillons d'édition et les protections de l'inspecteur.

**Multi-rattachement :** un fil apparaît **une seule fois** dans les résultats, avec son image/icône/couleur issues du projet actif s'il y est directement rattaché, sinon du premier rattachement stable (résolveur existant). Fil non classé : couverture solaire/générique. **Pas de personnalisation propre au fil dans cette mission.**

## 5. Trois vues, une recherche et une reprise de session

- Ajouter **Mosaïque** au commutateur central `Liste | Détaillée | Mosaïque` et au menu **Affichage** existant. Réutiliser le style des deux premiers boutons, sans redessiner le menu « Windows plus plus ».
- Passer de Liste → Détaillée → Mosaïque → Liste, sans perte de **texte de recherche, tag, catégorie, périmètre gauche, branches ouvertes, sélection centrale, ordre de tri, état de l'inspecteur**, et sans effacer un brouillon de l'éditeur droit.
- **MG-004a est un contrat fonctionnel à préserver intégralement.** `mon_gpt/ui_state.py` accepte `view: list|detail` dans `interface.json`. Y ajouter **`mosaic`**, en maintenant la rétrocompatibilité des préférences anciennes et l'état par défaut en cas de fichier invalide.
- Mémoriser aussi le choix **Normal/Grand** de la Mosaïque comme **simple préférence d'interface** (pas dans `catalogue.json`), avec valeur par défaut « Normal » et validation bornée.
- Après fermeture et relance en Mosaïque : **même recherche, mêmes filtres, même branche, même fiche sélectionnée, même aperçu et même taille de cartes** ; scroller pour rendre la sélection visible si nécessaire. **Aucune ouverture automatique de fil**.
- En cas d'identifiant périmé, choix invalide, résultat exclu du filtre : reprendre exactement les règles de repli MG-004a ; aucun projet fantôme.

## 6. Limites fermes et architecture

**Ne pas retoucher :**
- le dessin/les hitboxes des vues **Liste** et **Détaillée** déjà acceptées ;
- navigation gauche et fils exclusivement au centre, menu principal, bandeau contextuel, champ de recherche, filtres, inspecteur, éditeur, icônes/couleurs/galeries ;
- moteur `core.py`, URL, déduplication, stockage `schema:2`, migration, import, ZIP, `chatgpt.py`, gestion des rattachements.
- l'anomalie historique des doublons d'URL et le glisser droit physique ne font pas partie de ce lot.

Un petit composant réutilisable pour la géométrie de grille et le calcul du hit-test/visibilité est bienvenu ; pas de refonte générale du Canvas ni d'introduction de framework GUI supplémentaire.

**L'utilisateur prévoit une grande passe graphique avec un autre spécialiste en fin de projet.** Cette mission doit produire une **vraie troisième vue fonctionnelle, visuellement propre sans surenchère**, pas une succession de refontes de styles. Priorité à la **composition des cartes, non à la décoration**.

## 7. Recette vraie application et tests

Jeu **fictif** dans un data-dir de développement. Contrôler les trois tailles : **1360×820, 1000×680, maximisée**, inspecteur ouvert/fermé. Les captures ne doivent pas masquer des défauts derrière des objets vides : galerie réellement remplie et plusieurs projets/couvertures distincts.

### Parcours de validation

1. Préparer au moins **4 projets** ayant des couvertures/icônes/couleurs distinctes, dont un sous-projet, et **12 discussions** incluant : un non-classé, un multi-rattaché, un titre long, un résumé vide, une image personnelle portrait et le défaut solaire.
2. Montrer **la même recherche et les mêmes résultats** en Liste, Détaillée puis **Mosaïque**. La grille doit être réellement distincte et **mettre les images en valeur** ; pas de chemins répétés sous chaque carte.
3. En Mosaïque, cliquer une image : **sélection sans ouverture** ; titre puis ↗ : une ouverture simulée chacun ; double-clic et Entrée également vérifiés ; un projet n'ouvre jamais de discussion.
4. Tester flèches quatre directions, défilement, changement Normal/Grand, redimensionnement, changement de vue, fenêtre étroite, survol, clic droit/F2, renommage et annulation.
5. Glisser gauche une tuile de fil vers un autre projet, dont fil déjà multirattaché ; inspecter les rattachements et le contexte avant/après, puis restaurer le jeu fictif. Tester cible interdite et menu équivalent.
6. Activer recherche, tag/catégorie, périmètre et sélection avec aperçu ouvert ; quitter et relancer **en Mosaïque Grand** : **tout doit être restauré**, aucune ouverture dans le journal simulé. Une ancienne préférence `list/detail` doit rester lisible.
7. Images PNG/JPEG/WebP déjà importées, couverture 16:9, portrait, défaut solaire : **aucun recadrage destructeur** ; garder accès à l'inspecteur et aux données lors du changement de mode.
8. Vérifier une Mosaïque à **zéro résultat** et une grille chargée avec beaucoup d'éléments sans artefacts ni surcharge.

### Tests et preuves

- **Conserver les 100 tests MG-004a** et ajouter uniquement des tests pertinents : grille responsive/tailles, cache/position, ouvertures/hitboxes, clavier, DnD, context menus, filtres et multi-rattachements, switch des vues, migration de préférences `mosaic`/taille, redémarrage, anciens modes et aucun lancement automatique.
- Recette **Windows/Tk réelle** avec `--simulate-open`, pas un rendu HTML ou une capture générée.
- Fournir **4 à 5 captures natives** : Mosaïque normale en largeur confortable, Mosaïque Grand, compact avec inspecteur, plusieurs univers distincts, et éventuellement la même sélection en Détaillée/Mosaïque.
- Rapport `reports/MG-005/rapport.md` synthétique avec comparatif aux spécifications, scénarios testés, captures, limites et résultats ; README/version/À propos actualisés sobrement. Commit/push sur `origin/main`, SHA distant vérifié, dépôt propre.

**La validation visuelle appartient à David.** Stop après MG-005. On fera la recette ensemble puis décidera des dernières fonctionnalités, de l'extension Chrome et de la future passe graphique spécialisée.
