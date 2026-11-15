# MG-008a — Identifier les projets ChatGPT par leur clé ET leur nom

**Statut : à réaliser puis à valider par David sur son Chrome connecté.**  
**Base :** Mon GPT Collector **0.8.0**, `origin/main` au commit `b6fbd335d5715e5cdef3609c808352a0ed04987d` (MG-008, 22 tests JS + 121 tests Python ; collecte confirmée par David sur ChatGPT connecté).  
**But :** obtenir les correspondances sûres **`projectKey → observedName`** pour préparer le classement automatique dans Mon GPT<3.

## Décision utilisateur prioritaire — repartir de zéro

> « NOOOOOOOOOOOOOOOOOOOOOOON : XD »  
> « J'ai déjà vidé le cache et effacé les fichiers ! XD »

**AUCUNE compatibilité ascendante n'est demandée.** Les observations et anciens exports de recette ont déjà été effacés par l'utilisateur :
- **Ne pas migrer ni préserver** l'ancien `chrome.storage.local`, l'ancien état `monGptCollectorStateV1` ou les anciens exports JSON `schemaVersion: 1`.
- **Ne pas développer** de lecteur v1, mécanisme de rétrocompatibilité, script de migration, sauvegarde préventive d'anciens caches ou récupération de fichiers effacés.
- Il est **autorisé et préférable** de créer un stockage neuf et un contrat d'export neuf (**v2** par exemple), uniquement conçu pour les futures collectes de cette version. Si l'ancienne clé reste physiquement présente chez certains utilisateurs, l'ignorer ; pas de tentative de conversion.
- **Préserver en revanche les fonctions utiles** de MG-008 : modes Manuel / Auto cible / Auto large, scan, dédoublonnage par UUID de conversation, copie, export JSON/TXT, interface agréable, composants modulaires, permissions minimales. Refaire les tests avec un état **vierge**, pas avec les anciens exports.

La mission doit **rester simple**. Ne pas coder des fonctionnalités historiques dont personne n'a besoin.

## 1. Comprendre où se trouve le vrai nom d'un projet

Aujourd'hui l'adaptateur `companions/chatgpt-collector/adapters/chatgpt.js` reconnaît déjà `/g/g-p-.../c/UUID` et extrait `observedProjectKeys`, mais **n'associe pas ces clés à un nom**.

**Lire et réutiliser** :
- `companions/chatgpt-collector/adapters/chatgpt.js`, `core/observations.js`, `browser/runtime.js`, `browser/repository.js`, `browser/content.js`, `browser/background.js`, `ui/popup.*`.
- Source historique `https://github.com/ugadavid/3GPT3`, surtout `docs/dom-analysis.md` et `src/scanner/dom-scanner.js`. Leurs sélecteurs décrivent l'interface **de juin 2026**, donc vérifier leur pertinence actuelle.
- Les deux exports de recette fournis à GPT en novembre ont démontré que les **clés de projets** existent dans les liens ; ils ne sont pas à récupérer ni à réimporter : les tests repartent de données fictives.

**Phase d'audit DOM obligatoire avant code** : rechercher les éléments natifs de ChatGPT qui permettent de prouver une paire **clé + libellé**. Sources de preuve acceptables :

1. Un **lien/contrôle projet** avec URL ou attribut portant effectivement la clé `g-p-...`, et son titre accessible/visible sur le **même contrôle**.
2. Une **page d'accueil projet réellement ouverte**, dont l'URL porte cette clé et dont le titre est clairement celui du projet, non celui d'une conversation.
3. Un **bloc projet développé** où l'appartenance des liens de fils à **ce bouton/titre de projet** est établie par une structure sémantique fiable ; confirmer que toutes les clés d'enfants utilisables sont concordantes, et que rien ne croise un autre bloc.
4. Autre correspondance explicite et reproductible dans le DOM **rendu** et documentée, sans supposition.

