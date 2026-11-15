# Architecture — Mon GPT<3

État actuel : 0.3.1, 15 novembre 2026. Les sections MG-002/MG-002a décrivent leur état historique avant MG-003a ; MG-003b précise les corrections de présentation actuelles.

## Choix techniques

Python 3.13 et Tkinter/ttk : application de bureau Windows sans serveur HTTP. Pillow 13.0.0, ajouté par MG-003a, décode et vérifie les images. Python/Tk et Pillow sont requis sur le poste cible ; aucun installateur autonome. [Tkinter](https://docs.python.org/3.13/library/tkinter.html) fournit les contrôles et dialogues de bureau utilisés.

JSON UTF-8 plutôt que SQLite pour cette première version : catalogue personnel facile à inspecter, exporter et restaurer. Chaque mutation est validée et écrite dans un temporaire du même dossier, avec flush/fsync puis [os.replace](https://docs.python.org/3.13/library/os.html#os.replace). Une erreur laisse l'ancien fichier intact ; l'interface revient aussi à son état métier précédent et conserve la saisie. Le verrou Windows `msvcrt.locking` garde une seule instance écrivaine et se libère à la fin du processus, même brutalement. La durabilité face à une panne matérielle complète dépend du système de fichiers et de son cache ; cela ne remplace pas une sauvegarde hors machine.

## Frontières concrètes

| Module | Responsabilité | Dépendances internes |
|---|---|---|
| `core.py` | `Record`, `Catalog`, identités, hiérarchie, ordre, rattachements, recherche commune | Aucune |
| `chatgpt.py` | URL, UUID distant, déduplication, entrée `ChatGPT.ingest` | Catalogue reçu par injection ; aucune UI ou persistance |
| `storage.py` | Schéma applicatif, validation, sérialisation, verrou, export/restauration | Socle et modèle de l'adaptateur |
| `ui.py` | Affichage, formulaires, confirmations, transactions applicatives, navigateur | Socle, adaptateur, stockage |
| `__main__.py` | Assemblage et chemin des données | Stockage et interface |

La fiche générique ne contient **aucune URL ou identité ChatGPT**. `Record` possède UUID interne stable, type projet/fiche, titre, description/résumé, notes, tags, catégories, dictionnaire texte, dates zonées, parent/ordre pour les projets et emplacements pour les fiches. Toutes les relations utilisent les UUID internes. Les parcours d'arbre sont itératifs, sans plafond métier de profondeur. Le socle se teste seul avec des fiches génériques ; un test AST interdit les dépendances UI, stockage et ChatGPT.

`Conversation(record_id, conversation_id, url)` est une collection séparée jointe par UUID interne. La déduplication compare l'UUID distant normalisé ; titre et notes restent locaux. Le point d'entrée `ChatGPT.ingest(title, url)` retourne `(fiche, créée)` : une future collecte pourra l'appeler depuis l'orchestration applicative. Aucun serveur ou extension dans cette version. L'ouverture revalide l'URL et appelle `webbrowser.open` avec l'URL comme donnée ; l'application ne compose pas de commande shell.

La recherche du socle ne connaît que les champs communs et métadonnées. Normalisation Unicode NFKD, suppression des marques diacritiques, casefold et traitement de œ/æ. Le filtre projet inclut les descendants, résultat unique par UUID. Le tri d'affichage ne modifie jamais `order` ; les commandes manuelles le modifient explicitement.

## Schéma et cohérence

Racine actuelle : `schema: 2`, `records: […]`, `chatgpt: […]`. Le décodeur vérifie champs obligatoires, types, UUID, unicité, dates zonées, parents présents, absence de cycles, rattachements et identités ChatGPT cohérentes. Toute fiche applicative a exactement une entrée ChatGPT, chaque projet aucune. Versions inconnues et fichiers illisibles sont refusés sans recréer de catalogue. Le format 1 strict reste décodable ; sa migration ajoute seulement `visual: {}` aux fiches après copie exacte du catalogue ancien. Le détail des ressources et sauvegardes MG-003a figure ci-dessous.

La restauration valide avant confirmation puis revalide l'objet en mémoire, exporte l'état courant vers une sauvegarde horodatée unique et écrit le nouvel état atomiquement. Une erreur de validation ne produit aucune écriture. La copie préalable demeure si le remplacement échoue. Les exports conservent champs communs, identités, relations, ordre et entrées de l'adaptateur. Le verrou n'est pas une donnée métier.

## Extraction future

Déplacer `core.py` et ses tests génériques dans une bibliothèque commune ; conserver assemblage et adaptateur dans Mon GPT. Le socle n'important rien de l'application, cela demande essentiellement des changements d'import et de packaging. Si un autre produit partage la persistance, extraire ensuite la sérialisation générique de `Record`, chaque application orchestrant ses données de source. Aucun registre de plugins ou moteur universel anticipé.

## Limites

Parcours des collections en mémoire ; un très gros catalogue demandera des mesures, puis éventuellement SQLite. Tri pour les usages français courants, sans collation linguistique exhaustive. Notes et liens en clair dans les exports. La seule activité réseau possible est l'ouverture explicite d'un fil dans le navigateur.

## MG-002 — Coque et interactions de la Liste (0.2.0)

Le moteur `core.py`, l'adaptateur `chatgpt.py`, `storage.py`, le modèle `Record` et les tests MG-001 sont conservés sans modification. **Aucune migration du schéma 1.** Le changement est dans la couche de présentation : `ui.py` orchestre la navigation, les filtres passés à `Catalog.search`, l'ouverture immédiate et les gestes de classement. `details.py` conserve l'édition détaillée et les protections MG-001, désormais appelées volontairement. `theme.py` centralise la charte et génère quelques petites icônes locales ; `widgets.py` fournit le sélecteur de pastilles. Ce sont des composants ttk concrets, sans nouveau moteur ou framework.

Les créations et renommages sont des brouillons UI : ligne superposée à l'arbre ou zone intégrée à la liste. Aucune écriture avant Entrée/bouton explicite ; Échap détruit seulement le brouillon. Les doublons sont vérifiés par l'adaptateur et requièrent une action explicite inline. La confirmation reste liée à l'UUID vérifié, même si l'URL saisie change ensuite.

Le glisser-déposer ne modifie rien pendant le survol : la cible est validée puis marquée. À la dépose, `App.transfer` compose les opérations génériques existantes `Catalog.move`/`attach`. Il ne connaît aucune URL. Pour les fiches, un déplacement remplace uniquement un rattachement de départ explicite. Les autres liens sont conservés ; un départ ambigu ouvre un choix intégré sans mutation préalable. Le menu contextuel et le clavier utilisent la même orchestration. Le drag droit a des gestionnaires et tests de contrat mais reste une réserve de validation physique Windows, contrairement au menu équivalent réellement testé.

`ui_state.py` lit/écrit `interface.json` dans le dossier actif, avec son propre `version: 1`, et réutilise seulement l'écriture atomique. Il mémorise la vue Liste, la visibilité de l'inspecteur et les dimensions. Ce fichier n'est pas une donnée métier et n'est pas exporté/restauré avec le catalogue. Une préférence illisible n'entraîne aucune réinitialisation métier et est annoncée. L'application n'ajoute aucun champ visuel aux fiches : couvertures et vues suivantes demanderont leur lot dédié.

Le navigateur est une fonction injectable à la frontière UI. Le mode de recette explicite `--simulate-open` utilise la même validation `parse_url` puis journalise localement, sans lancer de navigateur. Le titre et le statut signalent cette simulation ; le dossier utilisateur par défaut est refusé pour ce mode. En usage normal, la même action validée appelle `webbrowser.open` sur le geste de l'utilisateur.

## MG-002a — Atelier dessiné (0.2.1)

`atelier.py` rassemble des composants de présentation concrets : bandeau vectoriel Canvas, cartes papier, boutons arrondis, liste dessinée et menus habillés. La liste expose les opérations nécessaires à l’interface (sélection, colonnes, défilement, zones cliquables) ; elle ne connaît ni URL, ni stockage, ni règle de classement. Les badges sont des données transitoires de rendu. Les menus conservent leur modèle de commandes `tk.Menu`, affiché dans une surcouche de la fenêtre avec choix souris/clavier et fermeture Échap. L’arbre hiérarchique reste un Treeview habillé. Aucun framework, image de référence, actif distant ou dépendance supplémentaire.

Les ajustements fonctionnels restent dans `ui.py` : retrait du projet courant après `Catalog.search`, molette limitée aux descendants de l’inspecteur, inférence d’un rattachement source seulement s’il est unique. Le moteur, l’adaptateur, le stockage, le schéma et les 35 tests précédents sont inchangés. Les suggestions restent globales. La déduplication n’est pas réécrite.

Au lancement, les séparateurs sont positionnés après réalisation de la fenêtre, y compris lorsque l’inspecteur est restauré depuis les préférences. Le format compact adapte la hauteur du bandeau et des lignes ; le défilement horizontal préserve la largeur des colonnes. Les tests ciblent les corrections et régressions constatées ; les captures proviennent séparément de la recette native Windows.

## MG-003a — Identité visuelle des projets (0.3.0)

`Record.visual` est un dictionnaire générique, vide pour les fils, portant les identifiants facultatifs `image`, `icon`, `color` des projets. Aucun champ ChatGPT supplémentaire. `identity.py` définit les repères et **l’unique résolveur pur** `resolve_identity(catalog, identity, scope)` : projet choisi ; pour un fil, contexte direct s’il existe dans ses liens, sinon premier lien conservé ; sans projet, état neutre. Il ne connaît ni UI, ni fichiers, ni ChatGPT. Détaillée et Mosaïque pourront réutiliser ce résultat sans nouvelle règle d’héritage.

`identity_ui.py` ajoute les trois contrôles à la seule fiche projet. Les layers occupent le Canvas de l’inspecteur et possèdent leur défilement ; leur choix temporaire est distinct du brouillon de la fiche. Utiliser alimente ce brouillon, Annuler/Échap le laisse intact. Ctrl+S applique aussi le choix du layer ouvert puis utilise la transaction existante. L’avertissement `dirty` protège les départs. `ContextMasthead` dérive du bandeau existant et remplace seulement les objets marqués `landscape`, sans changer les dimensions, les marges, la marque ni le moteur de Liste. Vignettes recadrées sans déformation, icône et discret trait coloré ; le cliché du bandeau est réutilisé tant que ses repères et dimensions ne changent pas.

`images.py` vérifie taille, contenu PNG/JPEG/WebP, dimensions et absence d’animation avant décodage complet. Il corrige l’orientation, retire les métadonnées, réduit au plus à 2400 px et copie le PNG normalisé dans `<data-dir>/images/<sha256>.png`. La référence persistée `asset:<sha256>` n’est jamais un chemin fourni par l’utilisateur. Les couvertures `pack:<id>` proviennent de `mon_gpt/assets/covers`, hors données personnelles. Les copies sont immuables : pas de suppression automatique après remplacement ou suppression d’un projet. Une annulation peut donc laisser une copie non référencée ; elle n’entre pas dans l’export.

`storage.py` assure la validation explicite des versions 1 et 2 et la copie `avant-migration-v1-…json` avant écriture du format 2. Le lecteur v1 n’ajoute aucune règle ChatGPT. `Backup(data, images)` est un contenu vérifié avant confirmation de restauration ; les anciens JSON v1 restent acceptés. L’export UI est ZIP, avec `catalogue.json` et exactement les images référencées. L’export JSON programmatique refuse les images personnelles pour éviter une sauvegarde silencieusement incomplète.

Les archives refusent doublons de noms (y compris casse), liens symboliques, chiffrement, chemins inattendus, fichiers supplémentaires, empreintes incorrectes et ressources manquantes. Aucun `extractall` : les noms d’images sont reconstruits depuis les empreintes validées. Bornes : 10 Mo pour le catalogue, 20 Mo par image, 100 Mo pour le ZIP, 200 Mo décompressés et 512 images. Ces limites sont vérifiées aussi à l’écriture afin de ne pas produire une sauvegarde que le lecteur refuserait.

La restauration revalide, vérifie les collisions et sauvegarde d’abord l’existant complètement. Les nouvelles images sont installées avant le remplacement atomique du catalogue. Un échec peut laisser des images supplémentaires, jamais des anciennes références détruites. Les fichiers existants d’un même hash doivent être identiques ; une collision incohérente bloque la restauration au lieu d’écraser une ressource partagée. Le schéma et l’adaptateur ChatGPT restent séparés. Les composants validés de menu, navigation, Liste, tags/catégories, aperçu et dialogues ciblés n’ont pas été redessinés.

## MG-003b — Corrections visuelles (0.3.1)

`project_icons.py` rassemble 36 tracés homogènes et un cache Tk retenu par l’application, indexé par identifiants icône/couleur/taille. Le même dessin sert dans l’arbre, les sélecteurs et le brouillon de création. Les huit identifiants historiques et les seize couleurs sont inchangés. Le champ inline tient compte de la profondeur pour laisser l’icône visible.

`ContextMasthead` remplace les vignettes recadrées du bandeau par `contained_picture` : scène entière contenue dans un cadre exactement 16:9 calculé après les textes existants, au plus 128×72 dans les 80 px de hauteur inchangés. L’icône reste à l’extérieur de l’image. Aucune modification du menu, de la recherche, de la Liste ou des colonnes. La rangée `ProjectVisualStrip` est interactive dans la fiche et strictement passive en aperçu projet ; l’aperçu des fils reste identique. Les layers gardent leurs transactions et commandes précédentes, avec grille d’icônes réactive et palette ronde 4×4.

`pack:soleil` est le défaut pour les repères sans image explicite et le paysage neutre. Les six références existantes restent valides avec leur contenu original. `identity.py` reste pur ; ni le schéma 2, ni `core.py`, `chatgpt.py`, `storage.py` et `images.py` ne changent. La migration, l’import et le ZIP complet sont conservés.
