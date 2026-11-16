# MG-010b-01 — Gestes naturels, glisser-déposer multiple, noms lisibles et ouverture ↗

**Mission corrective Codex — à exécuter, puis recette par David/GPT.**  
**Base :** Mon GPT<3 **0.9.2**, MG-010b livrée au commit `197418fe0f1606b707959dd19529b8c6a9283087`. **Version de correction suggérée : 0.9.2a** (ou 0.9.3 si la convention du dépôt l'impose). Collector Chrome inchangé.

## 0. Le retour utilisateur, priorité sur les hypothèses de la mission précédente

Sur la **vraie interface avec plus de 1 400 discussions**, David valide la sélection multiple mais refuse trois choix d'ergonomie de MG-010b :

1. **« Ce qui fonctionne pour une fiche doit fonctionner pour plusieurs. »** Glisser gauche ou droit un ensemble sélectionné doit faire le même classement qu'une seule fiche, sur tout le lot, et avec la même simplicité. **Plus de blocage volontaire du drag multiple**. Les trois gros boutons permanents du bandeau sont inutilement envahissants ; les actions groupées peuvent rester dans le menu contextuel et être déclenchées par les gestes normaux.
2. **Les GUID sont des détails applicatifs**, pas du contenu à afficher partout. **Nom/chemin seuls par défaut ; désambiguïsation seulement en présence d'homonymes** (numéro stable dans la liste ou identifiant abrégé, l'utilisateur accepte les deux). Un projet unique « Ian » doit s'afficher simplement « Ian », jamais « Ian [GUID complet] ».
3. **Cliquer sur le titre d'un fil ne doit jamais ouvrir son URL.** Le titre/ligne sert à **sélectionner**. **L'ouverture de ChatGPT est réservée au bouton ↗ en fin de ligne/carte**. Ni simple clic ni double-clic sur le texte ne doivent ouvrir le navigateur.

**Important sur les données de recette :** David indique explicitement **« prudence 0 sur mes données, nous sommes toujours en test »**. Ne pas créer de cérémonial de sûreté, confirmation supplémentaire, avertissements dramatiques, sauvegardes ou copies préventives à chaque geste. **Réutiliser simplement les transactions déjà fonctionnelles** et les comportements natifs de classement. Si une source est vraiment ambiguë, demander un choix concret, pas une validation générale du risque. Pas de refonte du stockage ou de la sécurité.

**Périmètre exclusif :** interaction de sélection/glisser/ouvrir, présentation des projets dans les sélecteurs de classement, bandeau de lot. Ne pas toucher au Collector Chrome, import MG-009, galerie, configuration des colonnes, tableau de bord, installateur, design global. Le parking `docs/idees-et-finitions.md` reste le parking.

## 1. Réutiliser les vraies briques existantes — audit préalable

Inspecter et corriger **les chemins de code existants**, notamment :

- `mon_gpt/ui.py` : `drag_press`, `drag_motion`, `drag_release`, `drop_target`, `drop_action`, `result_double`, `title_hit`, `open_click`, `result_enter`, `hover_result`, `context_menu`.
- `mon_gpt/batch_ui.py` : `BatchActions.build_group_bar`, `group_menu`, `BatchDialog.projects`, `sources`, `destination_box`, `open_batch`.
- `mon_gpt/batch.py` et `mon_gpt/storage.py` : moteur validé pour appliquer un lot en une transaction, **sans le dupliquer**. `build_batch` sait calculer déplacement/ajout/retrait, `Store.commit_batch` sait écrire atomiquement.
- `mon_gpt/atelier.py` : `CatalogList.open_hit`, `select_click`, sélection, `resize_motion`, `motion`, dessiner l'icône ↗.
- `mon_gpt/results.py` et `mon_gpt/mosaic.py` : hit-tests `open_hit` / `mosaic_open_hit`, événements souris, titres, sélections et flèches de navigation.
- `mon_gpt/selection.py` : sélection multiple déjà stable, ancre/focale, conservation entre les vues.
- `docs/MG-010b-selection.md` et les tests existants : mettre à jour les gestes, ne pas conserver de consigne obsolète « le drag de lot est interdit ».

**Causes identifiées dans le code 0.9.2 :**

