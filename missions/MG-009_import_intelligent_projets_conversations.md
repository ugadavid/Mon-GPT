# MG-009 — Import intelligent des projets et conversations ChatGPT dans Mon GPT<3

**Mission Codex à réaliser : application Windows uniquement, avec recette réelle sur CODEX-VM.**  
**Version cible suggérée : Mon GPT<3 0.9.0.** Le Collector Chrome **0.8.2** demeure inchangé.  
**But :** enfin transformer l'export JSON de notre extension en **projets et fils navigables dans le catalogue local**, puis en faire une opération **répétable, vérifiable et sans doublons**.

## 0 — SOURCE RÉELLE DÉJÀ DANS LE DÉPÔT : À LIRE AVANT TOUT DÉVELOPPEMENT

**Fichier de recette expressément fourni par David :**
`missions/MG-009-imports/mon-gpt-observations.json`

C'est le **vrai export** de Mon GPT Collector 0.8.2 en **schemaVersion: 2**, avec `projects[]` et `conversations[]` ; **ce n'est PAS une sauvegarde du catalogue Mon GPT**.

Contrôle de ce fichier déjà effectué lors de la rédaction de mission (15 novembre 2026) :
- `source: "mon-gpt-collector"`, `schemaVersion: 2`.
- **58 projets / 58 clés distinctes / 58 noms connus**, **115 discussions / 115 UUID distincts / 115 titres connus**.
- **56 discussions ont au moins un projet observé** ; les autres restent à classer (sans inférence).
- **Toutes** les clés de projets référencées par des discussions existent dans `projects[]`.
- Deux **paires d'homonymes exacts** : deux projets appelés « M2 », deux autres appelés « Cours M2 », **quatre clés distinctes**.

**Important : ce fichier est personnel.** Le lire localement sur CODEX-VM pour **la recette isolée demandée**, sans l'intégrer au programme, le dupliquer dans les ressources de distribution ni en reprendre des titres/URL/identifiants dans les rapports/captures/journaux publics. **Ne pas créer d'autre commit le contenant ni exposer de données supplémentaires.** Créer des fixtures totalement fictives pour les tests versionnés et screenshots. Respecter `AGENTS.md` (« ne publier que des exemples fictifs »). Le fichier fourni reste intact.

Lire aussi, AVANT code :
- `docs/collector-export-v2.md` (contrat exact, preuves et limites).
- `mon_gpt/core.py` (projets `Record(kind="project", parent)`, fiches `item`, `projects: list[str]`, doublons de titres **autorisés**, hiérarchie et attachements multiples).
- `mon_gpt/chatgpt.py` (les URL ChatGPT, `Conversation(record_id, conversation_id, url)`, déduplication par UUID, pas par titre).
- `mon_gpt/storage.py` (catalogue **schéma 3** strict, `encode/decode/Store.save/Store.export`, images personnelles, écriture atomique, verrou mono-instance).
- `mon_gpt/ui.py`, `mon_gpt/details.py`, `mon_gpt/main_menu.py`, `theme.py`, `ui_state.py` (menus Tk, fiches en édition, `can_leave`, transaction, vues et préférences existantes).
- `README.md`, `AGENTS.md` ; rapports MG-006, MG-008b ; tests existants.

**Précision sur les anciennes versions :** David a explicitement refusé toute migration et compatibilité des **anciens exports du Collector v1**. **Cet import lit le v2 uniquement** : aucun chargeur v1, reconstitution de vieux caches ou import de données supprimées. Cela ne remet pas en question la nécessité de préserver **les données déjà présentes dans l'application Mon GPT**.

## 1 — Expérience attendue : importer sans transformer l'opération en casse-tête

Ajouter dans le menu **Fichier**, à côté des deux commandes existantes mais **distinctement** :
**« Importer depuis Mon GPT Collector (JSON)… »**

Parcours attendu :

