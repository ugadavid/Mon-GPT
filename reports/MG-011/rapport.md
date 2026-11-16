# MG-011 — Finitions fonctionnelles

Mon GPT<3 **0.9.4** · 16 novembre 2026 · CODEX-VM / Windows / Python 3.13 / Tk.

Base synchronisée sans perte de travail local : `56f506b` sur `origin/main`, après la version validée 0.9.3. Collector **0.8.2 inchangé**. [Guide](../../docs/MG-011-navigation-et-informations.md).

## 1. Extraits dans Détaillée et Mosaïque

`refresh_results()` transmet désormais les notes sans les confondre avec la description. Les deux rendus partagent une extraction pure des champs non vides, normalisée uniquement pour l’affichage. Résumé et Note restent libellés séparément. Détaillée garde sa hauteur de 126 px et ses emplacements. Mosaïque conserve les deux lignes de titre, ajoute jusqu’à deux extraits puis les pastilles existantes, avec repli `+N`. Les cartes sans repères gardent leur hauteur sobre et leurs hit-tests propres, même au milieu de cartes enrichies.

La grille conserve un pas commun pour un parcours prévisible. La hauteur maximale des compléments est calculée à l’insertion, sans rescanner les 1 429 fiches à chaque dessin. Seules les cartes visibles sont dessinées ; le cache d’images existant reste borné. En fenêtre basse, la couverture entière reste en 16:9 et se réduit pour préserver titre et repères. L’infobulle donne les champs complets ; l’aperçu et l’éditeur restent disponibles.

## 2. Informations du projet dans le bandeau

`ContextMasthead.set_context()` reçoit séparément l’identité effective et les métadonnées du **scope**. Changer de fil ne remplace donc pas les catégories/tags du dossier. Description et pastilles réutilisent les composants existants à gauche de la couverture. En largeur contrainte, une ligne compacte supplémentaire porte les pastilles ; aucun faux badge dans Tous, À classer ou un projet sans métadonnées. Les valeurs sont mises en cache par tuples ; aucun enregistrement métier.

## 3. Navigation générale épinglée

Deux Treeview natifs forment une navigation logique : deux entrées fixes, puis l’arbre défilant. Chaque entrée existe une seule fois. La façade `NavigationTree` adapte explicitement sélection exclusive, focus, clavier, API de lignes, coordonnées de hit-test, infobulles et événements souris. Haut/Bas traverse la frontière ; Alt+↑/↓ reste natif pour le classement manuel. La touche contextuelle Windows (`App` dans Tk) est aussi écoutée, avec le nom historique `Menu`.

L’API utilisée par restauration, création intégrée et classement est conservée. Les dépôts sur projets gardent leur moteur existant. Un projet peut rejoindre la racine via Tous ; À classer reste virtuel, et un fil n’y est pas déposé comme dans un dossier.

## 4. Titre et décompte

Un scope projet affiche **Contenu du projet**, puis compte séparément discussions et sous-projets directs. Les mêmes filtres alimentent cartes et compteurs. Tous et À classer gardent Discussions. La recherche générique récursive n’a pas été modifiée : la restriction directe reste une responsabilité de la navigation, comme en MG-010a.

## 5. Emplacements en haut de l’éditeur

Après titre, identité et lien, l’éditeur montre les rattachements enregistrés et la liste multi-sélection, avec les projets actuels en premier. Les libellés réutilisent `project_choices` : chemins lisibles, homonymes numérotés, identifiants stables non affichés. Ctrl+clic et Retirer les rattachements restent disponibles. Enregistrer applique ; ouvrir ou abandonner ne mute aucun champ. Les projets conservent leur parent unique.

## 6. Fenêtres Aide et À propos

`information_ui.py` contient un petit composant commun aux deux vraies fenêtres redimensionnables. Aide propose huit rubriques au clavier et un texte défilant, conforme aux gestes actuels. À propos affiche 0.9.4, le rôle local et un bouton explicite vers GitHub, sans attribution ni licence inventée. Une fenêtre déjà ouverte est réutilisée. Échap, Fermer et la croix rendent le focus à l’application. Aucune messagebox d’information pour ces commandes.

## 7. Redimensionnement libre

Les deux tailles de recette ont disparu d’Affichage. Le menu conserve vues, colonnes, aperçu, recherche et filtres. `resize()` demeure pour les tests. Les contrôles Windows et la persistance de `interface.json` restent utilisés, sans nouveau format.

## Architecture et périmètre

Aucun changement à `core.py`, `chatgpt.py`, `identity.py`, `storage.py`, aux formats métier/préférences, à l’import ou au Collector. Catalogue schéma 4, GUID, mappings, sauvegardes et images personnelles conservent leurs contrats. Aucun asset créé ou modifié. Les retouches de géométrie sont limitées à la lisibilité des informations demandées ; aucune direction artistique supplémentaire ni chantier du parking.

## Vérifications et recette Windows

**199 tests Python réussis en 243,265 s**, dont les 192 historiques et sept nouveaux tests fonctionnels. Deux assertions historiques ont été adaptées aux exigences explicites : les métadonnées apparaissent désormais sur la Mosaïque, et le compteur distingue les types. Aucune couverture historique retirée. **43 tests JavaScript réussis**, Collector non modifié. `git diff --check` réussi.

