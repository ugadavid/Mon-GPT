# MG-004a — Reprendre là où j'en étais (état de l'interface)

**Statut : mission à réaliser, puis recette utilisateur.**  
**Base :** `origin/main`, commit `57bbe5f05dcae78ad28ea21e1c83a7c94a341687` (Mon GPT<3 0.4.0 ; **92 tests réussis**). MG-004 / Vue Détaillée validée.  
**Position dans la feuille de route :** petit lot **fonctionnel**, **avant MG-005 Mosaïque** ; aucune nouvelle vue créée ici.

## 1. Besoin exprimé par l'utilisateur

Aujourd'hui, l'application rouvre dans la dernière vue **Liste** ou **Détaillée**, mais perd le reste. L'utilisateur souhaite **retrouver l'espace de travail tel qu'il l'a laissé** :

1. **Texte du champ de recherche** ;
2. **Projet/périmètre sélectionné dans la colonne gauche** (y compris Tous les fils ou À classer) ;
3. **Fiche/résultat sélectionné dans le panneau central**, avec **son aperçu restauré** dans la colonne droite si l'inspecteur est ouvert ;
4. **Filtres actifs** (tags et catégories) pour que les résultats restent identiques ;
5. **État développé/replié des projets dans l'arborescence**, afin de retrouver les mêmes branches ouvertes.

**Déjà persistants et à conserver :** dernière vue, état ouvert/fermé de l'inspecteur, géométrie de la fenêtre.

Décision de l'utilisateur : **en cas d'état invalide ou illisible, revenir à la vue et à l'espace par défaut**, comme le mécanisme actuel de `ui_state.py` — sans dialogue intrusif, sans planter, sans réinitialiser le catalogue. **Ne pas lancer de discussion ChatGPT au démarrage** !

## 2. Où et comment stocker

L'application utilise `<data-dir>/interface.json` pour les préférences d'interface. `mon_gpt/ui_state.py` stocke aujourd'hui `version: 1`, `view: "list"|"detail"`, `inspector: bool`, `geometry`. La fermeture dans `App.close()` écrit ces préférences via l'écriture atomique existante.

**Étendre CE fichier**, séparé du catalogue métier (`schema: 2`). Exemple indicatif (noms exacts libres, sémantique obligatoire) :

```json
{
  "version": 1,
  "view": "detail",
  "inspector": true,
  "geometry": "1360x820",
  "query": "voyage",
  "tag": "Idées",
  "category": "Imaginaire",
  "scope": "PROJECT_ID_OR_all_OR_unfiled",
  "selected": "RECORD_ID_OR_NULL",
  "expanded_projects": ["PROJECT_ID"]
}
```

- **Compatibilité ascendante :** le fichier d'interface historique avec seulement `view`, `inspector`, `geometry` doit continuer de fonctionner normalement : propriétés manquantes = valeurs par défaut, **pas de message d'erreur** pour une ancienne version saine.
- Valider les types/bornes des nouveaux champs (texte, listes, identifiants, tailles raisonnables) avant leur application. Si le fichier est corrompu ou mal formé, **fallback de l'interface complète vers l'état par défaut**, avec le comportement discret actuel du statut — **jamais de remplacement, de remise à zéro ni de suppression du catalogue métier**.
- Un identifiant de projet/fiche anciennement enregistré peut ne plus exister dans le catalogue. **Ne pas inventer une sélection fantôme** ; revenir à une situation valide (par défaut `Tous les fils` et aucune fiche sélectionnée), sans exception. Une fiche existante mais exclue par le périmètre/recherche/filtre restaurés ne doit pas être artificiellement affichée : retirer sa sélection (et mettre l'aperçu dans l'état vide correspondant) ou replier vers l'état par défaut de façon cohérente.
- Dans `interface.json`, utiliser seulement les **identifiants locaux de fiches/projets**, jamais les URL ChatGPT, les images ni les notes ; ce fichier de confort n'est pas inclus dans les sauvegardes du catalogue.
- Sauvegarder les préférences **à la fermeture réussie**, APRÈS la protection `can_leave()` pour les changements non enregistrés. Conserver l'écriture atomique et le comportement de gestion d'échec déjà existants.

## 3. Restauration : ordre important pour éviter les réinitialisations involontaires

Au lancement, `App.__init__()` construit les widgets, peuple l'arbre via `refresh_tree()`, charge les résultats via `refresh_results()`, puis ouvre éventuellement l'inspecteur. **Un chargement trop tôt effacerait les sélections restaurées.**

Ordre attendu :
1. Charger le catalogue comme aujourd'hui, sans changement métier ; lire/valider les préférences.
2. Créer l'interface et installer la vue choisie (Liste/Détaillée).
3. Restaurer **recherche et filtres**, puis **périmètre de l'arbre** et **branches ouvertes** ; remplir les résultats avec ces critères.
4. Restaurer la **sélection centrale** seulement si la fiche existe ET apparaît dans ce jeu de résultats ; sinon aucune sélection fantôme. **Faire défiler pour rendre visibles** le projet et la fiche restaurés, si nécessaire.
5. Restaurer l'inspecteur à l'état précédent ; si ouvert et sélection valide, afficher **l'aperçu en lecture seule** de cette fiche, avec bandeau/identité visuelle correspondant. Si aucun élément valide, présenter l'état vide cohérent.
6. Éviter que les événements Tk `<<TreeviewSelect>>`, les `trace` de `StringVar` et les rafraîchissements initiaux **écrasent** le périmètre/filtre/sélection pendant cette phase : garde temporaire ou ordre d'initialisation adapté.
7. Ne surtout **pas** appeler `open_thread`, ne pas cliquer sur un titre par programmation, ne pas appeler le navigateur ni écrire dans `ouvertures-recette.log` au démarrage.

