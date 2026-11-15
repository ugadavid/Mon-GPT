# MG-008b — Audit du VRAI DOM ChatGPT connecté et correction de l'association GUID ↔ nom de projet

**Statut : mission Codex à exécuter sur CODEX-VM, puis validation utilisateur.**  
**Base :** Mon GPT Collector **0.8.1**, dernier commit livré `5c099d0acf3d9c8c1a695d2e3c71b8373a748fc0`.  
**Contexte décisif NOUVEAU :** David a **ouvert Chrome sur CODEX-VM et s'est connecté à son compte ChatGPT**. Il autorise expressément l'observation en lecture seule du DOM **de cette session authentifiée** pour corriger notre collecteur. **Ne plus étudier exclusivement des fixtures fictives !**

## 0. Le problème, observé sur données réelles

MG-008a (0.8.1) a livré 35 tests JS + 121 tests Python et fonctionne sur fixtures. David a testé dans Chrome connecté, parcouru des projets et exporté plusieurs JSON **schemaVersion 2** :
- Les fils, UUID, titres, URL, et clés `g-p-...` sont collectés et accumulés correctement.
- Dernier export réel examiné : **15 projets** dont **0 nom récupéré** (`observedName: null`, `evidence.kind: "key-only"`) ; les conversations rattachées à ces clés sont conservées.
- Même en ouvrant des projets, les noms sont restés absents. Il y a donc une **incompatibilité réelle entre nos hypothèses de structure DOM et la page authentifiée**.

**Hypothèse de travail, non vérité :** les contrôles portant les libellés peuvent être séparés des liens portant les GUID ; l'encadrement par `aria-controls`, treeitems, ou attributs `data-project-*` envisagé ne correspond pas à cette version de la sidebar. D'autres causes existent, notamment notre fonction `projectName` trop stricte ou un sélecteur non pertinent. **Déterminer la vraie cause à partir du DOM réel avant de coder.**

## 1. PRIORITÉ ABSOLUE : observer le Chrome déjà connecté sur CODEX-VM

**Ce n'est pas une demande de créer un profil de test.** David a préparé une vraie session ChatGPT dans Chrome sur **CODEX-VM**.

1. Rejoindre **le navigateur Chrome de CODEX-VM déjà authentifié**, en utilisant l'outillage de navigation/inspection permis dans la session Codex (Computer Use, DevTools DOM, console en lecture seule, accès browser autorisé, etc.). **Ne pas lancer par défaut un nouveau profil Chrome jetable non connecté.**
2. Vérifier visuellement que `https://chatgpt.com/` est **connecté** et que **la barre latérale expose des projets réels** ; ne pas effectuer d'action durable sur le compte.
3. Examiner **2 ou 3 projets de la barre latérale**, idéalement un ouvert et un replié, et **une page d'accueil de projet**. Si possible examiner deux projets de même nom, mais ne pas imposer de création ou renommage d'un projet sur le vrai compte.
4. Relever pour **chaque cas** des faits DOM concrets :
   - type de contrôle (lien, bouton, wrapper, section) portant le **nom affiché** ;
   - texte propre, `aria-label`, attributs `role`, `href`, `data-*` sémantiques et `aria-expanded` pertinents ;
   - **chemin exact qui établit le GUID `g-p-...`** : URL de projet, attribut sur le contrôle, lien conversation enfant, parent de structure vérifiable, relation `aria-*`, etc. ;
   - rapport DOM réel entre le contrôle nommé et les conversations liées : ancêtres communs, enchaînement dans un bloc projet, frontière claire entre projets voisins et la section des conversations globales ;
   - comportement lors d'un repli/dépli **manuel** du projet et à l'accueil projet ;
   - pourquoi `scanProjects` retourne `key-only` avec la structure réelle.
5. **Livrer une preuve technique anonyme** : mini-extrait DOM **réduit aux éléments nécessaires** avec noms et GUID remplacés par `Projet A`, `g-p-AAAA`, etc., et le raisonnement précis permettant de relier une clé et un nom. Le vrai DOM est utilisé **en observation** ; les fixtures ne servent qu'ensuite, pour tester la correction.

