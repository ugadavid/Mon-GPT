# RT-001 — Audit des licences et gouvernance continue Trucabule (étude uniquement)

**Demande utilisateur — 17 novembre 2026**  
**Priorité : avant la revue des composants et avant la distribution des prochaines versions.**  
**Périmètre : les six productions Trucabule, dont cinq dépôts contenant du code et Ma Capture à l'état de projet.**

## Décision de l'atelier

Trucabule est un **atelier de création d'applications Windows, gratuites pour leurs utilisateurs et destinées à être open source**. Son propre site Internet est la seule exception à la règle « Trucabule ne produit que des applications ». Dans quelques années, un passage de certains produits au multiplateforme peut être envisagé, **sans le décider ni le préparer coûteusement aujourd'hui**.

**Cette mission commence par un audit et des recommandations, PAS par le choix ou l'application d'une licence.** David et GPT étudieront les options, puis David décidera explicitement. Ne pas confondre « code visible sur GitHub », « application gratuite », « source ouverte sous licence », ni « licence de la marque et des illustrations ».

L'utilisateur souhaite un mécanisme **permanent et léger** de gestion des licences pendant les développements, les imports d'actifs, les mises à jour de dépendances, les nouvelles fonctionnalités et les distributions. Le simple ajout ponctuel d'un fichier `LICENSE` ne résoudrait pas le problème.

## Projets à examiner — et seulement eux

| Produit | Dépôt / matière première | État |
| --- | --- | --- |
| **Mon GPT<3** | `ugadavid/Mon-GPT` | Application Windows Python/Tk + extension Chrome Collector ; dépôt public au premier relevé |
| **Ma Médiathèque** | `ugadavid/ma-librarie` | Application Windows Python/Tk ; dépôt public au premier relevé |
| **Mon Bureau** | `ugadavid/mon-bureau` | Application Windows .NET/WinForms ; dépôt privé au premier relevé |
| **Chrome Organizer** | `ugadavid/chrome-organizer` | Application Windows Python/Tk ; dépôt privé au premier relevé |
| **Mon Aise** | `ugadavid/mon-aise` | Prototype très précoce d'application ; React/TypeScript/Vinext, actuellement hébergé via Sites ; dépôt privé au premier relevé. **Ne pas le traiter comme un produit site Web définitif.** |
| **Ma Capture** | Cahier des charges, décisions et éventuels documents accessibles ; **ne pas inventer un dépôt** | Projet non codé : proposer les conventions de licences et de provenance dès le départ, mais **aucun audit de dépendances fictives** |

**Hors périmètre :** le site institutionnel `trucabule.fr`, Iconothèque, Textothèque, TRAME, atelier, dev-lab, les prototypes LIDILEM ; ne pas les explorer ni modifier pour cette mission.

**Accès :** si l'un des dépôts ou cahiers de charges n'est pas accessible dans le contexte Codex, inscrire **« Non examiné — accès absent »**, sans déduire son contenu de suppositions.

## Constat de départ — à recontrôler, pas à traiter comme conclusion juridique

