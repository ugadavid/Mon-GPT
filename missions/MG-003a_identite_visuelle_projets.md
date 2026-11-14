# MG-003a — Identité visuelle des projets : image, icône, couleur et bandeau contextuel

**Statut : mission à réaliser, soumise à la recette de David après livraison.**  
**Base :** Mon GPT<3 0.2.1, `origin/main` au commit `68369dfe881152086c4fe4890377020c2afec53c` (MG-002b-01 à 06 terminées et validées).  
**But :** permettre à l'utilisateur de se repérer par les **images, les icônes et les couleurs** de ses projets, et faire réellement vivre ces repères **dans la fiche du projet et dans la vue Liste**. Les vues Détaillée et Mosaïque viendront **après**.

## 1. Ce que nous avons décidé ensemble — à respecter

> « Il faut que ça fasse partie du projet. On n'a aucune raison de l'isoler. On ajoute les champs image, icône et couleur directement là. »

> « Image ouvre un layer avec plusieurs propositions d'images, idem pour icônes, couleur un sélecteur de couleurs (peut-être 16 couleurs bien choisies). La seule différence étant qu'images offre la possibilité à l'utilisateur d'ajouter la sienne. »

> « L'image pourrait directement apparaître à la place de la petite illustration [prairie, arbres et livre] quand je sélectionne un projet, une fiche. Elle réapparaîtrait dans la vue Mosaïque. »

**Il ne s'agit PAS de développer un gestionnaire séparé de thèmes, une boîte de dialogue de préférences, ni une nouvelle application.** Ces **trois propriétés appartiennent au projet lui-même**, et se modifient dans la **fiche de projet existante** (mode Édition).

### Contrat simple

| Propriété du projet | Choix utilisateur | Par défaut |
|---|---|---|
| **Image de couverture** | Galerie locale ou **Importer mon image** | **Toujours une belle couverture fournie par Mon GPT<3** sans saisie obligatoire |
| **Icône** | Petite galerie d'icônes au trait homogènes | Icône générique automatiquement visible ; choix personnel facultatif |
| **Couleur** | **Palette de 16 nuances choisies** (pas de roue RGB) | Couleur Atelier chaleureux du thème ; choix personnel facultatif |

**Fils / discussions** : pour ce lot, **héritage automatique** des repères du projet auquel le fil appartient, **sans ajouter trois champs de personnalisation au fil**. Les préférences propres à un fil restent prévues plus tard. Un fil sans projet utilise le repère de l'application. Un fil à plusieurs rattachements n'est **pas dupliqué** et n'en perd aucun pour obtenir son image.

## 2. Les gestes : trois sélecteurs intégrés à la fiche

Dans `Modifier la fiche` d'un **projet**, ajouter trois zones sobres, compactes, harmonisées avec les champs déjà validés :

- **Image** : vignette actuelle + action `Choisir`. Elle ouvre **dans la fenêtre** un *layer* / panneau temporaire présentant **plusieurs vraies images distinctes** fournies localement. Une vignette sélectionnée est prévisualisée ; un bouton `Importer mon image…` permet de choisir un fichier personnel. `Par défaut` et `Annuler` sont accessibles.
- **Icône** : aperçu de l'icône + action `Choisir`, puis **galerie réduite** d'icônes cohérentes. Choix facultatif, retour à l'icône générique. **Pas de grille de milliers d'icônes/émojis de styles incohérents**.
- **Couleur** : pastille actuelle + `Choisir`, puis une **grille 4×4 de 16 couleurs harmonisées** (vert sauge/sapin, terracotta, sable, bleu doux/pétrole, lavande, rose doux, ocre, etc.). Nom/infobulle de chaque nuance, sélection visible, retour à la valeur par défaut. **Aucun color picker système de 16 millions de couleurs**.

**Layer = intégré à l'expérience actuelle**, pas une grosse popup indépendante « Créer une personnalisation ». Il doit se fermer par `Échap`, un clic de fermeture/annulation, et rester navigable à la souris/clavier. On doit pouvoir personnaliser un projet sans interrompre inutilement le parcours.

**Sémantique d'enregistrement :** les choix font partie de la même fiche et suivent **Enregistrer / Ctrl+S**, la gestion `dirty` et l'avertissement des modifications non enregistrées existants. `Annuler` le layer revient au choix précédent, `Revenir à l'aperçu` sans enregistrer conserve la protection MG-001. Pas de sauvegarde silencieuse des autres champs.

### Galerie de couvertures

