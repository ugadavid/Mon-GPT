# 03 — Première cartographie fonctionnelle des quatre produits Trucabule

**17 novembre 2026 — phase A, premier passage utilisateur + GPT. Lecture seule ; ce document ne lance aucune implémentation.**

Cette cartographie part de **besoins fonctionnels**, pas d'une préférence pour Python, .NET ou un framework. Elle sert à repérer ce qu'il faudra **mesurer dans le code**, sans prétendre avoir déjà prouvé que des modules sont identiques.

## Sources et méthode

- [Mon GPT<3 — première revue](01-inventaire-technologies.md), [rapport MG-011](../../reports/MG-011/rapport.md) et [code](../../mon_gpt/).
- [Ma Médiathèque — README](https://github.com/ugadavid/ma-librarie/blob/main/README.md), consulté pour les fonctions et l'emballage Windows.
- [Mon Bureau — README](https://github.com/ugadavid/mon-bureau/blob/main/README.md), consulté pour les fonctions, la configuration et la distribution.
- **Ma Capture** : projet en conception, **pas de code livré établi** à ce stade. Les exigences décrites dans les échanges (capture, annotation immédiate, fiche et classement documentaire) sont traitées comme des **besoins prévus**, à confronter ensuite au cahier des charges écrit.

**Légende :** **Présent** = documenté pour l'application actuelle ; **Prévu** = besoin de conception, non développé ; **À vérifier** = non suffisamment établi par les sources examinées ; **—** = pas de besoin retenu à ce stade, pas une preuve d'absence.

## Matrice initiale

| Famille / fonction | Mon GPT<3 | Ma Médiathèque | Mon Bureau | Ma Capture | Mutualisation à étudier |
| --- | --- | --- | --- | --- | --- |
| **Interface Windows locale** | Présent : Python/Tk | Présent : Python/Tk | Présent : .NET/WinForms | Prévu : application Windows | Conventions UX communes ; widgets communs seulement **par pile compatible** |
| **Navigation par collections / catégories / projets** | Présent : arbre projets et dossiers virtuels | Présent : bibliothèques, collections et racines | Présent : épinglés, catégories et administration | Prévu : bibliothèque de captures et catégories | Navigation, sélection, titres de périmètre : **comparer les interactions** |
| **Liste / grille ou mosaïque / aperçu** | Présent : Liste, Détaillée, Mosaïque | Présent : Liste, Mosaïque, volet de détails | Présent : tuiles de lanceurs ; autres vues à étudier | Prévu : bibliothèque et édition/aperçu de captures | Composants d'affichage et conventions, notamment entre les deux apps Tk |
| **Fiches et métadonnées** | Présent : résumé, notes, tags, catégories, emplacements | Présent : informations sur fichiers, auteurs, formats et collections | Présent : fiche de lanceur, catégories, chemins et arguments | Prévu : titre, description, tags, catégories et annotations | Formulaires, validation, champs optionnels, relations : **identifier noyau commun + spécifique** |
| **Recherche, filtres et tri** | Présent | Présent | À vérifier dans le détail | Prévu : recherche documentaire | Modèle de filtrage, sort, réemploi des contrôles |
| **Sélection et opérations sur plusieurs éléments** | Présent : sélection multiple et rattachements | Présent : sélections et menus documentés ; gestes groupés précis à vérifier | Présent : gestion de l'ordre des épinglés ; lot à vérifier | À préciser | Actions / undo éventuel : **ne pas assimiler toutes les opérations** |
| **Images / couvertures / vignettes** | Présent : Pillow, galerie et héritage visuel | Présent : couvertures et vignettes ; Pillow facultatif selon fonction | Présent : décoration et ressources graphiques, pile .NET | Prévu : capture, annotation, image archivée | Gestion des images, miniatures, caches ; lib maison potentielle **surtout dans les apps Tk** |
| **Stockage local** | Présent : JSON versionné | Présent : SQLite | Présent : JSON | À définir/vérifier | **Conventions** de stockage, migrations, validation, intégrité ; ne pas imposer le même moteur |
| **Préférences et état de l'interface** | Présent : `interface.json` | Présent : mémorisation des vues/filtres | Présent : configuration des lanceurs et catégories JSON | Prévu : décisions d'UX à documenter | Conventions de préférence/état et API modulaires |
| **Import / export / échanges** | Présent : Collector JSON et sauvegarde ZIP | Présent : inventaire et métadonnées, exports à approfondir | Présent : import/configuration de lanceurs JSON | Prévu : archivage d'images et métadonnées | Formats, validation, dossiers, interfaces d'import ; **cas très différents** |
| **Sauvegarde et restauration** | Présent : ZIP | À documenter précisément | À documenter précisément | À préciser | Comparer les fonctions réelles avant extraction d'un service partagé |
| **Distribution Windows / mises à jour** | Pas d'installateur validé à ce stade | Présent : ZIP portable et installateur | Présent : installateur .NET | Non construit | **Candidat transversal immédiat :** conventions, scripts et procédure de recette par pile |
| **Tests et rapport de mission** | Présent : Python unittest et Collector JS | Présent : recette/build documentés | Présent : rapports de missions et builds | Prévu : méthodologie à appliquer | Gabarits, recettes, génération de preuves et qualité des livraisons |

Les états ne sont **pas** des pourcentages de code réutilisable. Ils décrivent seulement le premier niveau de besoin.

## Premières pistes à examiner (hypothèses, pas des conclusions)

### Hypothèse 1 — Un socle d'interaction et d'interface Python/Tk

**Mon GPT<3 et Ma Médiathèque** sont les deux premiers candidats à un rapprochement technique réel : navigation, tables, mosaïques, barres de filtres, panneaux de détails, galeries et dialogues. Il faudra examiner les **classes et appels existants**, la ressemblance exacte et les différences ergonomiques. Le bénéfice possible est une maintenance commune de composants déjà réalisés ; le risque est d'extraire prématurément un composant couplé aux besoins d'une seule application.

### Hypothèse 2 — Services transversaux, sans bibliothèque unique

**Mon GPT<3, Mon Bureau et Ma Médiathèque** ont des besoins de persistance et de configuration, mais pas le même moteur (JSON / JSON / SQLite). Une **convention commune** de versions, sauvegarde, export, restauration, emplacement des données et politique de mise à jour pourrait être plus utile qu'une bibliothèque exécutée par les trois technologies.

### Hypothèse 3 — La distribution comme terrain de réemploi rapide

Les solutions **ZIP portable et installateur** sont déjà documentées pour Ma Médiathèque ; Mon Bureau possède un installateur. Comparer leurs scripts et les besoins de Mon GPT<3 avant toute nouvelle fabrication. Un **modèle de build/recette** commun par pile est peut-être plus rentable qu'une abstraction de code.

### Hypothèse 4 — Ma Capture comme banc d'essai de conception

Comme son architecture n'est pas encore figée, **Ma Capture** permet d'interroger le réemploi *avant* le développement (formulaires, galerie, annotations, métadonnées, sauvegardes). **Ne rien lui imposer** tant que les briques réelles des autres produits ne sont pas étudiées.

## Notre prochaine étape précise

1. Faire confirmer/corriger cette **carte des besoins** par l'utilisateur (périmètre et priorités).
2. Choisir **une première famille** à examiner, par exemple **les composants UI Python/Tk** ou **préférences/sauvegardes/distribution**.
3. Pour cette famille seulement, demander à Codex un **relevé de code factuel** : fichiers, classes, API tierces réellement utilisées, appels, contraintes et tests.
4. Estimer ensuite **Conserver / Encapsuler / Extraire / Réécrire maison**, avec **efforts séparés** (étude, écriture, tests, intégration par application, maintenance) et scénarios **4 puis 5 et 10 applications**.
5. Décider **à deux** si un prototype se justifie ; **aucun développement** tant que l'étude reste ouverte.

**Hors périmètre :** TRAME, atelier, dev-lab, prototypes LIDILEM, Textothèque et Iconothèque (galaxie non décidée). Aucun de ces dépôts ne doit être ajouté à la phase 1 sans décision explicite.

**Statut : premier tableau à discuter. Pas de comparaison quantitative du code encore réalisée, pas de GO à Codex ni à Work.**
