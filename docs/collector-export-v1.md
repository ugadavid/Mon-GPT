# Contrat d’observation et d’export — version 1

MG-008, Mon GPT Collector 0.8.0. Ce document décrit un **échange**, pas le schéma métier du catalogue. Aucun import n’est livré : MG-009 le traitera séparément.

## Enveloppe ChatGPT

```json
{
  "source": "mon-gpt-collector",
  "schemaVersion": 1,
  "exportedAt": "2026-11-15T12:05:00.000Z",
  "conversations": [
    {
      "conversationId": "11111111-2222-4333-8444-555555555555",
      "url": "https://chatgpt.com/c/11111111-2222-4333-8444-555555555555",
      "observedTitle": "Un jardin fictif sur la Lune",
      "firstSeenAt": "2026-11-15T12:00:00.000Z",
      "lastSeenAt": "2026-11-15T12:04:00.000Z",
      "seenCount": 2,
      "observedUrls": [
        "https://chatgpt.com/c/11111111-2222-4333-8444-555555555555",
        "https://chatgpt.com/g/g-p-fictif/c/11111111-2222-4333-8444-555555555555"
      ],
      "observedProjectKeys": ["g-p-fictif"],
      "lastObservedActive": true
    }
  ]
}
```

Cet exemple est entièrement fictif. Toutes les dates sont UTC ISO 8601 exactes, avec millisecondes et `Z`. Dates impossibles, compteurs invalides et incohérences d’identité font échouer la validation ; aucune date de remplacement n’est inventée.

| Champ | Type et sens |
| --- | --- |
| `source` | Chaîne fixe `mon-gpt-collector`, identifie ce format d’échange |
| `schemaVersion` | Entier `1`, indépendant des versions du catalogue et de l’extension |
| `exportedAt` | Instant de création de cet export |
| `conversations` | Tableau de 0 à 5 000 observations, trié par UUID normalisé |
| `conversationId` | UUID de conversation en minuscules, identité de dédoublonnage de la **source**, pas identifiant interne du futur catalogue |
| `url` | Première URL valide réellement observée pour cet UUID ; une des `observedUrls`, jamais synthétisée à partir d’un UUID seul |
| `observedTitle` | Chaîne non vide de 512 caractères maximum ou **`null`** si inconnu ; uniquement `aria-label` du lien, sinon son texte pertinent |
| `firstSeenAt`, `lastSeenAt` | Premier et dernier relevés enregistrés ; premier ≤ dernier |
| `seenCount` | Entier sûr ≥ 1 ; un incrément par UUID et par lot enregistré, même avec plusieurs liens identiques dans ce lot |
| `observedUrls` | 1 à 10 URL uniques validées pour le même UUID, triées à l’export |
| `observedProjectKeys` | Tableau additionnel de 0 à 10 slugs distincts réellement vus dans des URL `/g/SLUG/c/UUID`, chacun ≤ 128 caractères, triés ; aucun nom ou arbre de projet déduit |
| `lastObservedActive` | Booléen additionnel : discussion active **au dernier relevé**, pas nécessairement actuellement ouverte |

Les deux champs additionnels sont toujours émis par la version 0.8.0 ; un futur consommateur peut les ignorer et devrait accepter leur absence. Les champs inconnus ne doivent jamais être copiés sans contrôle dans le catalogue. Le contrat n’inclut ni mode de collecte, ni structure du stockage Chrome, ni qualité interne du titre, ni données de navigateur.

## Normalisation et fidélité

HTTPS et autorité exacte `chatgpt.com` (insensible à la casse), sans port, identifiant/mot de passe, sous-domaine ou ancien domaine. Chemins stricts `/c/UUID` et `/g/SLUG/c/UUID`, UUID de forme 8-4-4-4-12 hexadécimale et slug ASCII `[A-Za-z0-9_-]+`. Un href relatif commençant par `/` devient absolu sur cet hôte, sauf `//`. Aucun chemin `..` normalisé à la place d’un chemin reçu invalide. URL de 2 048 caractères maximum ; caractères de contrôle et espaces internes refusés.

La canonicalisation suit `mon_gpt/chatgpt.py:parse_url` sans le modifier : hôte mis en minuscules, slash final et fragment retirés, query non vide conservée. La casse du chemin reçu reste inchangée ; seul l’UUID d’identité est normalisé en minuscules. Les tests comparent directement JS et Python sur un corpus admis/refusé.

