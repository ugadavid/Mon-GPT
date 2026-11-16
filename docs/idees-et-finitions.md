# Mon GPT<3 — Suivi des finitions et idées après MG-009

**Document de suivi / parking d'idées, pas une mission exécutable dans son ensemble.**  
**Contexte :** première utilisation approfondie de Mon GPT<3 0.9.0 sur CODEX-VM, avec une bibliothèque locale d'environ **1 429 conversations** et les vrais projets importés depuis Chrome, le 16 novembre 2026.

**Cap décidé : un seul projet informatique actif, finir l'existant, avancer tranquillement.** Chaque lot doit être validé séparément avant de commencer le suivant. Ne pas développer le tableau de bord ou de nouveaux modules pendant les corrections de cette version.


## Situation au soir du 16 novembre 2026 — après recette MG-011

**Validés par David sur la bibliothèque réelle :** MG-010a (0.9.1), MG-010b et MG-010b-01 (0.9.2a), MG-010c (0.9.3).  
**MG-011 (0.9.4), sept finitions fonctionnelles :** ensemble jugé « globalement vraiment très bien » sur capture réelle ; une réserve de **placement dans le bandeau** est expressément reportée à la passe graphique de demain. Les tests Codex sont verts (199 Python, 43 JavaScript).

### PRIORITÉ DEMAIN — 17 novembre 2026 : placement des informations du bandeau

**Demande explicite de David, ne pas oublier :** dans le bandeau supérieur, les **catégories, tags et courte description du projet** apparaissent actuellement **près du logo « Mon GPT<3 »**, alors que la **couverture est à l'extrême droite**. C'est une séparation visuelle illogique. **Regrouper toutes ces informations immédiatement à GAUCHE de l'image de couverture, sur le CÔTÉ DROIT du bandeau**, en laissant le logo, le titre et le slogan seuls sur le côté gauche. Maintenir le lien fonctionnel avec le projet courant, pas avec le fil sélectionné ; conserver l'absence de fausses pastilles, le repli sur petit écran, les largeurs et l'inspecteur ouvert/fermé. **Simple correction de placement graphique, sans nouveau comportement métier.**

### Autres décisions graphiques à discuter demain, sans implémentation automatique

- **Images héritées répétées :** un dossier dont les 10 fils héritent de la même couverture donne une Mosaïque monotone ; étudier une hiérarchie visuelle plus utile, **sans inventer de couvertures ni altérer l'héritage des données**.
- **Cartes Détaillée/Mosaïque enrichies en 0.9.4 :** examiner proportions image/texte, densité, typographie, espaces, hauteur lorsque les notes, résumé, tags et catégories sont présents ; la fonctionnalité est déjà livrée.
- **Aide / À propos** : ce sont maintenant de véritables fenêtres fonctionnelles (MG-011), donc ne pas refaire leurs interactions ; éventuellement harmoniser visuellement leur style.
- **Arbre de projets, bandeau, éditeur :** polissage de lisibilité, contraste, hiérarchie et alignement seulement après discussion. Les entrées « Tous les fils » / « À classer » sont maintenant épinglées, les emplacements sont remontés en haut de l'éditeur et le titre du centre est devenu « Contenu du projet ».
- **Ne pas relancer** les modifications déjà terminées (colonnes, clic sur titre, glisser multiple, aide structurée, notes visibles, épinglage, tailles de fenêtres retirées).

**Après le travail graphique validé** : envisager une version Windows portable et un installateur. **Tableau de bord/statistiques** à garder au parking jusqu'à la finition/distribution, sans lancer un nouveau chantier ce soir.

**Les sections historiques ci-dessous conservent les observations originales de 0.9.0 et ne sont pas des missions encore à réaliser.**

## Historique validé : MG-010a — Navigation directe, colonnes existantes et galerie

Mission : `missions/MG-010a_corrections_recette_fonctionnelle.md`.

Observations :
- Lorsqu'un projet est choisi, la partie centrale montre actuellement les fils de tous ses descendants ; l'utilisateur **ne veut que les fils directement affectés** à ce projet. Les sous-projets continuent d'exister dans l'arbre.
- La liste affiche « Titre local », « Projet / emplacements » : préférer **« Titre »**, **« Projet »** ; largeur des colonnes impossible à ajuster aisément malgré un mécanisme incomplet.
- Dans le sélecteur d'images, les deux colonnes de vignettes semblent toujours de la même hauteur lorsque le volet est élargi ; les images doivent s'adapter en maintenant un format cohérent. Un **double-clic** sur une vignette doit équivaloir à « Utiliser », sans sauter l'enregistrement final de la fiche.

## Historique validé : MG-010b / MG-010b-01 — Sélection multiple et gestes naturels

