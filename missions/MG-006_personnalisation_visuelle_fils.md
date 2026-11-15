# MG-006 — Personnalisation graphique des fils : Image, Icône, Couleur, héritage indépendant

**Statut : mission à réaliser puis recette par David et GPT.**  
**Base vérifiée :** `origin/main`, commit `1c5d4d7199a78a38e6fd8b619747f6d3f5492dc6`, Mon GPT<3 **0.5.0**, **108 tests réussis**.  
**Décision utilisateur :** les trois vues Liste / Détaillée / Mosaïque restent en place, sans retouche esthétique. Les fils gagnent les **mêmes trois possibilités que les projets**. La grande passe graphique sera confiée ultérieurement à un spécialiste.

## 1 — EXIGENCE PRIORITAIRE : NE PAS RÉINVENTER LA ROUE

> « Mêmes trois champs graphiques que les projets, on peut leur affecter une image, une icône, une couleur. »  
> « Qu'il ne réinvente pas la roue, qu'il se serve de ce qui existe pour les projets niveau code et présentation !! »

**La mission est fonctionnelle et d'intégration, PAS une nouvelle mission de graphisme.**

Le code livré contient déjà :
- `mon_gpt/identity_ui.py` : `ProjectVisualStrip`, `ProjectVisualFields`, `IdentityControl`, `VisualLayer`, `ChoiceTile`, `ControlTip`, `contained_picture` ;
- `mon_gpt/identity.py` : `COVERS`, `ICONS` (36), `PALETTE` (16), `DEFAULTS`, `VisualIdentity`, `resolve_identity`, `validate_visual`, `image_references` ;
- `mon_gpt/project_icons.py` : pictogrammes/couleurs et caches ;
- `mon_gpt/images.py` : images intégrées/personnelles, validation, copies locales ;
- `mon_gpt/details.py` : `render_editor()`, `save_record()`, validation, `dirty` ;
- `mon_gpt/results.py` et `mon_gpt/mosaic.py` : couvertures et repères actuellement fournis par le résolveur unique ;
- `mon_gpt/storage.py` : catalogue JSON strict et sauvegarde ZIP complète.

**Réutiliser ces composants et leurs actifs EXACTEMENT**. Factoriser proprement la petite différence « projet avec valeurs propres / fil avec héritage et surcharges » par paramétrage ou mince adaptation du code existant. **Pas de deuxième `VisualLayer`, de seconde galerie, de nouvelle palette, de nouvel ensemble d'icônes ni de deuxième moteur de sauvegarde.** Si besoin, renommer/refactoriser `ProjectVisualFields` en contrôle générique avec compatibilité pour les projets.

**Même présentation** : une **seule rangée compacte de trois commandes** Image, Icône, Couleur dans la fiche d'édition d'un fil, au même endroit logique que dans la fiche projet ; mêmes dimensions, styles, survols, focus, interactions et sélecteurs. Ne pas demander trois en-têtes de champs, trois nouvelles fenêtres ou des boutons multiples « Choisir ».

## 2 — Contrat de données : hériter par défaut, surcharger séparément

**Projet :** `visual` définit ses propres propriétés comme aujourd'hui (les défauts restent ceux de l'application). Rien à modifier dans sa logique.

**Fil :** `visual` contient UNIQUEMENT les propriétés explicitement personnalisées parmi `image`, `icon` et `color`.

- **Absence de clé = hérite** de la propriété du projet de référence. `visual: {}` signifie que les **trois** propriétés sont héritées.
- Une clé présente représente un **choix local explicite** ; même si sa valeur est égale à la valeur héritée du moment, ce choix reste explicite et ne change pas lorsque le projet change.
- Chaque propriété est indépendante : un fil peut prendre sa **propre image** tout en héritant **l'icône et la couleur** de son projet, ou les trois, ou aucune.
- Dans **chaque sélecteur du fil**, proposer la commande explicite **« Revenir à l'héritage »** qui supprime **uniquement cette clé** de `visual`. Pour un projet, conserver « Par défaut » qui revient aux valeurs génériques — **ne jamais confondre hériter et valeur par défaut**.
- Prévisualiser la **valeur effective** ET distinguer sobrement « Héritée » / « Personnalisée » (info-bulle ou petit libellé non intrusif). Un clic sur « Revenir à l'héritage » doit montrer immédiatement la valeur actuelle du projet sans modifier les deux autres propriétés.
- Les choix passent par **Utiliser → brouillon de la fiche → Enregistrer/Ctrl+S** et les protections de sortie actuelles. `Annuler`/Échap le layer ne modifie aucun choix ; abandonner le brouillon n'enregistre rien. Les données existantes (titre, notes, URL, tags, catégories, rattachements) restent intactes.

**Détermination du projet hérité :** reprendre la fonction et la règle établies `resolve_identity(catalog, identity, scope)` :
1. Si le fil est directement rattaché au projet **actif dans l'arborescence gauche**, utiliser ce projet comme base d'héritage ;
2. Sinon, utiliser son **premier rattachement** conservé dans son ordre actuel (notamment dans `Tous les fils`) ;
3. Si le fil est **À classer**, utiliser l'identité générique de l'application, dont la couverture « Prairie au soleil » ;
4. Appliquer par-dessus les **trois surcharges locales éventuelles, clé par clé**.

