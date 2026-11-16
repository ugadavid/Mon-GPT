# MG-010b — Sélection multiple et classement groupé des discussions

**Statut : à réaliser par Codex, puis recette David/GPT.**  
**Base validée par David :** Mon GPT<3 **0.9.1 / MG-010a**, commit `0690cde920de70498c52d7915eba0b0539d15a4f`.  
**Version cible indicative : 0.9.2**. Le Collector Chrome **0.8.2** ne change pas.

## 0. Objectif et frontières

La vraie recette sur une bibliothèque de plus de **1 400 fils** a confirmé que la sélection unique dans la partie centrale ralentit le rangement. David demande de **sélectionner plusieurs fils à la souris et au clavier**, puis de **déplacer ou « copier » plusieurs fils vers des projets**.

Le mot **« copier »** signifie ici **ajouter un rattachement supplémentaire vers un projet sans créer de fiche ni dupliquer la conversation**. Le modèle métier sait déjà conserver plusieurs emplacements par fiche (`Catalog.attach`).

**Cette mission couvre** :
1. sélection multiple des **discussions** en Liste, Détaillée et Mosaïque, modèle et gestes cohérents ;
2. bandeau/commandes contextuelles **d'actions groupées** : **Déplacer des rattachements**, **Ajouter un rattachement**, **Retirer un rattachement** ;
3. aperçu des conséquences, contrôle explicite du rattachement source et **transaction atomique** ;
4. recette Windows sur catalogue isolé de 1 429 conversations fictives, puis validation David.

**Hors périmètre** : sélection groupée ou déplacement massif de **projets/sous-projets**, suppression de masse, renommage/édition de tags ou catégories par lot, déplacement de fichiers Windows, édition d'un fil dans ChatGPT, récupération de nouveaux fils, configurateur des colonnes MG-010c, dashboard, installateur, refonte graphique. Ne créer aucun projet logiciel distinct.

Consulter `docs/idees-et-finitions.md` comme **parking seulement**. Ne pas lancer ses autres idées.

## 1. Code à étudier avant conception

