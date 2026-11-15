# Mon GPT Collector — 0.8.0

Extension Chrome Manifest V3, locale et autonome. Elle conserve les **liens de discussions observés**, jamais leurs messages, puis les exporte. L’import dans Mon GPT attend MG-009. Aucun serveur, compte applicatif, service distant ou compilation nécessaire.

## Installer

1. Récupérer ce dépôt sur Windows et ouvrir `chrome://extensions` dans Chrome.
2. Activer **Mode développeur**, puis **Charger l’extension non empaquetée**.
3. Choisir le dossier contenant `manifest.json` :

   ```text
   C:\Users\codex\Documents\Projets\mon-gpt\companions\chatgpt-collector
   ```

4. Actualiser les onglets ChatGPT déjà ouverts, puis ouvrir **Mon GPT Collector** depuis le menu Extensions de Chrome. L’épingler est facultatif.

Après une mise à jour, utiliser **Actualiser** sur sa carte dans `chrome://extensions`, puis actualiser ChatGPT. Conserver le même dossier permet de garder le même identifiant local. Une désactivation suspend la collecte et conserve les observations ; une désinstallation peut supprimer le stockage : exporter auparavant.

## Choisir son rythme

| Mode | Collecte automatique | Scanner cette page |
| --- | --- | --- |
| **Manuel** | Aucune : ni observateur ni minuterie de collecte | Liens de discussions déjà rendus dans la sidebar, plus l’URL courante valide |
| **Auto cible**, valeur initiale | Uniquement la conversation actuellement ouverte, avec son titre si observable dans la sidebar | Même scan explicite complet |
| **Auto large** | Liens déjà rendus dans la sidebar, puis mutations utiles et changements de route | Même scan explicite complet |

Les modes sont mémorisés. Auto large peut conserver beaucoup de liens ; il n’ouvre ni projets ni conversations. Un projet replié, une liste virtualisée ou un élément non chargé ne peuvent pas être devinés. Les compteurs concernent **l’extension**, pas le nombre total de discussions ni les fiches déjà importées dans Mon GPT.

**Scanner cette page** indique les nouvelles et les déjà connues, par UUID. Une conversation ayant une URL globale et une URL de projet reste une seule observation. Deux conversations de même titre restent distinctes. En automatique, les liens inchangés ne provoquent pas de nouvelle écriture ; `seenCount` n’est donc pas un compteur de visites.

Les dernières discussions montrent titre, date et état au dernier relevé. Un titre long est accessible au survol ; **Titre non observé** est seulement un libellé d’affichage, jamais un titre inventé dans les données. La liste présente les 50 observations les plus récentes ; les exports les contiennent toutes. Les liens de cette liste s’ouvrent uniquement sur demande de l’utilisateur.

**Copier les URLs** et **TXT** donnent une URL réellement observée par ligne. **Exporter JSON** conserve aussi les métadonnées, selon le [contrat v1](../../docs/collector-export-v1.md). Les téléchargements utilisent le dossier et les réglages habituels de Chrome. **Vider** demande confirmation, Échap annule ; le mode est conservé. Sur un autre site, le scan est désactivé et les exports restent disponibles. Si un onglet est signalé à actualiser, le recharger après l’installation/réactivation.

Tab, Maj+Tab, Entrée et Espace utilisent les contrôles natifs, avec un focus visible. Les trois modes sont des radios : les flèches les parcourent. Les états de scan et les erreurs sont annoncés par une zone `role=status`.

## Permissions et données

