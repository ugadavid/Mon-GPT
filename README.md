# Mon GPT<3 — 0.7.0

Application Windows locale pour organiser ses discussions ChatGPT. MG-002a donne corps à l’« Atelier chaleureux » : bandeau illustré, cartes papier, titres affirmés, icônes harmonisées, badges et menus dessinés. La **vue Liste** conserve l’ouverture directe. Aucun serveur, compte applicatif ou API OpenAI ; aucune modification dans ChatGPT.

![La Mosaïque réelle sur CODEX-VM](reports/MG-005/01-mosaique-normale.png)

**MG-007 : 31 couvertures locales.** Les 24 illustrations fournies par David rejoignent les sept historiques dans les mêmes sélecteurs Image des projets et des fils. Versions JPEG optimisées 1200×675, scènes entières ; les anciens choix et l’héritage restent inchangés. [Correspondances, recette et captures](reports/MG-007/rapport.md).

**MG-006 : personnaliser les fils.** La même rangée Image / Icône / Couleur que sur les projets est disponible dans les discussions. Chaque propriété hérite indépendamment du projet de référence, ou conserve un choix personnel explicite. Les sélecteurs existants proposent **Revenir à l’héritage** ; les infobulles distinguent Héritée et Personnalisée. [Rapport et captures natives](reports/MG-006/rapport.md).

**MG-005 : la Mosaïque.** Une grille adaptative met les couvertures entières au premier plan : image, icône colorée, titre et petite ouverture ↗. Deux tailles **Normal / Grand**, sans chemins ni métadonnées répétés. Les trois vues partagent recherche, filtres, sélection, tri et aperçu ; la reprise de session inclut la taille des cartes. [Rapport, vérifications et cinq captures natives](reports/MG-005/rapport.md).

**MG-004a : reprendre son espace de travail.** À la fermeture normale, Mon GPT<3 mémorise aussi recherche, filtres, périmètre, branches ouvertes et fiche sélectionnée. La relance retrouve le même aperçu en lecture seule, sans ouvrir de discussion. Tout reste dans `interface.json`, hors catalogue et sauvegarde métier. Un fichier ancien reste compatible ; un état invalide revient discrètement à l’affichage par défaut. [Rapport et captures avant/après](reports/MG-004a/rapport.md).

**MG-004 : la vue Détaillée.** De petites couvertures entières, les icônes colorées des projets, titres, extraits de résumés, emplacements et pastilles composent des cartes légères. Le commutateur près de Discussions et le menu Affichage changent la présentation en gardant sélection, recherche, filtres, tri et fiche ouverte. [Rapport et cinq captures comparatives réelles](reports/MG-004/rapport.md).

**MG-003b : les repères deviennent visibles.** L’arbre affiche l’icône et la couleur de chaque projet ; la fiche regroupe ses trois sélecteurs sur une rangée. Le bandeau montre toute l’image en 16:9 dans son gabarit existant. Sept illustrations locales, dont la prairie solaire par défaut, 36 icônes au trait et les seize nuances conservées en pastilles rondes. Les images personnelles restent incluses dans les sauvegardes complètes. [Rapport et cinq captures réelles](reports/MG-003b/rapport.md) · [Origine des illustrations](docs/illustrations-MG-003a.md).

MG-002b-02 place les colonnes directement sous le menu validé : arbre et aperçu utilisent toute la hauteur, tandis que l’identité et la recherche compacte restent au centre. La recherche est plafonnée en largeur ; les pastilles n’occupent une ligne que si un périmètre ou un filtre est actif. [Rapport et trois captures](reports/MG-002b-02/rapport.md).