**Impératif :** cette résolution est **pure**, fonctionne dans les trois vues comme dans le bandeau et l'inspecteur, et **ne déplace, ne duplique ni ne modifie** aucun rattachement. Si le projet change de couleur/image, les propriétés héritées des fils suivent le changement ; les propriétés personnalisées restent identiques. Si le fil change de projet, seules les propriétés héritées changent. L'héritage est calculé, **jamais matérialisé en recopiant trois valeurs dans le fil**.

## 3 — Fiche d'édition ET aperçu des discussions

- Activer sur chaque **fil** la même rangée de trois contrôles que sur un **projet**, sans toucher à la densité du reste de l'éditeur. Une couverture personnelle importée se sélectionne via **la galerie existante** et les mêmes contrôles d'import/validation.
- Pour les fils, l'infobulle de chaque contrôle peut dire `Image · Héritée de « Atelier des idées »` ou `Image · Personnalisée`, idem Icône/Couleur ; si aucun projet, `Héritée du défaut`. Éviter les chemins longs et les labels répétés.
- L'**aperçu en lecture seule** d'un fil doit montrer discrètement ses trois repères **effectifs**, exactement comme celui d'un projet actuellement équipé de `ProjectVisualStrip`. Pas d'éditeur supplémentaire ni de nouveau panneau.
- Le passage **Aperçu → Modifier → Enregistrer → Aperçu** met à jour la petite identité affichée immédiatement, avec les règles `dirty` et de sauvegarde existantes.
- Les projets doivent **rester identiques**, au clic comme dans la forme. Régression zéro sur leur personnalisation.

## 4 — Effets immédiats dans les trois vues et le bandeau

Une seule résolution visuelle doit alimenter les résultats et le bandeau :

- **Liste :** l'icône de fil devient son icône effective dans sa couleur effective, **sans élargir la ligne ni changer les hitboxes** ; ouverture directe et colonnes inchangées.
- **Détaillée :** la petite couverture, l'icône et la couleur reflètent la combinaison héritée/personnalisée.
- **Mosaïque :** chaque carte utilise **sa propre couverture si choisie**, sinon la couverture héritée, ainsi que son icône/couleur effectives. Deux fils d'un même projet avec deux images personnalisées doivent donc afficher **deux images différentes**. Conserver les tailles Normal / Grand, le titre et les gestes existants ; **ne pas enrichir/redessiner ici le contenu des cartes**.
- **Bandeau central :** lorsque le fil est sélectionné, utiliser la même identité visuelle effective. L'image reste entière en 16:9, sans recadrage.
- **Projet sélectionné dans l'arbre :** inchangé. Les fils restent dans le panneau central, **pas dans l'arborescence gauche**.
- Actualiser les caches/vignettes, la sélection et l'aperçu après enregistrement/changement de contexte, sans images périmées ; aucune nécessité de redémarrage.

**Rappel** : nous laissons volontairement la Mosaïque visuellement sommaire pour la future passe graphique ; MG-006 ajoute la personnalisation des fils, **pas une nouvelle présentation**.

## 5 — Schéma, migration et ZIP : ne pas casser le socle

**État réel actuel :** `Record.visual: dict` existe déjà sur toutes les fiches, mais `validate_visual(..., kind="item")` **refuse expressément tout dictionnaire non vide**. Le schéma actuel est strict (`schema: 2`). `image_references(catalog)` inclut aujourd'hui les images importées **des projets seulement**.

**Travail requis :**
- Autoriser pour un fil les trois clés optionnelles reconnues, avec les **mêmes identifiants et validations** (`pack:...`, `asset:<sha256>`, icône connue, couleur connue) et **refuser les clés ou valeurs inconnues**. `visual: {}` des fils existants doit continuer à représenter l'héritage complet.
- Puisque le schéma 2 actuel **interdit ces valeurs pour les fils**, préférer une **évolution explicite du format (schéma 3)**, avec migration sûre des catalogues v1/v2 vers v3 et **copie préalable fidèle** avant réécriture. Anciennes sauvegardes JSON v1/v2 et ZIP v2 doivent rester restaurables. Ne pas laisser un ancien programme interpréter silencieusement un schéma v2 aux règles devenues incompatibles.
- Protéger les identifiants, l'ordre des projets, les UUID de conversations, les URL, tags, notes, métadonnées et rattachements. Les projets v2 explicitement personnalisés restent strictement identiques.
- Étendre `image_references` et le parcours de validation/sauvegarde ZIP afin d'inclure les **images personnelles référencées par les fils** (y compris si aucun projet ne les utilise). Les références d'images importées continuent de désigner une copie locale immuable ; supprimer/modifier un fil ne doit pas détruire une image partagée avec un projet ou autre fil.
- La sauvegarde complète ZIP doit retrouver après restauration **les surcharges partielles**, les images propres aux fils, leurs fichiers et les héritages effectifs. Un ancien JSON sans image personnelle reste lisible ; un export incomplet est refusé explicitement comme aujourd'hui.
- Ne pas ajouter de nouveaux types de fichiers, d'accès réseau, de tables supplémentaires, de service externe ni de deuxième gestionnaire d'assets.

