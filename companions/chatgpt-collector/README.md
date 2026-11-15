# Mon GPT Collector — 0.8.2

Extension Chrome MV3 locale : conserver les discussions observées, identifier les projets **par clé**, observer leurs noms quand une preuve DOM le permet, exporter le tout. Deux projets « Développement » restent distincts si leurs clés diffèrent. Aucun import dans Mon GPT : MG-009 sera une mission séparée.

## Installer ou mettre à jour : charger la distribution propre

Depuis PowerShell, à la racine du dépôt :

```powershell
cd C:\Users\codex\Documents\Projets\mon-gpt
python tools/package_collector.py
```

Ce script Python standard, sans paquet à installer, produit **16 fichiers exécutables seulement** et un ZIP compact dans `dist/`. Aucun `node_modules`, test, profil Chrome, export, cache ou outil de développement dans ce dossier. Ne pas charger le dossier source `companions` pour cette livraison.

1. Ouvrir `chrome://extensions`, activer **Mode développeur**.
2. Pour une nouvelle installation, choisir **Charger l’extension non empaquetée** et sélectionner :

   ```text
   C:\Users\codex\Documents\Projets\mon-gpt\dist\Mon-GPT-Collector-0.8.2
   ```

3. **Mise à jour d’une 0.8.1 déjà chargée : conserver son dossier et son identifiant Chrome.** Décompresser le ZIP 0.8.2 dans **ce même dossier**, en remplaçant les 16 fichiers exécutables, puis utiliser **Actualiser** sur sa carte Chrome. Le nom du dossier peut rester `Mon-GPT-Collector-0.8.1` ; la carte doit afficher **0.8.2**. Ne pas désinstaller pour cette correction : le stockage v2 existant doit rester en place. Ne pas charger en parallèle une seconde copie depuis un autre chemin.
4. Actualiser les onglets ChatGPT déjà ouverts, puis ouvrir **Mon GPT Collector** depuis le menu Extensions. L’épingler est facultatif.

Le ZIP `dist/Mon-GPT-Collector-0.8.2.zip` contient la même distribution à décompresser avant chargement. Le script refuse un dossier de sortie pollué par des fichiers inattendus et ne supprime aucun dossier existant.

**Départ vierge décidé pour MG-008a.** Stockage neuf `monGptCollectorStateV2`, export **schemaVersion 2 exclusivement**. Aucun lecteur v1, migration, récupération ou sauvegarde d’anciens caches. Une ancienne clé éventuellement présente n’est ni lue ni convertie. L’application Windows demeure en 0.8.0 et n’est pas modifiée par cette mission.

**MG-008b conserve ce stockage v2.** La correction réobserve les clés existantes et enrichit leurs noms à partir du DOM natif ; aucun nouveau schéma ni vidage automatique.

## Modes et gestes

| Mode | Automatique | Scanner cette page |
| --- | --- | --- |
| **Manuel** | Aucun scan, observateur ou timer de collecte | Discussions et projets déjà rendus, plus l’URL courante valide |
| **Auto cible**, initial | Discussion courante et son projet si identifiable, ou accueil du projet ouvert ; pas les autres projets | Même scan explicite complet |
| **Auto large** | Discussions et projets déjà rendus dans la navigation, changements utiles du DOM et de route | Même scan explicite complet |

L’extension ne clique, n’ouvre, ne déroule et ne scrolle jamais ChatGPT. Les sections repliées, liens virtualisés et données non chargées ne peuvent pas être devinés. Parcourir ses projets **manuellement** enrichit les relevés suivants. Les modes persistent ; une désactivation suspend la collecte et conserve les observations. Après réactivation, actualiser l’onglet ChatGPT. Exporter avant une désinstallation, qui peut supprimer le stockage.

Le compteur principal mesure les discussions conservées dans **l’extension**, pas celles importées dans Mon GPT. **Projets identifiés** indique le total, les noms connus et les noms inconnus. La petite liste conserve deux homonymes sur deux lignes, avec des clés abrégées distinctes et leur valeur complète au survol. Faire défiler les projets pour voir les autres ; les 50 premiers sont affichés, tous sont exportés. Les discussions récentes gardent titre, date et état au dernier relevé.