- `drag_press` marque le glisser multiple `batch=True`, `drag_motion` l'arrête et affiche « Glisser de lot désactivé » ; `drag_release` renonce à le traiter.
- Les menus de `batch_ui.py` construisent leurs libellés systématiquement avec `project_label(...) + " [" + r.id + "]"`, d'où les UUID complets partout.
- `CatalogList.open_hit` et les équivalents Détaillée/Mosaïque incluent le **titre** ; `drag_release` appelle `open_click`, et `result_double` ouvre aussi tout texte double-cliqué. Le message d'aide actuel dit « Titre ou ↗ : ouvrir ».

**Il faut traiter toute la chaîne d'événements**, pas seulement cacher des boutons ou remplacer un libellé.

## 2. Une ligne/un lot — mêmes gestes, dans les trois vues

| Geste | Une discussion sélectionnée | Plusieurs discussions sélectionnées |
| --- | --- | --- |
| Clic sur la ligne, titre, image ou carte hors ↗ | Sélectionner la fiche, montrer l'aperçu | Sélectionner/réduire le lot selon Ctrl/Maj ; aucun navigateur |
| Ctrl+clic / Maj+clic | Construire la sélection | Ajouter, retirer, étendre |
| **Glisser gauche vers un projet dans l'arbre** | Déplacer le rattachement depuis le contexte source | **Déplacer le même rattachement pour tout le lot** |
| **Glisser droit vers un projet** | Menu « Déplacer ici / Ajouter un rattachement ici » | **Exactement le même menu**, appliqué au lot |
| **Clic droit sur une sélection** | Menu fiche | Menu de lot : Déplacer / Ajouter / Retirer, sans GUID techniques omniprésents |
| **Clic sur ↗** | Ouvrir **ce fil uniquement** dans ChatGPT | Ouvrir ce fil précis seulement si l'utilisateur clique délibérément son propre ↗ ; aucune ouverture du lot |
| Double-clic sur titre/ligne/carte | Pas d'ouverture ChatGPT | Pas d'ouverture ChatGPT |

**Sémantique prioritaire du drag :**

- Démarrer un glisser sur **l'une des discussions déjà sélectionnées** doit prendre tout le lot comme source (ne pas réduire furtivement à une seule fiche sur ButtonPress / ButtonRelease).
- Démarrer sur une discussion **hors du lot** quitte la sélection groupée et déplace cette **seule** discussion (comme un geste simple).
- Ctrl/Maj + clic servent toujours à sélectionner ; ils ne lancent ni déplacement ni ouverture accidentelle.
- Le **glisser gauche applique directement** le déplacement à la dépose valide, sans dialogue de confirmation si la source est connue. Le **glisser droit** affiche le menu « Déplacer ici / Ajouter un rattachement ici » ; exécuter le choix sans une deuxième étape artificielle.
- Le **projet source** est le projet affiché/sélectionné dans l'arbre s'il est un rattachement direct commun à **tous les fils du lot** ; par exemple déplacer deux des huit fils directement dans « BHE - réalisation » vers « Réflexion » retire ce seul rattachement et ajoute « Réflexion » à chacun.
- Depuis **À classer**, si **tous** les fils sont sans projet, le glisser gauche ajoute leur premier rattachement dans le dossier de destination.
- Depuis « Tous les fils » ou avec un lot multi-rattaché sans source commune évidente : ne **jamais choisir le premier GUID arbitrairement**. Préférer une sélection simple de la source commune si elle est unique, sinon **petit choix de source seulement** (prérempli si possible), puis appliquer le déplacement. Cela ne doit pas devenir une modale de validation du risque. Pour `Ajouter`, aucune source à choisir.
- **Source = destination** = aucun déplacement utile, sans effet de bord. Une destination inexistante/non-projet n'accepte pas la dépose ; retour normal de la souris.
- Préserver les autres rattachements, ordre, notes, tags, catégories, URL, couvertures et fiches. **Copier = ajouter un emplacement** ; **jamais cloner une conversation**.
- Drag gauche/droit des **projets dans l'arbre** garde sa sémantique existante, sans lot de projets.
- État visuel de cible survolée et curseur identiques pour une/plusieurs fiches ; message compact « Déplacer 3 discussions vers Réflexion » plutôt que menus et bannières de peur.

**Aucun autre niveau de confirmation pour plusieurs fils que pour un seul**. Si la source demande réellement une résolution, c'est une **question de choix métier**, pas une confirmation générale.