La même conversation revue sous une URL globale et une URL de projet possède un seul enregistrement. Le titre accessible est préféré au simple texte ; à qualité égale, un titre nouveau peut remplacer l’ancien. Dans un même lot, le lien actif est préféré aux alias de même qualité. Un titre absent ou moins précis n’efface pas un titre de meilleure qualité. Contrôles et espaces sont normalisés, puis le titre est borné. `Titre non observé` est un libellé UI et reste `null` dans le JSON.

Les relevés automatiques inchangés sont filtrés : `seenCount` ne mesure ni le nombre de visites ni tous les passages dans ChatGPT. Un scan manuel répété incrémente une fois et distingue nouvelles/connues ; un double événement simultané partage la même requête. Les requêtes réémises avec le même ID sont dédoublonnées dans une fenêtre mémoire bornée du worker ; aucune garantie de transaction distribuée après arrêt brutal du navigateur.

## Déterminisme, limites et sécurité

À état et `exportedAt` identiques, le JSON est identique : ordre des champs fixe, conversations triées par identité, listes URL/contexte triées. `exportedAt` varie normalement entre deux exports. TXT et copie suivent le même ordre par UUID, une **URL représentative observée** par ligne ; le fichier TXT se termine par un saut de ligne. Les autres variantes restent dans le JSON.

Le stockage de l’extension est borné à 5 000 identités et 6 Mio sérialisés, 10 variantes et 10 contextes par identité. Dépasser une limite ou subir un échec de stockage refuse le lot entier et affiche l’erreur : aucune ancienne observation n’est supprimée en silence. Les données invalides ne sont pas automatiquement effacées. L’attente de l’onglet n’est pas une sauvegarde durable.

Seuls les vrais liens rendus dans la navigation et l’URL courante sont observés : pas de contenu de discussion, prompt, réponse, cookie, token, formulaire, compte, donnée React ou API privée. Un titre peut néanmoins contenir une information personnelle : le fichier exporté doit être protégé comme un document personnel. Le texte est affiché avec `textContent`, jamais interprété comme HTML. Aucun transfert réseau de cet export ; téléchargement Blob local.

## Socle générique

Le cœur manipule une observation neutre `{source, identity, url, title, titleQuality, context, active}` et un index par identité. Il ne connaît ni UUID ChatGPT, ni DOM, ni Chrome. Une politique `normalize` injectée valide la source et l’URL. La fusion, les limites et le dépôt restent inchangés pour une autre source.

`exportData` produit l’enveloppe commune `{source, schemaVersion, exportedAt, [collectionKey]: [...]}` avec une projection `map` injectée. Pour ChatGPT, l’adaptateur choisit `conversations` et les champs ci-dessus ; une autre source pourrait choisir `observations`. La version du schéma définit le contrat de chaque source, sans confondre leurs identités. Le test avec `atelier-fictif` et `chatgpt` démontre cette API ; aucun deuxième collecteur ni bibliothèque NPM publique n’est livré.

## Stratégie prévue pour MG-009, sans implémentation ici

Le futur import devra lire et borner le fichier, valider sa source/version, repasser chaque URL par l’adaptateur Python et dédoublonner par UUID de conversation. Une prévisualisation présentera ajouts, éléments déjà présents et rejets avant application ; une sauvegarde précédera une écriture transactionnelle du catalogue.

Pour une conversation nouvelle, créer une fiche à identifiant **interne distinct et stable** et sa relation de source. Utiliser un titre observé seulement comme proposition initiale ; une absence de titre ne devient pas une invention dans les données d’observation. Pour une conversation existante, **ne pas écraser** titre local, résumé, notes, tags, catégories, identité visuelle ou rattachements. Les slugs observés ne créent ni n’attribuent automatiquement de projets locaux. Les métadonnées de provenance éventuelles devront rester dans l’adaptateur/source ou un journal d’import, pas dans le cœur générique.

Réimporter le même UUID ne doit créer aucune seconde fiche, même si son URL, son titre ou son contexte diffèrent. Les compteurs d’observation ne doivent pas devenir des compteurs métier. Aucune communication native ou import direct n’est ajoutée dans MG-008.
