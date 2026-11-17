# MG-013a — Grande passe graphique : diagnostic, direction et découpage

**17 novembre 2026 — Mission d'ouverture pour un NOUVEAU fil Codex dans le projet Mon GPT<3 existant.**  
**GO : analyse visuelle, choix de composition à proposer et préparation d'un plan de réalisation.**  
**PAS DE GO pour refondre l'application dans cette première tranche.**  
**Produit au départ : Mon GPT<3 0.9.4 ; MG-012 livrée et validée humainement par David.**

## Contexte et intention

Après de nombreuses missions fonctionnelles, la petite application Windows/Tk fonctionne. L'utilisateur veut désormais **une réelle montée en qualité graphique**, en confrontant trois maquettes créées au départ avec l'interface native actuelle sur CODEX-VM, avant la future distribution Windows. L'enjeu n'est **pas** de réinventer ses fonctionnalités : « Liste = efficacité ; Détaillée = équilibre ; Mosaïque = plaisir visuel ».

Dans notre discussion du 17 novembre, l'utilisateur a fourni **six captures** : trois maquettes de conception, puis trois captures de la réalisation actuelle (mosaïque, liste/À classer et détaillée). Ces captures de la conversation ne sont pas implicitement accessibles au nouveau Codex ; **retrouver les trois références graphiques originales dans le dépôt**, et **prendre des captures actuelles sur CODEX-VM** pour comparer réellement, plutôt que prétendre avoir vu des fichiers absents de son contexte.

### Références à étudier intégralement AVANT toute proposition

- `missions/MG-002-maquettes/01_specification_UX.md` : décisions et charte validées le 14 novembre ; **préférer ses contrats aux inventions des images** lorsque les deux divergent.
- Les trois PNG présents dans le même dossier :
  - `Image ChatGPT 14 nov. 2026, 11_51_22-1.png` — explorateur rapide, teintes fraîches ;
  - `Image ChatGPT 14 nov. 2026, 11_51_54-2.png` — bibliothèque/aperçu, vert doux ;
  - `Image ChatGPT 14 nov. 2026, 11_51_55-3.png` — gestionnaire fluide, accents terracotta.
- `README.md`, `AGENTS.md`, `docs/MG-011-navigation-et-informations.md`, `reports/MG-011/rapport.md`, `reports/MG-012/rapport.md`, captures actuelles et code UI.
- Anciennes missions `MG-002a` et `MG-002b-01..06` à relire comme histoire des arbitrages, en distinguant ce qui est encore valable de ce que le code actuel a déjà dépassé.
- `mon_gpt/theme.py`, `ui.py`, `atelier.py`, `navigation.py`, `mosaic.py`, `results.py`, `information_ui.py` et autres modules UI réellement présents (ne pas inventer leurs rôles avant lecture).

**Ne pas dupliquer, renommer, transcoder ou re-publier les trois maquettes originales.**

## Contrats fonctionnels à préserver

- Trois vues partageant une sélection, une recherche et des filtres cohérents.
- Treeview/rattachements multiples, hiérarchie projet-parent unique, navigation et tri manuel.
- Identité visuelle et héritage des images/icônes/couleurs existants.
- **Titre et clic de sélection ≠ ouverture automatique** : le comportement réellement validé des missions récentes prime sur les anciennes propositions MG-002. Le lien explicite ↗ et ses raccourcis doivent rester exacts.
- Gestes glisser gauche/droit, actions groupées, menus, éditeur, sauvegardes et imports inchangés.
- Menu Aide, Gestes/raccourcis, À propos et **Licences et crédits MG-012** préservés ; l'évolution esthétique devra inclure leur cohérence sans les réécrire.
- Aucun nouveau schéma métier, service cloud, collecte Chrome, migration de données d'essai ou refactorisation du cœur. Les données de recette sont fictives et jetables.
- L'éventuelle création future d'un exécutable/installateur est un chantier **distinct**, non lancé ici.

## Charte et latitude artistique

Palette de base validée dans `01_specification_UX.md` : ivoire `#F7F3EA`, sable `#E7D9C5`, sapin `#315E4F`, terracotta `#C87A50`, encre `#292D30`. Des nuances ou ajustements sont possibles, sans rebâtir la marque ni imposer une palette identique aux trois mockups.