Si une variante technique plus simple garde **effectivement** cette compatibilité et cette sécurité, la justifier brièvement dans le rapport avant de l'utiliser. **Le contrat observable prévaut : on ne perd ni les anciens catalogues ni les personnalisations.**

## 6 — Tests ciblés et vraie recette Windows

Conserver **les 108 tests existants**, avec adaptations limitées aux assertions de version de schéma qui doivent évoluer ; ajouter des cas précis sans réécrire toute la suite.

**Sur un catalogue fictif**, vérifier :

1. Projet A : image Montagne, icône Boussole, couleur Pétrole. Un fil F rattaché à A sans `visual` propre : les trois sont hérités dans **Liste, Détaillée, Mosaïque, bandeau et aperçu**.
2. Pour F, ne personnaliser que **l'image** (choisir « Voyage » ou importer un PNG personnel) : image nouvelle dans Détaillée/Mosaïque/bandeau, mais icône Boussole et couleur Pétrole toujours héritées. Fermer et rouvrir : même résultat.
3. Personnaliser uniquement **l'icône**, puis uniquement **la couleur**, puis les trois ; changer dans A la couleur ou l'image : seules les propriétés encore héritées changent chez F.
4. **« Revenir à l'héritage » sur Image uniquement** ; Icône et Couleur personnalisées restent intactes. Répéter l'opération sur les deux autres commandes. Vérifier la suppression effective de la clé dans le JSON, pas l'enregistrement de la valeur copiée.
5. F a deux rattachements A et B (identités visuelles contrastées). Dans A, il hérite de A ; dans B, de B ; dans `Tous les fils`, du **premier rattachement** ; les surcharges de F restent constantes, un seul UUID/contenu de fil. Déplacement d'un rattachement et changement du contexte ne réécrivent pas le visuel.
6. Fil **À classer** : hérite du soleil et des repères par défaut, mais peut choisir son image/icône/couleur propres. Retour à l'héritage ramène bien au générique.
7. Import PNG/JPEG/WebP personnels via **les sélecteurs existants**, fermeture de l'original puis réouverture de l'application. Sauvegarder ZIP, restaurer dans **un nouveau data-dir fictif** : référence et image personnelle du fil conservées. Ressource corrompue ou manquante refusée sans détériorer l'ancien catalogue.
8. **Migration d'un catalogue v2 réel de recette** et d'un ancien v1, restauration d'un ZIP v2 : nouveaux fils `visual: {}` valides, personnalisation projets conservée, backup préalable exact, protection des versions futures. Contrôler les anciennes URL et tous les rattachements.
9. **Gestes de non-régression** : Enregistrer/Ctrl+S, Annuler/Échap, avertissement de sortie, sélection d'un autre fil, recherche, tri, Liste ↔ Détaillée ↔ Mosaïque, tailles Normal/Grand, menu contextuel, ouverture simulée par titre/↗, glisser d'un fil sans perte de relations et reprise de session MG-004a/MG-005.
10. Vraies fenêtres **1360×820, 1000×680 et maximisée**, inspecteur ouvert/fermé ; la rangée Image/Icône/Couleur reste compacte et fonctionnelle, y compris pour les fils à plusieurs projets.

**Recette dans la vraie application Tk** sur CODEX-VM, pas seulement mocks. Au moins **3 à 5 captures natives** :
- éditeur de **fil** montrant les trois contrôles réutilisés ;
- layer de fil avec **« Revenir à l'héritage »** pour une propriété ;
- deux fils du **même projet** affichant **deux couvertures différentes en Mosaïque**, et aperçu du fil ;
- écran dans un second projet qui montre l'héritage dynamique ;
- format compact si pertinent.

Publier `reports/MG-006/rapport.md`, tests, éventuelles notes de migration et commande de lancement. Commit/push `origin/main`, SHA distant vérifié, dépôt propre ; **validation de l'utilisateur uniquement** après recette.

## 7 — Frontières strictes

**Ne pas redessiner** la colonne gauche, le menu « Windows plus plus », la Liste, Détaillée, Mosaïque (géométrie, titre, badges, cartes), le bandeau, l'inspecteur hors son petit repère effectif, ni les sélecteurs. **Ne pas créer d'illustrations, d'icônes ni de couleurs supplémentaires**. Ne pas modifier le cœur du classement, les URL, le système de préférences, l'ouverture ChatGPT ou les règles de glisser-déposer. Aucun développement d'extension Chrome, aucune grosse refonte UX.

**Critère de réussite :** trois commandes **identiques à celles des projets** sur les fils ; chaque commande hérite ou se personnalise **indépendamment**, et les trois vues + le bandeau affichent toujours la bonne combinaison, **persistante et restaurable**.

**Ne commence rien d'autre après MG-006.** Nous ferons la recette, puis déciderons des prochaines étapes du projet.