Un premier relevé GitHub, le 17 novembre 2026, a trouvé **aucun fichier `LICENSE`, `LICENCE`, `COPYING`, `NOTICE`, `REUSE.toml` ou `LICENSES/`** sur la branche principale des cinq dépôts codés (exploration d'arborescence complète, non tronquée). Le champ de licence détectée par GitHub était également vide. Ce constat **n'exclut pas** des notices dans les sources, dépendances, binaires, images, README, artefacts ou conditions propres à un fournisseur.

## Travail demandé

### A. Inventaire factuel par projet

Sans modifier les sources, relever pour chacun des cinq dépôts :

- Visibilité actuelle, éventuelle déclaration de licence, mentions de copyright, contributeurs/ayants droit à confirmer, informations dans README, packages et sources ;
- **Dépendances directes de production et de développement**, leurs versions déclarées et licences à confirmer sur sources officielles ou métadonnées fiables ; distinguer directes, transitives et composants livrés effectivement ; noter « inconnue » si non établie ;
- **Ressources et contenus** : images, icônes, logos, polices, captures, couvertures, illustrations, exemples, documentations, extraits repris, outils embarqués, binaires, code copié d'ailleurs ; pour chaque catégorie indiquer *origine vérifiée / origine à documenter / droits à confirmer* ; ne jamais présumer qu'une ressource « dans le dépôt » est librement redistribuable ;
- Particularités de **packaging et publication** (exécutable avec runtime embarqué, ZIP portable, extension Chrome, publication Sites, éventuelle dépendance à un service) ; inventorier les textes de licence à fournir éventuellement avec ces livrables ;
- Risques concrets de provenance non documentée, licence incompatible ou attribution manquante, **sans qualifier juridiquement la situation au-delà des preuves** ;
- Pour Ma Capture, seulement une **checklist de conception** sur code, ressources, bibliothèques, licences et attribution à prévoir ; **aucune hypothèse de stack**.

Indiquer **preuves vérifiables (chemin + extrait court ou référence officielle) et niveau de certitude**, sans publier le contenu des dépôts privés dans le dépôt public Mon GPT<3.

### B. Comparaison de licences possibles — recommandation, pas décision

Préparer une explication concise et neutre, à destination d'une personne qui veut offrir des logiciels **gratuits et open source** :

- Comparer quelques familles pertinentes, au minimum **MIT**, **Apache-2.0**, **MPL-2.0** et **GPL-3.0** (ou variante appropriée motivée), en distinguant **permissive**, **copyleft de fichier**, **copyleft étendu** ;
- Comparer les obligations de conservation des notices, accès au code, modification, redistribution de binaires, brevets lorsqu'ils sont concernés, compatibilités possibles, conséquences de contributions externes et éventuels actifs/ressources sous des licences distinctes ;
- Montrer que **gratuit pour l'utilisateur** n'est pas synonyme de **licence interdisant la revente** : pour être open source, la redistribution commerciale ne peut pas être interdite (définition OSI) ;
- Ne pas présumer le titulaire exact des droits ou l'étendue des droits sur des contributions ou actifs : **questions ouvertes à remonter à l'utilisateur** ;
- Recommander au plus **deux options argumentées** pour la politique de licences Trucabule, en indiquant s'il faut une licence commune ou des exceptions par application, et **ce qui reste à vérifier avant décision** ;
- Référencer les textes et documentations **officielles**, avec liens actifs (GitHub Docs, OSI, SPDX, REUSE et sites des titulaires des licences de dépendances).

**NE CRÉER aucun `LICENSE` dans les applications à ce stade ; NE CHOISIR aucune licence au nom de David.**

### C. Gouvernance *vivante* et intégration au travail quotidien

Proposer un **processus minimal mais durable**, adapté à une petite famille d'applications et à un développement fréquent par Codex :

1. À la **création d'une application** : licence du code après décision, titulaire à confirmer, contenu du README, politique initiale des assets, règle d'hébergement/distribution ;
2. À chaque **ajout ou mise à jour de dépendance** : identifier version, licence, finalité, source de référence, notices/conditions à suivre, éventuelles incompatibilités ;
3. À chaque **nouvelle image, icône, police, couverture, fichier de démo ou contribution** : documenter origine, titulaire présumé/confirmé, droit de redistribution et éventuelle attribution ; en cas d'incertitude, marquer « à valider », sans attribuer fictivement une licence ;
4. À chaque **livraison Windows, extension Chrome ou publication Web** : vérifier les **fichiers de licence, notices des tiers, dépendances embarquées, ressources redistribuées, disponibilité du code source lorsque requis**, ainsi que l'état des validations ;
5. À chaque **mission Codex ou PR** : courte section « Licences et provenance : changements / aucun changement vérifié / point bloquant » ; avec un moyen de contrôle automatisé **léger**, mais seulement après accord sur l'outil et le coût ;
6. Prévoir un **point de contrôle périodique raisonnable**, sans surveillance automatique de nouvelles dépendances ni fichier supplémentaire tant que le processus n'a pas été validé.

Étudier sans implémenter les composants éventuels : `LICENSE` (code), `THIRD_PARTY_NOTICES.md` ou équivalent, inventaire/licences des actifs, mentions `SPDX-License-Identifier`, `REUSE.toml`, `reuse lint`, génération éventuelle de SBOM et un contrôle de CI. **Privilégier la voie la plus simple** : ne pas déployer toute la norme REUSE si la charge est disproportionnée, mais indiquer les conditions de montée en maturité.

### D. Chiffrage indicatif, avec hypothèses

Estimer **en fourchettes**, par tâche, sans fausse précision :

- audit ponctuel des cinq dépôts ;
- attribution/clarification des ressources inconnues ;
- mise en place après validation par David (fichier(s) de licence, notices, métadonnées, checks légers, instructions Codex) ;
- coût **récurrent par évolution et par livraison**, sur un portefeuille de six puis dix applications ;
- valeur/coût d'une gestion maison ou d'un outil existant (REUSE, détecteur de licences de dépendances, simple checklist), sans choix imposé.

**Séparer** temps d'analyse, décisions qui nécessitent l'utilisateur, modifications après GO, recette et maintenance. Afficher les inconnues empêchant une estimation fiable.

## Livrables attendus

1. **Rapport décisionnel lisible** : bref résumé, constat par application, matrice « éléments / licence connue ou inconnue / source / risque / action » et différences entre les familles de licences ; tableau des coûts ; **questions nécessitant une décision de David** ; proposition de procédure permanente ;
2. **Plan RT-002 éventuel** pour la phase d'application **après validation explicite** : pas un GO implicite ;
3. **Version partageable** du rapport dans `reports/RT-001/` du dépôt **public** Mon GPT<3, **SANS détail non public ni contenu du code privé**, et, si nécessaire, un **inventaire complet conservé localement, sous `.recette/RT-001/`** (répertoire ignoré par Git de Mon GPT<3) ; ne pas publier de secrets, données réelles, copies de dépendances ni contenus privés. Si un rapport détaillé ne peut être rendu sans fuite d'information privée, l'écrire **uniquement en local** et fournir à David le chemin exact.
4. Conserver un **sommaire daté des sources consultées** et les limites de l'audit.

### Critères de réussite

- Les **cinq dépôts existants** et **Ma Capture comme projet** sont tous listés, sans confondre « non examiné » avec « aucun » ;
- Les informations de licence sont **tracées aux sources**, non déduites d'une intuition ou d'un nom de package ;
- Les **ressources et dépendances réellement livrées** sont traitées, et pas seulement les fichiers `LICENSE` à la racine ;
- La comparaison aborde bien **gratuité, redistribution et source ouverte**, et propose une **gestion continue concrète** ;
- Les **coûts ponctuels et récurrents** sont séparés, les incertitudes visibles ;
- **Aucune modification** du code, des licences, de la CI, des dépendances, des préférences, du packaging, de la visibilité GitHub ou des paramètres des applications. Aucune publication de contenu des dépôts privés ;
- **STOP et demande de validation utilisateur** avant toute implantation des licences.

## Références de départ

- [Documentation GitHub : licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- [Open Source Definition — OSI](https://opensource.org/osd)
- [SPDX License List](https://spdx.org/licenses/)
- [REUSE Specification](https://reuse.software/spec/)
- [Cadrage Trucabule](../docs/revue-technique/02-vision-trucabule-et-mutualisation.md)
- [Matrice des six applications](../docs/revue-technique/03-cartographie-fonctionnelle-trucabule.md)

**Fin de RT-001 : rapport et recommandations uniquement.** David/GPT choisissent ensuite le modèle de licence et le degré d'automatisation ; Codex n'entreprend aucun changement de licence sans demande explicite.
