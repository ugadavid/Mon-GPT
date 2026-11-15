# MG-003b — Corriger l’intégration visuelle des projets (recette utilisateur MG-003a)

**Statut : mission corrective à réaliser ; pas de nouvelle vue.**  
**Base :** Mon GPT<3 v0.3.0, `origin/main` au commit `cf1852d86edc57337ccb8e38399f093c94f54b7b` (**80 tests réussis**).  
**Origine :** retour utilisateur du 15 novembre 2026 sur **cinq captures de recette réelles** de MG-003a. La migration, l'import et les archives sont livrés et ne font pas l'objet de cette correction.

## 0. Intention et règle générale

L'utilisateur **ne valide pas encore MG-003a au plan UX**. Les images, icônes et couleurs existent mais ne sont pas assez intégrées dans l'interface. Il ne demande **ni une nouvelle application, ni une vue Mosaïque**, mais que la personnalisation d'un projet soit vraiment visible, agréable et compacte.

**Priorités :**
1. **Dans l'arbre à gauche : icône choisie, dans la couleur choisie.**
2. **Dans le bandeau : l'image entière en 16:9**, dans la place libre existante, sans agrandir le bandeau ni déplacer recherche/menu/colonnes.
3. **Dans la fiche projet : trois commandes sur UNE rangée**, pas trois sections verticales.
4. **Illustration au soleil comme véritable image par défaut**, cohérente avec l'état neutre.
5. **32 à 40 icônes au choix**, pas huit.
6. **Palette 16 couleurs conservées mais sélecteur plus fin.**
7. **Supprimer le retour de l'ancien dossier beige** pendant la création inline.

Les cinq captures de l'utilisateur sont dans le fil ChatGPT de recette MG-003a ; les comparer visuellement à la vraie interface sur CODEX-VM et aux captures de `reports/MG-003a/` si elles sont accessibles. Ne pas utiliser les maquettes PNG comme couvertures.

## 1. Navigation de gauche : c'est le repère visuel du projet

**Observation :** `ui.py:refresh_tree()` injecte `self.nav_icons["project"]` pour chaque projet, ignorant `Record.visual`. `navigation.py:navigation_icons()` ne propose actuellement qu'un dossier générique vert.

**Attendu :**
- Chaque projet **et sous-projet** dans le `NavigationTree` affiche **son icône choisie** (`visual.icon`) **teintée avec la couleur choisie** (`visual.color`).
- Le résultat doit être cohérent avec la prévisualisation de l'icône de projet (icône au trait, pas un carré beige).
- Au retour de `Enregistrer`, l'arborescence se met **immédiatement** à jour ; idem après redémarrage, changement de projet, renommage, tri et déplacement.
- Icône et couleur génériques de l'Atelier pour un projet non personnalisé. `Tous les fils` et `À classer` gardent leurs pictogrammes spéciaux.
- **Ne pas casser les indentations, les chevrons natifs, l'ellipse/infobulle des titres longs ni les états de sélection/survol/dépôt.**
- Générer et **conserver des références Tk PhotoImage** pendant la vie des lignes (cache par couple icône/couleur/taille), pour éviter les icônes disparues ; proportions et lisibilité aux deux tailles de fenêtre.
- **Création inline** : la capture du 15/11 montre l'ancien pictogramme « dossier orange dans un carré beige » pendant la saisie du nom. Remplacer ce témoin temporaire par le **même pictogramme au trait** que le nouvel arbre, teinté de la couleur par défaut. Pas de régression `Entrée` pour créer / `Échap` pour annuler, ni de pseudo-projet résiduel.
- Si une ligne de la Liste centrale correspond à un projet, réutiliser éventuellement le même pictogramme **sans refondre la Liste**. La priorité reste **l'arborescence gauche**.

## 2. Bandeau : image ENTIÈRE, proportions respectées, zéro modification du shell

**Observation technique vérifiée :** `identity_ui.py:ContextMasthead.draw()` appelle actuellement `thumbnail()`, qui utilise `ImageOps.fit()` sur les couvertures 1200×675 (16:9), vers un cadre d'environ 225×51, donc **recadre massivement le haut et le bas**. C'est le défaut visible signalé par l'utilisateur.

**Attendu :**
- **AUCUNE modification de hauteur du bandeau** `Masthead`, de la hauteur de la recherche, de la position du logo, des trois colonnes ou des gouttières.
- Exploiter **l'espace déjà libre en haut et en bas** de l'illustration, à droite du bandeau. Afficher la scène entière **dans son ratio 16:9**, en calculant sa taille depuis l'espace réellement disponible et en respectant les marges et éléments voisins. **Jamais `ImageOps.fit` / `crop` pour ce bandeau** ; utiliser un rendu contenu/`contain` sans déformation, et sans agrandir grossièrement l'image.
- Il est acceptable que l'image soit **moins large et plus haute** que la bande actuelle : c'est précisément le prix d'un vrai 16:9 à hauteur constante. Ne pas forcer une image 16:9 dans un emplacement 4:1.
- Conserver discrètement la petite couleur et l'icône si leur affichage reste harmonieux et ne masque **aucune partie de l'image**.
- Le bandeau continue de changer selon le projet sélectionné, le fil et le contexte de rattachement (résolveur existant), **sans flash ni superposition** d'anciens paysages ou icônes à chaque sélection/redimensionnement.
- Quand un projet utilise l'image intégrée « Montagne », vérifier qu'on retrouve **la montagne entière** et non une bande horizontale au centre. Même test avec une image personnelle portrait (contenue, sans étirement, avec éventuelle marge) et une image 16:9.