**Copier les URLs / TXT** : une URL représentative réellement observée par discussion, par ligne. **Exporter JSON** : projets **et** conversations, y compris les projets sans nom. Le JSON reste disponible si seuls des projets sont connus ; copie et TXT demandent au moins une discussion. **Vider** demande confirmation, Échap annule ; seul le stockage v2 de ce collecteur est vidé, le mode reste mémorisé. Sur un autre site, scan désactivé et exports conservés. Tab, Maj+Tab, Entrée, Espace et les flèches des radios restent natifs, avec focus visible.

## Ce qui prouve un nom

- **Contrôle natif réellement observé en session connectée :** `div[role="button"][data-app-action-sidebar-project-row]`, clé dans `data-app-action-sidebar-project-id`, nom dans `data-app-action-sidebar-project-label`. Le propriétaire `data-sidebar-project-kind="local"` / `data-sidebar-project-container-id="project:CLÉ"` doit concorder, ainsi que le titre propre visible référencé par `aria-labelledby` (ou son emplacement sémantique de titre). Aucune classe générée. Les enfants visibles, s’ils existent, ne doivent pas contredire la clé. Le même contrôle replié peut donc fournir son nom sans ouvrir ses fils.
- Lien d’accueil `/g/g-p-…[/project]` avec son propre nom, ou contrôle portant explicitement `data-project-id` / `data-project-key`.
- Accueil projet réellement ouvert : URL stricte portant la clé, un seul `h1` visible dans le contenu principal, **uniquement en absence de contrôle natif identifié pour cette clé**. Un H1 générique ne tranche jamais un nom natif absent ou contradictoire. Jamais le H1 d’une conversation.
- Groupe développé : treeitem propriétaire, liens contenus dans le bouton du projet ou relation réciproque `aria-controls` / `aria-labelledby`. Les enfants utilisables doivent tous porter la même clé ; aucune section/sous-projet concurrente. Cette preuve est de niveau inférieur aux preuves directes.

Pas d’association par ordre, voisinage, titre de discussion, nom identique ou clé ressemblante. Les titres de boutons d’action ne deviennent pas des noms de projet ; aucun préfixe d’action n’est supprimé approximativement. En cas de conflit de même niveau, aucun nom nouveau n’est choisi. Un relevé plus faible ou sans nom n’efface pas une preuve plus fiable. Un renommage fiable de même niveau actualise la même clé. Si seul le groupe change après une ancienne preuve directe, ouvrir manuellement l’accueil projet permet de relever à nouveau une preuve directe.

**Nom non observé** et **Titre non observé** sont des libellés UI ; le JSON contient `null`. L’[audit du vrai DOM connecté](../../reports/MG-008b/audit-dom-reel-anonymise.md) explique la cause prouvée de l’échec 0.8.1. Le [rapport MG-008b](../../reports/MG-008b/rapport.md) distingue cet audit réel, les tests sur sa reproduction anonymisée et la vérification de l’export corrigé dans la session connectée.

## Recette courte sur le Chrome connecté de David

1. Mettre à jour **dans le même dossier** vers **0.8.2**, actualiser ChatGPT, choisir **Manuel**. **Ne pas vider** le stockage v2 pour une mise à jour ; les clés déjà collectées vont s’enrichir. Garder toute autre copie du collecteur désactivée.
2. Repérer 2–3 projets. Si possible, choisir deux homonymes existants ; relever leur **clé dans les liens**, pas seulement leur nom. Ouvrir et replier leurs sections soi-même, puis **Scanner cette page**. Vérifier noms, nombres et clés complètes au survol.
3. Si un nom reste inconnu, ouvrir soi-même **l’accueil de ce projet**, sans ouvrir une conversation ; scanner. Vérifier que le nom obtenu correspond exactement à cette clé. Un nom non prouvé doit rester inconnu, plutôt que celui d’un fil voisin.
4. Exporter JSON. Vérifier `schemaVersion: 2`, deux entrées `projects` distinctes pour les deux homonymes, noms exacts et `evidence`. Vérifier les `observedProjectKeys` de quelques conversations ; une conversation reste unique même sous plusieurs URL.
5. Si un projet de recette est renommé manuellement, revoir son accueil et scanner : même clé, nouveau nom, pas de doublon. Tester ensuite Auto cible puis Auto large, uniquement sur les sections rendues. Ne rien modifier dans un projet réel juste pour la recette.