**Interdit :** rapprochement par ordre d'apparition, index de ligne, voisinage incertain, texte d'un fil, similarité des noms, ou inférence d'un nom depuis le GUID. Les attributs CSS générés, l'état interne React, appels d'API privées et réponses réseau ne sont pas des surfaces de collecte.

**Si aucune preuve fiable n'est disponible dans une situation, garder la clé sans nom**, sans inventer une association. Un projet replié/non chargé peut rester sans nom ; ne pas le dérouler automatiquement. L'utilisateur pourra lui-même explorer ses projets dans Chrome, et un prochain scan enrichira les observations.

## 2. Identité des projets : deux homonymes = deux projets

- **Clé `g-p-...` observée** = identité source stable. Ne pas déduire son nom depuis la clé.
- Le **nom est une propriété observée**, qui peut changer et peut aussi être le même pour plusieurs clés. **Ne jamais dédoublonner/fusionner les projets sur leur nom.**
- Si `g-p-A` et `g-p-B` s'appellent tous deux « Développement », conserver **deux enregistrements distincts**.
- Si le nom de `g-p-A` change, actualiser son libellé selon la dernière **observation fiable** ; ne pas créer un deuxième projet.
- Si seul l'ID est connu, `observedName: null`, et éventuellement un état `unknown` dans la présentation ; n'enregistrer ni nom fictif ni nom de fil.
- Valider strictement type, longueur, caractères, taille totale, dates et source de preuve. Pour un nom extrait de `aria-label`, ne retirer des préfixes d'action (« Ouvrir... », « Options... ») que s'ils sont séparables de façon certaine. Préserver accents et caractères du vrai nom.
- Une conversation avec plusieurs variantes d'URL/contexte reste une **seule conversation par UUID**, quelle que soit la quantité de projets liés observés ; ne pas écraser les observations plus fiables avec les plus faibles.

## 3. Architecture : enrichir le collecteur modulaire, pas en écrire un autre

**Évoluer le socle existant**, sans réinventer sa file d'écriture et sa popup :
- **Adaptateur ChatGPT** : `scanProjects` (ou équivalent), fournissant des observations `projectKey/observedName/evidence` ; pas d'accès au stockage, ni DOM écouté depuis la popup.
- **Moteur pur** : validation, fusion et index des projets **par clé**, bornes et historisation des noms si réellement utile. Une fonction générique réutilisable à une autre source est préférable à des exceptions ChatGPT dispersées.
- **Runtime/worker** : recevoir de façon atomique conversations + projets du même scan ; préserver le mécanisme d'écrivain unique, debounce, gestion d'erreurs et modes existants ; un lot refusé ne doit pas perdre les données précédemment validées.
- **Nouveau stockage local vierge** : politique/version libre mais **documentée**, aucune migration depuis v1.
- **Popup existante** : la soigner sans la refondre ; montrer clairement nombre de conversations et **nombre de projets identifiés**, avec distinction **nom connu / nom inconnu**, et, si pertinent, une liste compacte des projets connus en plus des discussions récentes. Aucun second panneau de configuration compliqué. Pas d'injection d'overlay.
- **Modes** : Manuel = scan explicite seulement ; Auto cible = observation de la page/conversation en cours (et son projet si preuve) ; Auto large = projets et liens déjà rendus, avec observer de mutations. Aucune exploration/scroll/ouverture de sections sans clic utilisateur.

## 4. Export neuf pour MG-009

**Nouvelle version de contrat**, par exemple `schemaVersion: 2` avec liste `projects` :

```json
{
  "source": "mon-gpt-collector",
  "schemaVersion": 2,
  "exportedAt": "2026-11-15T17:30:00.000Z",
  "projects": [
    {
      "projectKey": "g-p-11111111111111111111111111111111",
      "observedName": "Développement"
    },
    {
      "projectKey": "g-p-22222222222222222222222222222222",
      "observedName": "Développement"
    }
  ],
  "conversations": []
}
```

