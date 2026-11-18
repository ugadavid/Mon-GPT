# MG-014d — Bandeau, vues et création rapide

Sur CODEX_VM, le même projet fictif « Écriture » a été affiché avec la même discussion sélectionnée et l’inspecteur ouvert. La signature garde sa place. La couverture grandit jusqu’à 580 px et la colonne d’informations reçoit la largeur restante.

| Fenêtre | Bandeau central | Contenu observé |
| --- | --- | --- |
| 1000 × 680 | 434 px | Présentation compacte, deux tags visibles et indicateur des sept autres repères. |
| 1440 × 884 | 799 px | Extrait de description, trois catégories et quatre tags visibles. |
| 3840 × 2160 simulée | 3199 px | Description intégrale de 114 caractères, quatre catégories et cinq tags visibles. |

La grande largeur a été obtenue en dimensionnant la vraie fenêtre Tk sur la VM. La comparaison montre la portion dessinée de chaque bandeau et sa barre de commandes. Les trois vues partagent une surface bordée à 30 px du bouton d’effacement. [Comparer les trois largeurs](01-bandeau-trois-largeurs.png)

Dans le formulaire, l’erreur de saisie utilise une terre cuite discrète. « Annuler · Échap » précède l’action sauge « → Ajouter » de 20 px. [Voir la création avec un lien incomplet](02-creation-lien-incomplet.png)

## Recette L1

- Clic successif sur Détaillée, Mosaïque et Liste avec conservation de la sélection.
- Lien incomplet refusé, formulaire encore ouvert. Annulation par bouton, par Échap et par clic dans la recherche. Le clic extérieur a donné le focus à la recherche et le nombre de fiches est resté identique.
- Création par Entrée avec un lien valide et vérification du rattachement au projet courant.
- Dix tests ciblés réussis, couvrant les colonnes et la recherche compacte, le cadrage des couvertures personnelles, la distinction entre contexte et sélection, les changements de vue et leur persistance, les doublons et l’annulation du brouillon. Le test ajouté vérifie également qu’un clic dans le formulaire ou dans une fenêtre fille conserve le brouillon et qu’un clic sur une vue l’annule tout en activant la vue.
- Contrôles statiques des modules Python modifiés, du diff et des liens des captures. La suite complète a été omise conformément au périmètre L1.