1. **Choisir** le JSON avec le sélecteur Windows, sans le confondre avec **Restaurer le catalogue** (restauration = remplacement ; import = ajout/raccordement).
2. **Analyser sans rien modifier** : lecture/validation, déduplication par identité, détection des noms multiples et des projets locaux correspondants. Afficher un aperçu intelligible.
3. **Choisir les correspondances des projets** (voir §2). Un conflit ne doit jamais entraîner une fusion tacite.
4. **Prévisualiser** combien de projets seront créés, réutilisés, fusionnés via correspondance ou ignorés ; combien de fils nouveaux/existants/rejetés/à classer et leurs destinations. La liste peut être longue : panneau scrollable, recherche/filtre et détail des anomalies ; conserver les choix quand on revient à une étape précédente.
5. **Confirmer**, puis enregistrer en une opération cohérente et afficher un bilan : « X projets créés, Y projets réutilisés, Z fils créés, W déjà présents, N à classer », plus erreurs éventuelles. La fermeture ou Annuler avant confirmation ne change rien.

**Les premières correspondances sans conflit doivent être proposées intelligemment.** Sur un catalogue vierge, le scénario nominal est : créer **58 projets portant exactement les noms observés** (y compris les projets encore sans fils) et **115 fiches**, dont 56 rattachées, les autres simplement « À classer ». L'option de ne pas importer les projets sans fils est facultative, mais si elle existe, le choix et le résultat doivent être explicites ; **par défaut conserver tous les projets** du JSON.

Sur un catalogue déjà rempli, ne pas mélanger des projets parce qu'ils s'appellent pareil ; aucun rapprochement d'une fiche par titre identique. Ne pas modifier l'organisation native de ChatGPT, ni ouvrir automatiquement ses liens.

## 2 — Identité d'abord : projets homonymes, existants et fusions choisies

**Le GUID externe `g-p-...` identifie un projet ChatGPT ; le nom n'est qu'un libellé.**

Pour chaque projet importé, permettre ces actions :
- **Créer un nouveau projet local**, portant exactement `observedName` (ou un titre local saisi si nom `null`), même si ce nom existe déjà. Deux projets locaux peuvent porter le même nom.
- **Associer à un projet local existant**, choisi explicitement. La sélection doit utiliser un **identifiant interne stable**, afficher chemin complet et, si besoin, suffixe de GUID pour désambiguïser.
- **Fusionner les rattachements de plusieurs projets ChatGPT dans un même projet local**, sur une **décision explicite**, sans jamais modifier ou supprimer les projets distants et sans effacer aucun dossier local existant.
- **Ignorer ce projet à cet import** ; ses fils concernés restent « À classer » s'ils n'ont aucune autre destination.

**Exemple de collision à traiter dans le vrai fichier :**
- `M2` (GUID source A), `M2` (GUID source B) : proposer **deux dossiers locaux distincts** (option sûre par défaut), **un seul dossier local commun** si l'utilisateur le choisit, ou **liaison à des dossiers locaux existants**.
- Même cas avec `Cours M2`, deux GUID indépendants.
- Si un projet local du même nom existe déjà sans lien source connu : **suggérer**, mais exiger validation de la liaison ; ne jamais déduire son identité par nom seul.
- Un GUID déjà connu du catalogue local au prochain import : **réutiliser sa correspondance mémorisée** (sauf si le projet local a disparu, cas à résoudre visiblement).
- Renommage distant après import : garder l'identité GUID et **préserver le nom local personnalisé**, sans recréer un dossier ni le renommer silencieusement.
- Plusieurs GUID sources peuvent être liés au **même** projet local lorsque l'utilisateur a choisi une fusion ; **ne jamais perdre les GUID individuels**. La prochaine collecte doit savoir quelle destination choisir.

**Exigence de persistance :** conserver une table explicite **`projectKey ChatGPT → id du projet local`** ; ne pas utiliser les noms comme clés, et ne pas la mettre dans `Record.metadata` ou dans les champs du **socle générique** (`AGENTS.md`). Cette correspondance appartient à l'**adaptateur ChatGPT / sa couche de persistance** et doit être incluse dans **les sauvegardes/restaurations complètes** et dans la validation atomique de l'état. Choisir une évolution minimale et propre du stockage ; si le catalogue strict impose une évolution de son schéma, documenter précisément ce choix et préserver les catalogues existants. **Éviter un fichier parallèle indépendant qui pourrait être désynchronisé lors d'une panne.**

