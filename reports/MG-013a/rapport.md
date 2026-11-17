# MG-013a — Cadrage de la refonte visuelle

**17 novembre 2026 · Mon GPT<3 0.9.4 · CODEX-VM / Windows. Étude uniquement, direction proposée à David.**

La recommandation est un **Atelier chaleureux à la composition plus éditoriale** : une navigation calme, un centre nettement dominant, des titres affirmés et des images généreuses là où elles aident à reconnaître les fils. La transformation doit porter sur les proportions, la hiérarchie et le dessin des surfaces, pas seulement sur la palette. Les fonctionnalités et les gestes validés restent le contrat.

## 1. Références effectivement examinées

Départ propre sur `main` à `b0bb3fa`, puis synchronisation en avance rapide vers `fb271b2`, qui ajoute la [mission MG-013a](../../missions/MG-013a_cadrage_passe_graphique_finale.md). Aucun code applicatif différent de MG-012 dans cette synchronisation.

Les **trois PNG originaux ont été ouverts et regardés intégralement**, à leur emplacement existant, sans modification ni copie :

| Référence locale | Apport retenu | Dessins à ne pas convertir en fonctions |
|---|---|---|
| [11_51_22-1 — explorateur](../../missions/MG-002-maquettes/Image%20ChatGPT%2014%20nov.%202026,%2011_51_22-1.png) | Menu papier fin, recherche bien identifiée, sélection douce, chaleur du paysage et des accents d'ouverture. | Gros boutons orange répétés, nouveau dossier distinct du projet, raccourci de sauvegarde dessiné. |
| [11_51_54-2 — bibliothèque](../../missions/MG-002-maquettes/Image%20ChatGPT%2014%20nov.%202026,%2011_51_54-2.png) | Hiérarchie titre/extrait/repères, profondeur légère, panneau de lecture accueillant. Sa dominante paraît plutôt bleu pétrole que le vert annoncé dans le cadrage. | Favoris, Récents, partage, étoiles et confusion « catégories/emplacements ». |
| [11_51_55-3 — gestionnaire](../../missions/MG-002-maquettes/Image%20ChatGPT%2014%20nov.%202026,%2011_51_55-3.png) | Liste compacte, colonnes nettes, icônes libres, navigation indentée et terracotta ponctuelle. | Actualiser, arborescences de tags/catégories, cases supplémentaires et consigne double-clic/Entrée pour ouvrir. |

La [spécification UX](../../missions/MG-002-maquettes/01_specification_UX.md) a été lue avec `AGENTS.md`, le README, le [guide MG-011](../../docs/MG-011-navigation-et-informations.md), les rapports [MG-011](../MG-011/rapport.md) et [MG-012](../MG-012/rapport.md), ainsi que les missions MG-002a et MG-002b-01 à 06. Ces dernières racontent les arbitrages successifs : menu familier et soigné ; trois colonnes sous le menu ; recherche au centre ; Liste fine ; actions d'aperçu sur une rangée ; continuité avec l'éditeur ; navigation sauge. Leurs gels concernaient leurs tranches respectives. Ils ne justifient ni une réécriture des gestes actuels ni le retour à leurs anciens périmètres fonctionnels.

**Priorité des contrats :** titre/image/icône sélectionnent ; ↗ ouvre explicitement le fil, Alt+Entrée active l'action du fil focal. Les formulations historiques d'ouverture par le titre sont dépassées par MG-010b-01/MG-011. Les vues et identités visuelles existent désormais ; le catalogue est au schéma 4, les préférences UI au format 1. Aucun retour aux anciens schémas n'est proposé.

### Photographie actuelle reproductible

Application réellement lancée avec `python -m mon_gpt --data-dir .recette/MG013a --simulate-open`, sur le catalogue créé par `python -m examples.create_detail_demo .recette/MG013a` : **5 projets, 24 discussions fictives**, un sous-projet, un fil à deux emplacements, un fil à classer, titre long, notes, catégories/tags et image portrait. Les trois premières captures utilisent exactement le même périmètre Tous, le même tri Titre et le même catalogue. Les maquettes historiques ont leurs propres textes : leurs données n'ont pas été prétendues identiques ni recréées dans les PNG.

