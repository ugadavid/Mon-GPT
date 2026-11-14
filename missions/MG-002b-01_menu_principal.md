# MG-002b-01 — Menu Windows « plus plus » : discret, élégant, fidèle à la maquette

**Statut : à réaliser.** Première micro-mission de correction visuelle après Mon GPT<3 **0.2.1** (base `57e86bd8b29193f32bff09f141e60fc2ad08241c`).

## Rectification explicite de David — PRIORITAIRE

> « L'idée c'est Windows mais plus plus quand même. Voici ce que tu avais toi-même produit. L'idée c'est de se rapprocher de ça. »

**Référence graphique de premier rang :** `missions/MG-002-maquettes/Image ChatGPT 14 nov. 2026, 11_51_22-1.png`, également transmise dans le chat du 14 novembre (l'explorateur rapide, menu `Fichier` déroulé).

**La mission précédente était trop stricte en réclamant un retour au menu Windows natif gris. Elle est corrigée : nous voulons le comportement familier d'un menu Windows, avec une belle réalisation graphique inspirée de la maquette.**

Ne **pas** interpréter « Windows mais plus plus » comme « menu natif obligatoire sans style », ni comme « quatre gros boutons à la place d'une barre de menu ». Le choix technique (Tk Menu natif ou dessin sur mesure) est libre si le rendu **ET** les gestes correspondent à la référence.

## Objectif unique

Une **barre haute discrète**, à la Windows, avec `Fichier`, `Édition`, `Affichage`, `Aide` en petits libellés, espacés justement et intégrés à notre ivoire. Aucun aspect toolbar de boutons en relief, capsules larges ou étiquette décorative occupant la ligne.

Quand `Fichier` s'ouvre, obtenir un **panneau de menu élégant** comme dans la maquette :

- surface ivoire/papier, bord subtil, coins légèrement arrondis si faisable proprement, petite ombre discrète ;
- **petites icônes différentes selon la commande**, alignées à gauche sans carré encadré grossier ;
- libellés à gauche, raccourcis alignés à droite, séparateurs fins ;
- ligne survolée légèrement colorée, contraste et état désactivé lisibles ;
- hauteur contenue, proportions cohérentes et finition de vrai logiciel Windows — **pas un menu brut gris, pas une carte géante**.

L'accent doit rester mis sur la **composition graphique exacte** du menu visible en haut à gauche de la maquette. Ni toute l'interface, ni les boutons de la liste, ni la recherche ne font partie de ce lot.

## Étapes précises

1. Lire ce texte, le rapport MG-002a, et consulter **localement** les trois images dans `missions/MG-002-maquettes/`, en privilégiant la **première** pour le menu. **Ne pas télécharger, dupliquer, remplacer ni republier les PNG.**
2. Inspecter `build_menus()` et `MenuSkin` actuels : corriger leur disposition, rendu et interactions ; **réutiliser ce qui fonctionne** plutôt que reconstruire la navigation.
3. Tester l'accès souris et clavier, survol et clic, fermeture par `Échap` ou clic extérieur, changement de rubrique, focus après fermeture ; pas de menu qui recouvre le mauvais endroit ou reste bloqué. Si une réalisation custom gêne ces attentes, utiliser une alternative plus native **sans sacrifier inutilement la finition**.
4. Préserver les quatre rubriques et **toutes les commandes**, leurs libellés réels, raccourcis et protections : `Ctrl+S` garde **Enregistrer la fiche** ; `Fichier > Sauvegarder le catalogue…` garde l'export global. Le menu `+` et les menus contextuels ne changent pas.
5. Comparer la vraie fenêtre obtenue à la première maquette : proportions de la ligne, largeur des rubriques, style du menu ouvert, icônes, séparateurs, ombre, contrastes. **Mentionner explicitement dans le rapport ce qui correspond et ce qui reste différent.**

## Frontières impératives

**Une seule modification visible : la barre de menus principale et ses menus déroulants.** Ne toucher ni à la recherche, ni au bandeau illustré hors jonction technique avec le menu, ni à la Liste, ni aux icônes de fiches, ni à l'inspecteur, tags, catégories, création, DnD et doublons.

Aucun changement de `core.py`, `chatgpt.py`, `storage.py`, du schéma JSON ou des maquettes. Aucune opération sur un catalogue réel : recette avec données entièrement fictives. Pas de gros framework ni de bibliothèque installée sans nécessité.

## Validation et livraison

- Exécuter l'application sur CODEX-VM en fenêtre confortable et compacte, **ouvrir physiquement le menu Fichier** et parcourir les quatre rubriques ; tester souris/clavier et fermeture.
- Conserver les **42 tests** MG-002a et ajouter uniquement des tests ciblés nécessaires.
- Publier **deux captures de l'application réelle** : menu `Fichier` ouvert et barre haute complète ; **pas de nouvelle maquette générée**.
- Rapport court `reports/MG-002b-01/rapport.md` avec **comparaison point par point à l'image de référence**, limites, tests ; version/README ajustés seulement si utile.
- Commit, push `origin/main`, SHA distant vérifié et arbre Git propre. L'utilisateur décidera si ce petit lot est validé **avant** de commencer le suivant.

**Critère de succès :** au premier regard, « c'est bien le joli menu de notre maquette, avec la familiarité d'un menu Windows », et non « on a simplement remis un menu gris d'origine ».

**Règle de discipline : une micro-mission, une zone, aucun élargissement.**
