# Mon GPT<3 — MG-002 · Spécification UX et charte « Atelier chaleureux »

**Statut :** décisions de conception validées le 14 novembre 2026 ; document de référence pour les étapes de réalisation.  
**Base applicative :** MG-001 / Mon GPT 0.1.0 — Windows, Python/Tkinter, catalogue JSON local.  
**Principe :** trouver une discussion et **ouvrir son fil ChatGPT d'un geste** ; consulter ou modifier sa fiche est secondaire.  
**Important :** ce document décrit la **cible UX complète**. La mission d'exécution associée `02_mission_codex.md` limite volontairement sa **première livraison au socle commun et à la vue Liste** ; ne pas confondre cible finale et périmètre de développement immédiat.

## 1. Les trois maquettes déposées par l'utilisateur

Les trois PNG sont **déjà présents dans ce répertoire**. **Les conserver tels quels** ; ne pas les remplacer, renommer, transcoder, copier dans le code ni les re-publier inutilement.

- `Image ChatGPT 14 nov. 2026, 11_51_22-1.png`
- `Image ChatGPT 14 nov. 2026, 11_51_54-2.png`
- `Image ChatGPT 14 nov. 2026, 11_51_55-3.png`

Ils proposent des variations complémentaires de l'**explorateur rapide**, de la **bibliothèque avec aperçu** et du **gestionnaire fluide**. **Ne pas en choisir une à reproduire à l'identique** : en retenir le langage graphique et les bons gestes. Les maquettes sont des références d'intention, **la présente spécification prévaut** en cas de libellé, bouton ou comportement contradictoire. Codex peut consulter ces images **localement** sur CODEX-VM ; ne pas les recharger en blobs via le chat ou un outil de publication.

## 2. Charte visuelle commune

Nom : **Mon GPT<3** ; signature secondaire facultative « Votre organisation, en local ».

| Token | Usage | Valeur |
| --- | --- | --- |
| Ivoire | surface principale | `#F7F3EA` |
| Sable | surfaces secondaires / fonds doux | `#E7D9C5` |
| Vert sapin | actions primaires, sélection, navigation | `#315E4F` |
| Terracotta | accent ponctuel, action d'ouverture, survol maîtrisé | `#C87A50` |
| Encre | texte principal | `#292D30` |

- Typographie claire, proche de **Lexend** dans l'esprit ; préférer les polices déjà disponibles et un repli système lisible, **ne pas embarquer de fichiers de polices**.
- Icônes homogènes, sémantiques et facultatives sur chaque objet ; coins doux, séparations subtiles, contrastes lisibles, focus clavier évident.
- Illustrations de couverture **utiles comme repères**, pas une décoration massive dans les vues compactes.
- Contrôles adaptés au redimensionnement et à l'agrandissement Windows ; titres longs, accents, contrastes et états vides réellement lisibles.
- Animations discrètes et facultatives, jamais nécessaires pour comprendre un geste.
- Définir des constantes de thème réutilisables pour éviter de disperser les couleurs dans les widgets.

## 3. Modèle visuel des objets

### 3.1 Projets et sous-projets

| Propriété | Disponible | Obligatoire | Valeur par défaut |
| --- | --- | --- | --- |
| Nom | Oui | Oui | saisie de l'utilisateur |
| Couverture | Oui | **Oui** | image fournie par l'application, immédiatement attribuée |
| Icône | Oui | Non | icône générique si rien choisi |
| Couleur | Oui | Non | thème ou couleur de la couverture |
| Description | Oui | Non | vide |

**Le fait que la couverture soit obligatoire ne signifie jamais que l'utilisateur doit choisir une image pour créer un projet.** Une couverture par défaut existe immédiatement. Chaque projet possède ainsi un repère visuel même s'il n'a jamais été personnalisé.

Une **galerie locale intégrée** propose plusieurs ambiances (écriture, voyage, exploration, laboratoire, création, technique, etc.). L'utilisateur peut ensuite **importer sa propre image**, ou revenir à une couverture fournie. Les illustrations de la galerie ne sont pas les trois maquettes d'interface.

**Contraintes à présenter dans l'interface** : formats proposés **JPG/JPEG, PNG, WebP** ; paysage **16:9 conseillé**, **1200 × 675 px** comme taille de référence. Un plafond de poids/dimensions et un comportement de recadrage ou ajustement devront être **fixés et affichés avant l'import** ; ne pas annoncer de limite comme validée si elle ne l'est pas. Un import invalide ou trop lourd doit être refusé lisiblement, sans détruire l'ancienne couverture. Pas d'obligation de concevoir un éditeur d'images.

### 3.2 Fils / discussions

Un fil peut avoir son icône, sa couleur et une couverture **facultatives**. **Par défaut, il hérite du repère visuel du projet parent**. Un choix personnalisé remplace cet héritage jusqu'à ce que l'utilisateur choisisse « Revenir à l'héritage ».

