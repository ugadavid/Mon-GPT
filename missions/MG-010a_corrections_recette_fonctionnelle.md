# MG-010a — Premières corrections de recette fonctionnelle sur bibliothèque réelle

**Statut : à exécuter par Codex, puis recette David/GPT.**  
**Base :** Mon GPT<3 **0.9.0** sur CODEX-VM, `origin/main` après MG-009. **Version cible suggérée : 0.9.1.** Le Collector Chrome 0.8.2 ne change pas.

**But :** une passe limitée et utile après le premier vrai usage (bibliothèque locale d'environ **1 429 conversations**). Trois sujets seulement : **contenu du dossier sélectionné**, **largeur/libellé des colonnes en Liste**, **choix d'images ergonomique**. Ne pas engager une refonte ni de nouvelles fonctionnalités non demandées.

**Contexte et idées futures :** lire `docs/idees-et-finitions.md` ; ce document est un parking, **ne PAS le traiter comme une liste d'implémentation pour MG-010a**. La sélection multiple et les colonnes configurables feront l'objet de lots séparés.

## 1. Correctif fonctionnel : le projet affiche ses fils DIRECTS, pas ceux des sous-projets

**Constat sur la vraie application :** un projet parent comme **BHE** montre dans la partie centrale des fils qui n'appartiennent qu'à ses sous-projets **BHE - réalisation** et **Réflexion**. David veut **qu'ils ne s'affichent pas lorsqu'il sélectionne le parent**, sauf si la fiche est aussi directement rattachée au parent.

**Sémantique d'affichage requise :**
- Sélectionner un projet P → **fils directement rattachés à P** (`P in Record.projects`) et, s'ils étaient déjà affichés, **les projets immédiatement enfants** (`Record.parent == P`) comme destinations navigables, **pas les fils hérités des descendants**.
- Sélectionner un sous-projet → uniquement ses propres fils directs et ses projets enfants immédiats. **Aucun héritage automatique de fils** dans les listes parents.
- Fiche multi-rattachée volontairement à P **et** à un enfant → apparaît dans P, puisque P fait réellement partie de ses emplacements. **Pas de doublon de fiche**.
- La vue **« Tous les fils »** reste globale, la vue **« À classer »** conserve les fils sans rattachement, et filtres/recherche/tri continuent de fonctionner sur le périmètre visible.
- Ne pas supprimer ni changer les **rattachements** stockés. C'est **uniquement un changement de visibilité** de la partie centrale.
- Un projet ancêtre sélectionné ne doit plus afficher un fil du petit-enfant par simple descendance. Une recherche globale doit pouvoir le retrouver.
- Les trois vues **Liste, Détaillée et Mosaïque** doivent utiliser **strictement la même règle** ; même décompte et même jeu de résultats.

**Point technique à contrôler :** `Catalog.search(..., project=P)` utilise actuellement `Catalog.descendants(P)` ; `App.refresh_results()` l'appelle directement. Préférer un changement de **sémantique de vue/filtrage** plutôt qu'un changement impulsif de tous les appels à `Catalog.search` si cela casserait d'autres fonctions. Mettre à jour tests/README si cette règle devient universelle.

**Recette isolée :** projet parent P → sous-projet E → sous-sous-projet F ; trois fils rattachés respectivement à P, E et F ; un quatrième partagé P+E. Dans P, on voit les fils de P et P+E, pas les deux fils exclusivement descendants ; dans E, ceux de E et P+E, pas F ; dans F, son fil. Tester également les projets enfants affichés ou navigables. Comparaison sur bibliothèque réelle **sans publier de noms personnels dans les captures**.

## 2. Vue Liste : libellés simples et colonnes enfin redimensionnables à la souris

**Deux changements de libellé exacts :**
- `Titre local` → **`Titre`**
- `Projet / emplacements` → **`Projet`**

Ne modifier ni les données internes ni les valeurs des cellules. Une fiche avec plusieurs projets conserve dans la cellule Projet **tous ses rattachements lisibles**, pas uniquement le premier.

**Constat :** l'utilisateur ne parvient pas à régler les largeurs **Titre / Projet / Catégories / Tags**. Le composant n'est pas un `ttk.Treeview` natif : `CatalogList` dans `mon_gpt/atelier.py` est un **Canvas dessiné** et contient déjà une détection de séparateur dans `select_click` et un `resize_motion`. Le problème est donc à **reproduire et corriger à l'usage**, pas à « activer `selectmode` sur un Treeview ». `ResultsView` délègue à la vue Liste.

**Exigences :**
- Détecter de manière fiable une **poignée/séparateur** entre colonnes lors du survol de l'en-tête, avec curseur horizontal de redimensionnement et retour visuel discret (pas besoin de grosses séparations permanentes).
- Glisser à gauche/droite pour modifier visiblement la largeur de **chacune des quatre colonnes** demandées lorsque l'espace le permet. Gérer la colonne Titre aujourd'hui ancrée/auto-extensible, les colonnes secondaires défilantes et le bouton d'ouverture épinglé sans dessiner un débordement par-dessus les autres colonnes.
- Respecter largeurs minimales raisonnables, panneau central étroit, changements de taille de fenêtre, scrollbar horizontale, et tri en cliquant **hors des zones de poignée**. Une manipulation de largeur ne doit **ni trier** ni ouvrir de fil.
- Après changement de vue et retour à Liste, garder les largeurs durant la **session**. Leur mémorisation entre lancements et l'administration des colonnes seront traitées **ultérieurement** dans la mission dédiée : ne pas alourdir ce correctif.
- Ne pas supprimer ni casser les tris ascendant/descendant, la sélection d'une fiche, l'ouverture des liens et la lisibilité des titres longs.

**Hors périmètre :** afficher/masquer/ordonner des colonnes, ajouter `Création` et `Modification` comme colonnes, créer une page Administration : **reportés et notés** dans `docs/idees-et-finitions.md`.

## 3. Galerie des couvertures : hauteur responsive et double-clic pour choisir

**Constat réel :** dans le volet droit « Une image pour ce projet/fil », les deux colonnes de couvertures conservent des vignettes **de hauteur fixe** quand David élargit le volet ; choisir nécessite un clic simple puis **Utiliser**.

**Causes candidates observables dans `identity_ui.py` :**
- `ChoiceTile` utilise `height=94` pour une couverture ;
- sa vignette est rendue avec une hauteur `60` pixels ;
- `VisualLayer` conserve `columns=2` pour les images, seul le type icône dispose d'une redistribution sur `<Configure>` ;
- seul `<Button-1>` est relié à `choose()`.

**Changements demandés :**
- Pour les **couvertures uniquement**, faire évoluer la **hauteur des cartes/vignettes avec leur largeur disponible** lorsque le volet droit est redimensionné : image au **format 16:9** ou proche, intitulé lisible en dessous, espacements cohérents. Ne pas conserver une vignette de 60 px de haut à toute largeur. Conserver un scrolling fluide et un gabarit raisonnable.
- Garder les deux colonnes si cela fonctionne visuellement, ou adapter de façon simple selon la largeur, mais ne pas transformer en modale plein écran ni déplacer les autres sélecteurs d'identité visuelle.
- **Double-clic gauche** sur une couverture : la sélectionner **et exécuter exactement l'action du bouton « Utiliser »**, fermer la galerie puis revenir à l'éditeur. Le clic simple continue de **prévisualiser/sélectionner sans confirmer**, `Utiliser` et `Annuler` restent disponibles.
- **Très important :** double-clic = `Utiliser` dans la galerie, **pas** sauvegarde automatique de la fiche. Le bouton général `Enregistrer` garde sa signification ; annuler une édition reste possible.
- Navigation clavier et choix avec Entrée/Espace conservés, focus correct au retour. Aucune double application ni erreur lors de deux événements clic consécutifs.
- Les **sélecteurs d'icônes et de couleurs** restent inchangés, ainsi que l'héritage visuel des fils.

Tester sur un volet droit étroit/large, pour un projet et pour une discussion, avec couverture de pack et image personnelle **fictive**.

## 4. Recette et discipline de mission

**Tests :**
- Conserver les tests Python et JavaScript déjà validés ; ajouter régressions direct/descendant, multi-rattachement, tri/filtres et vues identiques.
- Tester la détection de séparateurs et les événements souris réels (pas uniquement appel direct à une fonction Python) ; vérifier chaque largeur, titres lisibles, scroll et clic de tri à proximité.
- Tester la galerie à largeur variable, clic simple, double-clic, bouton Utiliser, annulation, accès clavier, sélection d'une image pack puis d'une image personnelle fictive.
- Vérifier que le **catalogue schéma 4**, les mappings ChatGPT, le réimport v2, les images personnalisées et leurs sauvegardes restent intacts.

**Windows réel sur CODEX-VM :** le catalogue courant comporte de vrais projets, sous-projets, étiquettes et images, mais **ne jamais utiliser de tests destructifs sur la bibliothèque habituelle**. Exercer les opérations dans un catalogue de recette isolé `--data-dir .recette/MG010a` ; inspecter éventuellement la bibliothèque réelle en lecture seule pour confronter l'affichage au cas relevé. Aucune fuite de noms, titres, liens, GUID, métadonnées personnelles ou captures réelles dans GitHub public.

**Rapport :** `reports/MG-010a/rapport.md` incluant cause, fichiers touchés, avant/après, nombre de tests, résultats de recette et **4 ou 5 captures natives sur données fictives** (parent et enfant, redimensionnement, galerie étroite/large, retour après double-clic). Versionner le code seulement après tests, commit/push `origin/main`, SHA distant vérifié, dépôt propre.

**STOP après MG-010a.** **Ne commencer ni sélection multiple/actions groupées (MG-010b envisagée), ni configuration des colonnes (MG-010c envisagée), ni tableau de bord/stats, ni installateur, ni relooking global.** Ne pas créer de nouveau projet.

**Critère GO :** parent = fils directs uniquement ; largeurs des quatre colonnes réellement manipulables et deux labels simplifiés ; images de galerie responsives et double-clic équivalent à « Utiliser » ; aucune régression de données, édition, navigation ou trois vues.
