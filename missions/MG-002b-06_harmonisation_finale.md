# MG-002b-06 — Finition graphique finale : priorité à la colonne gauche

**Statut : à réaliser.** Dernière micro-mission de la série MG-002b, avant les vues Détaillée et Mosaïque.  
**Base contrôlée :** `origin/main`, commit `7bc53939e2da927d0f0131c3c6f6cb5188715d02` (MG-002b-05, Mon GPT<3 0.2.1, **60 tests réussis**).  
**Décision utilisateur :** MG-002b-01 à 05 validées. **Ne pas réouvrir leur conception**, sauf ajustements de marges et deux points de dialogue ci-dessous.

## 1 — PRIORITÉ ABSOLUE : la navigation de gauche n'est pas assez belle

> « Surtout menu gauche… pas beau là :D »

La colonne « Votre espace » doit désormais bénéficier de la même finesse que le menu principal et la Liste. **C'est la priorité esthétique n° 1, devant toute harmonisation cosmétique mineure ailleurs.**

**Référence graphique :** l'**arborescence de gauche** de la troisième maquette `missions/MG-002-maquettes/Image ChatGPT 14 nov. 2026, 11_51_55-3.png`, puis celles des deux autres maquettes. Consulte ces PNG **localement**, sans modifier, renommer, dupliquer, embarquer ni publier de blobs.

Aujourd'hui le panneau conserve l'impression d'une Treeview Tk un peu brute : bande de sélection vert foncé pleine largeur, dossiers marron dans des cadres/beiges, hiérarchie visuelle peu raffinée, titres longs tronqués brutalement, combobox « Manuel » visuellement datée, marges et gouttières peu travaillées, bas de panneau rempli de textes d'aide sans personnalité. L'utilisateur veut un **explorateur accueillant, raffiné et immédiatement lisible**, pas une arborescence de gestion technique.

**Demande ciblée :**
- **Composition de la carte « Votre espace »** : marges internes/externes équilibrées, en-tête discret, séparation souple, choix de tri compact ; éviter l'effet panneau plaqué contre le bord de la fenêtre. Faire respirer les panneaux sans rendre la navigation maigre.
- **Véritable hiérarchie graphique** : chevrons sobres, indentation régulière, lecture claire des niveaux, éventuellement guides subtils ; profondeur et parenté reconnaissables d'un coup d'œil. **Conserver intégralement l'arbre métier, les parents et l'ordre existants.**
- **Icônes plus fines** : dossiers et actions variés selon les types **sans carré beige systématique**, sans obligation de personnalisation persistante ici ; continuer à distinguer « Tous les fils », « À classer » et projets. Pas d'image de couverture dans cette vue compacte.
- **Sélections / survols / dépôt** : sélection vert sauge douce et confortable plutôt qu'un bloc vert foncé écrasant ; hover discret ; focus clavier et cibles de glisser-déposer visibles et distinctes ; cibles interdites identifiables.
- **Titres longs** : ne pas sacrifier toute l'information à une troncature sévère ; prévoir un accès simple au libellé complet (survol/info-bulle ou équivalent) sans casser l'arbre.
- **Actions** : le petit `+`, le tri manuel/alphabetique, clic droit, raccourcis et repli des projets conservent leur fonctionnement ; rendre les commandes contextuelles élégantes mais **ne pas modifier les menus** validés par MG-002b-01.
- **Pied de panneau** : garder l'aide réellement utile au glisser-déposer, mais réduire les slogans ou redites qui occupent inutilement de la hauteur. Soigner sa typographie, et réserver la place à l'arborescence.

**Ne pas inventer** une nouvelle hiérarchie, des catégories fusionnées aux projets, une copie de projet ou une persistance d'icônes/couvertures. Si des compteurs « 4 » ou « 12 » apparaissent dans les maquettes, ne les afficher que s'ils sont **calculés correctement depuis les données réelles** ; ils ne sont pas une obligation dans cette mission.

## 2 — Respiration générale : finitions MESURÉES

> « Immédiatement [sous le menu] ne signifie pas qu'on ne peut pas laisser un peu d'espace pour respirer. »

La structure trois colonnes MG-002b-02 reste acquise. **Ajouter une respiration maîtrisée autour des cartes**, surtout les **marges gauche et droite** et les gouttières entre colonnes, comme dans les maquettes ; un peu de fond ivoire autour des panneaux, surfaces distinctes, filets fins et ombres légères si utiles.

- Les colonnes commencent **près du menu validé** mais pas collées, sans restaurer l'ancien bandeau global.
- Le centre reste prioritaire en largeur ; l'inspecteur se replie et rend toute sa largeur à la bibliothèque.
- Ne **pas** bouleverser les proportions, repositionner la recherche, modifier la Liste ou recréer des marges géantes.
- Raccorder délicatement alignements, espaces, couleurs de survol et traits entre **gauche/centre/droite**, sans retoucher ce qui a été explicitement approuvé dans les lots précédents.

**La priorité de réalisation est la colonne gauche.** Si un compromis est nécessaire pour préserver les gestes et limiter les changements, privilégier la navigation gauche et des gouttières cohérentes plutôt qu'une refonte générale.

## 3 — Deux corrections UX précises : plus de popups grossières pour les cas ordinaires

### 3.1 Validation du Titre : message sous le champ, teinte pastel

Situation observée : le champ `Titre` est vide puis `Enregistrer` / `Ctrl+S` ouvre `Action impossible` avec une croix rouge.