MG-002b-03 affine uniquement la Liste : lignes de 42 px, catégories et tags séparés, petites icônes au trait et lien à droite. Le titre et le lien restent visibles pendant le défilement horizontal des colonnes secondaires. En largeur très réduite, `+N` indique les repères repliés ; le survol d’une ligne restitue son titre entier et tous ses repères. Les en-têtes trient et leurs limites se redimensionnent. Flèche droite dans la Liste focalise l’action de fin de ligne ; Entrée ouvre la sélection. [Rapport et quatre captures](reports/MG-002b-03/rapport.md).

MG-002b-04 compacte l’inspecteur : icône accolée au titre, trois actions sur une ligne (ouvrir, copier, modifier), info-bulles et activation clavier. Résumé, emplacements, catégories, tags et informations restent distincts. Les notes longues sont repliables et lisibles intégralement ; une scrollbar dédiée apparaît lorsque le contenu dépasse. [Rapport et trois captures](reports/MG-002b-04/rapport.md).

MG-002b-05 harmonise le seul éditeur avec cet aperçu : champs papier à bordure fine, libellés courts et pastilles colorées réparties selon la largeur du panneau. Les saisies de tags/catégories occupent la largeur utile ; Tab et Shift+Tab parcourent aussi les champs multiligne. Les protections et l’enregistrement restent identiques. [Rapport et trois captures](reports/MG-002b-05/rapport.md).

MG-002b-06 affine la navigation gauche : dossiers au trait, sélection sauge, niveaux réguliers, tri compact et libellés complets au survol. Les cartes respirent davantage. Les erreurs ordinaires de l’éditeur apparaissent sous leur champ ; la confirmation de suppression se limite au titre et, pour un projet, à son impact. Non, Échap et la croix annulent. [Rapport et quatre captures réelles](reports/MG-002b-06/rapport.md).

## Lancer

Windows 11 x64, Python 3.13 avec Tcl/Tk et commande `python` accessible. **Pillow 13.0.0** est le seul paquet requis pour décoder PNG, JPEG et WebP. Depuis le dépôt, installer une fois avec `python -m pip install -r requirements.txt`. Aucune police supplémentaire. Recette sur CODEX-VM avec Python 3.13.17 / Tk 8.6. Depuis PowerShell :

```powershell
& 'C:\Users\codex\Documents\Projets\mon-gpt\lancer.cmd'
```

Ou, depuis le dépôt : `python -m mon_gpt`. Le double-clic sur `lancer.cmd` convient aussi. Sur Zenith Ice : installer Python avec Tcl/Tk, cloner le dépôt puis utiliser son lanceur. Vérification de Tk : `python -m tkinter`.

## Retrouver et ouvrir

Un clic sur le **texte du titre**, l’icône du fil ou le **petit lien à droite de la ligne** ouvre le fil dans le navigateur par défaut, sans passer par un formulaire. Cliquer dans les autres colonnes ou dans l'espace vide du titre sélectionne seulement. Double-clic sur une ligne ou **Entrée dans la liste** ouvre aussi. Un projet (icône dossier) n'ouvre jamais ChatGPT ; double-clic/Entrée navigue vers son emplacement.

**Ctrl+K** focalise la recherche unique. Elle explore titres, résumés/descriptions, notes, tags, catégories et métadonnées, sans casse ni accents. Les suggestions et **Filtres** proposent les valeurs du catalogue : choisir un tag, une catégorie ou un projet ; les pastilles × retirent les filtres. Le projet sélectionné inclut **ses descendants**. Partout/Tous les fils retire ce périmètre ; Effacer remet à zéro texte, tag et catégorie. Un fil multi-rattaché reste unique dans les résultats. Entrée dans un champ de recherche/édition n'ouvre pas le navigateur.

L'**inspecteur** est facultatif, masqué au premier lancement. La commande discrète **Aperçu**, ou Affichage, affiche ses sections et Ouvrir/Copier le lien. **Modifier la fiche** rend volontairement accessibles tous les champs MG-001. Sa molette agit uniquement sous le pointeur dans ce panneau. Replier l'inspecteur laisse l'ouverture directe disponible. Les colonnes et séparateurs des panneaux sont ajustables ; cliquer un en-tête trie la liste. Affichage propose les formats compact 1000×680 et confortable 1360×820 ; le compact resserre le bandeau et les lignes. Un projet n’apparaît plus parmi ses propres résultats, ses descendants restent inclus.