Captures natives réellement vues et enregistrées sans retouche, dimensions clientes préparées à 1360×820 puis 1000×680, cadres Windows inclus :

- [01 Liste](01-liste.png), [02 Détaillée](02-detaillee.png), [03 Mosaïque Normal](03-mosaique.png) : aperçu fermé.
- [04 Mosaïque avec aperçu](04-mosaique-apercu.png), [05 Détaillée avec aperçu](05-detaillee-apercu.png) : même fil sélectionné.
- [06 Mosaïque compacte](06-mosaique-compacte.png), [07 Liste compacte](07-liste-compacte.png), [08 Éditeur compact](08-editeur-compact.png).
- [09 Licences et crédits](09-credits.png) : vraie fenêtre secondaire, ouverte depuis Aide.

Les six captures évoquées dans la conversation d'origine ne sont pas disponibles dans ce fil et ne sont pas revendiquées comme vues. La présente comparaison repose sur les trois originaux et les captures nouvelles ci-dessus.

## 2. Comparaison et intention de correction

| Zone / références | Existant observé | Intention proposée |
|---|---|---|
| Composition commune — 1 et 3 | Trois colonnes déjà bien distinctes ; centre libéré au repli. Mais marque, slogan, recherche, titre/décompte, création/aperçu puis modes occupent plusieurs rangées avant les résultats. | Conserver l'implantation MG-002b. Composer un petit en-tête central, puis recherche et barre de résultats cohérentes ; gagner de la hauteur par alignement, sans retirer une action. |
| Navigation — surtout 3 | Bonne sélection sauge, identités personnalisées et niveaux visibles. Carte très encadrée, tri presque aussi large que le panneau, pictogrammes fins et proches des libellés. Le peu de projets de ce jeu laisse un grand vide normal. | Une surface latérale plus calme, en-tête et tri plus discrets, gouttière icône/texte régulière. Préserver les deux entrées épinglées et la largeur des cibles de dépôt. Ne pas remplir artificiellement le vide. |
| Recherche — 1 | Unique, plafonnée, filtres accessibles : bon socle. Au compact, le texte indicatif se coupe rapidement ; les boutons ont le même poids que le champ. | Renforcer visuellement le champ comme point d'entrée, alléger ses commandes voisines et réserver une ligne aux seuls critères actifs. Suggestions toujours globales et dans le centre. |
| Liste — 3 | Vraies lignes compactes, titre gras, icône seule et ↗ épinglé : proche du contrat. À 1000 avec aperçu, le titre devient très court ; les secondaires défilent. | Affiner en-tête, filets, contraste des métadonnées et alignements. Préserver les 42 px comme base ; aucun bouton d'ouverture répété ni couverture en ligne. En compact, donner la priorité au titre dans la répartition disponible, sans écraser les largeurs choisies par l'utilisateur. |
| Détaillée — 2 | Vignettes entières, Résumé et Note séparés, emplacements et pastilles utiles. Les cartes à filets rapprochés et les petits textes donnent une impression de tableau agrandi ; titres longs sur une seule ligne. | Un rythme de lecture plus affirmé : vignette, titre dominant, extraits et contexte secondaires, repères en bas. Proposer jusqu'à deux lignes de titre dans cette vue, en recalculant ensemble dessin, hauteur et zones cliquables. |
| Mosaïque — synthèse des trois | Les belles illustrations assurent déjà une vraie identité ; 4 colonnes sans aperçu, 2 avec, 1 au compact. Les petites bordures et les libellés tronqués affaiblissent le plaisir de bibliothèque. | Couverture entière toujours prioritaire ; meilleur rapport image/texte, marges cohérentes, titre et ↗ mieux dégagés, sélection douce mais nette. Conserver Normal/Grand et les extraits MG-011. Pas de diversification artificielle des couvertures héritées identiques. |
| Aperçu / éditeur — 1 et 2 | Titre lisible, lecture distincte de l'édition, trois actions sur une ligne, sections explicites. Filets foncés répétés et sélecteurs visuels détachés rendent le haut chargé. Les champs d'édition sont déjà fins. | Rapprocher identité/titre/actions, alléger les séparations et renforcer le rythme des sections. Même langage dans l'éditeur ; conserver les emplacements en haut, toutes les données et l'accès aux notes longues. Pas de grande couverture supplémentaire dans l'aperçu. |
| Menu et crédits — 1 | Menu discret et fonctionnel ; crédits lisibles mais tableau/onglets ttk plus administratifs que les cartes Canvas. | Préserver le menu validé ; harmoniser les fenêtres d'information par styles dédiés, marges et hiérarchie, sans changer textes, notices ni cycle de vie. |

