# MG-002b-05 — Édition de fiche : la finesse de l'aperçu, sans formulaire disgracieux

**Statut : à réaliser — micro-mission de présentation strictement limitée à la colonne droite, mode Édition.**  
**Base :** `origin/main` au commit `88330c98a1bd8362edbba4ae1beee8f060ce82f4` (MG-002b-04, version 0.2.1 ; **57 tests réussis**).  
**Décision utilisateur :** **MG-002b-01 à 04 sont validées et figées** (menu, disposition/recherche, Liste, aperçu en lecture seule). MG-002b-05 rend seulement **l'éditeur de fiche** aussi élégant que l'aperçu ; **MG-002b-06 reste ultérieure**.

## 1 — Le retour utilisateur à traiter sans extrapoler

Captures de la recette du 14/11/2026 : l'aperçu lecture seule est apprécié, mais passer à `Modifier la fiche` provoque une rupture esthétique nette. L'utilisateur demande :

> « Pourquoi la modification est-elle toujours aussi grossière ? Il faudrait des traits plus fins, surtout autour des textarea. Être un peu moins verbeux : pas besoin de TITRE LOCAL, Titre suffit largement ; LIEN CHATGPT → Lien. Globalement, reprendre les mêmes styles que l'onglet aperçu. Pourquoi la page de modification devient vulgaire ? »

Et, pour les tags et catégories : **occupent réellement toute la largeur utile, affichent les valeurs existantes, utilisent les couleurs et les pastilles harmonisées des maquettes et de la Liste**. Pas une pauvre petite combobox et un grand vide, pas toutes les pastilles identiques par défaut.

**Mot d'ordre : en passant d'Aperçu à Modification, on doit avoir l'impression de rester dans la MÊME fiche.** C'est une petite mission visuelle, pas une nouvelle refonte de l'app.

## 2 — Références et périmètre de code

- Partir de l'**aperçu validé MG-002b-04**, en regardant sur CODEX-VM sa vraie présentation, et consulter **localement** les trois PNG de `missions/MG-002-maquettes/`, notamment leurs panneaux droits. **Ne pas recopier, modifier, re-uploader ni publier de blobs PNG.**
- Code cible : `mon_gpt/details.py`, méthode `DetailEditor.render_editor()` ; `mon_gpt/widgets.py`, composant `ChipPicker` ; styles dédiés si nécessaire dans `theme.py` ou une petite aide graphique locale déjà existante.
- Préserver `show_summary()` / `inspector.py` **tels que validés**. Préserver le conteneur, la largeur de la colonne droite, les scrollbars/molette/focus et le mécanisme de retour à l'aperçu. N'installer aucun framework ou dépendance pour la seule décoration.

## 3 — Livrables graphiques précis

### 3.1 En-tête et intitulés concis

- `Votre fiche locale` peut devenir un sobre **« Modifier la fiche »** (ou « Édition ») : un titre clair, sans slogans décoratifs.
- `← Aperçu` accessible discrètement à côté de l'en-tête, pas une rangée complète pour lui tout seul.
- **Libellés courts, en casse normale**, sans tout mettre en capitales : `Titre`, `Lien`, `Résumé` (pour un fil) ou `Description` (projet), `Notes`, `Tags`, `Catégories`, `Informations`, `Emplacements`, `Projet parent` selon le type.
- Les consignes techniques (`clé=valeur`, sélection multiple) deviennent une **aide discrète à proximité du champ**, pas un titre lourd. Aucun champ n'est supprimé ni rendu inaccessible.

### 3.2 Champs « papier » fins et lisibles

- Champs texte simples et multiligne dans le même langage que l'aperçu : **bordures fines à faible contraste**, coins doux si réalisables sans casser focus/édition, petites marges internes, fond ivoire/papier uniforme, typographie homogène.
- **Supprimer les contours noirs épais autour des `Text`** (actuellement `relief="solid", borderwidth=1, highlightthickness=1`), en conservant une **bordure/focus visibles** et le caret. Les contours doivent rester identifiables, pas disparaître.
- Espacements équilibrés, champs ni collés ni séparés par des vides inutiles. La largeur remplit le panneau disponible. Un long titre, une URL longue et des notes étendues doivent rester lisibles et éditables sans superposition.
- Bien distinguer les contenus modifiables de l'aperçu en lecture seule, mais **sans changement brutal de style** ni gros boutons en relief.

### 3.3 Tags et catégories : exploiter la largeur, valeurs réutilisables