## Parcourir en Détaillée

Cliquer **Détaillée** sous Discussions, ou choisir **Affichage → Détaillée**. Les cartes montrent une couverture 16:9 entière, avec des marges pour les portraits. L’icône et la couleur héritent du projet actif selon la même règle que le bandeau. Les résultats, leur tri et leurs UUID restent communs avec la Liste ; aucun projet supplémentaire n’apparaît dans Tous les fils.

Le titre ou **↗** ouvre directement une discussion ; l’image, les pastilles et le reste de la carte sélectionnent seulement. Double-clic et Entrée sur le résultat focalisé gardent le comportement de la Liste. Un projet utilise sa propre couverture et ne s’ouvre jamais dans ChatGPT : Entrée/double-clic navigue vers son périmètre. Flèches haut/bas parcourent les cartes, droite focalise l’action d’ouverture. Un titre coupé, le résumé et les repères complets sont accessibles au survol. En petite largeur, quelques pastilles se replient en `+N`.

Le bouton **Tri** de Détaillée reprend les quatre tris des en-têtes de Liste ; choisir le tri actif inverse son sens. Clic droit, F2, glisser gauche vers un projet et les raccourcis existants restent disponibles. Aucun nouveau raccourci de vue. À la fermeture, le choix Liste/Détaillée est mémorisé avec recherche, filtres, périmètre, branches et sélection centrale. La relance restaure un aperçu en lecture seule si la fiche figure encore dans les résultats ; aucune discussion ne s’ouvre automatiquement. Les anciens fichiers de préférences restent lisibles. Une sélection supprimée ou un périmètre disparu revient à l’espace par défaut ; une fiche simplement exclue par les filtres n’est pas réintroduite dans les résultats.

## Parcourir en Mosaïque

Cliquer **Mosaïque** ou choisir **Affichage → Mosaïque**. **Cartes · Normal / Grand** apparaît uniquement dans cette vue ; **Tri** reprend les mêmes quatre tris. La grille recalcule ses colonnes selon la largeur du centre, jusqu’à une colonne en compact avec aperçu. Grand agrandit principalement l’image ; les deux tailles convergent lorsque la largeur impose une seule petite carte. Les portraits restent entiers dans un cadre 16:9.

L’image et le fond sélectionnent ; le titre ou **↗** d’un fil l’ouvrent directement. Double-clic et Entrée ouvrent aussi ; un projet navigue dans son périmètre sans navigateur. Les quatre flèches parcourent la grille et font défiler la sélection. Le survol restitue le titre complet et son contexte, sans charger la face des cartes. Clic droit, touche Menu, F2/Échap et glisser gauche conservent les gestes existants. Le fil partagé apparaît une seule fois, avec les repères hérités du contexte actif.

La fermeture normale mémorise aussi **Mosaïque et Normal/Grand** dans `interface.json`. La relance restaure les mêmes critères, périmètre, branches, sélection visible et aperçu en lecture seule, sans ouvrir ChatGPT. Le tri et la position exacte de défilement restent des états de la fenêtre courante.

## Créer et modifier

Le **+** de Votre espace, **+ Fil** près de la Liste, Édition et le clic droit dans l'arbre proposent les créations. Aucun gros bouton permanent Nouveau/Inspecteur dans le bandeau :

