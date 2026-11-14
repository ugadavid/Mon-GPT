# Architecture — MG-001

Version 0.1.0, 14 novembre 2026.

## Choix techniques

Python 3.13 et Tkinter/ttk : application de bureau Windows sans serveur HTTP ni dépendance tierce, lancement avec Python déjà présent sur la VM. Coût : rendu sobre, Python/Tk requis sur le poste cible, absence d'installateur autonome. [Tkinter](https://docs.python.org/3.13/library/tkinter.html) fournit les contrôles et dialogues de bureau utilisés.

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

Racine : `schema: 1`, `records: […]`, `chatgpt: […]`. Le décodeur vérifie champs obligatoires, types, UUID, unicité, dates zonées, parents présents, absence de cycles, rattachements et identités ChatGPT cohérentes. Toute fiche applicative a exactement une entrée ChatGPT, chaque projet aucune. Versions inconnues et fichiers illisibles sont refusés sans recréer de catalogue. Une migration future devra être explicite et sauvegarder le format précédent.

La restauration valide avant confirmation puis revalide l'objet en mémoire, exporte l'état courant vers une sauvegarde horodatée unique et écrit le nouvel état atomiquement. Une erreur de validation ne produit aucune écriture. La copie préalable demeure si le remplacement échoue. Les exports conservent champs communs, identités, relations, ordre et entrées de l'adaptateur. Le verrou n'est pas une donnée métier.

## Extraction future

Déplacer `core.py` et ses tests génériques dans une bibliothèque commune ; conserver assemblage et adaptateur dans Mon GPT. Le socle n'important rien de l'application, cela demande essentiellement des changements d'import et de packaging. Si un autre produit partage la persistance, extraire ensuite la sérialisation générique de `Record`, chaque application orchestrant ses données de source. Aucun registre de plugins ou moteur universel anticipé.

## Limites

Parcours des collections en mémoire ; un très gros catalogue demandera des mesures, puis éventuellement SQLite. Tri pour les usages français courants, sans collation linguistique exhaustive. Notes et liens en clair dans les exports. La seule activité réseau possible est l'ouverture explicite d'un fil dans le navigateur.
