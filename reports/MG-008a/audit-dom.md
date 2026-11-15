# Audit DOM préalable — MG-008a

Audit effectué avant modification du collecteur, le 15 novembre 2026.

## Sources et constat

- Lecture de l’adaptateur, du cœur, du runtime, du dépôt, des points d’entrée Chrome et de la popup MG-008.
- Relecture sur GitHub de [3GPT3 / analyse DOM](https://github.com/ugadavid/3GPT3/blob/main/docs/dom-analysis.md), blob `dee053488ef303f294d0e5a5f6cdd5060df49760`, et du [scanner](https://github.com/ugadavid/3GPT3/blob/main/src/scanner/dom-scanner.js), blob `3fe95b68cda06c332edbeb5b02335e79ce538e4d`. Dépôt source non modifié.
- Cette analyse de juin 2026 constate des boutons projets, des actions secondaires et des liens enfants `/g/g-p-…/c/UUID`. Elle ne prouve **pas** que le parent arbitraire d’un lien soit toujours le bon projet. Le scanner historique ne relie pas les noms aux clés.
- Audit du ChatGPT public réellement chargé dans un profil Chrome neuf : origine `https://chatgpt.com`, chemin `/`, 7 conteneurs de navigation, **0 lien projet**, **0 attribut projet** dans la navigation. Aucun compte connecté ; aucune bibliothèque personnelle inspectée.

## Politique décidée avant code

| Surface rendue | Preuve exigée | Confiance logique |
| --- | --- | --- |
| Lien d’accueil projet | URL stricte `/g/g-p-…` ou `/g/g-p-…/project`, nom sur ce même lien | Forte, directe |
| Contrôle projet | `data-project-id` ou `data-project-key` strict sur un bouton/treeitem, nom propre de ce contrôle ; rejeter les clés contradictoires | Forte, directe, attribut à confirmer sur Chrome connecté |
| Page projet ouverte | URL d’accueil projet stricte, un seul `h1` visible dans le contenu principal, aucune URL de conversation | Forte sous ce contrat de page ; raccord actuel à confirmer |
| Projet développé | Treeitem et son groupe enfant, bouton contenant ses liens, ou relation réciproque `aria-controls` / `aria-labelledby` ; pas de sous-projet concurrent ; tous les liens enfants utilisables ont **une même clé** | Prudente, inférieure à une preuve directe ; forme réelle à confirmer |
| Lien de fil portant une clé seule | Clé valide réellement présente dans son URL | Identité connue, nom inconnu |
| Voisinage, nom de fil, ordre, noms identiques, section globale, clés d’enfants discordantes | Aucune preuve suffisante | Aucun nom associé |

Les exemples de DOM de la recette seront **des fixtures**, pas des extraits prétendument actuels de ChatGPT connecté. Ni noms tirés des titres de fils, ni suppression approximative de préfixes d’action, ni classes générées, React ou API privée. Aucun clic/scroll automatique. Les conflits de noms de même niveau dans un scan restent inconnus ; les preuves faibles n’effacent pas une observation plus fiable.

**Faisabilité :** l’enrichissement est possible sur les surfaces explicitement vérifiables. **PARTIEL sur association nom/GUID du vrai compte** tant que David n’a pas effectué la procédure connectée. Un nom absent vaut `null`, jamais une supposition.