- **Ctrl+Maj+P** : ligne de projet éditable insérée sous le projet sélectionné, ou à la racine depuis Tous les fils/À classer. Entrée crée ; Échap annule sans entrée fantôme. Aucune image à choisir.
- **Ctrl+N** : zone intégrée à la liste avec titre et URL. Entrée valide, Échap annule. URL invalide et doublon sont signalés dans cette zone. Un bouton explicite retrouve/rattache une fiche existante sans remplacer titre et notes.
- **F2** : renommer dans une ligne intégrée ; Entrée valide, Échap annule.
- **Modifier les détails** : résumé/description, notes, tags, catégories, métadonnées `clé=valeur` (une ligne par clé unique), emplacements et parent de projet. Dates automatiques avec fuseau local, affichées au format français.
- Tags/catégories : choisir une valeur connue dans la liste ou saisir une valeur puis Entrée/+ Ajouter. Les valeurs choisies sont des **pastilles** ; × retire une valeur de la saisie. Les variantes de casse/accents d'une valeur connue la réutilisent. Aucun champ de liste à virgules imposé.
- **Ctrl+S** ou Enregistrer : appliquer les modifications de fiche. Une saisie non enregistrée reste protégée avant navigation/fermeture. Ouvrir un fil par son menu ne détruit pas la saisie. Le panneau d'édition défile.

## Classer

Glisser gauche un **projet** vers un autre change son parent ; le déposer sur Tous les fils le remet à la racine. Les cycles sont interdits. Le mode Manuel mémorise l'ordre des frères, réglable par **Alt+↑/↓ dans l'arbre** ou Monter/Descendre dans le menu contextuel. Le mode Alphabétique français ne détruit pas cet ordre.

Glisser un **fil** vers un projet déplace seulement le rattachement du contexte de départ ; tous les autres restent intacts. Avec un seul rattachement, même depuis Tous les fils, le déplacement est immédiat. Si plusieurs rattachements rendent le départ ambigu, une zone intégrée demande **quel lien déplacer** avant toute écriture. La cible de dépose et les refus sont signalés visuellement.

Le **clic droit / touche Menu** offre les actions selon l'objet : ouvrir/copier le lien, créer ici, renommer, modifier, déplacer, ajouter/retirer un rattachement, supprimer. Ajouter un rattachement garde la même fiche et ses notes. Le glisser droit propose à la dépose Déplacer ici / Ajouter un rattachement ici / Annuler ; **son geste physique reste à valider manuellement sous Windows** : gestionnaires testés, outil de recette limité au drag gauche. Le menu contextuel équivalent est validé dans la vraie fenêtre et reste utilisable au clavier.

Supprimer demande confirmation. Un projet supprimé remonte ses enfants au parent et retire ses rattachements **sans supprimer les fils**. Supprimer un fil retire seulement sa fiche locale. Retirer le dernier rattachement conserve le fil dans Tous les fils et À classer. Emplacements accepte aussi Ctrl+clic/Maj+flèche dans l'édition détaillée. Catégories, tags et emplacements restent trois notions distinctes.

## Personnaliser un projet

Dans **Modifier la fiche** d’un projet ou d’un fil, cliquer sur la miniature d’image, l’icône ou la pastille de couleur, côte à côte sous le titre. Leurs noms apparaissent au survol et au focus clavier ; Tab puis Entrée ou Espace ouvrent le sélecteur. Le panneau temporaire permet de prévisualiser puis **Utiliser** le choix ; Annuler, la croix ou Échap reviennent au choix précédent. Sur un projet, Par défaut rétablit le repère fourni par l’application. Sur un fil, Revenir à l’héritage supprime uniquement le choix de la propriété courante ; Utiliser confirme ce retour dans le brouillon, Enregistrer/Ctrl+S le conserve. Même un choix égal à la valeur héritée reste personnel lorsqu’il est sélectionné explicitement. Les choix restent dans le même brouillon que les notes et suivent **Enregistrer / Ctrl+S**. Ctrl+S depuis un sélecteur applique sa prévisualisation puis enregistre la fiche. Revenir à l’aperçu ou quitter protège les modifications non enregistrées comme auparavant.