## 3. Direction artistique unique proposée

**Un atelier de papier clair, avec le sapin comme structure et la terracotta comme ponctuation.** De la première référence : finesse des menus et douceur des surfaces. De la deuxième : confort de lecture et hiérarchie éditoriale. De la troisième : précision de la Liste et sobriété de la navigation. La Mosaïque étend ce langage aux couvertures existantes ; aucune des trois références n'est une spécification exacte de sa grille actuelle.

Recommandations graphiques, à valider :

- Conserver ivoire `#F7F3EA`, sable `#E7D9C5`, sapin `#315E4F`, terracotta `#C87A50`, encre `#292D30`. Papier pour le contenu, ivoire pour le fond, sable pour les regroupements légers. Diminuer le nombre de contours simultanés ; aucune texture ou ombre massive.
- Garder Segoe UI disponible sur Windows. Établir des rôles communs : marque 20–22 pt, titre de fiche 16–18, titre de résultat 11–12 gras, contenu 10–11, métadonnées 9–10. Ce sont des bases à mesurer sous Tk, pas des tailles physiques promises à tous les DPI.
- Adopter une échelle d'espacement courte (4/8/12/16/24) et deux familles de rayons : surfaces/cartes, puis pastilles. Réserver les capsules aux filtres et repères ; différencier les modes de vue des boutons d'action.
- Distinguer **sélection sauge**, survol discret, focus sapin et dépôt autorisé/interdit. Une bordure ou un signe doit compléter la couleur ; ↗ reste identifiable et suffisamment ciblable sans agrandir son périmètre jusqu'au titre.
- Conserver une seule illustration contextuelle dans le bandeau central et sa règle d'identité actuelle. Les couvertures des cartes restent des repères métier ; aucun paysage global au-dessus des trois colonnes.

**Arbitrages demandés à David :** valider ce cap de papier clair plutôt qu'une dominante bleu pétrole ; autoriser la recomposition des rangées du centre et l'allègement du slogan ; accepter le titre sur deux lignes en Détaillée si le bilan de densité reste bon. Conserver par défaut la géométrie et le menu MG-002b. Toute modification plus importante de leurs proportions devra être explicitée dans la mission future, pas déduite du présent rapport.

## 4. Carte des composants et couplages

Le code a été consulté : ce n'est déjà plus une interface ttk brute.

| Surface | Composants réels à réemployer | Couplage à surveiller |
|---|---|---|
| Charte | `theme.py` : `COLORS`, `FONT`, `apply_theme` ; `atelier.py` : `Surface`, `PillButton`, `rounded` | Beaucoup de tailles et nuances sont encore locales dans les dessins. Centraliser seulement les rôles nécessaires ; un style ttk global peut aussi changer les tableaux d'import/crédits. |
| Coque/recherche | `ui.py` : `App.build_shell`, `layout_search`, `layout_view_controls`, `place_initial_sash` ; `identity_ui.py` : `ContextMasthead`, héritant de `Masthead` | Panedwindow, largeur des trois panneaux, repli à 112 px du bandeau avec métadonnées, suggestions, commandes compactes et restauration. Garder les règles d'identité séparées des informations du projet courant. |
| Arbre | `navigation.py` : `NavigationTree`, deux `_NavigationBranch` ttk, `NavigationScrollbar` | La façade convertit les coordonnées entre branches et partage sélection/focus ; toucher aux marges peut décaler hit-tests, dépôts et création intégrée. Garder les contrôles natifs. |
| Trois vues | `atelier.py` : `CatalogList` Canvas ; `results.py` : `ResultsView(MosaicRenderer, CatalogList)` ; `mosaic.py` : `GridLayout`, `MosaicRenderer` | Géométrie, `bbox`, `open_hit`, sélection commune, navigation grille et position de renommage doivent évoluer ensemble. Préserver rendu des seules cartes visibles et cache d'images borné. `columns_ui.py` conserve les choix de colonnes. |
| Fiche | `inspector.py` : `InspectorSummary`, `InspectorAction`, notes/badges/scrollbar ; `details.py` : `DetailEditor.render_editor` ; `widgets.py` : `ChipPicker`, styles d'éditeur ; `identity_ui.py` : `ProjectVisualStrip` | Canvas défilant de `ui.py`, molette sous le pointeur, dirty/abandon, erreurs de champ, héritage et sélecteurs partagés avec les projets. Aucun déplacement de logique métier. |
| Menus/informations | `main_menu.py` : `MainMenuBar`/`MainMenuSkin` ; `atelier.py` : `MenuSkin` ; `information_ui.py` : `InformationWindow`, Aide/À propos ; `credits_ui.py` : `CreditsWindow` | Focus, Échap, retour à la fenêtre appelante ; ttk Notebook/Treeview/Text. Conserver les textes documentaires et les liens exclusivement explicites. |

