# MG-014e — Espacement du bandeau

Inspecteur fermé, le bandeau réserve progressivement jusqu’à 32 px supplémentaires de chaque côté de l’illustration. Cet espace est pris sur l’image. Le bloc projet garde son point de départ et toute sa largeur de lecture.

| Fenêtre sur CODEX_VM | Illustration, inspecteur fermé | Comparaison du projet fictif « Écriture » |
| --- | --- | --- |
| 1440 × 884 | 366 → 302 px | [Inspecteur ouvert puis fermé](bandeau-1440.png) |
| 3840 × 2160 simulée | 580 → 516 px | [Inspecteur ouvert puis fermé](bandeau-3840.png) |

Les images montrent la portion utile de la vraie fenêtre Tk. En très grande largeur, la description complète, les quatre catégories et les cinq tags tiennent toujours à l’écran.

## Vérifications L1

Six configurations ont été comparées à MG-014d avant et après modification : fenêtres de 1000, 1440 et 3840 px, inspecteur ouvert puis fermé. Les textes effectivement dessinés, les indicateurs de débordement et la hauteur correspondent dans les six cas. La comparaison pixel par pixel de la portion capturée avec l’inspecteur ouvert a donné des images identiques aux trois largeurs.

La compilation des deux modules, le diff et les liens des captures ont été contrôlés. Les quatre tests ciblés de disposition des colonnes, d’ouverture de l’aperçu, de cadrage des couvertures et de contexte du bandeau ont réussi. La suite complète a été omise pour cette correction locale de géométrie.
