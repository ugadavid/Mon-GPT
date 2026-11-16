# Personnaliser les colonnes de la Liste

Dans **Affichage → Colonnes de la liste…**, cocher les colonnes souhaitées, puis utiliser **Monter / Descendre** pour les ordonner. Les colonnes masquées peuvent aussi être réordonnées avant de les réafficher.

**Appliquer** prend effet et mémorise les réglages. **Fermer** ignore les changements non appliqués. **Valeurs par défaut** prépare la configuration initiale ; cliquer Appliquer pour l’utiliser. Le panneau reste accessible depuis Détaillée et Mosaïque, dont il ne modifie pas la présentation.

| Colonne | Présentation |
| --- | --- |
| Titre | Toujours visible et épinglé à gauche, avant les colonnes secondaires. |
| Projet | Emplacements locaux de la fiche, y compris ses rattachements multiples. |
| Catégories / Tags | Pastilles colorées. |
| Création | Date de création de la fiche locale Mon GPT<3. |
| Modification | Dernière modification de cette fiche locale. |

Au départ : **Titre / Projet / Catégories / Tags**. Les deux dates sont facultatives et masquées. L’icône d’identité et **↗** restent fixes, hors des colonnes configurables.

Glisser un séparateur d’en-tête ajuste sa largeur. Le curseur et la poignée indiquent la limite active. La largeur est mémorisée au relâchement, sans enregistrement à chaque pixel. Les colonnes cachées ne réservent aucun espace.

Dans une fenêtre étroite, le titre s’adapte à l’espace disponible et ↗ reste à droite. La barre horizontale fait défiler les colonnes secondaires **sans changer leur ordre**. Une colonne cochée reste dans cette bande défilante.

Cliquer un en-tête trie ; cliquer de nouveau inverse le sens. Les dates sont triées sur leurs horodatages réels, avec les minutes et fuseaux. Elles ne représentent **pas** les dates d’origine des conversations ChatGPT. La cellule montre date et heure si elles tiennent, sinon la date complète ; un fragment trop étroit affiche « … », sans année tronquée. Le survol donne les deux dates complètes avec secondes et fuseau.

Masquer la colonne du tri actif via Appliquer revient au tri Titre. Le tri partagé de Détaillée/Mosaïque propose aussi les dates. En revenant à la Liste avec un tri masqué, le tri revient à Titre et le statut l’indique.

Visibilité, ordre, largeurs et tri sont conservés dans **`interface.json` version 1**, avec les autres préférences : recherche, filtres, projet, branches, aperçu et vue. Les anciens fichiers v1 restent valides. Une configuration de colonnes incorrecte revient aux colonnes par défaut en conservant les autres préférences valides.

Aucun changement des fiches, dates métier, mappings ou images ; ces préférences ne sont pas incluses dans le ZIP métier. Les [gestes validés](MG-010b-selection.md) restent identiques : sélection multiple, glisser gauche/droit, F2, clic sur titre pour sélectionner et **↗ seul pour ouvrir**.