Exemple **entièrement fictif**. Les conversations conservent leur UUID, URL, titre observé, horodatages et `observedProjectKeys` selon le contrat courant, éventuellement ajusté et documenté. Les projets exportés sont **indexés par clé, jamais par nom** ; proposer également les projets connus seulement par leurs clés avec `observedName: null`, pour ne pas filtrer silencieusement.

**Les anciens exports `schemaVersion: 1` ne sont pas pris en charge par cette version.** Inutile de coder leur lecture. Documenter le **nouveau** format dans `docs/collector-export-v2.md` avec exemple fictif, limites et sémantique des noms. `MG-009` devra alors importer exclusivement le contrat neuf. Ne **pas** démarrer cet import ici.

**Pour MG-009 (seulement une perspective)** : création de dossiers locaux par nom de projet, rattachement immédiat des fils, proposition de **fusion/séparation** si plusieurs clés partagent le même nom ou si des dossiers locaux existent déjà, mémorisation de chaque clé source vers son ID local même si plusieurs clés convergent. **Aucune décision de fusion, aucun projet local et aucun catalogue Python modifié dans MG-008a.**

## 5. Tests et recette

Conserver les **121 tests Python** (application inchangée) et les 22 tests JS MG-008 pertinents ; adapter ceux qui dépendent délibérément de l'ancien schéma, **sans ajouter un test de migration**. Ajouter :

- noms issus de DOM avec preuve directe et depuis projet développé/page projet, preuve absente ou ambiguë ;
- **deux projets avec un même nom**, GUID différents → deux fiches ;
- **un GUID renommé** → un seul projet au nom actualisé ;
- projet connu par clé seulement → nom `null` ; plusieurs contextes d'une même conversation ;
- anciens liens et déduplication UUID ; changement de mode / mutations / DOM partiellement replié / titres localisés, sans action automatique de navigation ;
- validation, refus atomique, limites, stockage vierge et **export v2** déterministe ;
- pas de collecte de messages ou données non liées.

**Chrome Windows réel sur CODEX-VM** : extension réellement chargée, compte de recette éventuellement non connecté, **fixtures fictives contrôlées** reproduisant projets développés/repliés, deux homonymes, un renommage, noms inconnus. Tests automatisés du moteur et de l'export.

**Recette sur le vrai compte connecté de David indispensable pour valider le raccord DOM** : documenter de manière courte les gestes exacts (actualiser l'extension, ouvrir/replier manuellement 2–3 projets, scanner, exporter v2) et les preuves attendues. Si Codex n'a toujours pas de compte connecté, noter **PARTIEL sur association nom/GUID réel**, ne pas affirmer que les noms réels sont capturés.

**Livrables :**
- modification ciblée du **collecteur Chrome seulement**, pas de vue Python ;
- `docs/collector-export-v2.md` ;
- `reports/MG-008a/rapport.md` avec **audit de faisabilité, exemples de preuves DOM et niveau de confiance**, test de deux homonymes, renommer, données inconnues, bilan des tests et limites ;
- **3 ou 4 captures natives Chrome** de la popup aux états significatifs, avec noms **fictifs** ;
- README d'installation/mise à jour et version ajustés, et procédure de recette sur Chrome connecté.

**Important** : la livraison Chrome doit être un **dossier de distribution propre** (`manifest.json` et actifs nécessaires uniquement), sans `node_modules`, `.recette`, profils Chrome, exports personnels ou tests lourds. Ne pas réintroduire le dossier de 332 Mo qu'il avait fallu nettoyer manuellement. Préférer un livrable compact ou script de packaging explicite.

Commit/push `origin/main`, SHA distant vérifié, dépôt propre. **Arrêt après MG-008a** pour validation David/GPT. L'extension n'a jamais à modifier ChatGPT ni Mon GPT<3 dans cette mission.

**GO uniquement si** les noms réellement observables sont associés aux bonnes clés, les homonymes préservés, les noms inconnus honnêtes, le nouveau contrat exporté, et aucune modification des trois modes/du collecteur n'a été régressée. Sinon **PARTIEL explicite**, pas d'association hasardeuse.
