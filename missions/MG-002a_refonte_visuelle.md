# MG-002a — Atelier chaleureux, pour de vrai : refonte VISUELLE de Mon GPT<3

**Statut :** à réaliser — après recette utilisateur de MG-002 (0.2.0).  
**Dépôt :** `ugadavid/Mon-GPT`, base constatée `2690dcdca295c5135a9d6ccb3aa9eaba1b1940fd`.  
**Priorité exclusive :** **rendu graphique, lisibilité, identité visuelle, sensation d'usage**. Les gestes MG-002 sont désormais le socle ; **ne pas repartir en mission de fonctionnalités**.

## 1 — La consigne de l'utilisateur

> « Lâche-toi, inspire-toi **réellement** des maquettes, ne sois pas timide. Nous savons que tu en es capable : regarde Ma Médiathèque et Mon Bureau. »

La recette MG-002 constate que la **fonction Liste fait globalement le travail**, mais que **le rendu reste très loin des trois maquettes**. On voit encore des champs et listes Tkinter bruts, menus gris, gros vides non intentionnels, scrollbars omniprésentes, minuscules icônes, hiérarchie typographique faible, sélection pâle, inspecteur de formulaire plutôt que volet accueillant.

**Cette mission doit produire une différence visuelle majeure et immédiatement visible**, pas simplement remplacer cinq codes hexadécimaux ou changer quelques paddings. L'objectif est que l'utilisateur retrouve l'univers accueillant, moderne et vivant des références, et puisse s'y repérer visuellement.

**Références non négociables :**
- `missions/MG-002-maquettes/01_specification_UX.md` (charte et gestes validés) ;
- les **trois PNG** du dossier `missions/MG-002-maquettes/`, déposés par l'utilisateur ;
- `reports/MG-002/rapport.md` (MG-002 livrée, 35 tests), ses captures de la vraie application, ainsi que le README et l'architecture.

**Consulter les images localement sur CODEX-VM sans les modifier, dupliquer ni les retransmettre en blobs.** La spécification et les décisions utilisateur priment sur les éléments contradictoires des images.

## 2 — Direction graphique : « Atelier chaleureux »

Palette approuvée :

| Élément | Teinte |
|---|---|
| Ivoire principal | `#F7F3EA` |
| Sable secondaire | `#E7D9C5` |
| Vert sapin | `#315E4F` |
| Terracotta | `#C87A50` |
| Encre | `#292D30` |

**Liberté artistique réelle** : proposer des tonalités dérivées, aplats doux, profondeur, bandeaux illustrés, icônes harmonisées, relief léger, cartes, zones de survol, sélection et états vides plaisants. Cohérence avant surcharge ; lisibilité avant fantaisie. Les trois maquettes ne sont pas des vues à coder simultanément, mais une **ambiance commune à concrétiser**.

### Résultats visuels attendus

- **En-tête reconnaissable** : identité Mon GPT<3, vraie composition graphique, espace respirant et **sans les deux gros boutons permanents `+ Nouveau` / `Inspecteur` en haut à droite**. Ces fonctions existent toujours, mais accessibles via menus, clic droit, raccourcis ou commande discrète au bon endroit.
- **Arborescence de gauche** : projet, sous-projet, sélection, indentation et chevrons immédiatement reconnaissables ; vrais repères graphiques, nuances, états de survol, dépôts glisser-déposer clairement illustrés ; plus d'impression de Treeview gris d'usine.
- **Zone Liste centrale** : plus de priorité visuelle au titre, ouverture du fil évidente, ligne choisie élégante, colonnes aérées/équilibrées, badges tags/catégories réellement soignés quand visibles. **En vue Liste : icônes uniquement**, pas d'images de couverture gigantesques.
- **Inspecteur secondaire** : aperçu chaleureux, structuré en sections nettement distinctes, ouverture du fil immédiatement identifiable, champs de modification (à la demande) faciles à parcourir ; éviter l'impression de long formulaire administratif.
- **Recherche unique** conservée, habillée avec suggestions et pastilles lisibles, sans en recréer trois champs.
- **Création inline** et **menus contextuels** : même langage visuel ; inputs et boutons lisibles, pas de popup de création, pas de menus gris par défaut si une alternative native/custom sûre est possible.
- États vides, aide discrète, survol, focus clavier, texte long et fenêtre compacte soignés, pas de commandes tronquées.

