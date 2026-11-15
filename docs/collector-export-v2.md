# Contrat d’export v2 — projets et conversations

Contrat introduit par MG-008a, conservé par MG-008b / Mon GPT Collector **0.8.2**. Même schéma v2 et même stockage `monGptCollectorStateV2` lors de la correction. **Aucun lecteur v1, migration ou compatibilité historique.** Aucune importation dans le catalogue Python n’est livrée.

## Exemple fictif

```json
{
  "source": "mon-gpt-collector",
  "schemaVersion": 2,
  "exportedAt": "2026-11-15T17:30:00.000Z",
  "projects": [
    {
      "projectKey": "g-p-11111111111111111111111111111111",
      "observedName": "Développement",
      "firstSeenAt": "2026-11-15T17:00:00.000Z",
      "lastSeenAt": "2026-11-15T17:20:00.000Z",
      "seenCount": 2,
      "nameObservedAt": "2026-11-15T17:20:00.000Z",
      "evidence": {"kind": "direct-link", "url": "https://chatgpt.com/g/g-p-11111111111111111111111111111111/project"}
    },
    {
      "projectKey": "g-p-22222222222222222222222222222222",
      "observedName": "Développement",
      "firstSeenAt": "2026-11-15T17:00:00.000Z",
      "lastSeenAt": "2026-11-15T17:20:00.000Z",
      "seenCount": 2,
      "nameObservedAt": "2026-11-15T17:20:00.000Z",
      "evidence": {"kind": "direct-control", "url": null}
    },
    {
      "projectKey": "g-p-33333333333333333333333333333333",
      "observedName": null,
      "firstSeenAt": "2026-11-15T17:00:00.000Z",
      "lastSeenAt": "2026-11-15T17:00:00.000Z",
      "seenCount": 1,
      "nameObservedAt": null,
      "evidence": {"kind": "key-only", "url": "https://chatgpt.com/g/g-p-33333333333333333333333333333333/c/11111111-2222-4333-8444-555555555555"}
    }
  ],
  "conversations": [
    {
      "conversationId": "11111111-2222-4333-8444-555555555555",
      "url": "https://chatgpt.com/g/g-p-33333333333333333333333333333333/c/11111111-2222-4333-8444-555555555555",
      "observedTitle": "Un jardin fictif sur la Lune",
      "firstSeenAt": "2026-11-15T17:00:00.000Z",
      "lastSeenAt": "2026-11-15T17:00:00.000Z",
      "seenCount": 1,
      "observedUrls": ["https://chatgpt.com/g/g-p-33333333333333333333333333333333/c/11111111-2222-4333-8444-555555555555"],
      "observedProjectKeys": ["g-p-33333333333333333333333333333333"],
      "lastObservedActive": false
    }
  ]
}
```

## Identité et champs

L’enveloppe est `{source, schemaVersion, exportedAt, projects, conversations}`. `source` vaut `mon-gpt-collector`, `schemaVersion` vaut **2**, dates UTC ISO 8601 exactes avec millisecondes et `Z`. Les dates impossibles sont refusées, sans remplacement inventé. Les tableaux sont triés par identité ; ordre des champs fixe, URL/contextes triés. À état et `exportedAt` identiques, l’export est identique. Une date d’export nouvelle change normalement le JSON.

**Projets :**

| Champ | Sémantique et borne |
| --- | --- |
| `projectKey` | Identité source opaque, sensible à la casse, `/^g-p-[A-Za-z0-9_-]{1,124}$/`, 128 caractères maximum. Ni nom ni ID local Mon GPT |
| `observedName` | Nom réellement observé, chaîne non vide ≤ 256 caractères ou `null` ; accents et ponctuation conservés, espaces normalisés ; jamais un titre de fil ou une clé transformée |
| `firstSeenAt`, `lastSeenAt` | Premier et dernier lots enregistrés pour cette clé, premier ≤ dernier |
| `seenCount` | Entier sûr ≥ 1, une occurrence par clé et par lot enregistré, pas un compteur d’ouvertures ni de renommages |
| `nameObservedAt` | Date de la dernière preuve de nom retenue, comprise entre premier/dernier relevé ; `null` si nom inconnu |
| `evidence` | Objet strict `{kind, url}` décrivant la preuve du **nom retenu**, ou de la clé seule si inconnue. Aucun extrait DOM, message ou donnée de compte |