- `mon_gpt/atelier.py` : **`CatalogList(tk.Canvas)`**, actuellement `self.selected` unique, `selection()` / `selection_set()`, `select_click`, `navigate`, `draw`, focus, curseurs de séparateur et scrolling.
- `mon_gpt/results.py` : **`ResultsView`** partagé, événements de Liste, Détaillée, Mosaïque ; render et sélection couleur.
- `mon_gpt/mosaic.py` : cartes, hit-test, navigation à flèches et image cliquable.
- `mon_gpt/ui.py` : `select_record`, `select_identity`, `refresh_results`, `result_enter`, `result_double`, `results_context_menu`, `context_menu`, `transfer`, `transfer_panel`, `drag_press/motion/release`, `drop_action`, `rename_selected`, `escape`, `set_view`, `close`.
- `mon_gpt/core.py` : `Catalog.attach`, `Record.projects` (liste de GUID locaux), recherche ; **ne pas modifier le socle générique si aucune nécessité**.
- `mon_gpt/details.py` : `can_leave`, `transaction` (rollback en cas d'échec), éditeur d'une fiche, sauvegarde.
- `mon_gpt/storage.py` : schéma 4, mappings ChatGPT, sauvegarde atomique, images personnelles.
- Tests `tests/test_recipe_fixes.py`, `test_catalog.py`, `test_mosaic.py`, `test_workspace.py`, `test_ux.py` ; `AGENTS.md`.

**Attention :** la partie centrale est un **Canvas maison**, non un Treeview Tk natif. Ne pas tenter un pseudo-correctif `selectmode="extended"`.

## 2. Modèle de sélection cohérent et sans régression

Utiliser un **ensemble ordonné d'identifiants locaux de discussions** (les `Record.id` des `item`), un **ancrage** de sélection et un **élément focal**. Le modèle doit vivre dans le composant commun et/ou un contrôleur clair, **pas trois implémentations divergentes**.

**Gestes obligatoires sur Windows :**
- **Clic simple sans modificateur** : sélection d'une seule fiche ; sur le titre ou l'icône ↗, **préserver l'ouverture directe existante** pour une sélection simple.
- **Ctrl+clic** : ajouter/retirer une discussion sans ouvrir le navigateur, sans lancer le glisser ; la sélection restante demeure.
- **Maj+clic** : sélectionner une plage **selon l'ordre visible actuel** (après tri et filtre), entre l'ancre et la ligne cliquée ; pas depuis l'ordre brut du catalogue. Si Ctrl+Maj est pris en charge, l'union avec la sélection courante ; sinon documenter une règle stable et intuitive.
- **Ctrl+A** lorsque la partie centrale a le focus : sélectionner **toutes les discussions visibles dans la portée et les filtres courants**, y compris celles hors écran ; exclure les projets immédiatement enfants éventuellement listés et les fiches cachées par filtres. Ne pas intercepter Ctrl+A dans les champs de texte, éditeurs ou rechercher.
- **Flèches** : déplacer la sélection/focale d'un élément comme aujourd'hui ; **Maj+flèches** étendre la sélection jusqu'à la nouvelle ancre ou focale, en gardant le scrolling. En Mosaïque, prendre en compte les colonnes de la grille (navigation en 2D) et les deux tailles Normal/Grand.
- **Échap** : en l'absence d'édition/popup/drag en cours, ramener une multi-sélection à une sélection simple ou la vider, sans fermer brutalement l'inspecteur ; respecter la priorité des traitements Échap existants.
- Sur les trois vues, **toutes les fiches sélectionnées** sont visibles avec le même vocabulaire de couleur/contour ; l'élément actif/focal peut être distingué. Aucun flicker ni confusion avec le survol.
- Les clics sur **en-tête/redimensionnement de colonnes, contrôles de tri, défilement, couverture, ouverture, glisser-dépôt** ne doivent pas être interprétés par erreur comme un Ctrl+clic, une sélection de plage ou un lancement de navigateur.

**Changement de contexte :** garder la sélection si on passe de Liste à Détaillée à Mosaïque **sans changer l'ensemble de résultats**. Lorsqu'on change de projet, de recherche, de filtres, de tri ou qu'un import rafraîchit le catalogue, conserver uniquement les identifiants encore visibles, en préservant l'ordre et l'ancre si possible ; aucune sélection invisible ne doit recevoir une action de lot. Préférer vider explicitement lors d'un changement de projet si le modèle devient ambigu.

**Compatibilité :** conserver une API claire pour les appelants qui attendent une sélection simple (surtout `selection()[0]`, `selection_set(id)`, `selected`, `focused`). Adapter soigneusement ces appelants et les tests ; ne pas laisser `self.current` pointer un fil unique en guise d'inspecteur d'une sélection de vingt fiches.

**Projets visibles dans la partie centrale :** possibilité de les sélectionner **seuls**, afin d'ouvrir/naviguer comme avant, mais ils ne doivent **jamais être ajoutés au lot des discussions**. Si l'utilisateur clique un projet après un lot de fils, quitter proprement la sélection groupée et naviguer selon la logique existante.

## 3. Signaux d'interface, sans nouvelle usine à gaz

Quand **2+ discussions** sont sélectionnées, faire apparaître un **bandeau compact** au-dessus de la partie centrale :

**« 23 discussions sélectionnées » — « Déplacer… » — « Ajouter un rattachement… » — « Retirer un rattachement… » — « Désélectionner »**.

Le bandeau ne doit ni masquer le tri/la recherche ni dégrader la fenêtre 1000×680. En dessous du seuil 2, comportement **inchangé**.

- En sélection multiple, l'inspecteur droit affiche un **état synthétique neutre** (« 23 discussions sélectionnées » et aide aux actions), **pas le titre, les notes ou les champs d'une seule fiche qui laisseraient croire qu'elle est la seule sélectionnée**. Aucun éditeur multi-fiche implicite.
- Un clic droit sur une des fiches sélectionnées conserve le lot et affiche les actions de groupe ; clic droit sur une fiche non sélectionnée peut basculer vers son menu individuel, sans agir sur le lot caché. Touche Menu / clavier accessibles.
- `Entrée`, `F2`, `Ctrl+S`, double-clic, boutons d'ouverture et actions de fiche unique : **ne jamais ouvrir, renommer ou modifier plusieurs conversations involontairement**. En présence d'un lot, privilégier désactivation claire des commandes individuelles ou action explicite limitée à l'élément focal (sans ambiguïté). Les actions groupées n'ouvrent aucun navigateur.
- Si une fiche est en **édition non enregistrée**, `can_leave()` reste prioritaire : annulation signifie **aucune mutation ni perte de brouillon**.
- Le bandeau se met à jour en temps réel ; les nombres sont des **fiches distinctes**, pas le nombre de liens/rattachements.

## 4. Les trois opérations groupées : exigences exactes de sûreté

### A. « Ajouter un rattachement… » (copie logique de lien)

- Choisir une **destination projet local existant** (racine = pas une destination de rattachement).
- Pour chaque fil sélectionné, ajouter cette destination à `Record.projects` **si absente**, en conservant **tous** les emplacements antérieurs, notes, descriptions, tags, catégories, métadonnées, UUID et URL.
- Si déjà rattaché à la destination : **inchangé**, comptabilisé comme tel.
- Ne jamais créer de fiche ou de conversation doublon : **une fiche, plusieurs dossiers possibles**.

### B. « Déplacer des rattachements… »

**Ce n'est PAS « vider tous les projets puis rattacher à destination » !**

- Proposer une **destination** et un **rattachement source explicite** commun aux discussions sélectionnées. Préremplir la source depuis le projet courant **uniquement si chaque fil sélectionné y est réellement directement rattaché**.
- S'il n'y a pas de source unique pertinente (sélection depuis « Tous les fils », fils multi-rattachés différents), **ne pas choisir arbitrairement le premier projet**. Lister les **sources communes à tous** pour faire un choix, ou expliquer qu'il faut sélectionner un lot homogène/recourir à « Ajouter un rattachement ». Aucune décision cachée par fiche.
- Déplacement = retirer **cette seule source**, puis ajouter la destination ; les **autres rattachements** de chaque fil sont conservés. Source = destination doit être un **no-op** et être signalé.
- Cas des fils **tous « À classer »** : permettre l'affectation directe à un projet (rattachement initial, sans source à retirer). Ne pas mélanger silencieusement « À classer » et fils déjà classés dans un déplacement.
- En cas de fil sélectionné ne possédant plus la source au moment de confirmer, refuser **tout** le lot avec message explicite, plutôt que modifier les autres.

### C. « Retirer un rattachement… »

- Choisir une **source existante** commune aux fiches sélectionnées. Supprimer **seulement** cette source et préserver tous leurs autres emplacements. Si un fil n'a ensuite plus aucun emplacement, il apparaît dans « À classer ».
- Pré-remplissage possible depuis le projet courant si valide pour tous. Depuis la vue Tous les fils, une source doit être choisie explicitement.
- **Ne pas supprimer les fiches** ni leurs informations ou couvertures.

### Prévisualisation et confirmation communes

Avant application, montrer dans une **petite interface cohérente avec l'Atelier chaleureux** :
- action, destination et source ; **nombre de discussions affectées / déjà dans destination / inchangées / devenant « À classer »** ;
- aperçu de quelques titres **dans la fenêtre locale uniquement**, sans imprimer ces noms dans les journaux ;
- indication « Les notes, tags, catégories, autres rattachements, URL et couvertures seront conservés » ;
- bouton **Confirmer** et **Annuler**, sans mutation pendant la prévisualisation.

Si l'opération est **impossible ou ambiguë**, blocage visible avant confirmation. Opérations identiques répétées = aucun changement supplémentaire, pas d'UUID en double. Pour un no-op, ne pas écrire/sauvegarder inutilement.

## 5. Atomicité : un lot = une transaction

**Exiger la validation d'un plan pur sur un instantané** du catalogue, puis un seul commit :

- Les opérations groupées sont sur **des identifiants internes**, jamais des titres ; les homonymes de projets sont identifiés par leurs UUID locaux.
- Revalider au commit la liste des fiches et les rattachements sources/destinations, l'état courant (possiblement changé depuis l'aperçu), ainsi que les limites du catalogue. Si changement inattendu : refus complet et proposition de rafraîchir le plan.
- Préparer le candidat sur copie ou faire une mutation à l'intérieur de la **transaction avec rollback** existante ; **une seule écriture atomique** du catalogue après validation. Éviter toute « boucle de 23 sauvegardes ».
- Sur annulation, panne disque, erreur en milieu de lot, sélection périmée, source supprimée, destination supprimée : **zéro effet partiel**, données et mappings `chatgpt_projects` schéma 4 intacts. Les images personnelles restent valides.
- Après succès, rafraîchir les trois vues, les comptes, l'arbre, le périmètre de projet et l'inspecteur ; gérer la sélection qui disparaît du filtre parce qu'on a déplacé les fiches **sans en agir une seconde fois par erreur**.
- **Interdire tout appel réseau ou modification de ChatGPT**, du Collector Chrome et de la structure des URLs.

