# 03 — Première cartographie fonctionnelle des six produits Trucabule

**17 novembre 2026 — phase A, premier passage utilisateur + GPT. Lecture seule ; ce document ne lance aucune implémentation.**

Cette cartographie part de **besoins fonctionnels**, pas d'une préférence pour Python, .NET ou un framework. **Règle de marque : Trucabule produit exclusivement des applications ; son propre site de présentation est la seule exception.** L'accès Web temporaire de Mon Aise n'en fait pas un « site » à la place d'une application. **Aucune pile observée dans une première alpha ne vaut choix de plateforme définitif.** Elle sert à repérer ce qu'il faudra **mesurer dans le code**, sans prétendre avoir déjà prouvé que des modules sont identiques.

## Sources et méthode

- [Mon GPT<3 — première revue](01-inventaire-technologies.md), [rapport MG-011](../../reports/MG-011/rapport.md) et [code](../../mon_gpt/).
- [Ma Médiathèque — README](https://github.com/ugadavid/ma-librarie/blob/main/README.md), consulté pour les fonctions et l'emballage Windows.
- [Mon Bureau — README](https://github.com/ugadavid/mon-bureau/blob/main/README.md), consulté pour les fonctions, la configuration et la distribution.
- [Chrome Organizer — README](https://github.com/ugadavid/chrome-organizer/blob/main/README.md) et [architecture des sauvegardes](https://github.com/ugadavid/chrome-organizer/blob/main/docs/architecture_sauvegardes.md), consultés pour les profils/favoris/sessions, sauvegardes, formats de données et tests.
- [Mon Aise — README](https://github.com/ugadavid/mon-aise/blob/main/README.md) et [package.json](https://github.com/ugadavid/mon-aise/blob/main/package.json), consultés pour les fiches Web, la persistance R2/JSON et la pile React/TypeScript/Vinext.
- **Ma Capture** : projet en conception, **pas de code livré établi** à ce stade. Les exigences décrites dans les échanges (capture, annotation immédiate, fiche et classement documentaire) sont traitées comme des **besoins prévus**, à confronter ensuite au cahier des charges écrit.

**Légende :** **Présent** = documenté pour l'application actuelle ; **Prévu** = besoin de conception, non développé ; **À vérifier** = non suffisamment établi par les sources examinées ; **—** = pas de besoin retenu à ce stade, pas une preuve d'absence. Les technologies et modes de diffusion indiquent **uniquement l'implémentation actuelle** ; les objectifs et options futures doivent être établis séparément.

## Matrice initiale

| Famille / fonction | Mon GPT<3 | Ma Médiathèque | Mon Bureau | Chrome Organizer | Mon Aise | Ma Capture | Mutualisation à étudier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Interface / plateforme** | Présent : Windows Python/Tk | Présent : Windows Python/Tk | Présent : Windows .NET/WinForms | Présent : Windows Python/Tk | Prototype actuel : React/TypeScript/Vinext via Sites ; **application cible, plateforme ouverte** | Prévu : Windows | Conventions communes ; widgets mutualisables surtout **dans la même pile** |
| **Navigation et regroupement** | Arbre projets et périmètres | Bibliothèques, collections, dossiers sources | Épinglés, catégories, administration | Profils, fenêtres, sessions, favoris | Fiches et catégories | Prévu : bibliothèque de captures | Hiérarchie, focus, sélection, navigation, vocabulaire |
| **Liste / grille / aperçu** | Liste, Détaillée, Mosaïque | Liste, Mosaïque, détails | Tuiles de lanceurs | Explorateur Tk de profils, favoris et sessions | Fiches consultables ; forme exacte à auditer | Prévu : archive et éditeur/aperçu | Composants Tk entre **trois** apps ; principes transversaux pour le Web |
| **Fiches et métadonnées** | Résumé, notes, catégories, tags, rattachements | Titres, auteurs, formats, collections | Lanceurs, chemins, catégories, arguments | Profils, fenêtres, onglets, URL, groupes, provenance | Nom, surnoms 1/2, catégories multiples, dates nommées | Prévu : titre, description, tags, annotations | Formulaires, champs optionnels, identifiants, provenance et validation |
| **Recherche, filtres, tri** | Présent | Présent | À vérifier en détail | Navigation présente ; recherche/tri à vérifier en détail | Recherche nom / surnom 1 / catégories, insensible aux accents | Prévu : recherche documentaire | Distinguer algorithmes et composants UI |
| **Sélection et actions groupées** | Sélection multiple et rattachements | Sélection/menu présent ; groupes à mesurer | Ordre des épinglés ; lot à vérifier | Sélection de plusieurs profils pour export | CRUD de fiches ; lot à vérifier | À préciser | Gérer les mêmes gestes lorsque les règles métier le permettent |
| **Images, couvertures, visuels** | Pillow, galerie, héritage | Vignettes et couvertures ; Pillow selon option | Illustrations UI .NET | Couleurs de groupes ; traitement d'images à vérifier | Décor et ressources Web ; gestion documentaire d'images non établie | Prévu : captures et annotations | Image/tuiles : potentiels modules Tk ; design tokens inter-piles |
| **Stockage / persistance** | JSON local versionné | SQLite local | JSON local | Archives locales de profils, manifestes, inventaires, SHA-256 | **JSON côté serveur, R2, ETag** ; pas de localStorage | À définir / vérifier | Contrats et validation partagés ; pas de moteur unique imposé |
| **Préférences / état UI** | `interface.json` | Modes et filtres mémorisés | Configuration JSON des lanceurs | Choix de sauvegardes et d'exploration ; détails à auditer | Catalogue JSON R2 ; préférences UI à vérifier | Prévu : besoins UX à documenter | Conventions d'état et de version, propres à chaque environnement |
| **Import / export** | Collector JSON, sauvegarde ZIP | Inventaires et métadonnées ; exports à détailler | Configuration JSON, lanceurs | Export **JSON / HTML**, lecture d'archives, sélection de profils | **Export JSON** du catalogue | Prévu : archivage d'images et fiches | Contrats export, métadonnées, ergonomie ; chaque domaine garde son adaptateur |
| **Sauvegarde / restauration** | ZIP du catalogue | À documenter précisément | À documenter précisément | Sauvegarde exhaustive vérifiable ; **préparation** de restauration, pas restauration réelle prouvée | Export de données ; restauration structurée à vérifier | À concevoir | Manifestes, vérification, séparer copie, intégrité et restauration |
| **Distribution** | Pas encore d'installateur | ZIP portable + installateur Windows | Installateur Windows .NET | Archive de sources portable ; **Python/Tk requis**, pas exe autonome | Prototype hébergé actuellement via Sites ; **distribution applicative future à définir** | Non construite | Modèles build et publication par plateforme ; convention de version |
| **Tests / recette** | unittest Python et tests JS Collector | Recettes/build documentés | Rapports et builds documentés | unittest, contrôles Tk et témoins synthétiques | TypeScript/build et recette de l'aperçu ; couverture automatisée à auditer | À prévoir | Gabarits de rapports, fixtures, critères de recette et traces fiables |

Les états ne sont **pas** des pourcentages de code réutilisable. Ils décrivent seulement le premier niveau de besoin, **pas des technologies ou formats de produits arrêtés pour les versions futures**.

## Premières pistes à examiner (hypothèses, pas des conclusions)

### Hypothèse 1 — Un socle d'interaction et d'interface Python/Tk

**Mon GPT<3, Ma Médiathèque et Chrome Organizer** sont trois candidats à un rapprochement technique réel : navigation, listes, panneaux de détails et dialogues ; **les mosaïques et galeries sont à comparer uniquement là où elles existent effectivement**. Il faudra examiner les **classes et appels existants**, la ressemblance exacte et les différences ergonomiques. Le bénéfice possible est une maintenance commune de composants déjà réalisés ; le risque est d'extraire prématurément un composant couplé aux besoins d'une seule application.

### Hypothèse 2 — Services transversaux, sans bibliothèque unique

**Mon GPT<3, Mon Bureau, Ma Médiathèque et Chrome Organizer** ont des besoins de persistance et de configuration, mais avec des stratégies variées (JSON, SQLite, archives locales). **Mon Aise** apporte le cas du JSON serveur R2 avec gestion des versions ETag. Une **convention commune** de versions, sauvegarde, export, restauration, emplacement des données et politique de mise à jour pourrait être plus utile qu'une bibliothèque exécutable commune à toutes ces piles.

### Hypothèse 3 — La distribution comme terrain de réemploi rapide

Les solutions **ZIP portable et installateur** sont déjà documentées pour Ma Médiathèque ; Mon Bureau possède un installateur ; Chrome Organizer distribue une **archive portable de sources nécessitant Python/Tk**. Le prototype de Mon Aise est **actuellement hébergé via Sites**, mais son mode de distribution applicatif à terme **n'est pas décidé**. Comparer leurs scripts et les besoins de Mon GPT<3 avant toute nouvelle fabrication. Un **modèle de build/recette** commun par pile est peut-être plus rentable qu'une abstraction de code.

### Hypothèse 4 — Ma Capture comme banc d'essai de conception

Comme son architecture n'est pas encore figée, **Ma Capture** permet d'interroger le réemploi *avant* le développement (formulaires, galerie, annotations, métadonnées, sauvegardes). **Ne rien lui imposer** tant que les briques réelles des autres produits ne sont pas étudiées.

### Hypothèse 5 — Contrats inter-piles à partir du prototype actuel de Mon Aise

**La réalisation actuelle de Mon Aise** permet d'étudier les fiches, catégories et la recherche implémentées en React/TypeScript/Vinext, en comparaison avec les applications Windows. Son ambition reste **une application**, sans engagement sur la plateforme ni le mode de distribution futurs. Le partage direct de code graphique avec Tk/WinForms n'est pas acquis ; comparer d'abord les **besoins et les contrats**, puis mesurer les possibilités réelles.

### Hypothèse 6 — Gestion de Chrome et des archives

**Chrome Organizer** traite des profils, fichiers et sessions Chrome ; **Mon GPT Collector** observe les liens et projets rendus dans la page ChatGPT. Les besoins et modèles sont différents, mais leurs exports JSON, tests, règles de provenance et gestion des états méritent d'être comparés **sans les assimiler**.

## Notre prochaine étape précise

1. Faire confirmer/corriger cette **carte des besoins** par l'utilisateur (périmètre et priorités).
2. Choisir **une première famille** à examiner, par exemple **les composants UI Python/Tk** ou **préférences/sauvegardes/distribution**.
3. Pour cette famille seulement, demander à Codex un **relevé de code factuel** : fichiers, classes, API tierces réellement utilisées, appels, contraintes et tests.
4. Estimer ensuite **Conserver / Encapsuler / Extraire / Réécrire maison**, avec **efforts séparés** (étude, écriture, tests, intégration par application, maintenance) et scénarios **6 puis 10 applications**.
5. Décider **à deux** si un prototype se justifie ; **aucun développement** tant que l'étude reste ouverte.

**Hors périmètre :** TRAME, atelier, dev-lab, prototypes LIDILEM, Textothèque et Iconothèque (galaxie non décidée). Aucun de ces dépôts ne doit être ajouté à la phase 1 sans décision explicite.

**Statut : première cartographie des six produits à discuter. Pas de comparaison quantitative du code encore réalisée, pas de GO à Codex ni à Work.**