- Fournir initialement un **petit lot réellement joli et différencié** (par exemple 6 à 8 paysages/ambiances originales : carnet-écriture, voyage, montagne/exploration, laboratoire, création, technique, etc.). Les références visuelles sont dans `missions/MG-002-maquettes/` ; **ne PAS transformer ces trois maquettes d'interface en couvertures**, ni les dupliquer/committer à nouveau.
- Les couvertures du pack sont **locales, intégrées à l'application** et accessibles hors connexion ; créer des illustrations originales légères, cohérentes avec **ivoire/sapin/terracotta**, sans téléchargement de stock ou emprunt d'œuvres non autorisées.
- **Format paysage 16:9 conseillé, 1200×675 px comme guide**, qualité d'image suffisante à la fois pour la vignette et pour les futures mosaïques. Le rendu s'adapte à la place disponible sans déformer l'image.
- Pour `Importer mon image…`, annoncer à l'utilisateur **avant sélection** les formats `PNG, JPG/JPEG, WebP`, la taille recommandée et les limites maximales que tu fixes de façon raisonnable, explicite et testée. Vérifier contenu réel et taille, ne pas faire confiance à l'extension seule. Un import invalide laisse l'ancienne couverture intacte.
- **La couverture d'un projet est obligatoire en résultat, pas en manipulation** : aucun formulaire ne doit bloquer `Nouveau projet` parce que l'utilisateur n'a pas choisi d'image.

## 3. La petite illustration supérieure devient CONTEXTUELLE

**Vue Liste actuelle uniquement** : dans la zone centrale où se trouve aujourd'hui le minipaysage « prairie/soleil/arbres/livre », afficher **la couverture du projet sélectionné**, à la place de ce paysage. **Ne pas remplacer le titre Mon GPT<3 ni créer une bannière géante** ; même place, mêmes proportions générales et marges validées.

Règle de sélection simple et déterministe :

1. Si l'utilisateur **sélectionne un projet** dans l'arbre ou une fiche projet : montrer la couverture **de ce projet**.
2. S'il sélectionne une **discussion**, montrer la couverture du projet dont elle hérite. Dans le contexte d'un projet actif auquel ce fil est rattaché, **préférer ce projet**.
3. Dans `Tous les fils` / recherche globale, si la discussion possède plusieurs rattachements, choisir pour le moment le **premier rattachement conservé dans son ordre existant** (règle stable et documentée ; surtout pas de réécriture de ses rattachements). Si elle n'est rattachée nulle part : image générique.
4. Si aucun projet/fil n'est choisi : garder **le paysage actuel** comme état neutre de l'application, ou couverture générique cohérente.

Une modification enregistrée de l'image/couleur/icône doit être visible immédiatement dans le bandeau et au retour à la Liste. Le bandeau ne doit ni clignoter ni nécessiter de redémarrer.

**Prévoir une fonction unique de résolution des repères (image/icône/couleur)** réutilisable plus tard par Détaillée/Mosaïque ; **ne pas implémenter ces deux vues maintenant**.

## 4. Données, migration et sauvegarde : attention, ne rien perdre

Le catalogue actuel est un JSON strict **`schema: 1`** : `mon_gpt/core.py`, `storage.py`, `chatgpt.py`. Des champs nouveaux ajoutés sans migration rendraient les archives illisibles.

- Introduire la **plus petite évolution versionnée explicite** compatible (par ex. `schema: 2` pour métadonnées visuelles de projet), sans déplacer les champs ChatGPT dans le modèle générique. Migration **1→2** testée, sans perte d'identifiants, projets, rattachements, tags, notes, ordre, URL. **Copie de sécurité avant toute mutation du catalogue ancien**, et refus explicite des versions futures inconnues. Ne jamais « recréer vide » en cas d'erreur.
- **Ne pas stocker un chemin absolu vers le fichier importé par l'utilisateur comme seule référence** : l'image doit continuer à fonctionner si le fichier d'origine est déplacé ou supprimé. Faire une copie locale sûre de l'image sélectionnée, dans un dossier de ressources applicatif hors Git et hors code.
- **Ne pas se contenter d'un export JSON qui oublie silencieusement les images personnelles.** Garder la **lecture des sauvegardes JSON historiques** et définir une **sauvegarde portable complète** contenant les données et images référencées (par exemple une archive ZIP sûre pour les données+assets, en préservant un import compatible avec l'ancien JSON). L'UI peut offrir cette sauvegarde complète par défaut ; si un export texte JSON subsiste sans images, il doit être **identifié sans ambiguïté comme incomplet pour les images**.
- À la restauration d'une sauvegarde complète, valider les fichiers, références et limites **avant remplacement**, conserver une sauvegarde préalable complète de l'existant, ne pas écraser arbitrairement des ressources partagées et garantir cohérence des références en cas d'échec. Contrôler les noms/chemins contenus dans une éventuelle archive (pas de traversée de chemin/zip-slip).
- Tester également que supprimer/remplacer une image de projet ne supprime pas la ressource encore utilisée par un autre projet, et que les anciennes sauvegardes sont correctement lues.
- La galerie fournie avec l'application doit être disponible même **sans assets personnalisés** et **sans aucun accès réseau**. Ne pas versionner les photos personnelles, les vrais liens ChatGPT ni les données de recette.
- **Une dépendance légère de décodage d'image, telle que Pillow, est acceptable** si nécessaire pour JPG/WebP, validation et vignettes ; dans ce cas documenter clairement les prérequis, installer/vérifier sur CODEX-VM et préserver le lancement sur Windows. Ne pas simuler la prise en charge de WebP/JPEG si elle ne fonctionne pas.