Le modèle `Catalog` n'a pas besoin d'un « vrai système de GUID métier » nouveau : **les projets et fiches locaux gardent leurs propres UUID internes** ; seuls les adaptateurs connaissent les identités ChatGPT.

## 3 — Règles d'import des conversations

- Normaliser chaque `conversationId` et toutes les `observedUrls` via les règles de `mon_gpt/chatgpt.py:parse_url` ; vérifier l'identité UUID et le domaine. Une URL **observée** est conservée ; ne pas fabriquer de lien ni utiliser de lien d'un autre UUID.
- **Identité unique = UUID de conversation**, indépendamment du titre, des URLs de projet et de l'historique de scans.
- Si **nouvelle**, créer une fiche locale une seule fois, avec **titre observé**, lien et rattachement(s) selon `observedProjectKeys` et les décisions du §2. Le fichier v2 ne contient **ni messages ni résumés** : ne rien inventer et ne pas remplir les notes/tags/catégories avec des suppositions. Couverture/icône/couleur restent les valeurs par défaut ou héritées, sans choix imposé.
- Si **déjà présente**, **ne jamais créer de fiche doublon**. Conserver **sans écrasement** titre local, résumé, notes, tags, catégories, métadonnées, dates, couverture/icône/couleur, projets locaux déjà attachés, ordre et URL locale. Par défaut, la réimportation est **sans effet** sur les fiches existantes ; une option explicite pourrait proposer **d'ajouter** les nouveaux rattachements importés sans retirer les anciens, mais ne doit jamais déplacer silencieusement.
- Si plusieurs clés de projet sont observées pour **un même** UUID, maintenir une **seule fiche**, rattachée aux différentes destinations locales retenues (`Catalog.attach`), sans dupliquer un lien. Si deux clés fusionnent vers un projet local identique, le rattachement reste unique.
- Une conversation dont `observedProjectKeys=[]` est créée **sans rattachement**, visible dans « À classer ». Une clé sans nom/ignorée/non résolue produit un cas visible de classement à traiter, **pas une attribution arbitraire**.
- Les titres homonymes sont permis ; le lien/UUID détermine l'identité. Les titres absents doivent produire un **titre local provisoire explicitement signalé**, jamais une invention prétendue observée ; l'utilisateur pourra le renommer.
- Le `seenCount`, dates d'observation, preuve DOM et clés source ne deviennent pas des catégories, tags ou notes métier. Ne pas incorporer l'export brut comme métadonnées génériques.

**Idempotence obligatoire :** réimporter exactement le même JSON, même après fermeture/relance ou restauration de sauvegarde complète, ne crée **aucun nouveau projet ni fil**, ne modifie aucun champ personnalisé et réutilise toutes les correspondances décidées. Réimporter ultérieurement un export enrichi doit ajouter seulement les nouveaux GUID/UUID.

## 4 — Architecture et fiabilité : séparation claire