Une couverture solaire est fournie automatiquement à tout projet sans choix explicite, y compris après migration v1. Les anciens choix restent conservés. Le pack de 31 illustrations 1200×675 est livré avec le code et fonctionne hors connexion. Les sept clés historiques sont conservées ; Écriture · carnet est une nouvelle variante distincte du Jardin des mots. La galerie existante défile jusqu’à Animaux, sa 31ᵉ couverture, à la souris et au clavier. **Importer mon image…** accepte PNG, JPG/JPEG et WebP fixes, vérifiés selon leur contenu réel : 20 Mo (20 × 1024² octets), 8192 px par côté et 24 millions de pixels maximum ; minimum 16 px par côté. Format conseillé : paysage 1200×675. Les images sont orientées selon EXIF, converties en PNG sans métadonnées et réduites à 2400 px par côté au plus. L’original reste intact ; sa copie demeure utilisable après déplacement du fichier source. Un import refusé garde la couverture précédente.

Le bandeau utilise les repères du projet sélectionné. Pour un fil, il préfère le projet actif **s’il est un rattachement direct de ce fil** ; en contexte global, il prend le premier rattachement dans l’ordre existant, sans le modifier. Sans sélection, le bandeau conserve le paysage neutre. Les fils conservent uniquement leurs choix explicites dans `visual` ; une propriété absente est calculée depuis le projet, jamais copiée dans le fil. Un fil À classer hérite des défauts. Les choix personnels priment indépendamment sur ces valeurs dans les trois vues, le bandeau et le petit repère de l’aperçu. L’arbre reprend l’icône colorée du projet. Le bandeau contient la scène entière au ratio 16:9 ; les portraits conservent des marges, sans étirement. Son gabarit reste inchangé.

## Menus et données

**Fichier** : Sauvegarder le catalogue, Restaurer, Dossier de données, Quitter. **Ctrl+S reste l'enregistrement de fiche**, distinct de la sauvegarde globale. **Affichage** : inspecteur, recherche, filtres et taille de fenêtre. **Aide** rappelle les gestes et raccourcis.

Les menus supérieurs et contextuels partagent un habillage papier ; leurs commandes sont réelles. Flèches/Entrée permettent de choisir, Échap ferme le menu. Illustration, icônes et contrôles sont dessinés localement avec Tk/Canvas : aucun téléchargement, actif de maquette, paquet graphique ou police supplémentaire.

Catalogue : `%LOCALAPPDATA%\MonGPT\catalogue.json`, hors dépôt ; chemin affiché en bas, cliquable pour ouvrir le dossier. JSON UTF-8 **schéma 3**, dates ISO 8601 zonées, validation stricte, fichier temporaire puis remplacement atomique, verrou d’instance. Un catalogue v1/v2 est vérifié puis copié à l’identique dans `avant-migration-v1-DATE.json` ou `avant-migration-v2-DATE.json` avant sa migration automatique vers v3. Ses identifiants, champs, relations, ordre et URL sont conservés. Versions futures et données invalides sont refusées sans réinitialisation. Les images personnelles résident dans le sous-dossier `images`, sous des noms dérivés de leur empreinte SHA-256.

**Sauvegarder** produit désormais une archive ZIP complète : catalogue et images personnelles référencées. **Restaurer** accepte ZIP v2/v3 et anciens JSON v1/v2 ; il valide contenu, empreintes, références et chemins avant confirmation. L’état courant est sauvegardé avant remplacement : ZIP lorsqu’il utilise des images personnelles, sinon JSON complet. Les ressources existantes ne sont pas écrasées arbitrairement. Un fichier invalide ou un échec laisse l’ancien catalogue utilisable. Conserver aussi une copie hors du disque du PC ; les données ne sont pas chiffrées. L’API d’export JSON reste disponible pour un catalogue sans image personnelle et refuse explicitement un export qui oublierait ces images.