Pas de Qt, moteur de thème universel, nouvelle grosse dépendance ou système de plugins. `core.py`, `chatgpt.py`, `identity.py`, stockage, formats, imports et Collector restent hors réalisation graphique.

## 5. Quatre lots proposés, aucun lancé

Estimations indicatives en jours de travail concentré, recette comprise, hors délai de validation humaine. Chaque lot donne une application complète et utilisable ; aucune commande n'est laissée décorative ou provisoirement inactive.

| Ordre | Périmètre borné / valeur visible | Risque et dépendance | Durée | Acceptation visuelle et continuité |
|---|---|---|---|---|
| **1 — Composition et navigation** | Tokens nécessaires, surfaces communes, en-tête/recherche/barre des résultats au centre, gouttières et habillage de l'arbre. Garder contenus, menu et moteur des vues. | Moyen : compact, styles partagés, coordonnées de l'arbre. Dépend de la validation des arbitrages ci-dessus. | 2–3 j | À 1360 et 1000, centre mieux hiérarchisé et gain visible de hauteur utile ; gauche/droite toujours sous le menu ; recherche et commandes accessibles avec aperçu ouvert/fermé. Les trois rendus actuels fonctionnent avec la nouvelle coque. |
| **2 — Bibliothèque illustrée** | Détaillée et Mosaïque : titres, proportions, rythme des extraits, pastilles, bordures et sélection. Réemploi de toutes les images et identités. | Élevé mais local : géométrie/hit-tests, renommage et clavier de grille. Dépend du lot 1. | 2–3 j | Avant/après du même jeu : Détaillée lisible avec titre long ; Mosaïque réellement plus accueillante, Normal/Grand distincts lorsque la largeur le permet ; portrait entier et notes/résumés conservés au compact. Liste utilisable pendant ce lot. |
| **3 — Précision de la Liste** | En-têtes, filets, repères et priorité du titre en largeur contrainte ; dessin de l'action ↗ et états focus/sélection. Pas de remise à zéro des colonnes. | Moyen : colonnes épinglées, resize, tri et défilement. Dépend du lot 1 ; après le 2 pour valider les trois vues ensemble. | 1–2 j | Une ligne par fil, icône seule, aucun CTA répété ; titre et ↗ accessibles ; choix/ordre/largeurs des colonnes conservés à la relance. Détaillée/Mosaïque inchangées fonctionnellement. |
| **4 — Fiche et cohérence des fenêtres** | Aperçu/éditeur, champs et pastilles, créations intégrées et dialogues existants ; styles dédiés Aide/À propos/Crédits et vérification des sélecteurs d'identité. Menu principal conservé. | Moyen : focus, saisies, molette et styles ttk partagés. Dépend des lots 1–3. | 2–3 j | Même fiche reconnaissable entre lecture et édition ; actions sur une rangée, erreurs locales lisibles, notes complètes ; crédits et notices toujours copiables et accessibles hors ligne. Aucune modification documentaire ou métier implicite. |

Chaque lot devra présenter ses captures comparables et s'arrêter à sa propre validation. Total indicatif **7–11 jours**, à réestimer après le premier lot ; ce découpage ne crée aucune mission ni autorisation d'exécution.

## 6. Vérifications proportionnées et limites