- Implémenter la **lecture/validation/planification/application** en fonctions/modules testables **indépendants de Tk**, par exemple un module `mon_gpt/collector_import.py` ou `mon_gpt/chatgpt_import.py` relié à l'adaptateur ; le parseur n'accède pas au DOM ni à Chrome.
- Interface dédiée `mon_gpt/import_ui.py` (ou composant équivalent), **pas une énorme refonte de `ui.py`**. Respecter les tokens visuels `theme.py`, les couleurs ivoire/sapin/terracotta, et les menus/clavier de Mon GPT.
- **Validation stricte du contrat v2** : `source` exact, `schemaVersion=2`, `projects[]`, `conversations[]`, bornes et types, dates UTC valides, clés et noms, `evidence`, UUID, URL, listes de liens et cohérence entre projets et conversations. Refuser un autre format/futur schéma, plutôt que l'interpréter comme une sauvegarde. Accepter seulement les ajouts prévus par le contrat et, pour tout rejet, afficher le motif.
- **Aucune omission silencieuse** : les lignes invalides et les références inconnues sont signalées dans l'aperçu avec **identifiant court, type d'erreur, total et action proposée**. Pour une erreur structurelle du fichier, refuser entièrement **avant** le moindre changement. Pour un rejet individuel explicite, ne permettre l'import partiel que si la sélection de lignes admissibles et le bilan des rejets sont clairs.
- **Pas de mutation pendant l'aperçu** : pas de création de projets, pas de sauvegarde, pas de changement du catalogue tant que l'utilisateur n'a pas confirmé. L'état de prévisualisation ne doit pas polluer les préférences du workspace. Si une fiche a des modifications non enregistrées, utiliser `can_leave()` et respecter Annuler.
- **Transaction complète** : construire l'état candidat sur une **copie** du catalogue et des tables d'adaptateur, valider l'ensemble avec le décodeur strict et les limites de taille, **faire une sauvegarde complète avant import** de l'état local courant (incluant images personnelles), puis écriture atomique de l'état candidat. En cas d'erreur/annulation/limite disque, **aucun import partiel** et état initial récupérable ; conserver la sauvegarde et afficher clairement le résultat. Une opération répétée ne multiplie pas les sauvegardes si elle ne change rien.
- Préserver le verrou mono-instance et les ressources image ; ne pas modifier le Collector Chrome ni ses schémas, ni créer de réseau/synchronisation. Sauvegarde/restauration de Mon GPT doivent inclure **les mappings GUID→projet local**.
- **Prévenir les rendus obsolètes** après commit : rafraîchir arborescence, compteurs et vues Liste / Détaillée / Mosaïque ; sélectionner éventuellement un projet nouvellement importé sans ouvrir de conversation. Garder un état d'interface raisonnable si déjà filtrée.

**Borne réaliste :** sur un catalogue qui contient déjà beaucoup de fiches, il peut y avoir jusqu'à 5 000 conversations et 1 000 projets sources (limites du Collector) : l'analyse et le rendu doivent rester réactifs, avec listes paginées/virtuelles ou scroll maîtrisé, et ne pas figer longtemps le thread Tk pendant parsing/planification. Ne pas utiliser d'opérations Tk depuis un thread secondaire.

## 5 — UX : aperçu lisible, homonymes résolus sans travail répétitif

Un assistant d'import **dans la fenêtre** ou une boîte dédiée cohérente (pas de nouvelle application, pas de popup Chrome). Pour la première version :
- En-tête : **projets nommés, homonymes, fiches nouvelles/existantes, sans projet, rejets** ; distinguer les projets du catalogue et ceux de l'export.
- Proposer **par défaut une opération globale « Créer séparément les projets sans correspondance »**, avec **décision visible et explicite** pour chaque groupe homonyme et chaque collision avec un dossier local. Éviter 58 confirmations répétées.
- Tableau **Projets** : nom complet, GUID abrégé (survol/détail = intégral), nombre de fils observés, décision, destination locale. Deux homonymes sont deux lignes, jamais une seule. Permettre de gérer les paires M2 / Cours M2 **sans ambiguïté**.
- Tableau/aperçu **Discussions** : titre, GUID abrégé, projet(s) source et destination(s), nouveau/déjà présent/à classer/rejet, recherche pour retrouver un fil.
- Options concrètes : **Créer séparément / Fusionner vers un dossier choisi / Associer un existant / Ignorer**, et possibilité de modifier la décision avant confirmation ; aperçu du classement résultant pour les cas ambigus.
- Contrôles clavier, Tab/Espace/Entrée/Échap, texte complet au survol/accessible, compteur de progression et confirmation. **Annuler** réversible. Ne pas casser l'ergonomie validée de MG-002b.
- Après import, l'utilisateur peut renommer, réorganiser, créer des sous-projets, ajouter tags, catégories et commentaires avec les fonctions existantes : **pas de nouveaux éditeurs de catégories ou de tags dans MG-009**.

Écran fictif attendu en recette : deux sources « Développement » portant **deux GUID différents** : choix séparés ou fusion, bilan différent, mais **toujours deux mappings source**. Même principe pour les homonymes réels, sans publier leurs valeurs.

## 6 — Recettes et livrables : la boucle complète est à vérifier

