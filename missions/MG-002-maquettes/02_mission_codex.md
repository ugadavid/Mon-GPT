# MG-002 — Refonte UX : socle commun et vue Liste

**Statut :** mission à réaliser.  
**Dépôt :** `ugadavid/Mon-GPT` · branche `main` · application actuelle **0.1.0** (MG-001 livrée).  
**Objectif :** transformer les **gestes** de l'application et sa lisibilité, **pas seulement la décorer**.  
**Référence de conception obligatoire :** [01_specification_UX.md](01_specification_UX.md) et les **trois PNG déjà présents dans ce même dossier**.  
**Périmètre immédiat :** **charte « Atelier chaleureux » + coque commune + vue Liste réellement utilisable**. Les vues Détaillée et Mosaïque et l'import des couvertures appartiennent à des lots **ultérieurs**, sauf petit travail d'architecture indispensable à ne pas refaire l'interface.

## A. Préparation et protections

1. Vérifier le chemin réel du dépôt local, `git status`, `origin` et `main`. Lire `AGENTS.md`, `README.md`, `docs/architecture.md`, la mission MG-001 et le rapport de recette `reports/MG-001/rapport.md`. Lire intégralement la spécification UX ci-dessus.
2. Consulter les **trois maquettes localement** ; leurs noms exacts figurent dans la spécification. Ce sont des **références**, pas des actifs à incorporer tels quels. **Ne pas les modifier, renommer, recopier ni republier en blobs.** Aucun aller-retour de binaires par ce chat.
3. Garder la séparation `core.py` (organisation générique), `chatgpt.py` (URL/identité externe), `storage.py` (persistance) et `ui.py` (interaction). Tkinter/ttk reste la base ; ne pas introduire d'autre framework, dépendance lourde ou moteur graphique sans nécessité et justification.
4. **Ne pas changer le schéma métier 1 pour MG-002**. Le validateur actuel rejette strictement les champs inconnus. Les couvertures personnalisées et leur persistance nécessitent une mission séparée avec migration/versioning et tests des anciennes archives. Dans la présente mission, des **icônes et ressources visuelles par défaut** peuvent être purement applicatives, sans ajouter de champs à `Record`.
5. Toutes les modifications se font avec des **données fictives** dans un `--data-dir` de recette explicitement isolé. N'ouvrir ni écraser le vrai catalogue `%LOCALAPPDATA%\MonGPT\catalogue.json` ; aucune URL réelle de conversation, capture privée ni données personnelles dans Git.
6. Préserver les fonctions MG-001 et ses protections : URL validées, ouverture explicite navigateur, déduplication, champs de fiche, filtres descendant projet, mode manuel/alphabetique, multi-rattachement, sauvegarde/restauration sûre, verrou exclusif, annulation/confirmation des modifications, lancement `lancer.cmd`.

## B. La première expérience à livrer : accès rapide, pas formulaires

**Le scénario décisif :** je sélectionne un projet à gauche, je repère une discussion dans la **Liste**, **un seul clic sur son titre ou son icône ouvrir** me mène à son chat. Pas besoin de lire une énorme fiche sur la droite.

### B1. Coque et hiérarchie

- Appliquer les tokens de la charte de `01_specification_UX.md` ; centraliser les styles, contrastes, focus et états de survol.
- Barre de menus **Fichier / Édition / Affichage / Aide** : mettre **Sauvegarder le catalogue…** et **Restaurer le catalogue…** sous `Fichier` ; enlever leurs gros boutons permanents. Conserver le chemin des données accessible.
- **Barre de recherche universelle unique**, sans trois champs distincts ; prise en charge des recherches globales + filtres tag/catégorie/projet via suggestions/pastilles/commandes discrètes. Préserver les comportements et protections de `Catalog.search` sans la dupliquer dans l'interface.
- Navigation gauche par arborescence (Tous les fils, À classer, projets et sous-projets), tri manuel/alphabétique et commandes contextuelles ; abandonner les gros boutons fixes Monter/Descendre si l'opération reste accessible par menu/raccourci.
- **Liste au centre prioritaire en largeur** : lignes compactes, **icônes uniquement** (pas de grandes couvertures), colonnes lisibles/triables quand pertinent, distinction projet/fil, titre visible et action d'ouverture au premier plan.
- **Inspecteur secondaire** masquable/repliable, minimal par défaut. Édition détaillée uniquement sur demande ; toute donnée/édition MG-001 reste atteignable.
- Taille de fenêtre et colonnes ajustables ; prendre soin des titres longs et du zoom Windows ; ne pas multiplier les barres de défilement imbriquées.