Un même fil peut appartenir à **plusieurs projets** sans être dupliqué. Il faut définir un **rattachement principal** pour l'identité visuelle dans une vue globale (ou une règle explicite et prévisible tant que cette préférence n'existe pas) ; dans un projet donné, son héritage doit rester compréhensible. Un fil non classé reçoit le repère générique de l'application. **Ne pas modifier silencieusement les rattachements pour choisir une couverture.**

**Persistance future :** le catalogue MG-001 est un **schéma JSON strict `schema: 1`** ; un ajout de propriétés visuelles nécessite une évolution de schéma et des migrations testées, sans perte des anciens enregistrements. Ne pas simplement injecter de nouvelles clés non reconnues. Les images appartiennent à un stockage local sûr et à une stratégie de sauvegarde/restauration explicite ; ne pas mélanger contenu binaire et URL ChatGPT. **MG-002 première livraison : utiliser des ressources visuelles par défaut sans imposer une migration prématurée du catalogue.**

## 4. Architecture de l'écran

- **Barre de menus compacte** : `Fichier` (sauvegarder le catalogue, restaurer, dossier de données, quitter), `Édition`, `Affichage`, `Aide`. **La sauvegarde/restauration du catalogue sont rares et ne prennent plus de gros boutons permanents**.
- **Recherche universelle unique**, visible et rapide, commune aux trois vues : titres, descriptions/résumés, notes, tags, catégories, métadonnées, projets, selon la recherche existante. Proposer suggestions et filtres sous forme de pastilles dans le même parcours, **pas trois champs textuels séparés**.
- **Colonne gauche** : arborescence de projets/sous-projets, `Tous les fils`, `À classer` ; tri manuel/alphabétique préservé ; zone de dépose visible ; menu contextuel.
- **Zone centrale dominante** : résultats, sélection, ouverture directe d'un fil et choix du mode Liste / Détaillée / Mosaïque. La place est donnée aux conversations, **pas à un formulaire**.
- **Inspecteur droit facultatif** : résumé utile et informations complémentaires, **replié/masquable** ; possibilité d'ouvrir une édition détaillée volontairement, sans imposer le panneau complet.
- Disposition redimensionnable ; recherche, sélection et filtres gardés lors d'un changement de vue. Dernière vue et état d'inspecteur mémorisés **sans altérer le catalogue métier**.

## 5. Gestes utilisateurs — contrat prioritaire

### 5.1 Retrouver puis ouvrir

**Geste principal = ouvrir le fil d'un clic.**
- Dans la liste : un clic sur **le titre actif ou son icône d'ouverture** ouvre le lien ChatGPT après validation ; un clic ailleurs dans la ligne ne fait que sélectionner.
- Double-clic sur la ligne et `Entrée` lorsqu'un résultat est focalisé : ouvrent aussi le fil. Le clavier dans un champ de recherche ou d'édition **ne doit pas déclencher une ouverture**.
- L'inspecteur fournit `Ouvrir le fil` / `Copier le lien`, mais il n'est **jamais nécessaire** pour ouvrir.
- Un **projet** se sélectionne et se développe ; il ne possède pas l'action `Ouvrir le fil`.
- Toute ouverture conserve les protections MG-001 : URL HTTPS `chatgpt.com` reconnue, aucune commande shell ni accès aux contenus des chats.

### 5.2 Créer et modifier dans le contexte

- Création depuis un petit menu `+`, le clic droit sur un projet/racine, le menu `Édition`, et des raccourcis documentés.
- **Pas de popup modale** pour la création ordinaire. Un projet est créé via une **ligne éditable insérée dans l'arbre** ; un fil via une **zone intégrée** à la liste (titre et URL au minimum).
- `Entrée` pour valider selon le champ ; `Échap` annule sans créer d'entrée fantôme.
- Pour une édition détaillée (résumé, notes, métadonnées), ouvrir volontairement l'inspecteur ou une zone latérale/pliable ; préserver les alertes de modifications non enregistrées de MG-001.
- Les confirmations de **suppression**, d'**écrasement de catalogue** et de sortie avec changements peuvent demeurer modales pour sécurité : la règle « pas de popup » concerne les opérations ordinaires de création/édition, pas les alertes nécessaires.

### 5.3 Déplacer et rattacher sans duplication

