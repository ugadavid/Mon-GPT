# MG-002b-04 — L'inspecteur : une vraie fiche d'aperçu, légère et élégante

**Statut : à réaliser — une micro-mission centrée sur l'inspecteur droit.**  
**Base :** `origin/main` après MG-002b-03, commit `303e038af4a71409edab8979722d54e97b33a83f` ; Mon GPT<3 0.2.1, **53 tests** réussis.  
**Validation utilisateur :** MG-002b-01 (menu), MG-002b-02 (trois colonnes/recherche) et MG-002b-03 (Liste centrale) sont **acceptées**. **Ne plus les retoucher**.

## 1 — Retour utilisateur précis

L'utilisateur souhaite retrouver dans l'inspecteur la finesse des maquettes, et a explicitement relevé :

- « **LE COIN DES IDÉES** » répété sur toutes les fiches : décoratif, mais sans information pertinente.
- Icône de type de fiche **isolée sur une ligne**, qui gaspille de l'espace.
- Grand bouton « Ouvrir le fil » **tout seul sur sa ligne** ; puis les actions « Copier le lien » / « Modifier la fiche » sur une autre ligne. **Trois actions doivent tenir sur UNE même ligne** quand la largeur le permet.
- **Privilégier une petite icône ↗** pour ouvrir, une icône de copie pour copier et un crayon pour modifier, plutôt que répéter des libellés lourds. Icônes compréhensibles avec info-bulles et accès clavier.
- L'**indicateur visuel de défilement** doit exister : molette fonctionnelle, oui, mais scrollbar **fine, discrète ET visible dès que le contenu dépasse** (pas un indicateur qui disparaît lorsqu'on doit défiler).
- Les sections « En quelques mots », « Vos repères », « Notes de carnet » peuvent être accueillantes, mais doivent devenir **des informations utiles regroupées sans grands espacements ou redites**.

**Mot d'ordre : une fiche lisible en un regard, pas un grand formulaire décoré.** L'inspecteur reste **secondaire et facultatif** : on peut toujours ouvrir un fil directement depuis la Liste.

## 2 — Références graphiques locales

Consulter **localement** les trois PNG de `missions/MG-002-maquettes/`, particulièrement :
- `Image ChatGPT 14 nov. 2026, 11_51_55-3.png` : **inspecteur droit compact**, titre, actions rapprochées, sections de détails repliables ;
- `Image ChatGPT 14 nov. 2026, 11_51_22-1.png` : hiérarchie, icônes, petits contrôles, tags et catégories accueillants.

La maquette sert d'inspiration **uniquement pour la colonne droite**. Le menu, la recherche, l'arborescence gauche, la Liste et la géométrie générale sont **figés**. **Ne pas télécharger, renommer, dupliquer ni republier ces images en blobs.**

## 3 — Résultat visuel attendu

### A. En-tête utile

- Un en-tête **« Aperçu » ou « Discussion »** discret, avec la commande de fermeture/repli `×` / chevron **sur la même ligne**. Supprimer « LE COIN DES IDÉES » et autres slogans décoratifs répétés.
- Le **titre** du fil ou du projet doit dominer. Petite icône de type placée **sur la même ligne ou immédiatement accolée au titre**, pas sur une ligne solitaire.
- Afficher éventuellement un sous-titre **informatif** : `Discussion · 2 emplacements`, `Projet`, chemin principal, etc., sans doublon.

### B. Actions en UNE seule ligne

- Pour une discussion, regrouper sur **une rangée compacte** les commandes réelles : `↗` **Ouvrir le fil**, `Copier` le lien (icône copie), `Modifier` la fiche (icône crayon).
- **Pas de gros bouton Ouvrir sur toute la largeur.** Le CTA reste reconnaissable par l'accent terracotta et un survol approprié, mais ne doit pas prendre une ligne entière à lui seul.
- Chacun des trois boutons possède une **info-bulle texte** (`Ouvrir le fil`, `Copier le lien`, `Modifier la fiche`), un focus clavier visible et une activation clavier ; ne pas sacrifier l'usage au dessin.
- Pour un projet : pas de bouton d'ouverture ChatGPT ; uniquement les actions pertinentes, notamment modification.
- Largeur réduite : adapter espace et taille des boutons tout en conservant la clarté et **sans renvoyer une action sur une ligne isolée ou masquer les commandes essentielles**.
- Ne pas changer les comportements ni la validation HTTPS de `open_thread`, `copy_link` et `show_record`.

### C. Corps de fiche compact et distinct