**Tests automatisés nouveaux**, tout en conservant les **121 tests Python déjà verts** et **43 tests JavaScript du collecteur** (ce dernier n'est pas à modifier) :
1. Lecture du vrai contrat export v2 sur **fixtures fictives** : noms, clés, preuves et dates cohérents, URL de projet, titre vide, caractères spéciaux, entrées supplémentaires interdites.
2. Enveloppe absente/future/v1/malformée, taille limite, faux domaine, UUID invalide, clé d'un autre projet, doublon conflictuel, titre long : erreurs lisibles et **zéro mutation**.
3. **2 projets homonymes** de clés distinctes ; séparés par défaut, fusion explicite ou liaison à projets locaux existants. Projet local portant le même nom ne suffit jamais à établir la liaison.
4. Source sans nom, projet sans conversations, discussion sans projet, discussion ayant deux projets, source ignorée, identités locales UUID distinctes des GUID source, renommage local puis réimport.
5. Préservation stricte des champs locaux d'un fil et de son icône/couverture ; nouvelles conversations créées avec valeurs par défaut ; pas d'écrasement des URL.
6. **Idempotence** (2 imports, redémarrage, ajout de 3 nouveaux fils, mêmes mappings), sauvegarde/restauration puis troisième import, pas de doublons.
7. Backup avant écriture, erreur de sauvegarde, panne d'écriture atomique, limite de taille, annulation et cas d'image personnelle : aucun état partiellement modifié, sauvegarde complète relisible.
8. Vérification clavier et apparence de l'aperçu, notamment une quantité proche de 115 fils / 58 projets ; données fictives.

**Recette Windows réelle sur CODEX-VM, jamais sur le catalogue personnel :**
- Démarrer `python -m mon_gpt --data-dir <dossier temporaire de recette> --simulate-open` ; `LOCALAPPDATA\MonGPT` réel ne doit pas être employé.
- **Importer le fichier réel `missions/MG-009-imports/mon-gpt-observations.json` dans cet espace vide**. Faire le contrôle **sans recopier les titres/noms/URL dans les rapports**. Avec choix de création séparée : 58 projets, 115 fils, 56 rattachés, reste « À classer », homonymes séparés. Si le résultat exact diffère, expliquer la cause, ne pas corriger arbitrairement des données.
- Relancer l'application et réimporter **le même fichier** : **0 nouveau fil et 0 nouveau projet**, mapping et classement intacts.
- Ajouter un scénario fictif avec projets/fils locaux déjà personnalisés ; choisir association puis fusion, annuler, recommencer, vérifier les notes/tags/catégories/couvertures et l'état du catalogue.
- Naviguer dans **Liste, Détaillée, Mosaïque**, ouvrir (en simulation), recherche, sous-projet, filtres, puis sauvegarder/restaurer et confirmer la stabilité.
- **Captures natives 4 à 6 uniquement sur des données fictives** : accueil de l'import, résolution de deux homonymes, aperçu des discussions classées, bilan, liste/arbre résultants. Ne pas publier de capture du vrai jeu de données.

**Livrer :**
- code Python et interface intégrés ; documentation française `docs/MG-009-import.md` (séparer import vs restauration, fonctionnement, homonymes, reimport, et structure des mappings);
- `reports/MG-009/rapport.md` avec nombre de tests, synthèse de recette réelle **statistique seulement**, bilan d'idempotence, preuves de persistance/restauration, limites et liens captures ;
- documenter toute évolution nécessaire du **format de catalogue** (distinct du format export Collector v2) et validation des sauvegardes.
- mise à jour de `README.md` et version application appropriée ;
- commit/push sur **`ugadavid/Mon-GPT` `main`**, état propre, SHA distant vérifié. Ne jamais ajouter de profils Chrome, `node_modules`, exports personnels supplémentaires, catalogues de recette ou fichiers de sauvegarde personnels au dépôt.

**STOP après MG-009 pour recette David/GPT ; ne pas développer de synchronisation automatique ou extension supplémentaire.**

### Critère GO

La même opération permet d'importer un export Collector v2 dans **Mon GPT<3**, **créer les projets et classer les fils en une seule confirmation**, préserver les homonymes tant que l'utilisateur ne les fusionne pas, mémoriser les GUID sources, **ne rien dédoubler au second import**, garder toutes les personnalisations locales et fournir une sauvegarde/restauration complète de cet état.
