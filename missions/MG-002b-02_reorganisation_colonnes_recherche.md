# MG-002b-02 — Trois colonnes dès le haut, recherche compacte

**Statut : à réaliser — micro-mission graphique ciblée.**  
**Base :** `origin/main` après MG-002b-01, commit `940fb196164d7ea5b4aac6a8786d397e3e0bf4f7`.  
**Décision utilisateur :** le menu « Windows plus plus » de MG-002b-01 est **VALIDÉ, À FIGER**. Ne plus le retoucher.

## 1. Le besoin exact

L'utilisateur ne demande **pas** seulement de diminuer la hauteur du champ de recherche. Il propose de **réorganiser la partie supérieure de toute la fenêtre** :

> « Il va libérer de l'espace qu'il nous faut réhabiter. Je pense que la barre latérale gauche pourrait justement profiter de cet espace, remonter jusqu'en haut. Idem pour l'aperçu quand il est visible. »

Nous avons validé ensemble la disposition suivante :

```text
┌─────────────────────────────────────────────────────────────────┐
│ Fichier   Édition   Affichage   Aide    ← MENU EXISTANT FIGÉ    │
├────────────────┬──────────────────────────────┬─────────────────┤
│ VOTRE ESPACE   │ Mon GPT<3 + identité          │ APERÇU          │
│                │ graphique compacte           │                 │
│ Arborescence   │ Rechercher…  [Filtres]        │ Fiche choisie   │
│ depuis le HAUT ├──────────────────────────────┤ depuis le HAUT  │
│                │ Votre bibliothèque           │                 │
│                │ Liste et actions             │                 │
│                │                              │                 │
└────────────────┴──────────────────────────────┴─────────────────┘
```

**Lorsque l'aperçu est masqué, la zone centrale récupère immédiatement toute sa largeur.**

**Règle structurante :** les trois colonnes commencent **immédiatement sous le menu principal validé**, sans bandeau ni recherche pleine largeur insérés au-dessus des colonnes.

## 2. Objectif visuel unique

- **Colonne gauche** : l'arborescence/« Votre espace » remonte jusqu'en haut, dès la fin du menu. Elle profite de la hauteur ainsi récupérée. Son en-tête et son organisation restent accueillants, sans ajouter une décoration qui mange l'espace utile.
- **Colonne centrale** : seule elle porte l'identité **Mon GPT<3**, une **petite composition graphique** inspirée de l'Atelier chaleureux (plume / carnet / paysage si réemployable), puis **une recherche compacte** et le bloc « Votre bibliothèque » / Liste. La décoration sert d'identité, mais reste contenue en hauteur. Elle **ne traverse pas la colonne de gauche ni l'aperçu**.
- **Colonne droite** : lorsque l'inspecteur/aperçu est ouvert, **il remonte lui aussi tout en haut**, juste sous le menu, et son contenu défile dans sa propre zone. Lorsqu'il est fermé, il disparaît proprement et la colonne centrale s'élargit, sans bande verticale vide.
- **Champ de recherche** : un seul champ (déjà fonctionnel) **de largeur raisonnable, non étiré à l'infini** ; compact en hauteur, avec filtre et effacement immédiatement accessibles. La recherche et ses suggestions restent cohérentes dans la zone centrale. Les pastilles actives occupent une petite ligne seulement si nécessaire.
- **Bandeau graphique** : réutiliser/recomposer l'illustration existante, **pas l'effacer ni créer un nouveau bandeau global**. Harmoniser l'échelle et préserver la signature de la marque sans voler l'espace destiné aux résultats.

**La différence essentielle par rapport à 0.2.1 est une nouvelle GÉOMÉTRIE D'ÉCRAN, pas un changement de palette ou de composants.**

## 3. Consignes techniques ciblées

