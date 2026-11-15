# MG-008 — Collecteur Chrome modulaire, réutilisant MJ Collector et 3GPT3

**Statut : mission à exécuter, puis recette utilisateur.**  
**Base :** Mon GPT<3 **v0.7.0**, `origin/main` après MG-007 (**121 tests réussis**).  
**Résultat visé :** une extension Chrome Manifest V3, autonome, jolie, locale, qui **observe et collecte les conversations ChatGPT visibles**, les dédoublonne et les exporte pour un import futur. **MG-009**, distincte, traitera l'import dans l'application Windows.

## 0 — LES DEUX SOURCES EXACTES SONT MAINTENANT SUR GITHUB

### Source A : notre MJ Collector v0.3.0, source du moteur de collecte
`https://github.com/ugadavid/Iconotheque/tree/main/companions/mj-collector`

Lire au minimum :
- `manifest.json`, `content-script.js`
- `popup.html`, `popup.css`, `popup.js`
- `README.md`, `REPORT_C001.md`, `REPORT_C002.md`, `REPORT_C003.md`

Cette extension opérationnelle apporte : `chrome.storage.local`, clé indexée par UUID, fusion/horodatage/compteur, `MutationObserver`, économies d'écritures par debounce, modes `manual / targeted / broad`, scan à la demande, copie, exports TXT/JSON, vidage et popup. **Réutiliser les mécanismes, ne pas reproduire tout le code de mémoire !** L'utilisateur a déjà fait fonctionner cette extension sur Chrome et montre une collecte de milliers de jobs.

### Source B : 3GPT3 v0.1.0, source de l'adaptateur DOM ChatGPT
`https://github.com/ugadavid/3GPT3` — **dépôt désormais publié et réellement accessible**, pas seulement dossier local.

Lire au minimum :
- `src/scanner/dom-scanner.js`
- `src/model/sidebar-view-model.js`
- `tests/scanner/dom-scanner-static-html.test.js`
- `docs/008-visible-conversations.md`, `docs/012-scanner-static-html-test.md`, `docs/dom-analysis.md`
- `ARCHITECTURE.md`, `SAFETY.md`

Le scanner a déjà reconnu les liens `a[data-sidebar-item][href*="/c/"]` dans la barre latérale, extrait le `conversationId`, `href`, `title`, `isActive`, `projectId` et des rectangles pour l'overlay, et possède un test HTML statique. **Réutiliser la logique d'extraction des discussions, PAS l'overlay expérimental 3GPT3**, ni le positionnement et les mesures de rectangles inutiles à la collecte.

Les sélecteurs de 3GPT3 datent de juin 2026 et peuvent avoir changé : les traiter comme **une base vérifiable**, pas comme vérité actuelle. Prioriser les vrais liens `href` et les identifiants UUID, puis des sélecteurs DOM robustes avec fallbacks. Tester sur Chrome réel, sans chercher des classes CSS éphémères.

### Source cible
`https://github.com/ugadavid/Mon-GPT` — moteur local strict `mon_gpt/chatgpt.py:parse_url` : domaines `chatgpt.com`, chemins `/c/UUID` ou `/g/SLUG/c/UUID` ; déduplication **par UUID de conversation**, jamais par titre.

**Les trois dépôts sont maintenant accessibles !** Codex peut les consulter ou les cloner **sur CODEX-VM**, sans solliciter de copie manuelle. **Ne pas modifier Iconotheque ni 3GPT3** ; mettre les fichiers de la nouvelle extension **uniquement dans Mon-GPT**.

## 1 — Principe : une extension ChatGPT aujourd'hui, un socle réutilisable demain

