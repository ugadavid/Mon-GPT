# MG-013a-01 — Correction du cadrage artistique : peinture uniquement, zéro refonte fonctionnelle

**17 novembre 2026 — RETOUR UTILISATEUR : NO-GO ABSOLU sur le plan MG-013a en l'état.**  
**GO : reprendre l'étude, corriger la proposition et publier un addendum documentaire.**  
**PAS DE GO : implémentation graphique, modification de code, réorganisation de l'interface, nouveaux tests applicatifs, MG-013b.**

> Nouveau Codex artiste, ou reprise du fil existant : **ne commence aucun chantier graphique**. Le rapport [MG-013a](../reports/MG-013a/rapport.md), livré au commit `1732196`, est **une étude reçue mais NON validée**. Cette mission en corrige substantiellement les hypothèses et le périmètre. Son seul résultat attendu est une proposition artistique revue à soumettre à David.

## 1. Le message du propriétaire, sans ambiguïté

« Nous ne déplaçons rien et ne changeons aucun fonctionnement. Il s'agit de peinture : couleurs, polices, icônes, finesse du dessin, habillage des commandes et des gestes existants. Pas de réécriture de ce qui est déjà codé fonctionnellement ; nous ne voulons pas repartir pour des semaines de régressions. »

**Règle fondamentale : NO-GO à toute refonte fonctionnelle.** Le contrat existant n'est pas matière à réinterprétation par une maquette. Les interfaces actuelles ont fait l'objet d'une longue série de missions et de validations humaines ; ce travail est acquis. Si une idée graphique impose un changement important de structure, de logique, de géométrie interactive, de données ou de comportements, **abandonner cette idée ou la soumettre comme suggestion future hors de cette passe**. N'en faire ni un prétexte à un refactor, ni une modification adjacente tacite.

## 2. Correction urgente de notre analyse des deux zones d'information

### A. Bandeau supérieur ≠ panneau droit

La documentation [MG-011](../docs/MG-011-navigation-et-informations.md) précise : le bandeau supérieur présente **les informations du projet sélectionné à gauche** (description, catégories, tags lorsque la place le permet). La couverture peut suivre la sélection du fil, sans remplacer les informations du projet courant. **Préserver précisément le comportement implémenté**, même lorsqu'il est plus subtil qu'une description schématique.

David souhaite y voir **autant d'informations utiles que possible** pour identifier le contenu de son projet, sans **jamais augmenter la hauteur actuelle du bandeau**, sans repousser les résultats vers le bas ni créer de scrolling supplémentaire. Pour les informations nombreuses : traitement visuel compact, hiérarchisation, ellipse/`+N` éventuellement *à proposer* dans l'espace existant, sans perte d'accès aux éléments complets ni changement de leurs règles de sélection.

### B. Inspecteur / Aperçu à droite

**Le panneau de droite affiche les données de l'élément actuellement sélectionné : celles du projet si c'est un projet, celles du fil si c'est un fil.** L'exemple utilisateur montre « BHE - Semaine 3 », type Discussion, 1 emplacement, vignette, icône, couleur, actions : ce n'est PAS la description permanente du projet du bandeau. Ne pas dupliquer ni figer ces informations sous prétexte d'harmonisation. Vérifier le code et les rapports pour préserver exactement la priorité de sélection et l'héritage des visuels.

La capture utilisateur du 17/11 à 18:04 montre aussi une composition peu heureuse : texte « Aperçu » tout en haut à gauche, bouton fermer à l'extrémité droite, puis beaucoup de vide avant le titre du fil/projet. **Proposition à étudier : retirer le titre statique superflu « Aperçu », utiliser directement le titre réel de l'élément sélectionné dans le même en-tête, et garder une fermeture discrète à proximité logique.** C'est un habillage ; ne pas toucher au fonctionnement du panneau, à la fermeture, au focus, aux actions ni à leur sémantique. Conserver l'éditeur, les notes et les sections existantes.

## 3. Révision de l'interprétation de « fenêtre compacte »

Les captures 07 et autres essais de MG-013a à 1000×680 sont des **cas de stress visuel** et non une cible ergonomique qui justifie de reconfigurer les composants. David relève notamment l'énorme largeur du volet droit dans ces exemples. **Avant de proposer des cartes plus hautes, de grossir les zones, de tronquer des titres ou de changer les mécanismes**, examiner le réglage manuel des proportions déjà disponible : réduire les volets latéraux et redonner la priorité au centre peut résoudre une partie de la gêne.

Le dimensionnement manuel, la possibilité de replier l'aperçu et les proportions choisies par l'utilisateur **doivent rester fonctionnellement inchangés**. Ne pas imposer de nouvelles largeurs automatiques, de nouveaux seuils ou de nouvelle logique de PanedWindow dans cette seule passe cosmétique. La proposition antérieure « deux lignes de titre en Détaillée » est **acceptable seulement si cela se fait naturellement et très localement**, sans refondre les cartes, leurs hit-tests, leur hauteur et leurs interactions. Sinon, conserver le comportement actuel. **Les deux lignes ne sont pas une exigence à implémenter.**

## 4. Exemples graphiques concrets à privilégier

### Remplacer des textes répétitifs par des icônes claires