**Ne pas créer de menus décoratifs ou de faux boutons.** Préférer un composant visuellement sobre mais fiable à un faux contrôle « joli » non opérationnel.

### Décision esthétique

Codex a le droit de **proposer une vraie solution graphique adaptée** (widgets Tk composés, Canvas, ressources/illustrations vectorielles intégrées, bibliothèques graphiques si elles sont effectivement nécessaires et compatibles Windows) au lieu de rester prisonnier du style ttk natif. **Documenter brièvement les choix et leurs prérequis**, ne pas installer silencieusement une grosse chaîne ou réécrire le moteur métier. Garder une application Windows facile à lancer. L'objectif est l'exécution réelle, pas des maquettes générées.

## 3 — Retours précis de la recette utilisateur à respecter

La recette utilisateur de 0.2.0 (14 novembre 2026) montre et demande :

1. **Projet courant qui apparaît dans ses propres résultats** : en sélectionnant `Écriture`, `Écriture` ne doit pas figurer parmi ses propres descendants. Correction d'affichage ciblée, sans changer `Catalog.search` ni la sémantique des descendants.
2. **Molette dans l'inspecteur** : son défilement doit fonctionner naturellement sous Windows, avec une gestion du focus qui n'intercepte pas celui de l'arbre ou de la Liste.
3. **Déplacement** : ne pas imposer un formulaire intermédiaire quand le contexte identifie déjà sans ambiguïté la source et la destination. Une action choisie au menu de dépose doit être immédiate. **Si plusieurs rattachements rendent l'origine ambiguë**, un choix ciblé et discret est acceptable ; jamais retirer au hasard des rattachements existants. Ne pas engager de refonte du moteur pour cela.
4. **Tags et catégories** : conserver les suggestions déjà calculées à partir de tout le catalogue, les présenter beaucoup plus proprement. **La recherche actuelle propose les valeurs globales, pas seulement celles des résultats filtrés** ; ne pas revendiquer une logique locale inexistante. Cette évolution de la portée des suggestions, si souhaitable, est un sujet de discussion distinct, **pas le cœur du présent lot**.
5. **Ouvrir un fil** : c'est toujours l'action majeure, et l'inspecteur doit rester facultatif. Ne pas réintroduire une longue fiche obligatoire.

**Précision importante sur les doublons, à consigner pour une mission fonctionnelle ultérieure :** l'utilisateur veut empêcher les doublons de **lien / identité de conversation ChatGPT**, même si les titres locaux sont différents (`Chat GPT<3`, `Mon GPT<3`, `Mon GPTouille` ne doivent pas créer trois fiches pointant vers le même fil). Déclencher au minimum un avertissement explicite donnant la fiche existante et proposant de l'ouvrir / y ajouter un rattachement. L'adaptateur actuel `chatgpt.py` déduplique déjà par UUID et le formulaire de création comporte un traitement des doublons : **la recette rapporte pourtant un cas suspect à reproduire**, en distinguant URL strictement identiques, variantes de la même conversation et changement d'URL lors d'une édition. **NE PAS réécrire cette logique dans MG-002a.** La noter clairement dans les « suites à investiguer », faute de preuve de reproduction ; aucune affirmation que le bug est corrigé sans test.

## 4 — Périmètre strict et sécurité

**À livrer dans MG-002a :** une **vue Liste et une coque commune spectaculairement plus accueillantes et soignées**, et les petites frictions d'interface ci-dessus nécessaires à l'usage. Une refonte graphique convaincante vaut mieux qu'une liste de fonctionnalités en plus.

