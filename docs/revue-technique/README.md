# Revue technique de Mon GPT<3

**Ouverture : 17 novembre 2026** · Application Windows **0.9.4** et Collector Chrome **0.8.2**.  
**Nature : dossier de réflexion, pas une mission de développement.** Aucun changement de code ni migration n'est décidé ici.

## Notre philosophie

> La mode et la popularité d'une technologie ne constituent pas des critères de choix. Nous regardons d'abord ce dont **notre application** a besoin.

La question importante n'est pas « quel framework utilise-t-on aujourd'hui ? », mais : **« que fait réellement cette bibliothèque pour nous, et combien coûte le fait de la garder, de l'adapter ou d'écrire notre propre petite brique ? »**

**Premiers principes de travail :**

1. **Comprendre avant de changer.** Identifier pour chaque technologie son rôle exact, ses appels réellement employés, ses contraintes et ses dépendances.
2. **Privilégier le nécessaire.** Une petite bibliothèque spécialisée — ou un module maison bien délimité — peut être plus pertinent qu'un énorme framework dont nous n'utilisons que quelques fonctions.
3. **Envisager sérieusement la bibliothèque maison**, particulièrement pour les fonctions circonscrites, les composants réutilisables et les conventions de notre interface ; ne pas l'écarter par principe.
4. **Comparer le coût total et non le seul nombre de lignes :** développement, tests, documentation, compatibilité Windows/Chrome, maintenance, correction des bugs et dette future. Une dépendance réduite n'est pas automatiquement une dépendance facile à remplacer.
5. **Réutiliser sans dupliquer.** Repérer les briques déjà écrites dans Mon GPT<3 et celles qui pourraient servir à d'autres applications, **sans lancer pour autant un nouveau projet**.
6. **Conserver le découpage existant** entre cœur générique, adaptateur ChatGPT, stockage, interface Windows et extension Chrome. Pas de refonte prématurée ni de nouvelle couche de plugins.
7. **Valider progressivement** toute éventuelle extraction/remplacement avec des tests et une recette, après une décision explicite. Ce dossier ne donne pas à Codex un GO pour modifier le code.

## Documents

- **[01 — Inventaire des technologies et bibliothèques](01-inventaire-technologies.md)** : tableau simple, rôles, alternatives, liens officiels, premières hypothèses.
- Les études suivantes pourront examiner le **graphe des dépendances**, les **API vraiment utilisées**, la taille des composants maison et la **pertinence d'une extraction/réécriture ciblée**.

## Questions pour chaque brique

| Question | Ce que nous voulons découvrir |
| --- | --- |
| Quel besoin précis couvre-t-elle ? | Fonctionnalités réellement utilisées, pas les possibilités annoncées |
| Quelle part en utilisons-nous ? | Modules/API importés, surface d'usage, taille et poids indirect |
| Quelle solution voisine existe ? | Simplicité, intégration, maintenance, indépendance |
| Et si nous la codions ? | Volume de code à écrire, cas particuliers, tests nécessaires |
| Où serait-elle réutilisable ? | Mon GPT<3 seulement, ou plusieurs applications personnelles |
| Que gagne-t-on réellement ? | Dépendances, performances, ergonomie, contrôle, compréhension |
| Quel serait le prix à payer ? | Nouveaux bugs, dette, compatibilité, mises à jour |
| Décision après étude | **Conserver / Encapsuler / Remplacer en partie / Écrire une brique maison / Reporter** |

## Pistes initiales, sans verdict

- **Pillow** est la seule dépendance Python tierce déclarée dans `requirements.txt`. Étudier précisément les traitements demandés (décodage PNG/JPEG/WebP, EXIF, normalisation, miniatures, caches) avant de parler d'une alternative. Le simple fait de n'appeler que quelques fonctions ne prouve pas que les réimplémenter serait simple.
- **Tkinter/ttk** n'est pas une dépendance à installer : il accompagne l'environnement Python/Tk. L'application possède déjà de **nombreux widgets Canvas et interactions sur mesure** : examiner s'il serait utile de consolider une petite bibliothèque *de composants d'interface maison* au lieu de changer de toolkit.
- **Collector Chrome** utilise principalement **JavaScript/HTML/CSS natifs et les API Chrome**, sans framework d'interface déclaré. La bibliothèque maison s'y trouve déjà en partie dans les modules `core` et `adapters`.
- **Puppeteer-core** est un outil **de développement/recette**, pas un composant livré au navigateur ; le juger selon l'utilité de ses tests, non selon la taille de l'extension finale.
- **JSON, ZIP, identifiants et dates** utilisent les outils standard de Python. Un format ouvert et une bibliothèque standard ne doivent pas être « remplacés par du maison » sans bénéfice concret : créer une couche commune au-dessus est une question différente de réécrire le format.

## Frontière avec le travail graphique

Cette revue arrive **avant** la passe esthétique de Mon GPT<3. Les décisions de présentation convenues le 16 novembre restent consignées dans [le carnet des finitions](../idees-et-finitions.md), notamment **déplacer les catégories, tags et description du projet vers la couverture située à droite du bandeau**. Cette priorité graphique n'est **pas oubliée**, simplement distincte de l'analyse technique.

## Sources du dépôt

- [Règles d'architecture `AGENTS.md`](../../AGENTS.md)
- [Dépendances Python `requirements.txt`](../../requirements.txt)
- [Dépendances de l'extension `package.json`](../../companions/chatgpt-collector/package.json)
- [Déclaration Chrome `manifest.json`](../../companions/chatgpt-collector/manifest.json)
- [Cœur générique](../../mon_gpt/core.py) · [Adaptateur ChatGPT](../../mon_gpt/chatgpt.py) · [Stockage](../../mon_gpt/storage.py) · [Interface](../../mon_gpt/ui.py)

**Statut : réflexion ouverte.** Les arguments « pourquoi plutôt qu'une autre » sont des hypothèses de lecture du projet, **pas des motivations historiques attribuées à Codex**.