**Attendu :**
- **Pas de popup** pour « Le titre est obligatoire. » : afficher cette aide **immédiatement sous le champ Titre**, en terracotta pastel, sobre et lisible, avec focus restitué au champ.
- Conserver toutes les autres valeurs saisies et tous les rattachements. Tant que le titre est invalide, **aucune mutation du catalogue**.
- Retirer le message une fois la valeur corrigée (au fil de la saisie ou à la prochaine validation cohérente).
- Pour une autre erreur de **saisie attendue et localisable** (`Lien` invalide ou informations `clé=valeur`), privilégier le même traitement sous le champ concerné **si cela reste petit et sûr**. Une **défaillance technique réelle** du stockage garde une alerte visible et adéquate.

Ne pas changer les validations métier ni prétendre que les URL en doublon ont été résolues.

### 3.2 Suppression : confirmation courte, Oui / Non

Situation observée : `Supprimer « qsdf » ?` suivi d'un long paragraphe détaillant que le fil sur ChatGPT est intact.

**Attendu :** une confirmation concise : `Supprimer « [titre] » ?` puis **Non / Oui**. Pas d'explication sur ChatGPT et pas de long pavé de texte.

- Présentation discrète/papier si elle reste fiable ; **pas de nouveau framework de boîtes de dialogue** ni surcouche générale pour toute l'application.
- **Non / Échap / fermeture = aucune suppression**, choix sûr initial. Seul **Oui** supprime.
- Garder les effets MG-001 : une discussion supprimée uniquement du catalogue local ; pour un projet, remontée des enfants et détachement des fils, sans supprimer les discussions.
- **Nuance de sûreté :** si la suppression d'un projet possède des descendants ou des rattachements qui seraient affectés, ne pas dissimuler cet effet. Préférer une **très courte indication factuelle** (`2 sous-projets et 5 rattachements seront réorganisés`) dans ce seul cas, sans long discours, ni cacher l'impact.
- Le dialogue peut être modal ici, car c'est une confirmation **destructive**, contrairement aux erreurs ordinaires de champ.

## 4 — ZONES FIGÉES et hors lot

- **Ne pas toucher au fonctionnement ou au style du menu principal « Windows plus plus »** : `main_menu.py` et `build_menus()` figés.
- **Ne pas retoucher la Liste centrale MG-002b-03** (composition, ligne/colonnes, tags, tri, icône ↗, hitboxes) ; ni l'aperçu MG-002b-04, ni l'éditeur MG-002b-05 **hors messages de validation et confirmation ciblés**.
- Recherche unique, filtres, contenu des fiches, création inline, moteur des rattachements, URL, raccourcis, glisser-déposer, persistance JSON et schéma 1 : **fonctionnement identique**.
- **Aucune nouvelle vue**, import ou galerie d'images, couverture persistante, extension Chrome, collecte ou migration dans ce lot.
- Le cas suspect de **doublons d'URL** sera étudié plus tard dans une mission fonctionnelle distincte. Ne pas le « corriger » discrètement dans MG-002b-06.
- Ne pas toucher aux trois images de référence. Données de recette **fictives uniquement** et `--simulate-open` ; aucune donnée utilisateur versionnée.

## 5 — Recette réelle et livrables

1. Étudier les **captures réelles MG-002b-05**, l'arborescence actuelle sur CODEX-VM, et la **troisième maquette** en privilégiant sa colonne gauche. Écrire dans le rapport un mini-audit « avant/après » : icônes, sélection, indentations, marges et informations.
2. Tester sur **1360×820 et 1000×680**, aperçu ouvert et fermé, puis fenêtre agrandie ; navigation à plusieurs niveaux, titres longs, ordre manuel/alphabetique, recherche dans un projet, ouverture au clavier et souris, clic droit, glisser gauche, cible interdite et défilement.
3. Tester `Titre` vide avec saisie existante : **message pastel sous le champ, pas de popup et pas d'écriture** ; correction puis enregistrement ; raccourci `Ctrl+S`.
4. Tester suppression fictive d'un fil et d'un projet, `Non`, `Échap`, `Oui`, plusieurs enfants/rattachements ; protections et effets inchangés.
5. **Conserver les 60 tests** existants et ajouter quelques tests de régression ciblés ; contrôler le résultat dans la **vraie application Tk**, pas seulement en widgets simulés.
6. Publier **3 ou 4 captures réelles maximum** : (1) gauche + ensemble avec inspecteur, (2) arbre avec survol/sélection ou menu de classement, (3) validation inline du Titre, (4) confirmation simple si utile.
7. Rapport `reports/MG-002b-06/rapport.md` **concis**, README/numéro de version ajustés seulement si nécessaire ; commit/push `origin/main`, SHA distant vérifié, dépôt propre. **Aucun GO esthétique global auto-proclamé : nous ferons la recette.**

**Critère de passage :** on reconnaît enfin, en ouvrant l'application, la qualité d'un vrai explorateur graphique : **navigation gauche élégante et lisible**, cadres qui respirent, sans perdre la sobriété du menu et le bon travail sur la Liste/inspecteur. Les validations de formulaire sont discrètes et les confirmations destructives sont courtes.

**Après validation de MG-002b-06 seulement :** on reprendra les idées de David pour les **vues Détaillée et Mosaïque**, les couvertures et personnalisations ; l'extension Chrome viendra plus tard. **Ne commence aucune de ces étapes ici.**