### B2. Création sans popup et raccourcis

- Un menu `+`, un clic droit dans l'arborescence et des raccourcis donnent accès à **Nouveau projet** / **Nouveau fil**.
- **Nouveau projet :** insertion d'une ligne éditable dans l'arbre, au niveau approprié, avec validation/annulation inline ; le projet créé est visuellement identifiable par son icône par défaut. Pas d'obligation de choisir une image.
- **Nouveau fil :** zone de saisie **intégrée à la liste** (titre et URL avec validation MG-001) ; doublon traité de façon sûre en préservant la fiche existante. Pas de fenêtre modale ordinaire pour créer.
- Les confirmations de suppression/restauration et d'abandon de modifications peuvent rester des dialogues de sécurité.
- Conserver `Ctrl+S` = **Enregistrer les modifications de la fiche**, jamais sauvegarde globale. Ajouter des raccourcis non conflictuels suggérés dans la spécification (Ctrl+K, Ctrl+N, Ctrl+Maj+P, F2, Entrée, Échap), uniquement si testés dans les contextes de focus corrects.

### B3. Ouverture et menus contextuels

- Cliquer **titre / icône de fil** ouvre ChatGPT **en un clic** ; cliquer le reste de sa ligne sélectionne sans ouvrir ; double-clic/Entrée sur un fil actif ouvrent. Ne jamais ouvrir le chat en sélectionnant un projet.
- Menu contextuel différencié projet/fil : ouvrir, créer ici, renommer, modifier, déplacer, ajouter/retirer un rattachement, supprimer avec confirmation selon ce qui est applicable.
- **Tags et catégories** : présenter les valeurs déjà présentes dans le catalogue, sélectionnables et filtrables, avec ajout de nouvelles valeurs ; ne pas imposer la saisie de listes séparées par virgules comme unique parcours.
- L'absence de tag ou de catégorie doit produire un état vide utile.

### B4. Glisser-déposer

- Avec le **bouton gauche** : un projet change de parent ; un fil est déplacé vers une autre destination de manière explicite. Afficher cible et interdictions avant la dépose ; interdire les cycles.
- Avec le **bouton droit**, à la dépose d'un **fil**, menu `Déplacer ici` / `Ajouter un rattachement ici` / `Annuler`. **« Copier » signifie second rattachement, jamais seconde discussion.**
- Les autres rattachements existants d'un fil ne doivent **jamais disparaître silencieusement**. Si l'utilisateur est dans `Tous les fils`, le départ d'un déplacement est ambigu : demander ou choisir explicitement quel rattachement modifier plutôt que supprimer au hasard.
- Les projets demeurent un arbre à parent unique ; ne pas ajouter de copie/multi-parent de projet.
- Une action équivalente doit rester possible depuis le menu contextuel si l'utilisateur ne pratique pas le DnD.
- Si un geste natif de drag droit est impossible à rendre fiable dans Tkinter, le **documenter comme PARTIEL** ; ne pas inventer un fonctionnement non testé.

## C. Hors du lot MG-002, mais à anticiper dans la mise en page

Ces décisions sont **validées dans la spécification** mais **à ne pas développer maintenant**, sauf contrat d'interface minimal sans bouton trompeur :

- **Vue Détaillée** = petite vignette + icône, résumé et tags.
- **Vue Mosaïque** = grandes couvertures illustrées + icônes, éventuellement tailles de cartes.
- Galerie de couvertures de projets (couverture obligatoire **attribuée par défaut**, donc aucun choix forcé à la création), import personnel JPG/PNG/WebP avec limites affichées, personnalisation de couleurs/icônes, fil héritant du projet, rattachement visuel principal, stockage des images, migration JSON et sauvegarde des actifs.
- Refonte de moteur métier, extension Chrome, lecture des messages ChatGPT, collecte/synchronisation réseau, installateur autonome.

**Ne pas placer des boutons Liste/Détaillée/Mosaïque actifs si deux vues n'existent pas.** La première livraison peut n'afficher que la vue Liste et documenter le futur sélecteur. Éviter les faux boutons décoratifs.

## D. Recette réelle de l'interface, pas de validation cosmétique

### Scénario utilisateur synthétique de référence

Créer ou générer un catalogue **fictif** qui contient :
- Un projet racine `Atelier des idées`, sous-projet `Écriture`, et un autre `Laboratoire`.
- Plusieurs fils fictifs, dont `Préparer une exploration imaginaire` et `Travaux`, avec liens ChatGPT **fictifs valides de forme** (UUID inventés, aucune conversation réelle).
- Un même fil rattaché à **deux projets**, tags/catégories existants, notes, titre long, un fil non classé, un projet sans enfant.

