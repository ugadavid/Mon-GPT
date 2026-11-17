# MG-013b — Lot A : surfaces et dessin

**17 novembre 2026 · Mon GPT<3 0.9.4 · CODEX-VM / Windows. Livraison pour validation visuelle de David.**

Les mêmes écrans reçoivent un papier plus clair, des titres sapin, des filets plus doux et des pastilles mieux accordées. Les retouches restent dans les styles et dessins existants : **aucun changement de placement, de dimensions interactives ou de comportement**. Les lots B et C ne sont pas engagés.

## Retouches livrées

| Fichier | Peinture réalisée |
|---|---|
| `mon_gpt/theme.py` | Papier `#FFFCF7` → `#FFFFFF` sur le fond ivoire conservé `#F7F3EA`. Tokens de bord `#DED8CC`, filet `#EAE4D9`, ombre légère `#EDE7DD`, fond d'en-tête `#E8EDE3`. Styles ttk des boutons, en-têtes de tableaux, séparateurs et onglets raccordés, sans modifier padding, police ou disposition. |
| `mon_gpt/atelier.py` | Contours/ombres des surfaces et boutons plus légers ; en-tête de Liste sauge, titres sapin, filets moins présents. Sélection de Liste raccordée au sauge existant `#DBE5D7`, contour de focus sapin plus net. |
| `mon_gpt/results.py`, `mon_gpt/mosaic.py` | Titres sapin, bords des cartes et vignettes adoucis ; survol de Mosaïque souligné en sapin. Aucun recalcul de grille, hauteur, texte, image ou zone ↗. |
| `mon_gpt/inspector.py`, `mon_gpt/widgets.py` | Titres des sections en sapin ; mêmes nuances de pastilles dans résultats, lecture et édition. Deux petites palettes constantes dans `theme.py` remplacent leurs trois copies locales, sans changer l'affectation déterministe des couleurs aux valeurs. |

Catégories : `#E7E4C6`, `#F2D7C6`, `#F0E0B5`, `#D6E6D9`. Tags : `#F1E8D9`, `#E6DDF0`, `#DCE9DE`, `#F0DDD2`. Les catégories gardent leur bord distinct ; les textes restent encre `#292D30`. Contrastes calculés sur les aplats : titres sapin/papier **7,38:1**, en-têtes **6,21:1**, minimum des textes de pastilles **10,12:1**. Cela ne constitue pas un audit général d'accessibilité.

La hiérarchie typographique évolue par la couleur : **Segoe UI, tailles, graisses et métriques existantes conservées** pour préserver troncatures et retours à la ligne. Les pictogrammes gardent leur tracé et leur sens. Aucun nouvel asset, aucune dépendance ou couche de thème.

## Comparaison réelle avant / après

Même catalogue que MG-013a, copié dans le seul dossier jetable `.recette/MG013b` : **5 projets, 24 discussions fictives**, titre long, multi-rattachement, notes, repères et portrait. Lancement réel avec `python -m mon_gpt --data-dir .recette/MG013b --simulate-open`. Même périmètre Tous, tri Titre et géométrie cliente **1360×820** ; Mosaïque Normal. Les cinq images nouvelles sont des captures natives brutes, sans retouche. Les originaux « avant » sont réutilisés par lien, sans duplication.

| Écran | Avant MG-013a | Après MG-013b |
|---|---|---|
| Liste, aperçu fermé | [Avant](../MG-013a/01-liste.png) | [Après](01-liste-apres.png) |
| Détaillée, aperçu fermé | [Avant](../MG-013a/02-detaillee.png) | [Après](02-detaillee-apres.png) |
| Mosaïque, aperçu fermé | [Avant](../MG-013a/03-mosaique.png) | [Après](03-mosaique-apres.png) |
| Mosaïque, même premier fil sélectionné et aperçu ouvert | [Avant](../MG-013a/04-mosaique-apercu.png) | [Après](04-mosaique-apercu-apres.png) |
| Licences et crédits, onglet Composants | [Avant](../MG-013a/09-credits.png) | [Après](05-credits-apres.png) |

Différences de contexte explicites : le chemin fictif affiche MG013b ; le statut de la quatrième capture signale l'ouverture simulée effectuée pendant la recette. Le cadrage des crédits porte directement sur la fenêtre secondaire 860×640. La comparaison montre le changement d'habillage, sans présenter ces images comme de nouvelles maquettes.

## Vérifications

**203 tests Python réussis en 240,326 s** ([journal complet](tests-python.txt)). Coût de la règle active : environ quatre minutes pour cette passe de peinture. La commande obligatoire `python -m unittest discover -s tests -v` est exécutée une seule fois avant publication conformément à `AGENTS.md` et à la mission. Aucun nouveau test applicatif ajouté pour recopier des couleurs.

**Contrôle Tk avant/après, distinct de la recette native :** 503 observations de widgets réparties sur Liste, Détaillée, Mosaïque, inspecteur et crédits ont les mêmes tailles demandées/réelles, positions locales, types/coordonnées/boîtes et textes des dessins Canvas. Seule la position écran de la fenêtre principale, décalée par Windows entre deux lancements, est exclue de la comparaison. Ce contrôle jetable n'est pas un nouveau dispositif de tests versionné ; il vérifie les scènes comparées, pas toutes les configurations possibles.

**Recette Windows pilotée :** bascule réelle des trois vues ; clic sur le premier titre avec sélection et focus visibles, **aucune ouverture** ; clic sur son ↗, **une seule ouverture simulée du fil fictif attendu** ; affichage de l'aperçu ; ouverture des crédits depuis Aide, consultation de la notice locale Python, fermeture par Échap avec retour à l'application ; fermeture normale de la session. Aucun navigateur lancé. Les cinq captures témoignent de ces écrans réellement observés.

Le catalogue fictif reste identique octet pour octet à celui de MG-013a, SHA-256 `07eb22d99cf10ec2047ec26ed19abd7108ba276f1c68c90e120a3dc700609c0e`. Seules ses préférences d'affichage jetables ont évolué. Aucun catalogue ou fichier personnel publié.

**Non rejoué séparément :** Collector JavaScript, campagnes d'import/migration/sauvegarde, autres DPI et longue recette de classement. Aucun lien causal avec ces retouches ; les tests historiques présents dans la suite Python ne sont toutefois pas retirés. La recette humaine d'appréciation graphique reste à David.

## Frontières et point d'arrêt

Départ propre à `52059ec`, synchronisation en avance rapide vers **`755fbaa`** contenant la mission. Six modules de présentation seulement modifiés ; `ui.py`, navigation, moteur, adaptateur, identité, stockage, formats, Collector, données, maquettes et `AGENTS.md` restent intacts. README et version 0.9.4 conservés.

Volontairement écartés : changement de police/taille ou marge qui modifierait les métriques, cartes plus hautes, nouveau dessin d'icônes de vues, suppression du titre « Aperçu », recomposition du bandeau ou nouvelle présentation du drag/menu de dépôt. Les seules nuances communes de papier/pastilles se propagent aux composants qui les utilisent ; aucune logique ni aucun style dédié de classement n'est retouché.

Contrôles de publication : liens du rapport, PNG lisibles, `git diff --check`, périmètre du commit, SHA distant et état propre. **STOP après publication du lot A, en attente de validation visuelle.** Aucun GO esthétique attribué à David, aucun lot suivant lancé.