Problème constaté : partie centrale **mono-sélection** dans les vues Liste / Détaillée / Mosaïque. Ce sont des rendus Canvas personnalisés, pas de simples `ttk.Treeview` à passer en `selectmode="extended"`.

À concevoir en **mission distincte** : sélection non contiguë Ctrl+clic, plage Shift+clic, Ctrl+A cohérent avec le périmètre filtré/visuel ; navigation clavier, mise en évidence et compteur. Puis **actions groupées vérifiables** : déplacer vers un projet, **ajouter un rattachement** (copie logique du lien, **pas dupliquer la fiche**), enlever un rattachement ; confirmation/annulation adaptées et zéro perte des autres emplacements, notes, tags, catégories. Les détails actifs n'affichent pas un seul élément trompeur lorsque plusieurs fiches sont sélectionnées. Ne pas introduire de gestes à moitié fonctionnels. Garder F2/ouverture/édition d'une seule fiche intelligibles.

**Ce point est volontairement hors MG-010a** pour ne pas fragiliser les gestes déjà validés.

## Historique validé : MG-010c — Colonnes configurables

Une petite **administration des colonnes de la vue Liste** :
- Colonnes par défaut : **Titre**, **Projet**, **Catégories**, **Tags**, avec action d'ouverture.
- Proposer des champs **Création** et **Modification** (dates propres aux fiches Mon GPT, ne pas les confondre avec l'ancienneté du fil dans ChatGPT).
- Choisir les colonnes visibles, leur ordre, largeur, tri et éventuellement rétablir les valeurs par défaut ; conserver la configuration dans `interface.json` ou les préférences UI, **pas dans le catalogue métier**.
- Adapter le comportement aux fenêtres étroites, maintenir l'ouverture directe et les titres accessibles. Ne pas encombrer la vue globale d'une administration permanente.
- Plus tard seulement, étudier s'il est pertinent d'afficher d'autres métadonnées typées.

Le remplacement des deux libellés et l'ajustement fiable de la largeur des **colonnes actuelles** relèvent de MG-010a ; **ce configurateur complet** sera une mission ultérieure.

## Compléments de présentation constatés sur les captures — à arbitrer après les correctifs

- Une **note de fiche** apparaît dans le panneau d'édition/aperçu, mais **pas en vue Détaillée ou Mosaïque**. Étudier un extrait facultatif (non tout le contenu), avec maîtrise de la hauteur, masquage des champs vides et respect de la place nécessaire aux images.
- Les cartes Mosaïque présentent aujourd'hui essentiellement la **couverture et le titre** ; selon les vrais usages, voir si un court résumé, les catégories et tags apportent suffisamment de valeur. Ne pas rendre toutes les cartes illisibles.
- L'icône / couleur / couverture ont été testées avec de **vraies fiches** : « BHE / Réflexion », « Écriture », « Mon GPT ». Les écrans se personnalisent, mais le visuel répété par héritage peut paraître uniforme. Examiner des variantes graphiques après stabilisation.
- **À propos** et **Gestes et raccourcis** s'affichent pour l'instant comme des boîtes de message Windows natives assez rudimentaires. Une passe d'ergonomie pourrait les harmoniser, sans refaire le code métier.
- Arbre de gauche potentiellement très dense après import massif ; travailler sa lisibilité et les repères sans rompre le tri manuel/alphabétique et la structure des sous-projets.
- Les nombreuses captures réelles de recette sont des **références de discussion**, pas à publier telles quelles dans le dépôt public ni à copier dans les assets de l'application.

## Après avoir FINI cette version : tableau de bord / statistiques (idée mise au parking)

**Idée appréciée par David, explicitement à conserver pour plus tard. Pas d'implémentation avant la finition et la distribution de la version actuelle.**

Futur tableau de bord : nombre total de projets, sous-projets et conversations ; volumes par projet/catégorie/tag ; fiches « À classer », sans catégorie ou sans note ; progression de classement ; éventuellement visualisation de la distribution. Les statistiques doivent provenir du **catalogue local** sans requête vers le compte ChatGPT, distinguer les fiches multi-rattachées afin de ne pas fausser les totaux et rester optionnelles et lisibles. D'abord une étude/maquette et des besoins, pas une usine à gaz.

## Distribution, tout à la fin

Une fois l'ergonomie et la fiabilité de la version validées : paquet Windows **portable** et **installateur** (comme Ma Médiathèque), données locales préservées à l'installation/désinstallation, mise à jour et version visibles. Ne pas créer l'installateur durant les corrections de recette.

---

**Règle pour les prochaines missions :** un changement à la fois, recette sur CODEX-VM, tests automatisés, rapport court, captures fictives publiables. Pas de nouveaux projets en parallèle et **aucun développement automatique à partir de ce seul parking d'idées**.