Ajouter l'extension sous un dossier explicite, par exemple `companions/chatgpt-collector/`, installable par **`chrome://extensions → Charger l'extension non empaquetée`**.

La rendre **modulaire, mais sans usine à gaz** :
- **`core` indépendant du site et de Chrome** : validation/normalisation de l'observation, gestion d'identité, déduplication/fusion, dates, limites, format d'export ; fonctions pures testables avec Node ;
- **`adapters/chatgpt`** : lecture des liens/titres actuellement visibles dans le DOM ChatGPT, normalisation des chemins et contexte de projet observé ; **aucun stockage et aucune présentation** dans cette couche ;
- **`browser` ou bridge Chrome** : modes, `chrome.storage.local`, communication popup ↔ content script, observation des mutations, throttling/debounce, téléchargement local des exports ;
- **`ui`** : popup, styles, affichage et commandes ; **aucune regex DOM et aucune logique métier du catalogue** dans la présentation ;
- **contrat d'observation/export versionné** et tests à base de données fictives.

L'objectif est de pouvoir plus tard créer un autre adaptateur (Midjourney, autre site autorisé) **en réutilisant le cœur, le pont de stockage et le composant de présentation**, sans cloner toute la popup ni modifier la fusion des observations. **Démontrer cette modularité avec un test de l'API pure sur deux types d'observations fictives**, mais **ne pas développer un deuxième collecteur ni republier une bibliothèque NPM**. Pas de serveur local, pas de framework lourd, pas de communication native, pas de service cloud.

**Dans le rapport, fournir une matrice de réemploi** : fonctions/fichiers **réutilisés de Iconothèque**, logique/scanner **réutilisé de 3GPT3**, adaptations spécifiques ChatGPT, portions volontairement non reprises. Transparence plutôt que « tout réécrit ».

## 2 — Périmètre des observations : ce que nous savons réellement

**Collecter seulement des conversations ChatGPT dont on observe un vrai lien :**
- UUID normalisé depuis une URL ou un href `https://chatgpt.com/c/UUID` ou `https://chatgpt.com/g/SLUG/c/UUID` ;
- URL observée, rendue absolue et validée avec **HTTPS + hôte exact `chatgpt.com`** ;
- **titre réellement visible ou accessible dans le lien** (`aria-label` puis texte si pertinent) ; si l'information est absente, garder le titre inconnu sans en inventer un ;
- éventuellement contexte de projet **observé dans l'URL** et état actif, **sans prétendre récupérer automatiquement tous les projets ou toute l'histoire** ;
- `firstSeenAt`, `lastSeenAt`, `seenCount`, et un petit ensemble borné des URLs explicitement observées.

**Ne collecter aucun message, prompt, réponse, contenu d'une discussion, cookie, token, phrase secrète, identifiant de compte, données de formulaire, données d'autres sites ou URLs arbitraires.** Ne pas lire les ressources internes React, API privées, réseau/fetch ChatGPT ni historique global du navigateur. **Pas de requêtes réseau supplémentaires.**

**Règle de vérité :** les discussions non présentes dans le DOM (projets repliés, listes virtualisées, contenu non chargé) **ne peuvent pas être détectées** ; le compteur est celui des éléments **observés**, pas celui des discussions de l'utilisateur. Aucun clic automatique, ouverture de projet, pagination forcée, scroll exploratoire ou visite de conversation pour « tout récupérer ». L'interface doit l'expliquer sans prétendre à l'exhaustivité.

**Identité :** dédoublonner par UUID, non par titre, contexte ou URL complète ; si la même conversation est revue depuis `/c/…` et `/g/…/c/…`, garder **une fiche d'observation**, préserver les URLs vues et un titre de meilleure qualité, sans inventer un projet. Deux titres identiques peuvent appartenir à deux conversations différentes.

Vérifier les règles avec `mon_gpt/chatgpt.py` ; l'extension et la future MG-009 doivent s'accorder sur le même UUID et la canonicalisation. **Ne pas changer le validateur Python pendant MG-008.**

## 3 — Modes de collecte : conserver ce qui marche déjà

Même trois modes **que MJ Collector 0.3.0** :

1. **Manuel uniquement (`manual`)** : aucun scan ni observateur automatique ; `Scanner cette page` collecte explicitement les liens présents sur l'onglet ChatGPT courant.
2. **Auto cible (`targeted`)**, **mode initial recommandé** : collecte passive limitée à la **conversation actuellement ouverte** (URL de conversation valide et, si observable, son titre dans la sidebar). Aucun parcours automatique de la liste complète ni des projets repliés.
3. **Auto large (`broad`)** : sur les pages `chatgpt.com` autorisées, collecte les **liens de conversation déjà rendus dans la sidebar** et suit les mutations DOM, sans ouvrir ni dérouler d'autres contenus.

Le bouton **Scanner cette page** fonctionne dans tous les modes ; il scanne les conversations actuellement **rendues sur cette page** et distingue **N nouvelles / M déjà connues**. Les trois modes persistent après fermeture du popup et redémarrage Chrome. Le mode Auto large est puissant mais peut enregistrer beaucoup d'éléments ; l'interface l'indique.