**Prudence sur les données personnelles :** observer uniquement la navigation projet (contrôles de navigation et href/titres utiles) ; **ne jamais inspecter, copier, capturer ou transmettre le contenu des conversations, prompts, réponses, formulaires, cookies, tokens, données de compte, localStorage de ChatGPT, requêtes internes ou profils Chrome**. Ne pas faire de dump complet du DOM. Aucun export de conversations/projets réels, capture portant des noms personnels ou journal nominatif dans le dépôt GitHub public. Les preuves publiées sont anonymisées ; les captures natives du rapport peuvent utiliser des **fixtures** uniquement pour la démonstration visuelle, mais **pas comme substitut à la preuve d'inspection réelle**.

**Actions dans ChatGPT autorisées pour cette mission :** navigation **réversible en lecture seule** vers la page d'accueil d'un projet, dérouler/replier manuellement des projets pour inspection et revenir à l'état initial autant que possible. **INTERDIT :** renommer, déplacer, créer, supprimer, archiver, partager, publier, envoyer des messages ou modifier le compte. Ne pas manipuler l'authentification, cookies ou raccourcis de profils.

**Si Codex ne peut pas atteindre la fenêtre authentifiée préparée par David :** relever le blocage concret, essayer les accès à l'interface autorisés et disponibles, **ne pas simuler une réussite par un nouveau profil non connecté**, ne pas demander d'identifiants ; rendre une **mission PARTIELLE** avec diagnostic d'accès. Ne pas développer une autre théorie DOM à l'aveugle.

## 2. Audit du code existant à confronter aux preuves