La seule permission est **`storage`** ; les scripts de contenu s’exécutent uniquement sur **`https://chatgpt.com/*`**, au niveau principal. Aucun `<all_urls>`, accès aux cookies, historique global, identité, `management`, `downloads`, `tabs` ou permission réseau. `tabs.query` sert seulement à obtenir l’identifiant de l’onglet actif et à lui envoyer un message ; aucune lecture de son titre ou URL privilégiée. Voir les références officielles [Tabs](https://developer.chrome.com/docs/extensions/reference/api/tabs) et [Storage](https://developer.chrome.com/docs/extensions/reference/api/storage).

Le scanner lit uniquement les href et titres de liens dans des conteneurs de navigation sémantiques, et l’URL courante. Aucun message, formulaire, jeton, ressource React, requête aux API ChatGPT, clic automatique ou overlay. Le DOM de ChatGPT n’est pas modifié. La popup ne rend les titres qu’avec `textContent`.

Les observations sont dans `chrome.storage.local`, sous **`monGptCollectorStateV1`**, indexées par UUID. Aucun transfert direct vers le catalogue ou `interface.json`. Ce stockage et les fichiers exportés ne sont pas chiffrés par l’extension : leurs titres et URL peuvent être personnels ; conserver ses exports avec soin.

Limites : **5 000 observations, 6 Mio de données sérialisées, 10 URL et 10 contextes par UUID**, URL de 2 048 caractères, titre de 512 caractères. Le contexte est un slug réellement présent dans l’URL ; au-delà de 128 caractères, il est omis. Les erreurs refusent le lot entier, sans éviction silencieuse. Exporter les données avant un vidage volontaire. Une corruption du stockage est signalée et n’entraîne pas de remise à zéro automatique.

Les observations refusées par le stockage restent temporairement en mémoire de l’onglet (5 000 liens maximum). Les modes automatiques réessaient ; en Manuel, relancer explicitement le scan. **Fermer/actualiser cet onglet perd cette attente non enregistrée**, pas les observations déjà conservées. Aucun mécanisme ne promet une collecte exhaustive.

## Architecture et réemploi

| Couche | Responsabilité |
| --- | --- |
| `core/observations.js` | API pure, validation, index/fusion, dates, limites, export générique ; aucun DOM, Chrome ou site |
| `adapters/chatgpt.js` | Politique URL/UUID, scanner sémantique adapté de 3GPT3, projection du contrat ChatGPT ; aucun stockage |
| `browser/repository.js` | Stockage injecté, file d’écriture unique, idempotence des requêtes |
| `browser/runtime.js` | Cycle générique, modes, observation, debounce et attente ; site/transport/horloge injectés |
| `browser/background.js`, `content.js` | Branchement Chrome, garde des messages et configuration ChatGPT |
| `ui/presentation.js` | Liste générique, libellés de modes, téléchargement Blob local |
| `ui/popup.*` | Présentation et commandes de cette extension ; aucun scanner DOM du site |

Un futur collecteur remplacera l’adaptateur et la configuration du branchement/popup (nom, clé, source, projection d’export), sans changer la fusion, le dépôt, le cycle ou le composant de liste. Aucun registre de plugins ni deuxième collecteur développé. Le test à deux sources fictives démontre l’API pure.

Le moteur de collecte est adapté de **MJ Collector 0.3.0** ; l’extraction de la sidebar provient de **3GPT3 0.1.0**. La [matrice de provenance et les preuves](../../reports/MG-008/rapport.md) distinguent les réemplois et adaptations. Aucun de ces dépôts sources n’a été modifié.

## Vérifier

Node 24 et Python disponible à la racine du dépôt :

```powershell
cd C:\Users\codex\Documents\Projets\mon-gpt\companions\chatgpt-collector
npm test
```

Les tests purs emploient `node:test`, sans paquet nécessaire. Le test de parité URL appelle le validateur Python existant. Pour la recette automatisée sur le Chrome Windows installé :

```powershell
npm ci
npm run test:chrome
```

`puppeteer-core` est uniquement une dépendance de **développement**, figée par le lockfile ; aucun téléchargement de navigateur. Le chemin par défaut est `C:/Program Files/Google/Chrome/Application/chrome.exe` ; `CHROME_PATH` permet un autre chemin. Le test ouvre un profil jetable dans `.recette/`, installe l’extension par l’API de test CDP, remplace seulement les navigations de fixture par le HTML fictif et vérifie le fonctionnement du vrai Chrome. Il ne touche pas au profil habituel. Le chargement CDP est propre au processus : la recette le réapplique explicitement après le redémarrage, avec le même ID et le même stockage. `node tests/chrome-recipe.cjs --hold` permet les arrêts pour captures Windows natives.

**Recette PARTIELLE sur le site réel** : Chrome charge ChatGPT sans compte, donc sans bibliothèque de conversations observable. Les gestes sont validés sur des fixtures dans Chrome, pas sur le DOM d’une bibliothèque ChatGPT connectée actuelle. Une recette utilisateur reste nécessaire. Aucun compte ni barrière d’authentification n’est contourné.