## 3. L'illustration au soleil = VRAIE valeur par défaut

**Observation :** la prairie au soleil/arbres/livre est le visuel **neutre du bandeau**, mais `identity.DEFAULTS["image"]` pointe vers `pack:ecriture` (« Le jardin des mots »). Ce ne sont pas les mêmes images ; l'utilisateur veut précisément **notre illustration au soleil** si aucun choix d'image n'a été fait.

**Attendu :**
- Créer/proposer dans la galerie une **couverture par défaut** qui représente **la prairie/soleil/arbres/livre** (même identité visuelle que le paysage historique, mise au format 16:9 si nécessaire, sans distortion ; une illustration locale originale, dérivée/refaite dans le style historique, pas une maquette UI).
- **Nouveau projet, sous-projet et projet v1 migré sans choix explicite** → cette couverture par défaut.
- Le bouton **Par défaut** du sélecteur Image revient à elle.
- **Aucun projet ayant explicitement choisi** `pack:ecriture` (« Le jardin des mots »), une des cinq autres couvertures ou une image personnelle **ne doit perdre son choix**. Ne pas réinterpréter tous les `pack:ecriture` comme « absence de choix ».
- Règle simple : les `visual` vides héritent du nouveau défaut ; les références déjà explicites restent explicites. Assurer la lecture du catalogue schéma 2 déjà livré, et sa validation strictement conforme ; éviter une migration destructrice ou une remise à zéro.
- **Sans projet sélectionné**, la marque continue d'afficher le paysage solaire neutre. Le visuel neutre et la valeur par défaut doivent être cohérents, pas deux images sans rapport.
- **Conserver les six couvertures existantes** dans la galerie, en plus de cette nouvelle valeur « Par défaut ».

## 4. Édition du projet : une unique rangée compacte et évidente

**Observation :** `identity_ui.py:ProjectVisualFields` affiche actuellement des lignes **Image**, **Icône**, **Couleur**, chacune avec nom/vignette et bouton « Choisir ». L'utilisateur a dit explicitement : « Tout doit pouvoir tenir sur une seule et même ligne […] pas besoin de mettre les titres, un bouton icône suffit […] idem pour les couleurs. »

**Attendu :**
- Dans **la fiche projet existante**, afficher **sur une seule rangée** trois petits contrôles clicables adjacents :
  1. miniature de **l'image** actuelle ;
  2. pictogramme de **l'icône** sélectionnée, teinté avec sa couleur ;
  3. pastille de **couleur** actuelle.
- **Pas trois en-têtes ni trois boutons « Choisir »** ; le clic sur chaque élément ouvre son propre layer existant. Nom/intention via **infobulle et focus clavier**, sans gaspiller des lignes. Un micro-intitulé commun « Identité visuelle », s'il aide, reste facultatif et discret.
- Rendu vraiment **compact**, adapté à la largeur de l'inspecteur en 1000×680. Les trois éléments restent visibles, tabulables, cliquables. En aperçu lecture seule du projet, montrer également ces repères en miniature **sans ouvrir l'éditeur** ; ne pas refondre l'aperçu des fils.
- **Enregistrer/Ctrl+S**, `dirty`, `Annuler`, retour à l'aperçu et validation des autres champs restent strictement inchangés. Ne pas appliquer automatiquement une sélection non validée.

## 5. Galerie d'icônes : une variété digne de vrais projets

**Observation :** huit icônes au trait seulement, insuffisant quand l'utilisateur transférera ses vrais projets. Il souhaite **au moins trois à quatre fois plus**.

**Attendu :**
- **32 à 40 icônes au trait distinctes**, de même poids et langage graphique. Exemples de thèmes : dossier, carnet, livre, plume, stylo, bulle, conversation, lampe, ampoule, planète, étoile, boussole, carte, globe, montagne, arbre, feuille, fleur, soleil, lune, loupe, code, terminal, circuit, base de données, outils, roue dentée, laboratoire, microscope, musique, caméra, palette, pinceau, calendrier, horloge, maison, cœur, cible, graduation, etc.
- **Ne pas changer les identifiants des huit icônes existantes** : anciens projets restent valides.
- Dessins reconnaissables à 16–24 px **sur l'arborescence** ; éviter les figures quasi-identiques ou des emojis de polices hétérogènes.
- Galerie en grille réactive/défilante ; choix et focus clairs, retour par défaut opérationnel ; pas d'accès réseau ni de catalogue immense.
- Des illustrations vectorielles tracées par code ou de petits actifs locaux cohérents sont acceptables, mais **ne pas rendre nécessaire une police externe**.