- Envisager **Résumé**, **Emplacements**, **Tags**, **Catégories**, **Notes** et détails complémentaires sous forme de sections lisibles, espacements maîtrisés, filets fins ou petites cartes de papier.
- Préserver l'accès à toutes les données **sans forcer leur affichage complet**. Notes longues et informations secondaires peuvent être **repliables**, mais pas cachées de manière permanente ; s'assurer que les états sont explicites et navigables.
- Garder **tags et catégories distincts**, idéalement petites pastilles cohérentes avec la Liste MG-002b-03, sans reproduire leurs menus d'édition. L'objectif du présent lot est **la présentation en lecture seule**.
- Aucun texte placeholder poétique ne doit masquer le fait qu'un champ est vide. Préférer `Pas de résumé`, `Aucune note`, `Aucun tag` ou équivalent sobre.
- Retirer les grandes marges verticales gratuites, sans coller pour autant les contenus : **respiration et densité équilibrées**.
- **Ne pas ajouter de couverture, de vignette ni de personnalisation persistante** : ce sera traité dans les futures vues Détaillée/Mosaïque.

### D. Scrollbar, molette, focus et dimensionnement

- **Scrollbar verticale fine mais identifiable** sur le bord droit de l'inspecteur **lorsqu'il y a du contenu à défiler**. Le code actuel utilise `AutoScrollbar` qui masque la barre quand tout tient ; vérifier son comportement quand le contenu dépasse, et, si nécessaire, substituer pour le seul inspecteur un contrôle plus discret mais visible.
- Molette et scrollbar suivent le même défilement, même quand le pointeur survole les boutons/sections ; aucune interception du scroll de la Liste ou de l'arbre.
- Lors d'un changement de fiche, retour de la lecture au début ; ne pas casser `Échap`, clavier, survol, ouverture/fermeture répétée de l'inspecteur ni l'accès à l'éditeur.
- Tester au minimum **1000×680 et 1360×820**, aperçu ouvert, ainsi qu'une fenêtre agrandie ; permettre des titres longs, plusieurs rattachements et notes très longues sans superposition. Préserver la géométrie et la largeur des colonnes déjà validées.

## 4 — Frontières strictes de la mission

**Zone autorisée :** présentation de `show_summary()`, petits composants de l'inspecteur et éventuel scrollbar/focus propre à ce panneau ; adaptation minimale des styles dédiés. `render_editor()` de `details.py` conserve ses fonctions d'édition : ne pas le transformer dans ce lot.

**Zones INTERDITES :** 
- `main_menu.py` et le menu validé ;
- Masthead, recherche, filtres, bandeau, trois colonnes, leurs marges, arborescence gauche et Liste centrale `CatalogList` ;
- glisser-déposer, édition des tags/catégories, création inline, raccourcis, logique d'ouverture des fils, doublons ;
- `core.py`, `chatgpt.py`, `storage.py`, schéma JSON et données utilisateur ;
- vues Détaillée/Mosaïque, import d'images, galerie et couvertures.

**Les idées utilisateur pour les deux futures vues centrales sont réservées à leur propre atelier de conception : ne pas les anticiper ici.**

## 5 — Recette ciblée et publication

- Lire `reports/MG-002b-03/rapport.md` et la spécification UX, puis analyser l'inspecteur réel. **Pas de réécriture de moteur ni de chantier transversal.**
- Préparer le catalogue **fictif** sous un `--data-dir` distinct, lancé avec `--simulate-open`.
- Vérifier : fil avec titre long et plusieurs emplacements, projet, fiche vide, tags/catégories, notes très longues, plusieurs pages de lecture, icônes d'action cliquées (ouvertures simulées), copie du lien, passage à l'éditeur puis retour à l'aperçu.
- Contrôler **molette + scrollbar visible**, survol de ses éléments, focus clavier, repli/réaffichage, redimensionnement, et **aucune régression** de la Liste directe.
- **Conserver les 53 tests** (ou leurs comportements) et ajouter seulement les nouveaux tests ciblés. Ne pas confondre contrôles simulés et gestes Windows effectivement observés.
- Fournir **3 captures réelles** de CODEX-VM : (1) aperçu d'un fil avec toutes les actions regroupées et titre, (2) notes/rattachements avec scrollbar visible pendant défilement, (3) aperçu en 1000×680 ou d'un projet.
- Rapport court : `reports/MG-002b-04/rapport.md` avec comparaison précise à la référence, tests, réussites et écarts. Commit/push `origin/main`, SHA distant vérifié, dépôt propre. Ne pas toucher aux trois PNG.
- **Pas de GO esthétique auto-décidé** : l'utilisateur juge l'inspecteur avant toute mission suivante. Aucun MG-002b-05 engagé automatiquement.

**Critère de passage : un inspecteur plus petit dans l'esprit, plus riche en information utile, plus agréable et plus fluide, qui ressemble enfin aux panneaux de nos maquettes.** Un seul lot, **uniquement l'inspecteur**.