Observer les changements de route d'une application SPA et les mutations utiles, sans scruter tout le DOM à chaque frappe ou mutation ; debounce et limites raisonnables comme dans MJ Collector. Les scans manuels ne doivent pas être comptés deux fois par double événement, et les modes ne doivent pas s'auto-activer.

**Permissions minimales :** `storage` et `content_scripts.matches: ["https://chatgpt.com/*"]` ; ne pas ajouter `<all_urls>`, `webRequest`, cookies, identité de compte ou accès à tous les onglets. Si une autre permission est techniquement incontournable, justifier précisément dans le rapport. Extension désactivable et réversible.

## 4 — Popup : « un truc qui claque », mais un outil, pas un sapin de Noël

L'ancienne popup MJ Collector fonctionne, **mais l'utilisateur veut vraiment améliorer la présentation**. Conserver les gestes, soigner l'expérience :

- **Nom clair : « Mon GPT Collector »** (ou variante cohérente avec Mon GPT<3), petite icône originale propre à l'extension, typographie Windows agréable, **charte chaude ivoire/sapin/terracotta** proche de Mon GPT, sans recopier ses défauts d'ergonomie ;
- largeur raisonnable Chrome (env. 380–420 px), alignements nets, espaces bien distribués, titres sobres, **contraste et focus visibles** ; pas de longues colonnes de cinq boutons tous identiques ;
- en haut : **total connu**, **nouveautés du dernier scan**, **mode actif** ; ne pas confondre « connu dans l'extension » et « déjà importé dans Mon GPT » ;
- choix des modes par **trois options lisibles** (segmentées, radio joliment intégrées, ou sélection claire) avec une brève explication et état actif ;
- **une action principale identifiable** `Scanner cette page`, puis **Copier les URLs**, **Exporter JSON**, éventuellement **Exporter TXT** ; `Vider` discret et destructif avec confirmation ;
- **petite liste des dernières discussions détectées**, présentant **titre, état observé, date courte et éventuellement source/contexte** ; pas un mur de UUID bruts. Titre long tronqué avec accès complet. Ne jamais insérer le texte DOM brut en HTML : uniquement `textContent` ou encodage sûr ;
- états propres : aucune discussion, page non autorisée, aucun lien détecté, scan en cours, erreur de permission/stockage, collecte auto suspendue et nombre élevé d'observations. Retours non intrusifs.
- **Aucune nouvelle interface injectée dans les pages ChatGPT**. Le prototype 3GPT3 avait un overlay expérimental ; notre interface de contrôle est **dans la popup**, pour ne pas perturber la sidebar native.

**Actions ergonomiques réelles** et testées, pas des maquettes : clavier/Tab/Entrée/Espace, état désactivé correct, mode et compteur mis à jour sans fermer/réouvrir la popup, scroll sur les éléments récents, nettoyage confirmé, exports valides. Éviter le mur de boutons de la popup historique.

**Ne pas intégrer de bibliothèque d'icônes massive ni de dépendances graphiques nécessaires à l'exécution ;** petits SVG originaux inclus localement et CSS suffisent. Chaque élément décoratif doit soutenir l'usage.

## 5 — Données et contrats pour MG-009

**Un export JSON clair, stable et versionné** orienté discussions ChatGPT :
```json
{
  "source": "mon-gpt-collector",
  "schemaVersion": 1,
  "exportedAt": "2026-11-15T00:00:00.000Z",
  "conversations": [
    {
      "conversationId": "11111111-2222-4333-8444-555555555555",
      "url": "https://chatgpt.com/c/11111111-2222-4333-8444-555555555555",
      "observedTitle": "Titre réellement visible",
      "firstSeenAt": "2026-11-15T00:00:00.000Z",
      "lastSeenAt": "2026-11-15T00:00:00.000Z",
      "seenCount": 1,
      "observedUrls": ["https://chatgpt.com/c/11111111-2222-4333-8444-555555555555"]
    }
  ]
}
```
Forme illustrative ; autres métadonnées observées possibles **mais documentées, bornées et facultatives**. Si un titre manque, exprimer explicitement `null` ou un autre marqueur documenté, **ne pas l'inventer**. L'export doit être **déterministe** et résistant aux dates/champs invalides, sans pollution par les données du navigateur. Pas de contenu des conversations.