Pour les futurs lots, garder le même catalogue fictif et les mêmes cadrages avant/après, ajouter seulement les cas manquants : projet à nombreux niveaux, métadonnées de projet longues, fiche vide, beaucoup de tags, note très longue et série de couvertures héritées identiques.

| Lot | Tests ciblés existants à mobiliser | Voisins et recette Windows |
|---|---|---|
| 1 | `test_atelier`, `test_visual_corrections`, `test_final_polish`, `test_functional_finishes`, `test_workspace` | Arbre épinglé/défilant, clavier entre branches, dépôt autorisé/interdit, recherche/filtres, création intégrée, repli et relance ; menu F10/Échap. |
| 2 | `test_detailed_view`, `test_mosaic`, `test_functional_finishes`, `test_natural_gestures`, `test_batch_ui` | Même sélection/lot/tri entre vues ; titre sans ouverture, ↗ ciblé et Alt+Entrée ; drag gauche/droit, renommage, scroll et grille après resize ; série volumineuse pour conserver le rendu borné. |
| 3 | `test_compact_list`, `test_column_layout`, `test_list_columns`, `test_natural_gestures` | Colonnes défilantes et épinglées, titres longs, dates, tri/resize/relance, clic droit et lot conservé au clic ↗. |
| 4 | `test_inspector`, `test_editor_layout`, `test_project_identity`, `test_thread_identity`, `test_main_menu`, `test_credits` | Molette par panneau, Tab/Shift+Tab, sauvegarde/abandon de fiche, erreurs sans perte, galerie et héritage ; Aide/crédits réutilisables, Échap/focus, notices copiables et aucun réseau implicite. |

Dimensions de recette futures : 1360×820 et 1000×680, aperçu ouvert/fermé, puis fenêtre agrandie. Vérifier réellement au moins 100 %, 125 % et 150 % de mise à l'échelle Windows dans des sessions préparées à ces valeurs : aucun changement de DPI n'a été effectué ici. Contrôler texte français, titres longs, contraste, focus et cibles indépendamment des seuls tests de pixels. Aucun nouveau test qui ne ferait que recopier les constantes du dessin.

**Coût de publication à discuter :** `AGENTS.md` impose actuellement `python -m unittest discover -s tests -v` et la recette Windows avant publication. MG-012 rapporte 203 tests Python en environ quatre minutes, plus 43 tests JS du compagnon. Pour les futurs lots applicatifs, la suite Python et la recette restent exigées tant que cette règle n'est pas révisée explicitement. Proposition à décider séparément : ciblage pendant l'itération, suite complète au jalon applicatif ; éviter de rejouer le Collector inchangé sans raison. `AGENTS.md` n'a pas été modifié.

**Exécuté dans MG-013a :** lancement Windows réel, bascules des trois vues, sélection d'un titre sans ouverture, ouverture de l'aperçu et de l'éditeur sans saisie, consultation du menu Aide et des crédits, fermeture et relance au format compact, puis fermeture de la session. Neuf captures fictives brutes. Le catalogue conserve exactement son SHA-256 initial ; aucun journal d'ouverture de fil n'a été créé. Les préférences du seul jeu jetable ont changé, comme attendu. Aucun fichier de recette n'est publié.

Empreinte exacte du catalogue avant/après : `07eb22d99cf10ec2047ec26ed19abd7108ba276f1c68c90e120a3dc700609c0e`.

**Non exécuté :** suite complète Python/JS, nouvelle recette exhaustive des gestes/imports/sauvegardes, drag physique, autres DPI et Mosaïque Grand. La mission MG-013a dispense explicitement des tests longs pour ce document seul ; aucun code produit n'a changé. Les bilans MG-011/012 sont des références historiques, pas des tests rejoués ici. Les images prouvent une présentation observée, pas une validation fonctionnelle universelle. Contrôles de publication : liens locaux du rapport, fichiers ajoutés limités au présent dossier, maquettes originales et code inchangés, `git diff --check`, puis vérification du SHA distant.

## Point d'arrêt

**Proposition prête à valider : direction artistique, arbitrages et quatre lots.** Aucun GO graphique auto-attribué. Après publication de ce rapport et de ses preuves sur `origin/main`, arrêt pour David. Aucune refonte, nouvelle mission d'exécution ou distribution Windows engagée.