Les maquettes montrent **trois interprétations complémentaires**, pas une maquette à copier pixel pour pixel. Analyse notamment :
- densité de la colonne gauche, indentation, cibles de sélection et drop ;
- visibilité relative des trois colonnes ; respiration et hiérarchie typographique ;
- zone de recherche et filtres ; menus, raccourcis et actions contextualisées ;
- Liste compacte, Détaillée et Mosaïque : garantir leurs usages distincts ;
- panneau d'aperçu à droite, titres longs, sections et actions ;
- repli de l'aperçu, fenêtre compacte, DPI Windows, scroll, focus, claviers et textes français ;
- cohérence graphique des fenêtres d'information sans effets gadget.

**Ne pas réintroduire des fonctions supprimées ou différées** simplement parce qu'elles sont dessinées sur une maquette (ex. navigation Favoris/Récents, filtres ou gros boutons inopérants). Aucun bouton décoratif.

## Travail demandé dans MG-013a — étude seulement

1. **Photographie de l'existant** : comparer les trois vues actuelles et les trois maquettes sur une même base fictive, noter les disparités vérifiées et les éléments déjà satisfaisants. Le rapport indique clairement quelles captures ont réellement été vues, avec chemins vérifiables.
2. **Proposition de direction visuelle unique** : expliquer quels traits retenir de chacune des trois références et pourquoi ; distinguer décisions UX validées, recommandations graphiques et points à arbitrer par David. Préférer un langage graphique cohérent aux trois interprétations juxtaposées.
3. **Carte des composants touchés** : repérer les classes/surfaces Tk, couplages et mécanismes de thème concernés. Préférer retouche localisée et réemploi des composants existants ; pas de migration vers Qt ni nouvelle grosse dépendance par réflexe.
4. **Découpage en lots de réalisation bornés**, par ordre de valeur visible, avec périmètre exact, risque, durée de travail indicative, critère d'acceptation visuel et dépendances. Suggérer au plus 3–5 tranches, chacune publiable/recettable ; montrer comment garder l'application utilisable entre deux tranches.
5. **Stratégie de vérifications proportionnées** : identifier le test de chaque zone et les voisins directement touchés ; dire ce qui restera non exécuté et pourquoi. Consulter `AGENTS.md` sans l'éditer dans MG-013a. Son instruction actuelle de suite complète avant publication applicative est à **signaler comme coût à réviser**, mais ne la contourner ni la réécrire silencieusement. Un document de cadrage seul n'exige pas de rejouer toute l'application.
6. **Aucune réalisation graphique importante** et aucune modification des cinq domaines métier dans cette tranche : notre utilisateur doit pouvoir valider le cap avant que Codex touche des dizaines de modules.

## Publication autorisée et livrables

Seul le dépôt **`ugadavid/Mon-GPT`** est destination des documents de MG-013a. Publier :
- `reports/MG-013a/rapport.md` : comparaison courte « références / existant / intention de correction », choix proposés, impacts et point d'arrêt ;
- éventuellement une grille/comparaison textuelle ou captures **réelles** de l'application actuelle sur jeu fictif, si elles ajoutent une preuve. Réutiliser les PNG de maquette déjà versionnés ; ne pas les copier.
- une proposition ordonnée de 3–5 lots futurs, **sans créer/GO les missions d'exécution avant décision de David**.

Autorisations Git ordinaires : vérifier l'état initial, synchroniser sans écraser le travail concurrent, documenter, commit/push sur `origin/main` puis vérifier le SHA distant. Ne jamais forcer un push. Aucun nouveau code produit ni tests longs applicatifs nécessaires à cette **mission de cadrage**.

## Point d'arrêt

**MG-013a terminée = direction artistique et lots proposés, publiés, puis STOP pour validation de David.** Ne pas enclencher la grande passe graphique, la distribution Windows ni un audit transversal supplémentaire.

L'objectif est une vraie transformation artistique **ensuite**, préparée avec suffisamment de précision pour éviter six refontes timides ou contradictoires.