**Ne pas introduire de raccourci risqué « Ctrl+X / Ctrl+V » dans MG-010b.** La copie demandée est l'ajout de rattachement via les commandes explicites.

### Point délicat : le glisser-déposer existant

Le glisser simple actuel ouvre parfois un fil au relâchement et gère les sources d'une fiche.

- **Préserver absolument** ses gestes validés sur une seule fiche, y compris redimensionnement de colonnes, glisser gauche/droit et ouverture directe au clic sur le titre.
- Pour un lot actif, **ne jamais glisser-déposer silencieusement une seule des fiches en laissant croire que tout le lot est déplacé**. Soit interdire clairement le drag de lot avec indication « Utilisez Déplacer… / Ajouter un rattachement… », soit le relier à **la même prévisualisation/confirmation de groupe** ; la première option est acceptable dans ce lot pour éviter un faux-semblant.
- Ne pas réutiliser `drop_action` tel quel pour chaque fiche si cela risque d'écraser les rattachements ou multiplier les sauvegardes.

## 6. Tests et recette réelle

Conserver tous les tests Python **153** et Collector JavaScript **43** de MG-010a ; adapter seulement ce qui attend volontairement la mono-sélection. Nouveaux tests unitaires et intégration avec vrais événements Tk :

1. Ctrl+clic ajoute/retire ; Maj+clic sélectionne une plage ordonnée ; Ctrl+A respecte périmètre, recherche et filtres ; Maj+flèches / mosaïque 2D ; touche Échap ; Ctrl+A dans zone de recherche conserve le comportement texte.
2. Fils de **même titre** avec UUID différents ; fil multi-rattaché ; projet enfant dans les résultats jamais compris dans le lot ; sélection persistant Liste → Détaillée → Mosaïque ; changement de projet/filtre ne déclenche aucune action sur des fiches invisibles.
3. Survol des séparateurs de colonnes, redimensionnement, clic d'ouverture, double-clic, F2, touche Menu, menu contextuel et drag simple : **aucun effet de bord**, zéro URL ouverte avec Ctrl/Shift.
4. Ajout de rattachement 20 fils vers un projet : **20 fiches préservées, zéro clone**, ignore les liens déjà présents et reimport v2 toujours sans doublon.
5. Déplacement 10 fils de P vers Q : retire **P uniquement**, conserve un autre rattachement R ; les fils uniquement dans P disparaissent de P et apparaissent dans Q ; un fil qui ne possède pas P refuse le lot entier.
6. Retirer le rattachement P de plusieurs fiches : autres emplacements conservés, celles sans autre emplacement vont dans « À classer ». Déplacer un lot « À classer » vers Q sans source.
7. Ambiguïté des origines depuis « Tous les fils », source/destination identiques, projet disparu, annulation, échec en milieu de lot, échec de sauvegarde : **aucune modification partielle**.
8. Impression au rapport d'**assertions statistiques seulement**, jamais les titres et les liens personnels.
9. Charge : sélectionner 100 fiches parmi une fixture de **1 429 conversations**, Ctrl+A avec liste défilante, les trois vues ; navigation et prévisualisation réactives. Pas de génération de widgets illimités au défilement.
10. Sauvegarde et restauration du catalogue avec image personnelle et mappings conservés ; fermeture / relance sans sélection de masse cachée.

