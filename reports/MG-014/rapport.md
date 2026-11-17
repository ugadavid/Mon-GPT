# MG-014 — Mon GPT<3, papier et sauge

Recette sur CODEX_VM, avec Mon GPT<3 0.9.4 et un catalogue temporaire fictif. Les six captures montrent le même projet « Écriture », les mêmes six discussions et la même sélection. La fenêtre mesure 1440 × 884 pixels hors barre de titre.

| Vue | Avant MG-014 | Après MG-014 |
| --- | --- | --- |
| Liste et fiche « Au seuil du jardin » | [Avant](avant-liste.png) | [Après](apres-liste.png) |
| Détaillée et inspecteur | [Avant](avant-detaillee.png) | [Après](apres-detaillee.png) |
| Mosaïque et inspecteur | [Avant](avant-mosaique.png) | [Après](apres-mosaique.png) |

## Comparaison avec la maquette

Le carnet illustré occupait une vignette à l’extrémité du bandeau. Il occupe maintenant le centre, entre la signature « Des idées plein les poches. » et les informations du projet. Les trois colonnes commencent sous le même menu. La fiche de droite présente le titre, les repères visuels et les actions de la sélection réelle. [Maquette de référence](../../missions/MG-014-graphisme/Interface%20GPT%20vert%20sauge%20et%20espace%20d%E2%80%99%C3%A9criture.png)

Dans la Liste, la sélection sauge et l’alternance papier donnent un repère horizontal. Les catégories se lisent en texte et les tags gardent leurs pastilles. Les six points et A–Z partagent la ligne « Votre espace ». Le retour de dépose apparaît pendant le glisser. Le nombre de discussions figure à côté de « Contenu du projet ».

## Adaptations visibles

- La silhouette organique s’applique au bandeau des illustrations livrées. Les images personnelles gardent leur cadrage entier, même en portrait. Les cartes Détaillée et Mosaïque conservent aussi la scène entière.
- La barre de création en bas ouvre le formulaire intégré et donne le focus au titre. Le lien ChatGPT et sa validation sont nécessaires à la création. Les catégories et tags se renseignent dans l’éditeur existant.
- Le rendu Tk utilise des aplats et des filets fins. Les ombres sont moins diffuses que sur la maquette. Les colonnes visibles dépendent des préférences du catalogue de démonstration. En largeur compacte, le bandeau réduit l’image et l’inspecteur peut placer les actions sous les repères visuels.

## Recette Windows

Les commandes ont été exercées dans la fenêtre Tk. Les deux tris ont conservé le projet courant. Replier puis rouvrir l’aperçu a retrouvé la même fiche. La recherche par titre a isolé un fil et l’effacement a rétabli les six résultats. La barre inférieure a refusé un lien incomplet puis créé un septième fil dans le projet attendu. Les trois vues sont restées utilisables à 1000 × 680.

Le menu + a également ouvert la création de sous-projet au clavier, puis Échap a annulé le brouillon. La suite `python -m unittest discover -s tests -v` a réussi ses **203 tests en 253,371 s**. Elle couvre notamment les glissers gauche et droit par événements Tk, la sélection multiple, les rattachements, les sauvegardes et la restauration. Les assertions graphiques du bandeau vérifient désormais les bords des images personnelles et l’absence de chevauchement avec le texte.