**Ces contraintes sont nécessaires parce que l'image fait désormais partie des données du projet.** Pas de moteur universel d'assets, de serveur, de plugins ou de fonction d'édition d'images sophistiquée.

## 5. Périmètre strict (ne pas rouvrir MG-002b)

**Autorisé :** fiche de projet et sélecteurs intégrés, modèles/persistance nécessaires à l'identité visuelle, galerie locale, import personnel et sauvegarde complète, rendu **contextuel de la seule illustration centrale**. L'héritage simple vers les fils doit fonctionner pour cette illustration.

**Figé :** menu principal « Windows plus plus », recherche unique, Liste centrale et ouverture ↗ en un clic, dimensions/gouttières des trois colonnes, arborescence et glisser-déposer, aperçu/éditeur de fils, tags et catégories, dialogues pastel et confirmations courtes. Ajuster seulement ce qui est indispensable pour afficher les nouveaux champs dans les fiches **projet**.

**Hors mission :** vues Détaillée et Mosaïque, couvertures individuelles des fils, couleurs personnalisées par fil, extension Chrome, synchronisation ChatGPT, import automatique de fils, changement des URL/doublons, refonte des notes, généralisation du thème de toute la fenêtre.

## 6. Recette, preuves et verdict

Sur **CODEX-VM**, avec données **entièrement fictives** dans un `--data-dir` dédié, ne jamais travailler sur le catalogue utilisateur normal :

1. Créer un projet sans personnaliser : **couverture par défaut visible**. Ouvrir sa fiche, changer image intégrée, icône et couleur dans leurs trois petits sélecteurs, Enregistrer ; retour à l'aperçu, ferme/réouvre : valeurs conservées.
2. Sélectionner projet → la **petite illustration du centre change** ; sélectionner son fil → même identité héritée ; autre projet → autre identité ; `Tous les fils` avec fil lié à 2 projets → règle stable ; fil `À classer` → image générique.
3. Choisir une image personnelle `PNG`, puis `JPG` et `WebP` fictifs valides, supprimer/renommer les originaux et redémarrer : la copie utilisée par le projet reste disponible ; fichier malformé, trop gros ou dimension excessive refusé avec message clair **sans effacer la couverture**.
4. Annuler un layer, modifier sans enregistrer puis revenir/fermer : protections/confirmations existantes conservées ; clavier, `Échap`, navigation et focus.
5. Ouvrir un **catalogue v1 fictif**, le migrer sans perte avec sauvegarde de sécurité ; ouvrir une archive JSON ancienne ; faire sauvegarde complète avec image personnelle, restaurer dans un **nouveau data-dir isolé**, vérifier contenu image, couverture, icône, couleur et tous les champs/relations ; archive volontairement corrompue refusée sans altération.
6. **Régression :** rechercher, ouvrir un fil simulé depuis son titre/icône, trier/déplacer les projets, changer de fil, ajouter tag/catégorie, ouvrir/fermer inspecteur. Aucune rupture des gestes ni des marges validées.
7. Fenêtre **1360×820**, **1000×680** et maximisée : image contextuelle bien proportionnée, sélecteurs utilisables et pas de contrôle masqué.

Maintenir les **65 tests existants** (les adapter uniquement pour la migration si nécessaire), ajouter des tests ciblés visualisation, héritage, import et validation, v1→v2, sauvegarde/restauration complète, relecture réelle, préservation des liens et sécurité des chemins.

**Livrables :** `reports/MG-003a/rapport.md` (résultats et limites, matrice de recette et **3–5 captures réelles** : fiche projet et galerie, palette/icônes, bandeau avec 2 projets distincts, format compact si utile). Conserver les maquettes inchangées. Actualiser README/architecture/version si nécessaire, commande de lancement exacte, prérequis éventuels, compatibilité des sauvegardes. Commit/push `origin/main` sans forcer, SHA distant vérifié et dépôt propre.

**GO développement** seulement si le projet peut choisir et conserver réellement image/icône/couleur, le bandeau est contextuel, les données v1 restent récupérables et l'export/restauration préservent les images personnelles. Si un de ces points manque, **PARTIEL explicite** plutôt qu'un faux GO.

**Ne commencer aucune autre mission** sans validation de David et GPT. Les futures vues Détaillée et Mosaïque exploiteront ces trois données, déjà présentes ; elles ne sont **pas** dans ce lot.