**Architecture attendue :** partir de la mécanique déjà valide de `batch.py` / `Store.commit_batch()` ; factoriser les appels de glisser-déposer individuel/lot si utile, mais éviter de réinventer un second moteur de déplacement. Une opération de lot = une application logique, une seule écriture, aucun clone ; pas une boucle de N fenêtres ou N appels à `save`.

## 3. Simplifier le bandeau de sélection

- Lorsque 2+ fils sont sélectionnés, conserver un **indicateur léger** « 3 discussions sélectionnées » et **Désélectionner** ; éventuellement une aide courte aux gestes au survol ou sous le compteur.
- **Retirer les trois grands boutons permanents** Déplacer / Ajouter / Retirer de ce bandeau : les gestes gauche/droit et le menu contextuel suffisent.
- Les **commandes groupées restent accessibles** par clic droit / touche Menu ; le menu doit proposer les trois actions, avec source/destination préremplies intelligemment et une utilisation sans dialogues à répétition.
- La multi-sélection reste visible dans Liste, Détaillée, Mosaïque ; l'inspecteur affiche un **aperçu neutre du lot** et non la fiche unique trompeuse. Pas de sélection cachée après navigation ou relance.
- Échap, Ctrl+A, Ctrl/Maj+clic, Maj+flèches et l'ouverture/édition d'une fiche individuelle restent cohérents.

## 4. Identifiants techniques : seulement lorsque nécessaire pour une homonymie réelle

**Règle unique de présentation :** identité interne toujours GUID ; **nom utilisateur par défaut**.

- Un projet au nom unique dans le choix proposé : afficher **« Ian »** ou **« BHE / Réflexion »**, **sans UUID ni suffixe**.
- Pour **deux choix réellement indiscernables**, afficher une distinction **locale, compacte et cohérente** : exemple `Cours M2 · 1` / `Cours M2 · 2`, ou identifiants **abrégés**. Le numéro doit être déterministe selon les ID internes dans une même liste, pas changer au gré d'un tri.
- Un **chemin complet déjà distinct** (`BHE / Réflexion` vs `Cours / Réflexion`) peut suffire : aucun ajout artificiel de GUID. N'ajouter un suffixe que lorsqu'il existe une **collision sur le libellé réellement affiché** dans ce sélecteur.
- Les identifiants intégraux restent dans les **valeurs internes** et éventuellement dans une zone « détails techniques » seulement si l'utilisateur le demande ; ne jamais confondre deux dossiers de même nom.
- Appliquer cette règle aux sélecteurs des opérations **groupées**, aux sources et destinations, et aux interactions individuelles de classement si elles affichent également des GUID techniques. Le menu de drop et la barre de progression ne doivent pas afficher des ID bruts.
- **Ne jamais transformer** le GUID en numéro métier persistant, ni modifier le schéma 4, ni fusionner les projets homonymes. Une simple fonction de libellé de choix avec table `libellé affiché → UUID local` suffit.

## 5. Séparation claire : sélectionner ≠ ouvrir ChatGPT

**Comportement impératif dans les TROIS vues :**