## 6. Sélecteur de couleurs : même palette, beaucoup moins de « cartes »

L'utilisateur **approuve les 16 couleurs** de `identity.PALETTE`, mais trouve leur sélecteur « assez vilain ».

**Attendu :**
- **Conserver strictement les 16 teintes et leurs identifiants** ; les présenter en **4×4 pastilles rondes élégantes**, sans le grand rectangle légendé sous chaque couleur.
- Nom de la nuance en infobulle et indication accessible au clavier. Sélection avec contour/cochage fin ; contrastes et focus visibles.
- Garder `Par défaut`, `Annuler`, `Utiliser`, `Échap` et le modèle de validation déjà livré ; pas de roue RGB et pas de nouvelle fenêtre extérieure.
- Retirer l'espace inutile et l'excès de grands libellés ; conserver l'identité « Atelier chaleureux ».

## 7. Limites fermes, non-régression

**Ne pas toucher** à : sauvegarde ZIP, import et validation des images, migration v1→v2, schéma 2 sauf l'ajout compatible du nouveau nom de couverture par défaut, données et URLs ChatGPT, moteur des rattachements, recherche, tags/catégories, menu principal validé, tailles de fenêtre, structure trois colonnes, proportions de la Liste centrale, comportement du DnD, sélecteurs d'images personnalisées. **Pas de vues Détaillée/Mosaïque, pas d'extension Chrome, pas de galerie de thèmes globale.**

**Aucune recommandation de sauvegarder les données fictives de recette** : tous les catalogues utilisés sont des jeux de développement de l'utilisateur. Pour la recette Codex, rester dans ses dossiers fictifs habituels sans toucher à d'autres environnements.

Conserver tous les **80 tests existants** (adapter les attentes strictement liées au nouveau défaut et au nombre d'icônes) ; ajouter des tests sur :
- identifiants d'icônes existants, nouvelle palette de pictogrammes, couleurs spécifiques dans le `Treeview`, cache PhotoImage et création inline sans ancien dossier beige ;
- affichage entier au ratio **16:9** sans recadrage, avec resize, changement de sélection, portrait et paysage, et image solaire cohérente sans choix personnalisé ;
- contrôle compact une rangée, trois activations indépendantes, layer annulé/accepté et refus de modifier les autres champs ;
- migration/réouverture de catalogues v1/v2, six anciennes couvertures et anciens choix visuels conservés ;
- maintien des protections d'édition et sauvegarde complète avec images personnelles.

## 8. Recette native et livraison

Tester dans **la vraie application Tk** sur CODEX-VM, avec les données fictives, aux tailles **1360×820, 1000×680 et fenêtre agrandie** :

1. Créer projet/sous-projet → **soleil** par défaut ; observer pendant la saisie du nom : **pas d'ancien dossier beige**.
2. Ouvrir fiche projet → **trois petites commandes côte à côte**. Choisir p. ex. icône microscope, couleur pétrole et image montagne. Enregistrer → à gauche, **microscope pétrole** ; dans le bandeau, **montagne entière sans recadrage** ; dans l'aperçu, repères visibles.
3. Passer d'un projet à l'autre, fermer/ouvrir l'inspecteur, sélectionner le fil partagé, changer de tri et de contexte, redimensionner : aucun décalage/ancien artefact ; les liens et rattachements ne changent pas.
4. Parcourir **au moins 32 icônes distinctes** et les 16 couleurs en pastilles rondes ; souris + tabulation/flèches/Entrée/Échap.
5. Sauver, quitter, rouvrir ; revenir à `Par défaut` ; restaurer l'ancien choix `pack:ecriture` explicitement conservé ; sauvegarde ZIP de référence et lecture avec images personnelles.
6. Faire **3 à 5 captures natives** utiles (arborescence à plusieurs icônes/couleurs, éditeur compact, bandeau avec image 16:9, palette ronde, galerie d'icônes).

Publier `reports/MG-003b/rapport.md` avec tableau avant/après **fondé sur le retour utilisateur** (ne pas déclarer « validé » avant notre recette), tests, captures et limites honnêtes. Pas de duplication des grosses maquettes PNG ; pas de téléchargement de photos externes pour cette correction. Commit/push sur `origin/main`, vérifier le SHA distant et laisser dépôt propre.

**Critère GO :** nous voyons les couleurs/icônes réellement utilisées **dans la navigation**, la personnalisation compacte **dans la fiche**, une **couverture solaire par défaut**, et **toute la scène de couverture dans le bandeau sans modification du gabarit**. Si une de ces choses manque : **PARTIEL**, pas de nouvelle vue engagée.