**Remarque :** une sélection de projet à gauche et une sélection de fil au centre sont **deux états différents** ; il faut sauvegarder/restaurer les deux, pas remplacer l'un par l'autre. Les fils restent dans le panneau central, **pas** à ajouter dans l'arborescence gauche.

Les modifications non enregistrées de l'éditeur ne sont **pas** à ressusciter après fermeture : le mécanisme existant `can_leave()` assure leur traitement avant d'écrire le dernier état. La restauration réouvre un **aperçu**, pas un formulaire d'édition à moitié rempli.

## 4. Préparer le mode Mosaïque sans le développer

- La sérialisation de `view` doit rester **extensible**, avec une valeur/machine à états claire. Aujourd'hui les valeurs admises restent `list` et `detail` ; **ne pas activer `mosaic` avant MG-005**.
- MG-005 devra pouvoir ajouter `mosaic` à cette préférence sans changer la logique de recherche, de sélection, d'aperçu ou de reprise de session.
- **Une seule source de vérité** pour filtres, scope et sélection, partagée entre les vues. Ne pas créer une copie du contexte par mode.

## 5. Frontières strictes

**Ne pas modifier** les graphismes et la composition des vues Liste/Détaillée, la navigation gauche, les couvertures, les icônes, le bandeau, la présentation de l'inspecteur, le menu « Windows plus plus », la recherche et sa logique, la déduplication des conversations, les gestuelles DnD, le schéma JSON 2, les imports d'images, ni les ZIP.

**Aucun nouveau bouton, popup ou réglage utilisateur** nécessaire : la reprise doit être automatique. Aucun nettoyage/sauvegarde recommandé de données fictives, aucun téléchargement ni collecte des vrais chats. Les modifications portent principalement sur `ui_state.py`, `ui.py` et des tests ciblés ; pas de réécriture de l'application.

## 6. Recette réelle obligatoire et critères d'acceptation

Sur **CODEX-VM** avec un catalogue fictif de recette isolé, `--simulate-open`, vérifier les gestes réels après fermeture/reouverture de l'application (pas seulement des mocks) :

1. En **Détaillée**, dans un sous-projet, définir `query = "voyage"`, un tag et une catégorie (avec des données de démonstration qui donnent au moins un résultat), sélectionner un fil **dans la Liste centrale**, afficher l'aperçu droit, développer deux branches supplémentaires. Fermer normalement ; rouvrir : **recherche, filtres, branche gauche, sélection centrale, aperçu et vue** identiques ; bonne vignette héritée.
2. Même scénario en **Liste** : reprendre le dernier périmètre et le dernier fil, la même recherche, l'inspecteur fermé puis ouvert. Aucun résultat ne doit être ouvert automatiquement.
3. **Modes/résultats :** basculer entre Liste et Détaillée avant la fermeture : la vue finalement active est restaurée, avec **la même fiche** et ses filtres. La future Mosaïque utilisera exactement ce contrat.
4. **Arbre développé/replié** : un projet parent fermé avant la sortie doit rester fermé ; les autres branches explicitement ouvertes restent ouvertes. La sélection restaurée reste atteignable ; ne pas rouvrir arbitrairement toutes les branches au premier `refresh_tree`.
5. **Préférences historiques** contenant seulement `version/view/inspector/geometry` : démarrage normal en mode conservé et les nouvelles propriétés à leurs valeurs par défaut.
6. **Préférences corrompues, types invalides, `view` inconnu** : retour à l'interface par défaut et statut non intrusif, catalogue intact, application opérationnelle.
7. **Projet/fil supprimé** ou sélection centrale ne correspondant plus au résultat filtré : ouverture sûre, pas de fantôme, aucune trace d'erreur, et aperçu vide au besoin.
8. **Protection d'édition** : avec des changements non sauvegardés, Annuler la fermeture doit laisser application et préférences inchangées ; accepter la fermeture doit restaurer la dernière situation valide.
9. Journal simulé : **aucune ouverture ChatGPT au lancement** ; les liens restent fonctionnels après le clic explicite de l'utilisateur.

**Tests :** conserver les **92 tests existants**, ajouter des tests unitaires `ui_state` (rétrocompatibilité, validation, défaut, écriture), tests UI ciblés (scope, filtrage, sélection, inspecteur, branches, démarrage sans ouverture) et recette Windows réelle.

**Livrables :** `reports/MG-004a/rapport.md` bref, résultat des tests, deux ou trois captures de l'état **avant fermeture / après redémarrage** au même contexte, cas de fichier ancien/corrompu ; README ajusté si nécessaire ; commit/push `origin/main`, SHA distant vérifié, dépôt propre. **Stop après MG-004a** : MG-005 Mosaïque viendra après notre recette.

**Critère de réussite en une phrase :** fermer Mon GPT<3, puis le relancer doit redonner **le même lieu, les mêmes résultats et la même fiche en aperçu**, sans ouvrir le moindre fil ni modifier les données métier.