- Un clic sur **le titre, l'icône de gauche, la couverture ou une zone vide de la ligne/carte** : **sélectionner** et mettre à jour l'inspecteur, sans appel à `open_thread`.
- Le **double-clic** sur ces mêmes zones : ne doit pas ouvrir ChatGPT (peut conserver la sélection/ouvrir le projet enfant s'il était déjà navigable).
- Cliquer sur **↗ à droite de la ligne ou dans l'angle de la carte** : ouvre **une seule fois** l'URL de **cette** discussion. Aucune autre zone de résultat ne doit déclencher l'ouverture.
- Le bouton ↗ doit rester **visuellement reconnaissable, accessible au clavier**, avec titre/infobulle « Ouvrir dans ChatGPT ». Prévoir l'activation clavier de cette action focalisée ; `Entrée` sur le **titre/ligne** ne doit plus ouvrir l'URL de façon implicite. Ne pas casser l'accessibilité du clavier.
- Si un lot est sélectionné, cliquer explicitement le ↗ d'un fil doit ouvrir **ce fil** uniquement, pas détruire la sélection ni lancer d'action de masse.
- **Différencier hit-test de sélection et hit-test d'ouverture** (par exemple `open_action_hit`/équivalent) dans `CatalogList`, `ResultsView`, `MosaicRenderer`. Vérifier le rendu à plusieurs tailles, zoom/DPI et titres longs ; **ne pas compter sur la proximité du texte**.
- Mettre à jour le **curseur souris** : main seulement sur ↗, normal sur titre/ligne, curseur de redimensionnement sur séparateurs. Aucun clic en en-tête ne doit ouvrir un lien.
- Réexaminer les trois chemins `drag_release`, `result_double` et `result_enter` (et les éventuels boutons d'aperçu qui ont leur **propre** action explicite Ouvrir) ; ne pas laisser de voie détournée qui ouvre sur un titre.
- Mettre à jour **« Gestes et raccourcis »**, le texte d'aide au bas de la liste, README, doc de sélection groupée, pour ne pas continuer à annoncer « Titre ou ↗ : ouvrir ».

**Note :** le bouton explicite « Ouvrir le fil » de l'inspecteur reste une action intentionnelle et peut subsister ; ce qui est supprimé est l'ouverture automatique par le clic sur le titre/ligne.

## 6. Tests et recette — zéro cérémonie supplémentaire

Conserver les tests existants (au dernier rapport : **173 Python + 43 JavaScript**) en adaptant les attentes qui impliquaient l'ancien geste. Ajouter des tests sur événements Tk **réels** (pas seulement appels directs) :

1. **Clic et double-clic** sur titre/icône/couverture en Liste, Détaillée, Mosaïque → zéro URL ouverte ; clic ↗ → une seule URL du fil ciblé. Ctrl/Shift sur titre : zéro URL, sélection correcte.
2. **Glisser gauche d'UN fil** vers un projet → déplacement immédiat sans changement de geste ; glisser gauche de **TROIS fils sélectionnés** → les trois déplacés en une écriture, source correcte, autres rattachements préservés. Droite = menu Déplacer/Ajouter, un et plusieurs.
3. Lancer un drag sur fiche **du lot** vs fiche **hors du lot** ; déplacement depuis parent / sous-projet ; depuis Tous les fils avec source unique ou plusieurs ; depuis À classer ; source=destination, cible interdite, projet homonyme.
4. Deux fils dans P dont l'un est aussi dans R → déplacer vers Q conserve R ; ajouter dans Q depuis P laisse P ; aucune duplication de fiche UUID. Mise à jour de l'arbre, listes, comptes et sélection.
5. Sélecteur affichant « Ian » sans GUID ; deux « Cours M2 » homonymes distingués sans ambiguïté, association finale au **bon ID**, y compris lorsque les chemins sont identiques ; chemins distincts sans suffixe inutile.
6. **Pas de bandeau à trois boutons** ; menu contextuel groupé utilisable ; raccourcis existants conservés ; inspecteur neutre et touches clavier toujours correctes.
7. Fenêtre compacte 1000×680, trois vues, colonne ↗ cliquable, redimensionnement des colonnes MG-010a, sélection par Ctrl/Maj, interaction avec scroll et en-têtes ; pas de double ouverture.
8. Recette sur **catalogue fictif isolé de 1 429 fils**, avec sous-projets, homonymes et multi-rattachements. Le catalogue habituel du compte reste simplement celui de David pour ses propres essais, **aucune discussion réelle ni URL personnelle publiée** dans le repo.
9. Conserver l'intégrité normale de l'application et l'idempotence de l'import ; **ne pas ajouter de nouvelles barrières, demandes de consentement, sauvegardes avant chaque drag, confirmations de masse ni workflows de récupération**. Les transactions existantes suffisent.

**Livrables :** version corrective (0.9.2a/0.9.3 selon convention), code et tests, `reports/MG-010b-01/rapport.md` avec diagnostic et résultats, **4–6 captures Windows natives sur données fictives**, README et aide actualisés. Commit/push `origin/main`, SHA distant vérifié, dépôt propre ; arrêt pour recette David/GPT.

### Critère GO

**« Un seul fil ou vingt fils, ce sont les mêmes gestes. »**  
Glisser gauche = déplacer ; glisser droit = menu Déplacer/Ajouter ; sélection sur toute la ligne et titre **sans ouverture** ; ouverture sur **↗ uniquement** ; nom simple sans GUID, homonymes désambiguïsés ; aucune nouvelle procédure bureaucratique.