- **Glisser bouton gauche** un projet vers un autre projet / racine : **changer le parent** ; empêcher les cycles et le déplacement sous soi-même ; préserver l'ordre manuel.
- **Glisser bouton gauche** un fil vers un projet : **déplacer son rattachement depuis le contexte d'origine** vers la destination, sans supprimer la fiche. Pour un fil ayant plusieurs rattachements, **ne pas retirer implicitement les autres** : préciser quel lien est déplacé.
- **Glisser bouton droit** un fil vers un projet : à la dépose, **menu contextuel** `Déplacer ici` / `Ajouter un rattachement ici` / `Annuler`. L'option « Copier » signifie **ajouter un rattachement au même fil**, jamais dupliquer la discussion, ses notes ou son identité.
- Pour un projet, seul `Déplacer` est actuellement défini : l'architecture MG-001 est un arbre à **parent unique** ; ne pas inventer de multi-parent/copie de projet.
- Mise en évidence du projet cible et des cibles interdites ; aucun changement de données avant la dépose confirmée. Si l'interface Tk ne permet pas de garantir le glisser droit, fournir un **menu contextuel avec les mêmes actions** et signaler honnêtement la limite, sans mode trompeur.
- Conserver l'accès sans DnD par menu contextuel et clavier.

### 5.4 Tags, catégories et recherche

- Tous les **tags et catégories existants** sont proposés par autosuggestion et sélection (chips), avec ajout d'une nouvelle valeur si absente.
- Respecter la distinction : **projets/emplacements** (rattachements), **catégories** (classification), **tags** (étiquettes). Une catégorie ne devient jamais automatiquement un dossier.
- Recherche unique avec suggestions et filtres combinables ; éviter les doublons lorsqu'une même fiche apparaît dans plusieurs projets.
- Le résultat reste filtré au projet sélectionné **et à ses descendants**, sauf choix explicite de recherche globale.
- Garder la normalisation de recherche français insensible à la casse/accents.
- Pas de nouvel index cloud ni d'import automatique des messages ChatGPT.

### 5.5 Menus et raccourcis

**Proposition de raccourcis à tester, en évitant tout conflit existant :**
- `Ctrl+K` recherche universelle ; `F2` renommer ; `Ctrl+N` nouveau fil ; `Ctrl+Maj+P` nouveau projet ; `Entrée` ouvrir résultat actif ; `Échap` annuler/fermer une édition intégrée.
- **`Ctrl+S` reste « Enregistrer les modifications de la fiche »** tel qu'en MG-001 ; ne pas le réattribuer à la sauvegarde complète du catalogue. `Fichier > Sauvegarder le catalogue...` est une action distincte.
- Menus contextuels `Ouvrir`, `Renommer`, `Déplacer`, `Ajouter un rattachement`, `Modifier`, `Retirer ce rattachement`, `Supprimer...` selon le type/état de la sélection.
- Donner des retours visibles non intrusifs : rattachement ajouté, déplacement effectué, annulation, échec. Ne pas demander de confirmation pour chaque geste réversible.

## 6. Trois modes de présentation au centre

| Vue | Repère visuel | Densité et priorité |
| --- | --- | --- |
| **Liste** | **Icône uniquement** | Lignes compactes, colonnes utiles et triables, titre cliquable / action ouvrir immédiate ; aucun grand visuel |
| **Détaillée** | **Petite vignette + icône** | Lignes aérées, nom, contexte, extrait de résumé, tags/catégories |
| **Mosaïque** | **Grande couverture + icône** | Cartes illustrées, reconnaissance visuelle forte, texte court ; éventuellement deux tailles de cartes |

Les **mêmes trois modes s'appliquent au catalogue**, non à trois jeux de données. La sélection, le tri pertinent, la recherche et les filtres persistent lors du changement de vue. La logique du clic, du clavier et du classement reste cohérente. Les vues Détaillée et Mosaïque sont des **étapes ultérieures** si non comprises dans la mission d'exécution courante.

**Principe mémorable : Liste = efficacité · Détaillée = équilibre · Mosaïque = plaisir visuel.**

## 7. États et confort

- États vides explicites : aucun projet, aucune recherche trouvée, fil sans URL valide, fil non classé, aucun tag existant.
- Un clic de sélection ne doit jamais écraser une édition non enregistrée ; conserver le contrôle d'abandon/annulation existant.
- La navigation clavier, le focus, les menus contextuels et les actions visibles doivent être cohérents en mode fenêtre réduite.
- Favoriser des intitulés compréhensibles et une indication claire de l'action qui modifiera le **catalogue local** versus celle qui ouvrira ChatGPT.
- Les couvertures et vignettes servent de repères, pas d'obstacles à la navigation.

## 8. Frontières fermes

Aucune modification des conversations dans ChatGPT ; aucune collecte Chrome, aucune nouvelle extension, aucun service réseau, aucune nouvelle base métier. Préserver : schéma JSON existant et règles de migration explicite, sauvegarde/restauration, recherche et déduplication d'URL, ordre manuel/alphabétique, rattachements multiples, suppression sûre, séparation `core.py` / `chatgpt.py` / `storage.py` / `ui.py`.

**Ce texte est une référence UX validée : toutes ses fonctionnalités ne sont pas des tâches à implémenter simultanément. Voir le périmètre MG-002 dans `02_mission_codex.md`.**