- Présenter les **valeurs sélectionnées en pastilles colorées cohérentes avec la Liste** ; tags et catégories visuellement distinguables. Couleurs **différenciées, stables et lisibles**, si possible selon la valeur, sans nouvelle persistance ni modification du catalogue.
- Les pastilles doivent **se répartir / revenir à la ligne sur la largeur réelle du panneau** ; **pas de grille figée à deux colonnes** qui laisse un grand espace inutilisé. Texte long et retrait `×` restent accessibles.
- La ligne de saisie/choix d'une valeur connue occupe **toute la largeur disponible**, avec bouton compact `+` en fin de ligne ; pas d'étroit champ `width=18` au milieu d'un grand panneau. Saisie filtrée et suggestions des valeurs existantes, sélection clavier/souris, ajout nouveau, suppression d'une pastille, absence de doublon : **fonctionnalités présentes à conserver**.
- Tags et catégories restent deux notions distinctes : **ni mélange ni transformation en rattachements**.
- Préserver la logique métier de `ChipPicker`, sa normalisation et la gestion du `dirty` ; dans ce lot, ne pas modifier la portée des suggestions ni le mécanisme de recherche global.

### 3.4 Actions et retour à l'aperçu

- **Enregistrer** reste l'action majeure et clairement identifiable, tout en s'intégrant dans une rangée soignée avec les autres actions légitimes ; `Supprimer…` ne doit pas ressembler à une action innocente. Éviter de doubler inutilement l'ouverture du fil.
- `Ctrl+S` doit continuer d'enregistrer **la fiche**, sans sauvegarde globale du catalogue.
- Enregistrer puis revenir à l'aperçu doit montrer immédiatement les modifications ; annuler/revenir avec changements non sauvegardés conserve l'avertissement MG-001. Aucun effacement silencieux des tags, emplacements, notes, URL ou champs personnalisés.
- Préserver l'éditeur des **projets** (description, notes, tags, catégories, métadonnées, choix du parent) ainsi que celui des **fils** (titre, URL, résumé, notes, tags, catégories, métadonnées, rattachements multiples). Pas de migration de schéma ni de suppression de champs.

## 4 — Frontières fermes

**Intouchables :** menu `main_menu.py`, arborescence gauche, bandeau Masthead, recherche et filtres, géométrie et marges des trois panneaux, Liste `CatalogList` / ouvertures directes, aperçu `InspectorSummary`, raccourcis/classement glisser-déposer, `core.py`, `chatgpt.py`, `storage.py`, schéma JSON 1 et les trois PNG.

**Hors lot :** les vues Détaillée/Mosaïque, la galerie de couvertures, personnalisations persistantes des icônes/couleurs, l'anomalie suspecte des URL de discussion en doublon et toute logique de saisie/création de nouvelles fiches en dehors de l'éditeur.

Le chantier est **strictement graphique** : petits changements locaux de l'éditeur et du sélecteur de pastilles uniquement. Aucune extrapolation « amélioration globale » de l'application.

## 5 — Recette de CODEX-VM et acceptation

Utiliser un catalogue **fictif** `--data-dir` isolé et `--simulate-open`, sans lire/écraser le catalogue normal. **Conserver les 57 tests** existants et ajouter uniquement des tests ciblés.

Vérifier sur la **vraie application Tk exécutée** :
1. Sur le même fil, capture avant/après **Aperçu → Modifier**, pour juger le style commun.
2. Fenêtre **1360×820**, puis **1000×680** ; champs, boutons, pastilles, scrollbar, molette et focus ; aucun contrôleur hors panneau.
3. Titre long, URL fictive longue, résumé/notes volumineux, métadonnées `clé=valeur`, nombreux tags et catégories dont libellés longs, éléments absents.
4. Sélectionner une valeur connue, saisir une nouvelle, retirer une pastille, **Enregistrer**, relire en aperçu, fermer/réouvrir et contrôler la persistance.
5. Modifier une fiche projet avec parent et une discussion avec **plusieurs rattachements** ; aucun rattachement perdu. Saisie invalide et annulation avec changements non enregistrés : sécurité inchangée.
6. Ctrl+S, Tab/Shift+Tab, navigation aux suggestions, actions au clavier : focus visible, pas de commande accidentelle.

**Preuves** : **3 captures natives maximum**, fictives : (1) aperçu validé et éditeur côte à côte si possible, sinon deux captures (une de chacun) ; (2) éditeur en format normal avec tags/catégories répartis sur toute la largeur ; (3) format compact avec scrollbar/notes. Pas de nouveau rendu d'image généré pour faire passer la recette.

Livrer `reports/MG-002b-05/rapport.md` (comparaison claire aux maquettes, tests, limites, captures), code, tests, README ajusté seulement si nécessaire ; commit/push sur `origin/main`, SHA distant vérifié et dépôt propre.

**Pas de GO graphique automatique** : Codex apporte la preuve, l'utilisateur valide avant tout MG-002b-06.

**Critère unique : l'éditeur ne doit plus paraître « vulgaire » par rapport à l'aperçu — même finesse visuelle, sans perdre la moindre donnée ni action.**