Étudier `companions/chatgpt-collector/adapters/chatgpt.js` et principalement :
- `ROOTS`, `roots`, `visible` ;
- `projectName` (ligne de défense contre les labels d'action, extraction du texte, rejet de certains préfixes français/anglais) ;
- `scanProjects`, blocs `direct-link`, `direct-control`, `expanded-group`, `project-page` ;
- le calcul de conflit de plusieurs noms, le choix de la meilleure preuve ;
- déclenchement des scans via `runtime.js`, changements SPA et mutations DOM ;
- `core/observations.js`, le stockage v2, et `exportJson`.

**Faire d'abord un diagnostic passif :** exécuter l'extraction réelle sur une vue inspectée et relever quels contrôles existent/échouent, quelle condition exacte élimine le bon nom. Un petit script de diagnostic en console **strictement lecture seule** peut être utilisé, sans injection d'UI et sans conserver des données personnelles. Documenter le résultat **anonymisé**.

## 3. Corriger uniquement la reconnaissance des projets

Après l'audit réel :

- Adapter les sélecteurs et la structure de parcours **à ce que le vrai DOM prouve**, en privilégiant `href`, attributs sémantiques, rôles, relations explicites ou un **bloc de projet aux frontières contrôlables**. Éviter les classes CSS générées et les indices positionnels fragiles.
- Si le **nom** est sur un bouton distinct du **GUID** qui apparaît dans les liens des fils, autoriser un rapprochement uniquement si **un bloc ou ancêtre propriétaire clairement délimité contient ce nom et exclusivement les liens du même projet**, avec tests de non-contamination par les blocs voisins. Une association par simple `previousSibling`/« le dernier nom vu » n'est pas acceptée sans preuve robuste de frontières.
- **Deux GUID portant le même nom doivent rester deux entrées.** Un même GUID renommé reste la même entrée. Un GUID sans nom vérifiable reste `observedName: null`.
- Récupérer les noms avec accents et ponctuation ; distinguer le nom propre de libellés d'action localisés comme « Couleur personnalisée », « Ouvrir… », « Options… » **sans les confondre ou les tronquer silencieusement**. Tester aussi les projets portant un mot générique, si prouvé par une source directe.
- Ne jamais déduire les noms d'un titre de fil ou du seul GUID. Ne jamais attribuer à un projet le nom d'un voisin.
- Garder **tous les comportements MG-008a** : collecte des conversations, les 3 modes, dédoublonnage UUID, stockage local, worker écrivain unique, limites, gestion d'erreurs, copie/exports, UI popup, tests.
- **Conserver le format JSON v2** si possible (il contient déjà `projects[].projectKey`, `observedName`, `evidence`). Ne créer **aucun nouveau format, aucune migration, aucune compatibilité v1** sans nécessité vérifiée : les seules corrections attendues concernent la reconnaissance. Il n'y a **toujours aucun import MG-009**.
- Pas d'overlay ni intervention sur ChatGPT. Permission Chrome toujours limitée au besoin exact.

## 4. Tests synthétiques APRÈS preuve réelle et recette VRAIMENT connectée

Construire ensuite une ou plusieurs **fixtures minimales reproduisant fidèlement la structure DOM réellement observée** (mais avec noms/UUID fictifs). Ajouter des tests de non-régression :
- une paire réelle de type nom ↔ GUID reconnue selon ce DOM ;
- projet replié/déplié ; accueil projet ; changement SPA ;
- deux projets de même nom, GUID différents ;
- deux noms voisins dans sidebar, projets différents (pas de croisement) ;
- ambiguïté, clé manquante, bloc mixte, nom absent → `null`, pas d'association hasardeuse ;
- stabilité des 3 modes et de l'export v2 ; absence de régression des tests existants.

**CRITÈRE D'ACCEPTATION NON NÉGOCIABLE :** Codex doit **tester la version corrigée dans Chrome réellement connecté à ChatGPT sur CODEX-VM**, en vérifiant au moins **2 noms exacts** reliés chacun au **bon GUID** dans l'export v2. Confirmer que des discussions observées sous ces clés sont bien rattachées et qu'aucun homonyme n'est fusionné par nom. Comparer DOM réel ↔ observations du collecteur ↔ export, sans publier les valeurs personnelles.

**Une recette Chrome sur fixtures seules peut être utile mais ne valide plus MG-008b.** Si la recette réelle est techniquement impossible : statut **PARTIEL** explicitement, preuve de ce qui a été testé et diagnostic du blocage ; ne pas déclarer GO.

## 5. Livraison et discipline

- Version de correction suggérée **Collector 0.8.2**, sans changer le schéma v2.
- Modifier seulement le collecteur, sa documentation, les tests et l'outil de packaging si nécessaire. **Ne pas modifier Mon GPT Python**, ni `Iconotheque`, ni `3GPT3`.
- Script existant `python tools/package_collector.py` : générer la **distribution propre** `dist/Mon-GPT-Collector-0.8.2` et un ZIP compact, sans `node_modules`, profil Chrome, captures personnelles ou exports utilisateurs. Le script doit rester fonctionnel et tester sa liste blanche.
- `reports/MG-008b/audit-dom-reel-anonymise.md` : preuves limitées, datées, détaillant l'écart entre hypothèses MG-008a et DOM authentifié réel ; préciser explicitement que le DOM a été réellement examiné (ou décrire l'impossibilité).
- `reports/MG-008b/rapport.md` : cause racine prouvée, stratégie de réparation, sélecteurs/relations, tests JS et Python, résultat réel au minimum 2 noms/2 GUID, absence de fuite de données privées, limites, procédure reproductible, preuves/captures non sensibles.
- Captures GUI possibles **sur fixture uniquement** ou cadrage complètement anonymisé ; **aucun screenshot nominatif du Chrome personnel publié**.
- Commit/push dans `ugadavid/Mon-GPT` sur `main`, SHA distant vérifié, dépôt propre.
- Arrêt après MG-008b pour contrôle David/GPT. Pas de MG-009, pas de fusion/import de projets, pas de création de dossiers Mon GPT.

**GO :** au moins deux vrais projets différents correctement identifiés **nom + GUID** sur le Chrome authentifié de CODEX-VM, procédure de preuve sûre, fonctionnalités MG-008a intactes. **PARTIEL sinon, sans enjoliver.**