Limites vérifiées : catalogue de 10 Mo maximum, archive ZIP de 100 Mo, contenu décompressé de 200 Mo et 512 images personnelles au plus. Les ressources inutilisées après annulation ou remplacement sont conservées localement par précaution ; elles ne sont pas exportées. Aucun nettoyage automatique susceptible de supprimer une image partagée.

`interface.json` conserve séparément taille de fenêtre, vue active, taille des cartes, recherche, filtres, périmètre, branches, sélection et état de l’inspecteur à la fermeture. Ce fichier de confort est exclu des exports métier ; colonnes, séparateurs, tri et position exacte de défilement ne persistent pas entre lancements. Le vrai catalogue n’est pas utilisé pour les recettes.

## URL reconnues

`https://chatgpt.com/c/UUID` et `https://chatgpt.com/g/IDENTIFIANT-OU-SLUG/c/UUID`. Slug ASCII : lettres, chiffres, tirets/soulignements. UUID standard avec tirets, casse indifférente ; barre finale facultative. Paramètres conservés, fragment retiré ; seul l'UUID déduplique.

Domaine exact `chatgpt.com`, HTTPS uniquement. Domaines voisins, identifiants utilisateur, ports explicites, schémas exécutables, anciens liens `chat.openai.com` et liens `/share/…` refusés. L'existence du chat et ses droits d'accès ne sont pas vérifiés. Aucun contenu de conversation n'est téléchargé ou indexé.

## Démonstration fictive et tests

```powershell
python -m examples.create_ux_demo "$env:LOCALAPPDATA\MonGPT-Demo-UX"
python -m mon_gpt --data-dir "$env:LOCALAPPDATA\MonGPT-Demo-UX" --simulate-open
python -m unittest discover -s tests -v
```

Le générateur refuse de remplacer un catalogue existant. `--simulate-open` est signalé dans le titre et le statut ; les ouvertures validées sont journalisées dans `ouvertures-recette.log`, sans navigateur. Ce mode est interdit sur le dossier utilisateur par défaut. Retirer l'option pour les ouvertures normales. Les tests utilisent des dossiers temporaires et Windows/Tk ; ils sont distincts de la recette visuelle. Le jeu MG-001 reste disponible via `examples.create_demo`.

[Architecture](docs/architecture.md) · [Rapport, 42 tests et captures MG-002a](reports/MG-002a/rapport.md) · [Rapport MG-002](reports/MG-002/rapport.md) · [Rapport MG-001](reports/MG-001/rapport.md).

## Limites

**Liste, Détaillée et Mosaïque sont disponibles.** Les fils héritent des repères de leurs projets et peuvent personnaliser séparément image, icône et couleur. Les trois PNG de référence sont inchangés et ne sont pas embarqués dans l’interface.

Les suggestions de tags/catégories portent sur **tout le catalogue**, pas seulement les résultats filtrés. Le cas suspect de doublon signalé en recette reste à reproduire dans un lot fonctionnel : MG-002a ne modifie pas la déduplication par UUID de l’adaptateur. L’accessibilité par lecteur d’écran des nouveaux contrôles Canvas n’est pas évaluée.

Saisie manuelle, pas de collecte Chrome, synchronisation, lecture des messages ou installateur autonome. Recherche en mémoire et réécriture du JSON complet ; performances massives non mesurées. Tri français courant sans collation exhaustive ni tri numérique naturel. Taille minimale 1000×680 ; titres/chemins longs consultables dans l'aperçu et les colonnes ajustables/défilantes. Un filtre tag et un filtre catégorie combinables à la fois, une fiche sélectionnée à la fois. Déposer dans la partie visible de l'arbre ; ouvrir/défiler l'arbre avant une destination lointaine ou utiliser le menu Déplacer. Réserve de recette sur le glisser droit physique ; menu équivalent validé. Autres zooms Windows et Zenith Ice restent à vérifier.