L'utilisateur a cité explicitement les trois boutons **Liste / Détaillée / Mosaïque** : il préfère un **sélecteur compact avec icônes compréhensibles**, du type contrôle déroulant/choix de vue d'un logiciel moderne, plutôt que trois boutons textuels occupant de la place.

**Portée** : remplacer uniquement la présentation de ces trois commandes en conservant **strictement** leurs trois actions existantes, le mode courant visible, les raccourcis, la persistance, le focus et l'accessibilité clavier ; prévoir infobulles/libellés accessibles pour lever toute ambiguïté. Si ce remplacement réclame une refonte du mécanisme, proposer une variante purement visuelle moins intrusive (trois icônes groupées ou commande actuelle habillée), pas de nouvel état métier ou modèle de vues.

De manière générale, préférer des pictogrammes à un texte explicatif redondant **lorsqu'ils sont immédiatement compréhensibles**. Ne pas rendre les actions mystérieuses : tooltip et intitulé accessible restent nécessaires. Ce sont des arbitrages visuels à soumettre, pas des suppressions de commandes.

### Rendre le geste de déplacement plus agréable

Étudier **le style du geste de déplacement** dans la maquette historique :
[Image bibliothèque `11_51_54-2.png`](../missions/MG-002-maquettes/Image%20ChatGPT%2014%20nov.%202026,%2011_51_54-2.png).

Retenir son **langage graphique** (repère de drag, emplacement cible, signal de dépôt, menu contextuel attrayant) sans reprendre une logique de geste dessinée qui contredirait le code. Les gestes déjà validés restent : glisser gauche, glisser droit, déplacer un rattachement ou en ajouter un, refus des cibles interdites, aucun clonage. Si les détails graphiques du modèle sont incompatibles avec Tk existant, préférer une peinture de la présentation actuelle.

### Finitions « peinture »

Palette, polices disponibles, niveaux typographiques, icônes, contrastes, tailles/espacement des contrôles dans leurs zones actuelles, filets, menus, cartes, pastilles, hover/focus et cohérence des fenêtres Aide/Crédits. Pas de nouvelle dépendance lourde, pas de moteur CSS inventé pour Tk, pas de migration de toolkit.

**« Uniquement de la CSS » est une analogie de l'intention** : Mon GPT est en Python/Tk, donc améliorer les styles/dessins de widgets existants, pas introduire une technologie Web.

## 5. Ce que MG-013a doit corriger explicitement

Le premier rapport suggérait une **recomposition des rangées centrales**, une **restructuration de cartes Détaillée/Mosaïque**, un **changement de présentation des fiches**, parfois des mesures de géométrie interactive. Ces idées dépassent la peinture souhaitée : elles sont **refusées comme périmètre de réalisation** en l'état.

Revoir donc les quatre lots proposés, ou les remplacer par **quelques lots purement cosmétiques, indépendants, courts et faciles à annuler**, sans architecture, sans déplacement de fonctionnalité et sans toucher au code métier. Chaque lot doit expliciter :
- éléments visuels concernés ;
- changements STRICTEMENT de présentation ;
- comportements et zones de code à ne pas toucher ;
- comment vérifier quelques interactions voisines **sans batterie de tests disproportionnée** ;
- aperçu avant/après envisagé et point d'arrêt humain.

**Ne pas attribuer de GO esthétique ou technique à David.** Les points validés ici sont des contraintes et des corrections d'interprétation ; la nouvelle proposition graphique reste soumise à son arbitrage.

## 6. Sources et livraison de cette correction

Relire au moins :
- [Rapport MG-013a](../reports/MG-013a/rapport.md), les neuf captures et les trois maquettes du dossier `MG-002-maquettes` ;
- [MG-011 — Navigation et informations](../docs/MG-011-navigation-et-informations.md) ;
- [MG-010b-01 — Gestes](../missions/MG-010b-01_gestes_naturels_et_libelles.md) et rapports associés ;
- [MG-012 — Fenêtre Licences](../reports/MG-012/rapport.md) ;
- `AGENTS.md`, modules d'affichage et inspecteur réels.

Les captures utilisateur complémentaires (bandeau rempli, schéma avec identité à gauche et information projet à droite, zoom de l'inspecteur « BHE - Semaine 3 ») ont été commentées dans le chat ; **ne pas prétendre les avoir vues dans le workspace si elles n'y sont pas**. Les descriptions et règles ci-dessus suffisent pour orienter la correction ; les originaux graphiques du dépôt sont déjà accessibles.

Publier **uniquement** `reports/MG-013a-01/rapport.md` (et, si utile, un tableau d'arbitrages textuel dans le même dossier). Présenter un tableau clair **ancien projet MG-013a → objection → proposition corrigée** et un plan minimal exclusivement esthétique. Pas de changement de code, d'interface, de données, de tests applicatifs, de maquettes originales ou de `AGENTS.md`. Aucun transfert d'images en blobs, aucune batterie de tests pour une correction documentaire.

Commit/push du seul dépôt `ugadavid/Mon-GPT` sur `origin/main`, SHA vérifié, état propre. **STOP pour validation de David**, sans lancer MG-013b ou la grande passe. Le présent fichier fait explicitement foi sur les intentions de l'utilisateur par rapport au rapport initial lorsque les deux divergent.

**Statut demandé : MG-013a-01 documentaire — NO-GO refonte fonctionnelle et structurelle.**