Créer `docs/collector-export-v1.md` dans Mon-GPT : sémantique des champs, normalisation, exemple fictif, sécurité, compatibilité future, **stratégie pour éviter d'écraser titres locaux, notes, tags, catégories, couvertures et rattachements** lorsque MG-009 importera. Le contrat doit servir à un autre futur adaptateur site sans changer son enveloppe générale si c'est raisonnable.

**Copier les URLs** et **Exporter TXT** : une URL réelle/canonique par ligne, plutôt qu'une liste d'UUID isolés, afin de permettre un usage direct. JSON sera le format privilégié pour les métadonnées. Export local par Blob/téléchargement standard, sans service ni backend.

Stocker sous une **clé dédiée** propre à Mon GPT (pas `jobs` de MJ Collector), indexer par UUID, contrôler quotas/limites et erreurs **visiblement** ; ne pas supprimer silencieusement des observations. `Vider` ne supprime que les données de **cette** extension, jamais celles des autres extensions ou les fiches Mon GPT. Pas de transfert direct vers l'application dans ce lot.

## 6 — Recette et qualité

**Tester d'abord sans données personnelles** : fixtures HTML artificielles de sidebar de type 3GPT3, liens `/c/UUID` et `/g/.../c/UUID`, titres longs, doublons, faux domaines, textes contenant un UUID sans lien, absent/fermé/virtualisé, changement de route, mutation DOM et scan manuel.

Tests pure JS pour :
- extraction stricte et normalisation des UUID/URL ;
- fusion, horodatages, fidélité des titres et métadonnées observées ;
- trois modes et transistions, déduplication et scans répétés ;
- contrat JSON/TXT, validation des limites, tolérance aux erreurs, sécurité et absence de données non prévues ;
- démonstration du **cœur réutilisable** avec une source fictive non ChatGPT ;
- popup accessible/éléments contrôlables dans des tests adaptés, sans dépendances lourdes.

**Recette dans le vrai Chrome sur CODEX-VM**, extension installée et activée (pas uniquement vérification syntaxique) :
1. `manual` n'enregistre rien avant clic ; scan d'une page ChatGPT avec liens visibles → N nouveaux puis N déjà connus au second scan.
2. `targeted` collecte uniquement la conversation courante ; `broad` reprend les liens présents dans la sidebar ; projets repliés/non chargés **non devinés**.
3. Couper/réactiver extension, changer d'onglet et de route SPA : persistance et absence d'exécution sur autres domaines.
4. Export JSON/TXT, copie URLs, relecture des champs, titre et UUID, double observation sous URL de projet et URL globale.
5. Affichage popup aux tailles usuelles et clavier, liste des derniers éléments, mode actif, validation de vidage, page non autorisée.
6. Vérifier **absence de toute modification des conversations ChatGPT** et d'appels réseau supplémentaires.

**Si l'interface réelle ChatGPT ne peut pas être chargée/testée sur CODEX-VM** : tester autant que possible sur une page/onglet fictif dans Chrome via un site/fixture contrôlé adapté aux contraintes du manifest, **indiquer PARTIEL honnêtement**, publier des captures de ce qui est réellement exécuté, **ne jamais prétendre que la collecte réelle est validée**.

**Livrables :**
- `companions/chatgpt-collector/` (extension MV3 complète, icône, popup soignée et module partagé) ;
- `docs/collector-export-v1.md` ;
- `reports/MG-008/rapport.md` : matrice de réemploi des **deux** repos, tests, preuves de fonctionnement sur Chrome, limites et **3 à 5 captures natives** popup (écran principal rempli, modes, erreurs/état vide, fin d'une liste, options si utiles) ;
- README d'installation `chrome://extensions`, fonctionnement, permissions et mode par défaut ; versions ajustées de manière cohérente.

Commit/push **uniquement sur `ugadavid/Mon-GPT`**, branche `main`, vérifier SHA distant et dépôt propre. Ne pas versionner de vraies URL/titres personnels ou des exports du navigateur. Ne pas créer un nouveau dépôt « framework » à ce stade.

**STOP après MG-008** pour la recette David/GPT. **MG-009** importera plus tard le JSON/TXT dans le catalogue Mon GPT, sans écraser les personnalisations ni réimporter deux fois le même UUID. Ne pas commencer cet import maintenant.

**Critère GO :** extension locale capable de collecter et exporter les conversations ChatGPT observées, trois modes fidèles au précédent collecteur, dédoublonnage correct, **interface réellement agréable**, et **architecture suffisamment factorisée pour être réemployée dans Iconothèque** sans recopier toute l'extension.
