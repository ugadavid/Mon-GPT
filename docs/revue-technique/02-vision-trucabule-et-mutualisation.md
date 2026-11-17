# 02 — Vision Trucabule : mutualisation, cohérence et coûts

**17 novembre 2026 — cadrage d'une étude, pas un développement.**

## Règle de périmètre : des applications, pas des sites Internet

**Trucabule ne produit que des applications. Sa seule exception est son propre site de présentation, trucabule.fr.** Un prototype temporairement servi par un Site, une URL ou un navigateur reste **un prototype d'application**, non un « produit site Web » de Trucabule.

**Règle méthodologique :** pour chaque produit, documenter séparément **(1) l'implémentation constatée aujourd'hui**, **(2) la vocation applicative et les usages visés**, **(3) les choix techniques et la distribution encore ouverts**. Ne pas prendre une pile actuelle (Tkinter, .NET/Windows Forms, React/Vinext, etc.) pour un choix définitif sans décision explicite. La première revue compare des **besoins** ; elle ne conclut pas trop tôt à l'avenir des produits.

**Mon Aise** est un prototype très précoce de l'application envisagée. **Aujourd'hui**, il utilise React/TypeScript/Vinext, un hébergement privé via Sites et des données JSON serveur R2. **À terme**, il est destiné à être une **application** ; le choix de sa forme, de sa plateforme et de sa distribution reste à étudier, sans présumer qu'il restera un site.

## Pourquoi nous faisons cette revue

**Mon GPT<3 n'est pas un produit isolé : c'est une application d'un ensemble d'applications personnelles publiées sous la marque Trucabule.** D'autres applications existent déjà ou sont envisagées ; la famille pourrait atteindre rapidement **une dizaine d'applications**.

Le risque n'est pas seulement une dépendance externe trop lourde : c'est de **réécrire et maintenir dix fois le même code**, de faire diverger les gestes, les formats, les outils, les installations ou les corrections. Notre objectif est de pouvoir produire plusieurs applications **autonomes, cohérentes et faciles à maintenir**, sans imposer une architecture unique partout.

**Principe directeur :** examiner ce qui est répétable *à l'échelle de Trucabule*, pas seulement ce qui est utile à Mon GPT<3. La mutualisation doit être envisagée dès l'étude, mais n'a **pas besoin d'être implémentée dans les premières versions alpha**.

## Ce que « avoir du commun » peut signifier

| Niveau de mutualisation | Exemples à rechercher | Ce qui serait partagé | Attention |
| --- | --- | --- | --- |
| **Conventions de produit / expérience utilisateur** | vocabulaire, navigation, raccourcis, classement, ergonomie, aide | document de conventions et règles d'interaction | Les applications gardent leurs usages et personnalités propres |
| **Design system léger** | palette, typographies, espacements, icônes, mises en page | tokens et composants par technologie | Même style visuel ne signifie pas nécessairement **même code exécutable** |
| **Bibliothèques de composants UI** | champs de métadonnées, menus, arbres, panneaux d'édition, galeries, notifications | modules Python/Tk réutilisables ou équivalents pour d'autres technologies | Ne pas contraindre une application .NET ou Web à importer du Tk |
| **Bibliothèques de services locales** | validation, JSON versionné, sauvegarde ZIP, gestion des préférences, fichiers, dates, import/export | API métiers et utilitaires réutilisables, si les besoins concordent | Chercher les différences de schémas et de cycle de vie avant extraction |
| **Outils de fabrication et de recette** | scripts de lancement, tests, génération de captures, versionnage, installateurs, ZIP portable | modèles de scripts, guides, outils de build par plateforme | Distinguer environnement de développement et logiciel distribué |
| **Contrats et documentation** | structure d'un rapport, missions, conventions de données, règles de contribution | gabarits, conventions de validation, checklist de publication | Éviter une bureaucratie documentaire sans bénéfice |

**Distinction capitale :** une application Python/Tk, une application .NET et une application Web peuvent partager **principes, conventions, schémas et design tokens**, mais pas forcément une même bibliothèque de widgets. La réutilisation effective doit être évaluée **par environnement technique**.