Commandes exécutées :

```powershell
python -m unittest discover -s tests -v
cd companions/chatgpt-collector
npm test
```

[Journal Python](tests-python.txt) · [Journal JavaScript](tests-javascript.txt) · [Bilan fictif vérifié sur disque](bilan-recette-fictive.json).

Recette lancée avec `python -m mon_gpt --data-dir .recette/MG011 --simulate-open`, sur **1 429 conversations et 67 projets entièrement fictifs**. Fenêtres réellement exécutées à 1600×900 puis 1000×680, aperçu fermé et ouvert. Le second format est préparé dans les préférences du catalogue isolé, application fermée. Aucun catalogue utilisateur ou export réel utilisé.

| Contrôle | Résultat et méthode |
|---|---|
| Résumé + longue note, note seule, résumé seul, aucun repère | Lecture réelle en Détaillée et Mosaïque Normal/Grand ; tests des variantes et absence de mutation. |
| Dix couvertures identiques héritées | Titres, extraits et repères distinguent les cartes ; tests de rendu borné, cache et absence de relance de recherche à la sélection. |
| Bandeau de dossier | Repères du scope visibles sans aperçu ; sélection multiple et changement de fil ne les remplacent pas. Repli compact observé avec aperçu. Tests Tous/À classer/projet vide. |
| Entrées épinglées | Défilement réel jusqu’au projet 58, puis clic Tous (1 429 fils), À classer (2 fils) et retour sur dossier. Tests clavier, focus, menu contextuel Windows, sélection exclusive et restauration. |
| Compte direct | Dossier réel fictif : **3 discussions · 2 sous-projets**, sans son fil indirect. Tests de filtres et des trois vues. |
| Emplacements | Éditeur réel avec deux homonymes numérotés, sélectionnés et visibles en tête. Ouverture/retour sans écriture. Ajout/retrait puis Enregistrer et abandon couverts par événements Tk/tests. |
| Gestes | Sélection au clavier de deux cartes, glisser gauche réel vers un projet : exactement deux fiches modifiées, seulement `projects`/`modified`, aucune autre donnée ni mapping altéré. Clic titre sans URL, une ouverture explicite ↗ simulée. F2/Échap réel. Ctrl/Maj/Ctrl+A, drag gauche/droit un/lot, flèches, tris et ↗ dans les trois vues couverts par les tests Windows/Tk. Le drag droit est exercé par événements Tk, le pilote de souris native utilisé ne proposant que le drag gauche. |
| Aide / À propos | Vraies fenêtres ouvertes depuis le menu, rubrique Ouvrir ↗ vérifiée, version 0.9.4, bouton Fermer réel. Échap, focus, réutilisation et lien GitHub explicite contrôlés par tests Tk. |
| Affichage et relance | Menu réel sans tailles imposées, autres commandes conservées. Fermeture normale et relance réelle sans modifier les préférences : recherche « couleurs », projet, branche, fil 05, aperçu, Mosaïque Grand et 1000×680 retrouvés. Aucune ouverture au démarrage : le journal conserve son unique clic ↗. Dimensionnement interne et persistance couverts par la suite. |
| Autres régressions | Galerie responsive/double-clic, sauvegarde/restauration/images, import v2 idempotent, dates et colonnes administrables : suite historique verte. |

Le journal d’erreurs de l’application reste vide. Les fichiers de recette, le catalogue et les préférences fictifs restent hors Git ; seuls les preuves et bilans sont publiés.

### Huit captures Windows natives

Captures brutes de l’application, sans retouche ni maquette ; les fenêtres secondaires sont capturées directement comme fenêtres Windows.

1. [Détaillée : notes distinctes et bandeau du scope](01-detaillee-notes-bandeau.png)
2. [Mosaïque Normal : dix couvertures héritées](02-mosaique-normale.png)
3. [Mosaïque Grand à 1000×680](03-mosaique-grande-compacte.png)
4. [Navigation épinglée, projet 58 visible](04-navigation-epinglee.png)
5. [Éditeur : deux emplacements homonymes en tête](05-editeur-emplacements.png)
6. [Aide structurée, règle ↗](06-aide-structuree.png)
7. [À propos : version exacte et fonctionnement local](07-a-propos.png)
8. [Contenu direct : 3 discussions et 2 sous-projets](08-contenu-direct.png)

## Limites

Les extraits et pastilles sont volontairement courts ; les textes entiers restent accessibles par l’infobulle et l’aperçu. La grille garde des rangées régulières : une carte sans repères est plus courte que sa voisine enrichie, avec un intervalle entre rangées. À 1000×680 avec aperçu ouvert, la couverture se réduit fortement pour préserver titre et repères. Les couvertures héritées identiques ne sont pas diversifiées artificiellement. L’esthétique approfondie reste pour une mission validée séparément. Aucun déploiement ou distribution supplémentaire.

**STOP après MG-011**, en attente de la recette utilisateur David/GPT.