Un nom peut changer ; la même clé reste le même projet. Deux clés de même nom produisent deux entrées. Pas d’historique de noms superflu. Un nouveau nom remplace l’ancien si la preuve est au moins du même niveau et n’est pas antérieure au nom enregistré. Une preuve faible ou sans nom n’efface pas un meilleur nom. Deux noms contradictoires de meilleur niveau dans un même scan ne sont jamais départagés par ordre DOM : aucun nouveau nom retenu. Un nom déjà connu peut donc rester ancien tant qu’aucune nouvelle preuve suffisante n’est disponible.

**Conversations :** `conversationId` = UUID 8-4-4-4-12 hexadécimal normalisé en minuscules, identité de source ; `url` = première URL représentative réellement observée ; `observedTitle` = titre du lien (aria puis texte pertinent), ≤ 512 caractères ou `null`. Premier/dernier relevés et `seenCount` portent sur les lots enregistrés. Plusieurs occurrences dans un lot incrémentent une seule fois. Les relevés automatiques inchangés ne provoquent pas d’écriture ; ce n’est pas un historique de visites.

`observedUrls` contient 1 à 10 URL uniques du même UUID. `observedProjectKeys` est l’union, bornée à 10, des **clés `g-p-…` réellement présentes dans ces URL**, pas des noms rapprochés. Les slugs d’autres types de GPT ne deviennent pas des projets. `lastObservedActive` signifie « actif au dernier relevé », pas « ouvert maintenant ». Un fil observé sous plusieurs projets reste une seule conversation par UUID.

## Preuves acceptées et prudence

| `kind` | Surface exacte | Niveau interne | `url` |
| --- | --- | --- | --- |
| `direct-link` | Lien d’accueil projet avec nom propre sur le même contrôle | 2, direct | URL d’accueil observée |
| `direct-control` | Contrôle natif `div[role="button"]` portant `data-app-action-sidebar-project-id` et `data-app-action-sidebar-project-label`, propriétaire et titre propre concordants ; ou bouton/treeitem aux attributs `data-project-id` / `data-project-key` précédents. Actions secondaires exclues | 2, direct | `null` : la clé vient de l’attribut, pas d’une URL inventée |
| `project-page` | Accueil projet ouvert à URL valide, un seul H1 visible dans main ; jamais sur `/c/UUID` | 2, direct | URL d’accueil courante |
| `expanded-group` | Propriétaire treeitem, bouton contenant ses liens, ou contrôle/groupe réciproquement reliés par aria ; aucun sous-projet concurrent ; clés de tous les enfants utilisables concordantes | 1, prudent | Une URL de fil enfant réellement observée portant cette clé |
| `key-only` | Clé observée, sans nom prouvé ou avec preuve contradictoire | 0, inconnu | URL de fil/accueil portant la clé, ou `null` si attribut seul |

Le niveau est calculé depuis `kind`, pas accepté comme une autorité externe ni exporté comme champ libre. `observedName: null` exige `key-only`. Les URL de preuve doivent porter la même clé. Contrôles aux attributs contradictoires, relation aria ambiguë (dont identifiants DOM dupliqués), groupe mixte ou section globale ne fournissent aucun nom. Les noms génériques de sections (`Projets`, `Chats`, etc.) sont exclus du fallback de groupe, même si un projet peut légitimement porter ce nom ; une preuve directe reste possible. Les noms d’action sont rejetés, sans découpage heuristique de préfixes.

