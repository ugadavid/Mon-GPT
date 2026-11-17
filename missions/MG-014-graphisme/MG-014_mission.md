# MG-014 — Donner à Mon GPT<3 sa véritable identité graphique

**GO pour la réalisation — 17 novembre 2026.** Nouveau fil Codex, application Windows existante. **Une seule maquette de référence** : [Interface GPT vert sauge et espace d’écriture.png](Interface%20GPT%20vert%20sauge%20et%20espace%20d%E2%80%99%C3%A9criture.png).

## Le défi

Nous avons terminé et validé le fonctionnement de Mon GPT<3 0.9.4. Il manque une vraie identité visuelle. **Reproduis aussi fidèlement que raisonnablement possible l'esprit, la composition, la finesse et la qualité graphique de cette image dans l'application Windows actuelle.** Nous voulons une transformation visible, pas une retouche de trois nuances de beige.

Notre méthode gagnante est celle de **Mon Bureau / MB-003** : un modèle visuel unique choisi ensemble, puis ta liberté de réalisation pour y parvenir. Tu es le directeur artistique chargé de l'adapter proprement au logiciel réel.

**Deux exigences :**
1. **Le fonctionnement existant est gelé** : données, modèles, recherche, sélections, édition, sauvegardes, menus, raccourcis, glisser-déposer, déplacements et rattachements conservent exactement leur sens et leurs effets. N'invente ni ne supprime de fonctionnalités. Utilise le code et les contrôles existants ; les modifications d'affichage et de présentation nécessaires à la maquette sont autorisées.
2. **Préserve le squelette des trois colonnes sur toute la hauteur sous le menu** : explorateur à gauche, centre (bandeau, recherche, Liste, création), inspecteur à droite. **Ne transforme jamais le bandeau en une rangée pleine largeur au-dessus des trois colonnes.** Le menu supérieur n'existe qu'une fois.

**Aucun blanc absolu `#FFFFFF`**, y compris les surfaces de cartes : nous préférons les ivoire/papier/sauge doux de l'image. Icônes de préférence fines et cohérentes.

## Comment lire la maquette

C'est une **cible graphique**, pas la source de données ni un nouveau cahier des charges fonctionnel. Les noms, dates, nombres et exemples affichés sont illustratifs. La Liste doit afficher les données réelles du jeu actif ; la fiche de droite doit suivre la sélection réelle (projet ou discussion). **Le bandeau du centre montre les informations du projet courant**, et sa couverture peut suivre un fil sélectionné selon le contrat MG-011. Ne confonds pas les deux zones.

Conserver les fonctions derrière les commandes existantes en changeant leur présentation :
- tri manuel / alphabétique de l'explorateur sous forme d'icônes, dont **six points** pour le manuel ;
- menu de création existant (Nouveau fil / Nouveau projet) et contrôle d'aperçu présentés près du logo ;
- filtres/effacer, modes Liste/Détaillée/Mosaïque, recherche et commandes contextuelles allégés par des icônes reconnaissables, avec noms accessibles/infobulles ;
- inspecteur avec titre réel en haut, actions regroupées et sections douces ; ne pas inventer de nouvelles actions ;
- dessin plus agréable du glisser-déposer sans modifier gauche/droite, déplacer/ajouter ou validation des cibles ;
- illustration de projet plus généreuse dans le bandeau central, silhouette organique de l'image, en respectant le fonctionnement des couvertures et la lisibilité des champs ;
- slogan **« Des idées plein les poches. »**.

**Trois dernières retouches souhaitées à la maquette**, à réaliser si compatibles simplement avec l'existant : retirer les deux aides permanentes « Glissez pour classer » et « Clic droit : actions » du bas de l'explorateur (conserver l'aide accessible ailleurs) ; afficher « Contenu du projet » avec le nombre de discussions dans une **petite pastille** ; présenter les catégories dans la Liste comme des **repères textuels discrets, non comme des boutons**. Ne change pas les vrais champs ou interactions de catégories.

La barre de création rapide permanente en bas du centre est une **cible d'ergonomie** de la maquette, pas une autorisation à développer une nouvelle logique de création. Réutiliser le parcours de création intégré, les règles de projet, catégories, tags et raccourcis déjà présents ; si ce déplacement nécessite un développement fonctionnel important, expliquer le compromis et s'arrêter sur ce point plutôt que créer un second système.

**Important** : les missions/rapports MG-013 racontent des essais **rejetés et annulés sur le code** ; ne pas les prendre comme programme de travaux. Partir de l'état courant de `origin/main` (MG-012 fonctionnel + documents/maquette MG-014). Ne pas restaurer ces essais rejetés par inadvertance. Les trois anciennes maquettes MG-002 sont historiques : **ne pas combiner trois directions artistiques concurrentes**.

## Réalisation et recette

- Consulter **visuellement** le PNG de référence, le lancer réellement sur CODEX_VM et prendre quelques captures de l'application avant modifications.
- Réaliser une passe graphique cohérente, avec ta liberté d'exécution, mais sans réécriture métier, migration de framework, dépendance lourde ni architecture nouvelle. Si nécessaire, découper la mise en œuvre en petits commits lisibles, **mais livrer une direction esthétique unifiée**.
- Comparer honnêtement les mêmes écrans **avant/après**, avec au moins Liste + inspecteur, puis Détaillée et Mosaïque pour vérifier la cohérence. Vérifier surtout que les trois colonnes, l'identité projet/fil et les commandes existantes restent intactes.
- Exercer une recette ciblée des interactions visuellement touchées ; respecter également les obligations effectivement en vigueur dans `AGENTS.md` sans ajouter gratuitement d'autres batteries. Utiliser des données fictives et ne publier aucune donnée personnelle.
- Signaler ce qui reste graphiquement différent de la maquette, ce qui est volontairement adapté à Tk, et tout comportement qui aurait nécessité un changement trop important. **Ne prétends pas à une fidélité parfaite sans comparaison visuelle.**
- Publier code, un rapport bref `reports/MG-014/rapport.md` et quelques vraies captures sur `origin/main`. Vérifier commit distant et dépôt propre. **STOP**, attendre la validation visuelle humaine avant de continuer ou de construire un installateur.

**En une phrase : reproduire la maquette choisie, avec ambition graphique et fidélité, sans réinventer notre application.**