## Périmètre décidé — phase 1 : les six productions Trucabule

**Décision de cadrage actualisée le 17 novembre 2026 : limiter la première comparaison à SIX productions Trucabule** — cinq applications avec code existant et Ma Capture, encore en conception. Ne pas élargir l'audit à d'autres dépôts sans nouvelle décision.

| Produit | État à étudier | Source / constat vérifié | Question pour la mutualisation |
| --- | --- | --- | --- |
| **Mon GPT<3** | Application Windows opérationnelle, version **0.9.4**, plus extension **Mon GPT Collector 0.8.2** | [Mon GPT<3](https://github.com/ugadavid/Mon-GPT) ; Python/Tkinter, Canvas et Pillow, catalogue JSON ; extension JavaScript/Chrome MV3 | Que peut-on réutiliser dans d'autres logiciels : composants Canvas, préférences, fiches, images, classement, sauvegardes, menus, tests ? |
| **Ma Médiathèque** | Application Windows déjà distribuée en version alpha, avec installateur et ZIP | [Ma Médiathèque](https://github.com/ugadavid/ma-librarie) ; README consulté : Python/Tkinter, SQLite, Pillow, pypdf et emballage Windows | Quels composants Python/Tk/Pillow, comportements d'interface, sauvegardes, métadonnées et scripts de distribution sont similaires ou divergents de Mon GPT<3 ? |
| **Mon Bureau** | Application Windows existante et distribuable | [Mon Bureau](https://github.com/ugadavid/mon-bureau) ; README consulté : **.NET** et installateur Windows, configuration JSON | Quels principes et contrats peuvent être communs **entre Python et .NET**, et quels composants doivent rester spécifiques à chaque technologie ? |
| **Ma Capture** | **Projet de produit, pas application codée/achevée à ce stade** | Cahier de besoins et choix d'architecture **à retrouver et examiner avant toute affirmation technique** | Opportunité d'**anticiper** des composants communs, sans imposer une architecture définitive ni compter de code inexistant comme réutilisable |
| **Chrome Organizer** | Application Windows en alpha, explorateur/sauvegarde et préparation de restauration ciblée | [Chrome Organizer](https://github.com/ugadavid/chrome-organizer) ; README et code consultés : **Python 3.13 + Tkinter**, lecture des sessions/favoris/profils Chrome, archives avec manifestes, empreintes SHA-256, exports JSON/HTML ; préparation de restauration sans restauration réelle validée | **Troisième application Python/Tk** : widgets, navigation, représentations arborescentes, export, validations et outillage de recette ; comparer sans généraliser ses contraintes propres à Chrome |
| **Mon Aise** | **Prototype applicatif très précoce**, actuellement accessible via un hébergement Web privé ; plateforme cible et distribution non définies | [Mon Aise](https://github.com/ugadavid/mon-aise) ; README et `package.json` consultés : **React, TypeScript, Vinext**, hébergement Sites, données JSON serveur sur **R2**, versions ETag ; recherche par nom/surnom/catégories | Comparer les **contrats de fiches, formulaires, tags/catégories selon présence réelle, préférences, validations**, ainsi que les conventions d'UX sans prétendre partager du code Tk/React |

**Important : comparer ce qui existe à ce qui est prévu sans les confondre.** Pour Ma Capture, recenser les choix et exigences documentés (capture, annotation, édition immédiate, fiches documentaires, archive, ergonomie), puis seulement dégager des besoins communs ; aucune estimation de réemploi de code tant qu'il n'existe pas.

**Statut de Textothèque et Iconothèque :** ces deux projets existent, mais **leur rattachement à la galaxie Trucabule (ou à une autre) n'est pas décidé**. Ils **ne sont pas comptés comme productions Trucabule** et **ne font pas partie de la phase 1**. Leur éventuelle inclusion dans une comparaison future demandera une décision explicite ; ne pas les classer d'office en phase 2.

**Photographie des technologies actuelles (pas des architectures définitives) :** **trois** applications existantes utilisent Python/Tkinter (Mon GPT<3, Ma Médiathèque, Chrome Organizer), **Mon Bureau** utilise .NET/WinForms, **Mon Aise** utilise React/TypeScript/Vinext sur le Web, et **Ma Capture** est en conception. Le socle de Trucabule ne peut donc pas se réduire à une bibliothèque graphique unique. Il faudra distinguer **code réutilisable dans une même pile**, **conventions transversales**, **contrats de données**, **design tokens**, **outillage**, et **bonnes pratiques de maintenance**. Ne pas traiter toutes ces couches comme si elles nécessitaient un framework commun.

### Phase 2 — comparaison élargie, explicitement différée

**Après la clarification du périmètre Trucabule**, envisager à titre de comparaison les projets plus conséquents et les briques déjà produites :

- **TRAME** ;
- **atelier** (conserver ce terme sans présumer qu'il correspond à un dépôt unique) ;
- les fragments et fonctionnalités du **dev-lab** ;
- les développements et prototypes réalisés au cours du **mémoire de M2 et du stage au LIDILEM**.

Ces sources pourraient contenir des composants réutilisables, des idées d'architecture ou des solutions techniques déjà explorées. **Elles ne font pas partie de l'audit initial.** Ne pas les étudier ni préconiser leur intégration dans la phase 1.

**Ordre voulu :** d'abord la carte des **six** productions Trucabule, puis un regard vers le reste du patrimoine logiciel pour éventuellement enrichir cette carte.

## Méthode de revue envisagée

### Étape A — Cadrage à deux (utilisateur + GPT)

- Pour chaque production Trucabule, distinguer **réalisation actuelle / usage voulu / options techniques et distribution ouvertes**. L'état d'une alpha n'est pas le plan de la version finale.
- Maintenir un tableau simple de ce qu'utilise réellement Mon GPT<3 : **technologie, modules, API appelées, raison du choix, alternatives, documentation**.
- Définir les critères : **simplicité, autonomie, réemploi inter-applications, temps de développement, temps d'intégration, maintenance, capacité d'évolution**.
- Distinguer **ce qui est certain**, **ce qui est une hypothèse**, **ce qui demande des mesures**.
- Conserver la règle : **aucune décision de migration ou de bibliothèque maison avant l'analyse**.

### Étape B — Inventaire factuel confié à Codex

**Lecture et recommandations uniquement, pas de code nouveau :**

- Cartographier les modules et dépendances directs/indirects des **cinq applications existantes** de la phase 1, et **les fonctions concrètement utilisées** des bibliothèques tierces et standard ; relever séparément le cahier des charges de **Ma Capture**, sans inventer son implémentation.
- Localiser les composants déjà maison (UI, sélection, identité, stockage, import, tests) ; distinguer les règles génériques du spécifique à ChatGPT.
- Comparer explicitement **Mon GPT<3, Ma Médiathèque, Mon Bureau, Chrome Organizer et Mon Aise** ; pour **Ma Capture**, confronter uniquement les besoins et décisions documentés. Les autres projets (TRAME, atelier, dev-lab, LIDILEM, Textothèque, Iconothèque) restent hors phase 1.
- Estimer **l'effort d'extraction, la réécriture maison, l'intégration et la maintenance** en *fourchettes indicatives*, avec hypothèses et incertitude.
- Proposer **Conserver / Encapsuler / Extraire / Écrire maison / Reporter**, avec avantages et risques. **Pas de refactorisation, publication de package ou changement d'architecture**.

### Étape C — Vue multi-dépôts éventuellement confiée à Work

Utiliser une revue **en lecture seule**, éventuellement dans **Work sur l'environnement local** si les dépôts sont réellement accessibles : comparer les **six productions Trucabule décidées pour la phase 1**, leurs besoins, technologies, interfaces, patterns et processus de livraison, en distinguant les **cinq applications codées** du projet Ma Capture.

**Work complète l'inventaire de Codex :** Codex peut approfondir le code d'un dépôt ; Work peut aider à rassembler les constats transversaux et une synthèse. L'accès aux projets locaux/VM doit être **vérifié dans le contexte d'exécution choisi**, pas supposé à partir de cette discussion.

### Étape D — Arbitrage à deux

Comparer les candidats, sélectionner **1 à 3 expérimentations éventuelles** *uniquement si* elles apportent un gain démontré. Un prototype de mutualisation n'est pas une obligation. Rien n'est exécuté sans nouvelle décision.

## Comment estimer les coûts en temps

Pour **chaque candidat** demander une fourchette argumentée (heures ou jours-personne) :

| Poste | Ce qu'on compte |
| --- | --- |
| **Étude / spécification** | comprendre les usages et contrats, écrire l'API minimale |
| **Extraction ou écriture** | isoler le code existant ou développer la brique maison |
| **Tests et documentation** | cas limites, qualité et mode d'emploi |
| **Intégration par application** | adapter Mon GPT<3 puis chacune des autres applications concernées |
| **Maintenance récurrente** | mises à jour, problèmes de compatibilité, corrections à répercuter |
| **Coût évité** | ce qui n'aurait plus besoin d'être recopié, retesté ou corrigé N fois |
| **Incertitude** | hypothèses non vérifiées, difficulté de portage entre langages ou plateformes |

**Formule de réflexion (pas une prévision chiffrée) :**

- *Avec mutualisation* ≈ coût initial (étude + développement + tests) + **N × coût d'intégration** + maintenance commune.
- *Sans mutualisation* ≈ somme des réalisations par application + maintenance de chacune.

**Demander d'abord un scénario chiffré sur les cinq applications existantes et les besoins prévus de Ma Capture, puis une projection pour 10 applications**, et une indication du *point de rentabilité* éventuel. Les estimations doivent venir **après inspection réelle du code** : **ne pas inventer de délais** maintenant.

## Premières pistes, ouvertes

1. **Composants Tk maison** : il existe déjà dans Mon GPT<3 une interface complexe utilisant Canvas et ttk. Comparer ce qui pourrait servir à **Ma Médiathèque et Chrome Organizer**, puis éventuellement à d'autres applications Python/Tk ; distinguer les dépendances graphiques et les modèles métier.
2. **Services locaux** : préférences JSON, sauvegardes, contrôle de fichiers et galerie d'images pourraient partager des conventions ou modules. Examiner d'abord leurs contraintes de données et de compatibilité.
3. **Contrats communs** : conventions de version, noms, documentation, rapports de recette et scripts de distribution pourraient fournir un fort réemploi même entre **technologies différentes**.
4. **Pillow et autres bibliothèques** : mesurer le coût réel avant de proposer leur remplacement. *Trois appels publics à une bibliothèque ne signifient pas trois fonctions faciles à réécrire*, notamment pour les codecs d'images, métadonnées et erreurs.
5. **Outils autour de Chrome** : Mon GPT Collector observe le DOM du navigateur, alors que Chrome Organizer lit et sauvegarde des profils locaux. Comparer les **contrats d'export, métadonnées de sessions et tests**, sans prétendre que les deux moteurs font la même chose.
6. **Prototype Mon Aise et données côté serveur** : son code actuel ouvre une piste de **conventions documentaires communes** aux autres applications (fiches, catégories, identifiants, versions). React/Vinext/R2 n'est **qu'une implémentation à analyser**, pas une décision d'architecture finale. Son hébergement actuel ne transforme pas ce produit Trucabule en site Internet.

## Principes de décision et état actuel

- **Les bibliothèques maison sont une option sérieuse, pas un dogme.**
- **La cohérence de Trucabule prime sur l'identité technique absolue.**
- **Pas de nouvelle application « framework Trucabule »** tant qu'un besoin partagé, mesuré et rentable n'est pas établi.
- **Pas de changement de code dans cette phase** ; on collecte des faits, compare et documente.
- **La passe graphique de Mon GPT<3 n'est pas oubliée** : le [carnet des finitions](../idees-et-finitions.md) comporte la priorité de rapprocher les métadonnées du projet de sa couverture.

**Statut : hypothèses et méthode validées comme pistes de réflexion ; aucune recommandation d'extraction ou de réécriture n'est encore approuvée.**