1. Lire `missions/MG-002b-01_menu_principal.md` et `reports/MG-002b-01/rapport.md` ; consulter **localement** les trois PNG dans `missions/MG-002-maquettes/`, sans les modifier ni les republier. Lire la spécification `missions/MG-002-maquettes/01_specification_UX.md`.
2. Examiner `mon_gpt/ui.py` : `build_shell()` place actuellement `Masthead(self.root)`, puis `search_area` sur `self.root`, puis `self.panes`. **Déplacer leur composition dans la colonne centrale** et faire commencer les colonnes juste après les menus. Adapter les parents et les modes `pack/grid/Panedwindow` proprement, sans casser les références aux widgets, callbacks et restaurations d'état.
3. Préserver strictement **`main_menu.py`, le composant des menus validés et les comportements du menu principal** : souris, clavier, survol, Échap, clic extérieur, raccourcis, focus et positionnement. Aucun remaniement esthétique ou fonctionnel du menu.
4. Préserver le redimensionnement des panneaux et le placement initial/restauré des séparateurs ; en particulier, la largeur centrale ne doit pas se retrouver écrasée après le réaffichage de l'aperçu ou le redimensionnement de la fenêtre.
5. Faire en sorte que `Ctrl+K` donne toujours le focus à la recherche, que ses suggestions et pastilles restent utilisables **sans sortir de l'espace central**, et que les menus déroulants ne soient ni coupés ni superposés à des zones de manière incohérente.
6. Ne pas ajouter une nouvelle surface de fond vide pour « compenser » la hauteur gagnée ; le gain doit se voir dans l'arbre, la Liste et l'inspecteur.

## 4. Ne PAS toucher

**La mission concerne uniquement l'implantation de l'interface, la recherche dans cette implantation et l'adaptation du bandeau illustré.**

- Ni retouche du **menu principal validé**, ni changement des menus contextuels.
- Ni changement des comportements de recherche, filtrage, catégories, tags, ouverture des fils, création, glisser-déposer, menu clic droit, inspecteur, sauvegarde/restauration.
- Ni modification du **moteur MG-001**, des règles de doublons, du schéma JSON, de la structure des données ou des trois PNG de référence.
- Ni développement des vues Détaillée/Mosaïque, ni ajout de couvertures persistantes.
- Pas de nouveau framework ou dépendance. Conserver Tkinter et le lancement existant.

## 5. Recette native à réaliser sur CODEX-VM

Avec données fictives et sans ouvrir des discussions réelles :

- **1360 × 820**, aperçu **fermé** : arbre en haut à gauche, identité/recherche au centre, Liste bien dominante et occupant la largeur libérée.
- **1360 × 820**, aperçu **ouvert** : trois colonnes alignées sous le menu ; inspecteur remonte en haut, scrollbar et molette fonctionnelles.
- **1000 × 680**, aperçu fermé et ouvert : aucun contrôle indispensable hors écran ; largeur de recherche raisonnable et titres/listes utilisables.
- **Fenêtre agrandie** : ne jamais étirer automatiquement la recherche sur toute la largeur disponible ; conserver la respiration et des proportions cohérentes.
- **Transitions** : ouvrir/fermer l'inspecteur plusieurs fois, redimensionner, changer de projet, chercher au clavier (`Ctrl+K`), ouvrir des suggestions, puis fermer/reouvrir l'application ; disposition stable et aucune perte de sélection ou de filtres.
- **Menus figés** : ouvrir `Fichier` et `Affichage` en haut depuis la nouvelle disposition, vérifier le fonctionnement de souris/clavier/Échap, le chevauchement et le focus. `Ctrl+S` conserve son sens « Enregistrer la fiche ».
- Conserver les **46 tests existants** et ajouter uniquement les tests de régression pertinents pour la nouvelle implantation ; s'assurer que la recette de fenêtres et de menus n'a pas été remplacée par des tests simulés seuls.

## 6. Livrables et acceptation

- **Deux ou trois captures de la vraie application exécutée** : aperçu fermé, aperçu ouvert, et format compact si nécessaire, avec catalogue fictif.
- Un rapport **court** `reports/MG-002b-02/rapport.md` : résultat, comparaison avec la disposition demandée, tests, blocages éventuels et liens aux captures.
- README/numéro de version seulement si utile ; commit/push `origin/main`, SHA distant vérifié, dépôt propre, **PNG et menu principal inchangés**.
- **Pas de GO esthétique auto-proclamé** : Codex indique les vérifications techniques et laisse à l'utilisateur l'approbation visuelle.
- **Ne lancer aucune mission suivante** avant notre validation.

**Critère unique de réussite :** sous le menu Windows plus plus validé, la gauche et la droite occupent enfin toute leur hauteur, tandis que le centre conserve une jolie identité graphique et une recherche **compacte**. La fenêtre respire et nous gagnons de l'espace pour nos discussions.
