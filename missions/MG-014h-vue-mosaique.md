# MG-014h — Finaliser la vue Mosaïque

**GO réalisation — passe graphique ciblée sur la vue Mosaïque uniquement.**  
Point de départ : `origin/main` après MG-014g.

## Objectif

Finaliser la troisième et dernière vue graphique de MG-014.

Trois changements seulement :

1. remplacer le menu de taille des cartes par **deux icônes Petit / Grand** ;
2. rendre les cartes Mosaïque **beaucoup plus informatives**, en réduisant significativement la place occupée par l’image ;
3. reprendre **exactement le même système de tri que la vue Détaillée**.

## 1. Taille des cartes : deux icônes

Le contrôle actuel `Cartes · Normal / Grand` sous forme de menu déroulant est trop lourd.

### Attendu

Remplacer par **deux commandes iconiques** regroupées :
- **Petit** : grille / carte compacte ;
- **Grand** : grille / carte plus grande.

Contraintes :
- les deux commandes utilisent la logique existante `normal / large` ;
- état actif en sauge ;
- infobulles / noms accessibles `Cartes petites` et `Cartes grandes` ;
- pas de troisième taille ;
- pas de nouveau modèle de persistance ;
- conserver navigation clavier et préférence existante.

Le groupe doit être visuellement cohérent avec le groupe Liste / Détaillée / Mosaïque.

## 2. Cartes Mosaïque : plus d’information, moins d’image

La recette visuelle montre clairement le problème actuel : la couverture occupe la majorité de la carte et la zone informative est réduite à quelques lignes sous l’image.

### Principe

**Une vue Mosaïque n’est pas seulement une galerie d’images : elle doit permettre d’identifier et comprendre rapidement chaque fil.**

Réduire **significativement** la hauteur de l’image afin de libérer une vraie zone éditoriale sous la couverture.

Les données sont déjà disponibles dans le rendu :
- titre ;
- résumé ;
- note ;
- projet/contexte ;
- catégories ;
- tags ;
- création ;
- modification.

### Priorité d’affichage

Dans chaque carte, afficher autant que possible, dans cet ordre :

1. couverture réduite ;
2. titre ;
3. résumé / note si présents ;
4. projet/contexte ;
5. catégories ;
6. tags ;
7. création / modification si la taille de carte le permet proprement.

Pour les dates, utiliser un rendu court et secondaire, par exemple :
- `Créé · 15/11/2026`
- `Modifié · 16/11/2026`

### Différence Petit / Grand

**Petit**
- image réduite ;
- titre + contexte ;
- au moins une partie du résumé/note si disponible ;
- catégories/tags utiles ;
- dates seulement si elles tiennent sans surcharge.

**Grand**
- image toujours secondaire par rapport à la fiche ;
- davantage de résumé/note ;
- contexte, catégories, tags ;
- dates création/modification visibles si disponibles.

Les deux tailles doivent réellement avoir un intérêt différent, sans que Petit devienne illisible ni que Grand redevienne une galerie d’images.

### Règles

- Conserver sélection, focus, ouverture ↗, renommage, navigation grille, scroll et hit-tests.
- Conserver le rendu borné aux cartes visibles et le cache d’images existant.
- Les images personnelles restent cadrées selon les règles existantes.
- Ne pas inventer de nouvelles données ni nouveaux boutons dans les cartes.
- Les textes longs peuvent être tronqués proprement ; ne pas laisser une image énorme pendant que les informations disparaissent.

## 3. Tri : identique à Détaillée

Ne pas conserver le vieux tri spécifique Mosaïque.

La vue Mosaïque doit reprendre le **même composant et la même présentation** validés en MG-014g pour Détaillée :

**Trier par : [ Catégories ]   [ ↑ / ↓ ]**

- même menu de choix ;
- mêmes six colonnes : Titre, Projet, Catégories, Tags, Création, Modification ;
- même commande séparée pour le sens ascendant / descendant ;
- même charte papier/sauge ;
- même alignement sur le bord droit utile de la zone de cartes ;
- pas de symbole `▾` ajouté au texte ;
- pas de petits carrés `·` ni de style de menu d’actions.

Réutiliser autant que possible le composant/présentation MG-014g au lieu de créer une variante Mosaïque différente.

## Hors périmètre

Ne pas toucher :
- à la Liste ;
- à la vue Détaillée validée ;
- au bandeau ;
- à l’inspecteur ;
- à l’explorateur ;
- à la barre de création ;
- au glisser-déposer ;
- au modèle métier / stockage.

## Tests proportionnés

Mission **L1 UI ciblée** selon `AGENTS.md`.

Attendu :
- tests existants Mosaïque, navigation grille, tailles, tri et ouverture directement concernés ;
- recette Windows courte :
  - Petit puis Grand ;
  - plusieurs cartes avec résumé/note/catégories/tags différents ;
  - tri par au moins Titre, Catégories et Création ;
  - inversion ↑ / ↓ ;
  - inspecteur ouvert puis fermé ;
  - navigation clavier et ↗ ;
  - largeur confortable et largeur plus contrainte ;
- vérifier visuellement que les cartes montrent **nettement plus d’informations qu’avant** ;
- **pas de suite complète**.

Rapporter ce qui a été exécuté et omis.

## GitHub — Marcel

Publier avec **Marcel / `Trucabule-M1`** :
- `gh auth status` : Marcel actif ;
- identité Git locale : `Trucabule-M1 <marcel@trucabule.fr>`.

## Livraison

- Données fictives uniquement.
- Rapport : `reports/MG-014h/rapport.md`.
- Quelques captures avant/après utiles, au minimum Petit et Grand.
- Commit/push `origin/main`, SHA distant vérifié, dépôt propre.
- **STOP pour recette humaine.**

**Critère d’acceptation :** la Mosaïque devient une vraie vue d’information illustrée : image plus petite, contenu utile plus riche, tailles Petit/Grand explicites et tri identique à Détaillée.