MG-008b ajoute une forme **réellement observée dans la session Chrome authentifiée**, sans changer le contrat : contrôle marqué `data-app-action-sidebar-project-row`, propriétaire `data-sidebar-project-kind="local"` et `data-sidebar-project-container-id="project:CLÉ"`. Le nom déclaré doit concorder avec son titre propre rendu dans ce contrôle, relié par `aria-labelledby` ou l’emplacement sémantique `data-marquee-content`. Les mots génériques ou préfixes d’action sont alors conservés intégralement s’ils sont réellement le nom prouvé. Un propriétaire contradictoire, des enfants visibles de clés discordantes, des IDs de titre ambigus ou un désaccord nom/texte laissent le nom inconnu. Le H1 de page reste un fallback seulement si cette clé n’a pas de contrôle natif identifié. Voir l’[audit réel anonymisé](../reports/MG-008b/audit-dom-reel-anonymise.md) et le [bilan de validation](../reports/MG-008b/rapport.md).

## Validation, bornes et sécurité

URL HTTPS à autorité exacte `chatgpt.com`, sans port, identifiant/mot de passe ni sous-domaine. Conversations : `/c/UUID` ou `/g/SLUG/c/UUID` stricts, validateur Python inchangé et testé en parité. Accueil projet : `/g/g-p-…` ou `/g/g-p-…/project`. Un href `/…` devient absolu sur cet hôte ; pas `//`. Hôte normalisé en minuscules, slash final et fragment retirés, query non vide conservée. Aucun `..` accepté après normalisation, aucune URL synthétisée à partir d’un UUID seul. Casse du chemin conservée, URL ≤ 2 048 caractères.

Maximum 5 000 conversations, 1 000 projets et **6 Mio cumulés** ; 10 URL/contextes par conversation. Champs de nom, dates, source et preuve sont contrôlés. Noms trop longs ou interrompus pendant la lecture d’un contrôle : inconnus, pas tronqués en faux noms. Les contenus invisibles ou enfants repliés ne sont pas explorés ; un contrôle visible portant explicitement sa clé peut suffire. Tout lot conversations + projets est écrit atomiquement par le worker unique ; erreur ou dépassement refusent le lot entier, sans suppression silencieuse. L’attente de l’onglet est temporaire, pas une sauvegarde durable.

Copie et TXT exportent seulement les URL de conversations, une représentative par UUID, triées par identité ; le TXT se termine par un saut de ligne. **Le JSON est nécessaire pour les projets et leurs noms.** Il reste exportable avec des projets seuls.

Pas de messages, prompts, réponses, formulaires, tokens, cookies, compte, React, API privée, overlay ou exploration automatique. Aucun réseau supplémentaire, export Blob local. Les noms/titres peuvent être personnels : protéger les exports, qui ne sont pas chiffrés. Les valeurs observées sont affichées avec `textContent`, jamais interprétées comme HTML. Aucun ancien JSON n’est lu par cette extension.

## Modèle générique et perspective MG-009

Le cœur manipule des `records` génériques et des `entities` nommées `{source, identity, name, evidence, confidence}`. Il ne connaît ni les clés `g-p-…`, ni ChatGPT, DOM ou Chrome. L’adaptateur valide ces clés et projette les champs `projects` / `conversations` à l’export. Une autre source peut réutiliser la fusion, le dépôt et les composants de présentation sans fusionner ses conteneurs par nom.

MG-009 devra importer **exclusivement v2**, valider avant écriture et prévoir une transaction/sauvegarde. Chaque clé source devra être mémorisée vers un ID interne local stable. Des dossiers locaux pourront être proposés à partir des noms ; deux clés homonymes ne devront jamais être fusionnées automatiquement : proposer fusion/séparation, y compris face à des dossiers locaux existants. Plusieurs clés pourront converger vers un même dossier uniquement après décision explicite.

Les fils devront rester dédoublonnés par UUID et rattachés selon ces correspondances de clés, pas selon la similarité de noms. Titres locaux, notes, tags, catégories, couvertures et rattachements personnalisés ne devront pas être écrasés silencieusement ; les noms inconnus demanderont un traitement explicite. Aucun dossier local, décision de fusion ou import Python développé dans MG-008a.
