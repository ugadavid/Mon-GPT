# MG-014h — Vue Mosaïque

Les deux icônes de grille choisissent la taille des cartes. La taille active apparaît en sauge. La Mosaïque utilise le sélecteur de tri de Détaillée et sa commande ↑/↓, alignés avec la dernière colonne de la grille.

En Petit, le résumé et la note se partagent deux lignes. En Grand, chacun dispose de deux lignes et les dates de création et de modification figurent en pied de carte. Les deux tailles affichent le contexte, les catégories et les tags.

### Comparaison sur CODEX_VM

Même projet fictif, même sélection, même fenêtre de 1440 × 884 pixels avec l’inspecteur ouvert.

| Taille | Avant | Après | Hauteur de couverture |
| --- | --- | --- | --- |
| Petit | [Ancienne carte](avant-petit.png) | [Carte finale](apres-petit.png) | 126 → 54 px |
| Grand | [Ancienne carte](avant-grand.png) | [Carte finale](apres-grand.png) | 198 → 72 px |

[Grand sur une colonne, en fenêtre de 1024 × 780 pixels](grand-compact.png)

### Vérifications

- Treize tests L1 réussis. Ils couvrent notamment les tailles, la navigation dans la grille, le renommage, la sélection et l’ouverture, le tri, la restauration de la préférence, les images personnelles et le rendu limité aux cartes visibles.
- Recette Windows sur six discussions fictives. Activation des deux tailles au clavier, choix de Titre, Catégories et Création dans le sélecteur partagé, inversion et vérification de l’ordre des résultats. Contrôle de la grille avec l’inspecteur ouvert puis fermé, puis navigation au clavier et clic sur ↗ en largeur contrainte avec un ouvreur simulé.
- Compilation ciblée et contrôle du diff Git. La suite complète a été omise conformément au périmètre L1.