**Preuve attendue :** la même clé constatée dans l’URL/attribut et dans l’export, le vrai libellé du contrôle/titre, le type de preuve, des clés distinctes malgré un nom identique. Pour un échec, noter le type de page, le mode et le seul contrôle/groupe concerné (attributs sémantiques), sans messages, tokens ou dump global de la page. Aucun export personnel ne doit être commité dans ce dépôt.

Un diagnostic de développement strictement en mémoire est généré par `node tests/build-connected-probe.cjs`. Il produit `.recette/connected-probe-readonly.js` sans données personnelles intégrées. Après lecture du code et uniquement si la console Chrome accepte son collage, l’exécuter dans l’onglet connecté : il compare deux titres natifs, les observations de production et le JSON v2 sérialisé/relu en mémoire, et retourne seulement des alias et booléens. Il compare aussi le scanner 0.8.1 issu du commit de référence ; ce n’est ni un lecteur d’ancien export ni un chemin de compatibilité. Aucun DOM, stockage ou réseau écrit, aucun export personnel sur disque. **Ne pas contourner une protection Chrome de collage ; elle doit être traitée par l’utilisateur.** Un résultat sur fixture ne prouve pas la recette connectée.

## Données et permissions

Seule permission **storage**, scripts uniquement sur `https://chatgpt.com/*`, cadre principal. Aucun cookie, token, message, formulaire, API privée, ressource React, historique global, `<all_urls>`, serveur, overlay ou appel réseau supplémentaire. Le DOM ChatGPT est lu, jamais modifié. Les noms/titres sont affichés avec `textContent`. `tabs.query` utilise seulement l’ID de l’onglet actif ; aucune permission `tabs` ou `management` dans l’extension.

Limites : **5 000 conversations, 1 000 projets, 6 Mio cumulés**, 10 URL/contextes par discussion, titre 512 caractères, nom 256, clé 128, URL 2 048. Les noms trop longs/ambigus ne sont pas tronqués en faux noms. Un dépassement ou échec de stockage refuse le lot entier, sans éviction silencieuse. L’attente en mémoire de l’onglet conserve discussions et projets ; elle est perdue si cet onglet est fermé/actualisé avant enregistrement. Stockage local et exports ne sont pas chiffrés par l’extension.

Le [contrat v2](../../docs/collector-export-v2.md) détaille les champs, preuves et protections prévues pour MG-009. Les anciens contrats ne sont pas pris en charge.

## Développer et vérifier

Le socle MG-008 est conservé : `core/observations.js` pur, conteneurs nommés génériques indexés par identité ; `adapters/chatgpt.js` pour URL/DOM/projection ; dépôt injecté à écrivain unique ; runtime générique avec lots atomiques ; popup et présentation commune. Pas de second collecteur ou de système de plugins. Le réemploi historique de MJ Collector et 3GPT3 reste documenté dans [MG-008](../../reports/MG-008/rapport.md).

Node 24 et Python à la racine du dépôt :

```powershell
cd C:\Users\codex\Documents\Projets\mon-gpt\companions\chatgpt-collector
npm test
```

Tests purs avec `node:test`, sans installation de paquet. Pour la recette Chrome automatisée, uniquement côté développement : `npm ci`, puis `npm run test:chrome`. `puppeteer-core` est une dépendance de développement figée, sans téléchargement de navigateur. Chrome installé à `C:/Program Files/Google/Chrome/Application/chrome.exe` par défaut (`CHROME_PATH` permet un autre chemin). Le banc charge **le dossier distribué**, un profil jetable `.recette/` et des fixtures fictives avec le manifest inchangé. Aucun profil personnel utilisé. Le chargement CDP est réappliqué explicitement après redémarrage pour vérifier le stockage ; ce n’est pas une recette de l’installation permanente manuelle.

`node tests/chrome-recipe.cjs --hold` prépare les deux arrêts pour captures Windows natives sur la fixture réduite du DOM observé. Ne pas lancer la recette Chrome en parallèle des tests Tk utilisant le focus. [Rapport, journaux et captures non personnelles](../../reports/MG-008b/rapport.md).