**NON demandés dans cette mission :**
- Implémenter les vues Détaillée et Mosaïque : leur conception est **validée**, elles feront l'objet d'étapes ultérieures ;
- Ajouter images de couverture persistantes, import JPEG/PNG/WebP, migration du schéma JSON 1, galerie ou héritage d'image : **lot ultérieur distinct** ;
- Développer un navigateur, lire les conversations ChatGPT, ajouter une API, collecte Chrome ou synchronisation ;
- Réécrire `core.py`, `chatgpt.py` ou `storage.py` pour des raisons purement graphiques ;
- Ajouter des modules et couches d'abstraction inutiles.

**Préserver intégralement :** catalogue JSON métier `schema: 1`, liens et rattachements multiples, tri manuel/alphabétique, validation HTTPS, recherche, sauvegarde/restauration, `Ctrl+S` = enregistrer la fiche, mode de démonstration `--simulate-open`, les raccourcis existants et les confirmations nécessaires.

Les préférences purement visuelles peuvent rester dans le fichier d'interface séparé. Aucune donnée utilisateur réelle dans Git ; jeu fictif `MonGPT-MG002-Recette` ou autre répertoire de recette explicite.

## 5 — Preuves et recette : comparer aux maquettes, pas au minimum Tkinter

**Avant d'écrire le code** : étudier les trois maquettes **et les six/sept captures de recette réelles** disponibles en plus du rapport MG-002. Mettre dans le rapport un **mini-audit visuel concret** : trois différences majeures de 0.2.0 par rapport aux références, puis les transformations choisies.

Sur CODEX-VM, vérifier réellement :

- Liste principale en fenêtre 1360×820 et 1000×680, à l'aide de données fictives ; mêmes scénarios de fils/projets/tags, titres longs et accents.
- Clic titre → ouvrir simulé sans inspecteur ; ouverture par clavier, aucune ouverture sur clic de simple sélection.
- Recherche unique et tags, menus Fichier/contextuels, création dans la fenêtre, glisser gauche, rattachement sans duplication.
- Molette de l'inspecteur ; inspecteur affiché/replié ; mise en page après redimensionnement et changement de projet.
- Projet courant absent de ses propres descendants dans les résultats ; ordre et filtrage corrects.
- Aucun autre rattachement effacé silencieusement, suppression sûre, reprise/fermeture.
- Suite automatisée existante **35 tests** conservée et tests ciblés des petites corrections. L'outil de capture ne remplace pas la recette native.

**À publier** : captures de la **vraie application exécutée** montrant au moins :
1. Accueil/Liste avec inspecteur masqué et bandeau graphique ;
2. Liste avec inspecteur aperçu ;
3. Nouvelle création inline soignée ;
4. Résultats/suggestions tags ;
5. Menu contextuel et cible de DnD ;
6. Format compact après correction.

Les comparaisons doivent rendre visibles les changements. Si le rendu reste au niveau d'une Treeview beige avec des boutons standard et quelques couleurs, **ce n'est pas un GO graphique**, même si les tests passent.

## 6 — Livrables, verdicts, publication

- Programme utilisable avec l'ancien lanceur, sans casse des données, des raccourcis ni du mode démonstration ; version cohérente si modifiée.
- `reports/MG-002a/rapport.md` avec audit visuel avant/après, captures réelles, scénarios de recette, tests, défauts résiduels et décisions techniques.
- `README.md` actualisé sur le rendu, prérequis, menus, inspecteur et limites ; aucune promesse de vues/couvertures non réalisées.
- **Verdict explicite séparé :** `GO graphique` si le changement est substantiel et visible, `GO gestes` sur les tests faits, `PARTIEL` sur ce qui reste non validé (notamment le glisser droit physique si toujours non prouvé).
- Commit, push sur `origin/main` sans forcer ni altérer les 3 PNG ; SHA distant vérifié, dépôt propre.

**Instruction finale à Codex :** laisse parler ton sens graphique. Nous savons que tu as su produire de belles interfaces sur **Mon Bureau** et **Ma Médiathèque**. Applique cette exigence ici. **Nous ne voulons pas une nouvelle liste de fonctionnalités : nous voulons ouvrir Mon GPT<3 et avoir plaisir à y rester.**
