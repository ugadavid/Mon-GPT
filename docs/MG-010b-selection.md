# Sélectionner et classer des discussions

Mon GPT<3 **0.9.2a** : une fiche ou vingt, les mêmes gestes dans Liste, Détaillée et Mosaïque.

| Geste dans les résultats | Effet |
| --- | --- |
| Clic sur titre, icône, image ou ligne | Sélectionne une fiche sans ouvrir ChatGPT. |
| Ctrl+clic | Ajoute ou retire une discussion. |
| Maj+clic | Sélectionne la plage dans l’ordre visible après tri et filtres. |
| Ctrl+Maj+clic | Ajoute cette plage au lot. |
| Ctrl+A, résultats focalisés | Sélectionne tous les fils des résultats, même hors écran, sans les projets. Dans un champ, sélectionne le texte. |
| Flèches / Maj+flèches | Navigue / étend la sélection ; Mosaïque respecte les colonnes. |
| Échap | Réduit le lot sans fermer l’aperçu, après les traitements d’édition/popup/drag. |
| Glisser gauche vers un projet | Déplace le rattachement de la fiche ou de tout le lot, immédiatement. |
| Glisser droit vers un projet | Même menu Déplacer ici / Ajouter un rattachement ici, pour une ou plusieurs fiches. |
| Clic droit / touche Menu | Actions individuelles ou groupées selon la sélection. |
| Clic explicite sur ↗ | Ouvre ce fil uniquement, sans détruire le lot. Ctrl/Maj restent des gestes de sélection. |
| Alt+Entrée | Active explicitement ↗ du fil focal. En Liste/Détaillée, droite focalise aussi ↗ ; Entrée active alors cette action. |
| Double-clic / Entrée sur titre, ligne ou carte | Aucune ouverture ChatGPT. Un projet reste navigable. |

Le bandeau de lot contient uniquement son compteur et **Désélectionner**. L’aperçu devient neutre. F2, Ctrl+S et l’édition restent individuels : sélectionner une seule fiche pour les utiliser.

Commencer un glisser sur un fil déjà sélectionné prend **tout le lot** ; commencer hors du lot sélectionne et déplace ce seul fil. Ctrl/Maj+clic ne lancent pas de glisser. Le passage entre vues conserve le lot ; tri et filtres le limitent aux fils encore visibles. Changer de projet vide la sélection. Aucun lot n’est restauré au redémarrage.

## Classement

- **Déplacer** retire uniquement la source commune et ajoute la destination, en préservant les autres emplacements et leur ordre. Depuis un projet, celui-ci est la source s’il est directement commun à tous les fils. Depuis Tous les fils, une unique source commune suffit. S’il en reste plusieurs, un petit choix demande **quel emplacement remplacer**, puis Déplacer applique directement. Sans source commune, choisir un lot homogène ou Ajouter. Un lot entièrement À classer reçoit son premier rattachement. Source = destination : aucun changement.
- **Ajouter un rattachement** conserve tous les anciens emplacements et ignore un lien déjà présent. **Copier signifie ajouter un emplacement, jamais créer une seconde fiche.**
- **Retirer un rattachement** enlève cette seule source commune ; les fiches sans autre emplacement deviennent À classer. Aucune fiche supprimée.

Le menu contextuel conserve le sélecteur avec aperçu des conséquences : choisir les emplacements, puis **Appliquer**. Il se ferme après application. Le glisser connu ne demande aucune confirmation ; le menu du glisser droit exécute directement son choix.

Les choix affichent les noms/chemins. Seuls des libellés réellement identiques reçoivent un petit numéro déterministe selon les identifiants locaux. Les UUID intégraux restent internes, sans fusion d’homonymes.

Une fiche ou un lot utilise le même moteur : plan pur, candidat détaché et **une seule écriture atomique**. Aucun enregistrement pour un no-op. UUID, URL, notes, tags, catégories, autres personnalisations, mappings, images et sauvegardes sont préservés ; seules les dates de modification des fils reclassés évoluent. Les projets gardent leur déplacement individuel dans l’arbre.

[Rapport et captures fictives](../reports/MG-010b-01/rapport.md).