Vérifier sous **CODEX-VM avec l'application graphique réellement exécutée** :

1. Recherche unique : retrouver un fil par titre, tag ou catégorie, puis activer/enlever les filtres ; ne pas afficher deux fois un fil multi-rattaché.
2. Sélectionner un projet, puis **ouvrir un fil d'un clic sur son titre**. Pour ne pas ouvrir un vrai navigateur sur une URL fictive, tester l'action via un adaptateur/mocking d'ouverture et conserver la vérification de validation HTTPS. Toute ouverture réelle doit rester sur geste utilisateur explicite.
3. Créer projet/fil **dans la fenêtre**, `Entrée` valider, `Échap` annuler, URL malformée refusée, doublon géré ; pas de fenêtre « Ajouter... » séparée.
4. Glisser un projet, essayer un cycle interdit ; glisser un fil à gauche, puis utiliser clic droit ou menu de destination pour **ajouter un second rattachement** ; vérifier qu'il s'agit de la **même fiche** et que les notes ne changent pas.
5. Tags/catégories : sélectionner une valeur existante, ajouter une valeur nouvelle, sauvegarder, rechercher ; aucun écrasement involontaire.
6. Basculer tri manuel/alphabétique puis revenir ; l'ordre manuel reste intact. Fermer/relaunch et vérifier catalogage / sauvegarde/restauration MG-001.
7. Replier l'inspecteur et confirmer que l'ouverture reste possible ; redimensionner à 1000×680 et grande fenêtre ; tester clavier/focus, titres longs, caractères français.
8. Afficher un état vide cohérent. Vérifier non-régression : supprimer un projet ne supprime pas ses fils, supprimer un fil ne supprime rien sur ChatGPT.

**Tests automatisés** : suite MG-001 conservée, nouveaux tests des gestes et adaptations d'interface, tests de persistance sans changer `schema: 1`. Un clic droit, une dépose ou une édition inachevée ne doit jamais produire de mutation non demandée. Ne pas valider uniquement à partir de captures générées ou de widgets simulés.

### Preuves livrables

- Captures **de l'application exécutée**, avec données entièrement fictives : (1) liste principale, (2) menu contextuel, (3) création inline, (4) recherche avec suggestions/tag, (5) glisser-déposer / emplacement cible, (6) inspecteur replié si possible.
- Résultat des tests + limitations exactes, en particulier glisser droit, gestion du focus et persistance UI.
- Les 3 maquettes fournies sont des références graphiques ; les captures ci-dessus prouvent **le résultat réel de la VM**, pas une image générée.

## E. Livrables et publication

1. Application réellement utilisable avec **socle commun et vue Liste** ; mêmes données métier, même commande `& 'C:\Users\codex\Documents\Projets\mon-gpt\lancer.cmd'`.
2. Tokens de thème et composants Tk réutilisables, sans refonte de `core.py`/stockage au-delà d'éventuelles réparations indispensables explicitement justifiées.
3. `reports/MG-002/rapport.md` avec tableaux **GO / PARTIEL / NO-GO** par geste (recherche, ouverture, création inline, menus, tags/catégories, déplacement/rattachement, clavier, visuel) et captures fictives publiables.
4. `README.md` actualisé : gestes, menus, raccourcis, compatibilité et limites ; mention explicite que les vues Détaillée/Mosaïque et la galerie/les imports sont **prévus, non livrés dans MG-002**.
5. Toute idée de mission ultérieure peut figurer dans le rapport sous **« Propositions non engagées »**. **Ne pas lancer MG-003 ni coder ses fonctions avant notre validation.**
6. Vérifier `git status` au départ et à la fin ; commit + push `origin/main` sans force, avec SHA distant vérifié. Ne pas modifier les PNG de ce dossier. Ne pas publier les fichiers utilisateur.

## F. Définition de terminé

**GO MG-002** si la vue Liste est accueillante et opérationnelle, le fil s'ouvre sans inspection obligatoire, les créations passent par l'interface existante, les tags/catégories déjà connus sont réutilisables, les gestes de classement conservent les rattachements, les actions rares sont rangées dans les menus et tous les tests/recettes essentiels sont vérifiés.

**PARTIEL** si l'un de ces gestes reste indisponible ou non prouvé ; exposer honnêtement ce qui manque plutôt que livrer une jolie coquille trompeuse.

**Règle de bon sens : pas d'usine à gaz.** On améliore ce que l'utilisateur **voit et fait**. Le cœur déjà livré fonctionne : il ne faut ni le réécrire ni construire un framework abstrait à côté.