**Windows sur CODEX-VM** : lancer `python -m mon_gpt --data-dir .recette/MG010b --simulate-open`. Toutes les manipulations destructives s'effectuent **sur des données entièrement fictives**, avec des projets parents/enfants, des fils multi-rattachés et des homonymes. L'utilisateur continuera sa recette sur sa vraie bibliothèque après livraison ; **ne pas la modifier à sa place**.

**Captures natives** : 4–6 captures sur fixtures fictives montrant Liste sélection multiple, Détaillée et Mosaïque, dialogue d'ajout/déplacement, bilan après validation. Aucun titre, URL ou donnée personnelle dans les livrables GitHub publics.

**Livrables** : code modulaire et tests, guide court des gestes clavier/souris, `reports/MG-010b/rapport.md` avec résultats précis et limites, README actualisé, version 0.9.2 indicative, commit/push `origin/main`, SHA distant vérifié, dépôt propre.

**STOP après MG-010b**, sans lancer MG-010c ni les statistiques ni l'installateur.

### Critère GO

La souris et le clavier permettent de sélectionner un véritable **lot de discussions** dans les trois vues et d'y appliquer des opérations **explicites, sûres, prévisualisées et atomiques** de déplacement ou d'ajout/retrait de rattachements, **sans dupliquer les conversations, sans perdre les autres emplacements et sans casser l'ouverture ou l'édition individuelles**.
