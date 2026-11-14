# MG-002b-01 — Retrouver un menu principal sobre

**Statut : à réaliser.** Première micro-mission de correction visuelle après Mon GPT<3 **0.2.1** (base `57e86bd8b29193f32bff09f141e60fc2ad08241c`).

## Retour utilisateur (prioritaire)

> « Menu principal immonde. S'il y avait un truc à ne pas trop modifier de la version précédente c'était bien le menu. »

**Objectif UNIQUE : restaurer un menu principal Windows sobre, discret, élégant et fonctionnel**, proche de ce qu'il était en MG-002 / 0.2.0. **Ne touche à aucune autre zone graphique ou fonctionnalité dans cette mission.**

## Travail demandé

1. Relire brièvement les trois maquettes et la charte dans `missions/MG-002-maquettes/`, le rapport MG-002a, et comparer le menu 0.2.0 avec celui de 0.2.1. Les images sont déjà sur disque : **aucune duplication, conversion, modification ou retransmission de PNG**.
2. Dans `mon_gpt/ui.py`, `build_menus()` crée déjà un vrai `tk.Menu` (`bar`) mais construit ensuite une **fausse barre** avec `ttk.Frame`, des boutons arrondis et des menus habillés par `skin_menu`. Revenir à une **vraie barre de menus native Windows/Tk** pour les quatre rubriques `Fichier`, `Édition`, `Affichage`, `Aide`. Laisser les panneaux et le thème Atelier chaleureux intacts.
3. Conserver **exactement** toutes les commandes, leur activation/désactivation, leurs destinations, raccourcis et protections. Notamment `Ctrl+S` enregistre **la fiche**, tandis que `Fichier > Sauvegarder le catalogue…` sauvegarde le catalogue entier.
4. Retirer la surcouche de faux menu principal **sans casser les menus contextuels** de clic droit ni le menu `+` intégré aux autres zones. Ne pas supprimer `MenuSkin` partout par principe ; isoler la correction au menu principal et éviter les modifications de portée inutile.
5. Le menu doit être lisible et navigable à la souris et au clavier, avec survol/sélection natifs et comportement normal de fermeture, sans laisser d'espaces morts en haut de la fenêtre.

## Périmètre interdit

- **Ne pas retoucher** : champ de recherche, bandeau illustré (sauf ajustement strictement nécessaire pour le menu), Liste, cartes, icônes, inspecteur, scrollbar, tags, catégories, création, glisser-déposer, doublons.
- Ne pas ajouter de fonctions ou de contrôles décoratifs ; pas de changement de framework, schéma JSON, catalogue, moteur `core.py`, `chatgpt.py`, `storage.py` ni d'assets de maquettes.

## Recette et livraison

- Tester les quatre menus **physiquement dans l'application exécutée sur CODEX-VM**, en grande fenêtre et en format compact. Vérifier souris, clavier, fermeture, absence de chevauchement. Les commandes doivent toujours fonctionner ; les contrôles destructeurs restent protégés.
- Conserver les **42 tests** MG-002a et ajouter seulement les tests nécessaires à cette petite correction.
- Publier **deux captures réelles**, dont une avec le menu Fichier ouvert et une de la fenêtre complète pour voir le résultat. Données fictives uniquement.
- Rapport court : `reports/MG-002b-01/rapport.md` ; version/README actualisés uniquement si nécessaire ; commit et push `origin/main`, SHA distant vérifié. **Ne pas annoncer de GO graphique général : nous validerons ce menu avant la prochaine micro-mission.**

**Critère de réussite :** le menu se fait oublier. Aucun effet « gros boutons », aucun menu stylisé artificiellement au détriment des usages Windows. Un seul résultat à juger : **le menu principal**, et rien d'autre.
