# MG-014c — Contexte et re-sélection du projet courant

Sur CODEX_VM, la sélection de « Au seuil du jardin » dans la Liste a affiché la discussion et son contexte « Écriture ». Un clic sur « Écriture » dans l’explorateur a ensuite rétabli la fiche du projet. Le périmètre, le filtre « Brouillon », les résultats, l’ouverture de la branche et le rattachement du fil ont été vérifiés avant et après ce clic.

- [Projet racine après le re-clic](01-racine-apres-reclic.png) — le titre court est suivi directement des repères visuels. Un tiret indique l’absence de parent dans la rubrique Emplacements.
- [Projet enfant](02-projet-enfant.png) — le pictogramme du titre est centré sur la première ligne du titre à deux lignes. Le nom et le pictogramme du parent apparaissent en retrait sous le titre.

Le re-clic est traité au relâchement sur la même ligne. Les notifications de sélection émises par une restauration ou un rafraîchissement de l’arbre gardent leur comportement. Un test de régression exerce la pression et le relâchement sur le projet déjà sélectionné.

## Vérifications L1

Les 12 tests ciblés ont réussi sur Windows. Les cinq tests de `test_inspector` couvrent notamment la nouvelle régression, les actions clavier et les notes longues. Sept tests voisins couvrent la navigation dans l’arbre, le contexte du projet, la restauration de sélection, l’aperçu replié, l’édition en cours, la sélection multiple et les emplacements multiples. La recette graphique utilise uniquement des données fictives.

La compilation des trois fichiers Python modifiés, le diff et les liens des captures ont également été vérifiés. La suite complète a été omise conformément au niveau L1 demandé.
