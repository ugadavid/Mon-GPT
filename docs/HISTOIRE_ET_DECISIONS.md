# Mon GPT<3 — Histoire et décisions

**État de référence : 19 novembre 2026 · version 0.9.4 installée sur Zenith Ice.**  
Ce document explique **ce qui a été construit, comment et pourquoi**. Il complète le README opérationnel, les missions et les rapports ; il ne les remplace pas.

## 1. Origine et objectif

Mon GPT<3 est né d’un besoin simple : **organiser localement les conversations ChatGPT** sans dépendre de l’organisation disponible dans l’interface ChatGPT elle-même.

Le produit devait rester :
- local, personnel et lisible ;
- indépendant des identifiants internes de ChatGPT pour son organisation métier ;
- capable de classer une même discussion dans plusieurs projets sans la dupliquer ;
- utilisable avec une bibliothèque volumineuse ;
- réversible et sauvegardable ;
- suffisamment simple pour rester un outil personnel plutôt qu’une plateforme.

L’application Windows et son compagnon **Mon GPT Collector** ont donc été volontairement séparés : le Collector observe/recueille les liens et projets accessibles dans Chrome, puis exporte un JSON ; l’application importe ce fichier et gère ensuite son propre catalogue local.

## 2. État livré

### Application Windows

Version : **0.9.4**.

Fonctions principales livrées :
- projets et sous-projets ;
- discussions multi-rattachées ;
- catégories, tags, notes, résumé/description et métadonnées ;
- recherche globale ;
- tris manuel et alphabétique de l’arbre ;
- trois vues : **Liste, Détaillée, Mosaïque** ;
- inspecteur facultatif ;
- sélection multiple et classement groupé ;
- glisser-déposer et menus de déplacement/rattachement ;
- personnalisation image / icône / couleur avec héritage projet → discussion ;
- sauvegarde/restauration complète, y compris images personnelles ;
- import intelligent des exports Collector ;
- reprise de session via préférences UI ;
- fenêtres Aide, À propos, Licences et crédits.

### Distribution Windows

MG-015 livre :
- un ZIP portable autonome ;
- un installateur Windows x64 par utilisateur ;
- aucun Python externe requis ;
- installation sous `%LOCALAPPDATA%\Programs\Mon GPT` ;
- données séparées sous `%LOCALAPPDATA%\MonGPT` ;
- raccourci Démarrer et Bureau optionnel ;
- désinstallation sans suppression des données ;
- icône Windows : **petit robot bleu tenant un cœur rouge**.

Les binaires sont **non signés**.

### Recette réelle

Le 19 novembre 2026, l’installateur a été copié sur **Zenith Ice**, installé et relancé avec succès. Un export réel du Collector a ensuite été importé dans l’application ; la bibliothèque réelle s’affiche et reste exploitable dans les vues livrées.

## 3. Décisions structurantes

### 3.1 Modèle métier séparé de ChatGPT

Le cœur d’organisation reste générique. Les URL et identités ChatGPT vivent dans l’adaptateur dédié. Ce choix permet de ne pas transformer le catalogue local en simple miroir du fournisseur.

### 3.2 Un fil peut appartenir à plusieurs projets

Un rattachement supplémentaire **ne clone pas la fiche**. Les notes, catégories, tags et informations restent attachés à une seule fiche locale.

### 3.3 Données locales distinctes de l’application

Le catalogue et les ressources utilisateur vivent dans `%LOCALAPPDATA%\MonGPT`, indépendamment des sources, du ZIP portable et du dossier d’installation. Cette séparation est fondamentale pour les mises à jour et désinstallations.

### 3.4 Identifiants visuels héritables

Les projets disposent d’une image, d’une icône et d’une couleur. Les discussions héritent de ces propriétés mais peuvent les surcharger indépendamment. Les images personnelles sont copiées localement sous un nom dérivé de leur empreinte.

### 3.5 Ouverture volontaire des conversations

Cliquer une fiche sélectionne ; **↗ seul ouvre ChatGPT**. Ce choix évite les ouvertures accidentelles pendant le classement.

### 3.6 Collector séparé

La collecte Chrome reste un compagnon distinct. Mon GPT<3 ne lit pas automatiquement les messages et ne synchronise pas en continu le compte ChatGPT.

## 4. Chronologie des grandes étapes

### MG-001 à MG-002 — socle et première UX

Création du catalogue local, puis mise en place de l’Atelier : arbre de projets, résultats centraux, inspecteur, recherche et premières règles d’ergonomie.

### MG-003 à MG-007 — identité visuelle des fiches

Ajout de l’identité image / icône / couleur, héritage, galerie locale, import d’images, personnalisation des discussions et pack de couvertures.

### MG-004 / MG-005 — trois vues

Création des vues Détaillée et Mosaïque, puis reprise de session et affinage des interactions communes.

### MG-008 à MG-009 — Collector et import

Création du compagnon Chrome, identification des projets ChatGPT dans le DOM connecté, export v2 puis import intelligent avec correspondances persistantes et réimport idempotent.

### MG-010 à MG-011 — usage réel et finitions fonctionnelles

La bibliothèque réelle révèle les besoins de navigation directe, colonnes configurables, sélection multiple, gestes de classement, informations plus riches, aide et fenêtres secondaires.

### MG-012 — licences et crédits

Ajout d’une fenêtre locale exposant versions, rôles et notices de Python, Tcl/Tk et Pillow. Cette étape déclenche aussi la réflexion sur la proportionnalité des tests.

### MG-013 — essai graphique rejeté

Première tentative de passe graphique **trop directive et trop ambiguë** : plusieurs directions artistiques sont proposées à Codex et le résultat se réduit à des retouches trop faibles ou mal orientées.

Décision :
- rollback du code MG-013 ;
- conserver les rapports comme historique ;
- revenir à une **maquette unique validée avant implémentation**.

### MG-014 à MG-014h — identité graphique finale

Méthode reprise de Mon Bureau :
1. une maquette unique ;
2. une direction graphique claire ;
3. fonctionnement gelé ;
4. petites passes successives avec recette humaine.

Ont été finalisés :
- palette papier / sauge ;
- bandeau illustré ;
- Liste ;
- inspecteur ;
- création rapide ;
- vue Détaillée ;
- vue Mosaïque ;
- tris et commandes de vues ;
- responsive du bandeau.

### MG-015 — empaquetage Windows

Capitalisation sur :
- **Ma Médiathèque** pour PyInstaller + Inno Setup + ZIP portable ;
- **Mon Bureau** pour le cycle installation / mise à jour / désinstallation / réinstallation et la préservation des données.

Résultat : chaîne Windows x64 autonome reproductible et recette réelle sur Zenith Ice.

## 5. Architecture et données

### Répertoire utilisateur

Par défaut :

`%LOCALAPPDATA%\MonGPT`

Il contient notamment :
- `catalogue.json` ;
- `interface.json` ;
- `images/` ;
- sauvegardes ou témoins de migration/import.

### Catalogue

Le stockage est JSON UTF-8 versionné, validé strictement et écrit par remplacement atomique. Les migrations conservent une copie préalable. Les sauvegardes complètes utilisent ZIP dès que des images personnelles sont référencées.

### Préférences

Les préférences d’interface restent hors catalogue métier : taille de fenêtre, vue, filtres, périmètre, branches, colonnes, sélection et inspecteur.

## 6. Méthode de développement et de recette

Le projet a été conduit par missions GitHub :
- David décide et recette ;
- ChatGPT cadre et publie les missions ;
- Codex implémente, teste et publie son rapport ;
- GitHub sert de source de vérité et de canal de transmission.

À partir du 18 novembre 2026, ChatGPT et Codex publient via le compte technique partagé **Marcel / Trucabule-M1**, tandis que les dépôts restent sous `ugadavid`.

### Tests proportionnés

Une règle globale rejouait initialement toute la suite à chaque petite modification. Elle a été remplacée par quatre niveaux :
- L0 statique ;
- L1 ciblé ;
- L2 transverse ;
- L3 complet.

Les micro-corrections graphiques ont ensuite utilisé des suites L1 de quelques tests. MG-015, jalon de distribution, a légitimement utilisé L3 et exécuté la suite complète.

## 7. Ce qui a mal marché — et ce qu’on en retient

### 7.1 Trop guider une mission graphique

Donner plusieurs maquettes différentes et détailler chaque moyen de réalisation a bridé la proposition graphique.

**Leçon :** pour le code fonctionnel, préciser fortement comportements et contraintes ; pour le graphisme, préciser surtout la cible et les invariants, puis laisser davantage de liberté sur les moyens.

### 7.2 Ne pas avoir une cible graphique unique

MG-013 a tenté de combiner plusieurs pistes. Le résultat était incohérent ou trop timide.

**Leçon :** une maquette unique et validée avant implémentation fonctionne mieux, comme sur Mon Bureau et Ma Capture.

### 7.3 Confondre validation technique et validation esthétique

Des centaines de tests verts ne disent rien sur la qualité visuelle d’une interface.

**Leçon :** une passe graphique exige des captures comparables et une recette humaine réelle.

### 7.4 Tests disproportionnés

203 tests ont été rejoués pour des retouches presque cosmétiques.

**Leçon :** prouver le changement au plus petit coût raisonnable ; réserver la campagne complète aux changements qui la justifient réellement.

### 7.5 Vérifier le code avant d’interpréter

Certains comportements supposés disparus étaient parfois seulement issus d’une maquette ou d’un souvenir.

**Leçon :** lorsqu’un détail précis du comportement est contesté, relire les sources avant d’en déduire la cause.

## 8. Distribution et exploitation

La chaîne de build est sous `packaging/windows/`.

Elle produit :
- `Mon-GPT-0.9.4-windows-x64.zip` ;
- `Mon-GPT-0.9.4-windows-x64-setup.exe` ;
- `SHA256SUMS.txt`.

PyInstaller embarque Python, Tcl/Tk, Pillow, couvertures et notices. Inno Setup installe par utilisateur sans élévation. L’installateur ne supprime pas le dossier de données à la désinstallation.

Les détails reproductibles et empreintes se trouvent dans [le rapport MG-015](../reports/MG-015/rapport.md).

## 9. Limites connues

- livrables non signés ; SmartScreen reste à traiter si une diffusion plus large le justifie ;
- accessibilité lecteur d’écran des contrôles Canvas non évaluée ;
- pas de synchronisation continue avec ChatGPT ;
- pas de lecture/indexation automatique du contenu des messages ;
- performances massives non benchmarkées formellement ;
- glisser droit physique conserve une réserve de recette historique ;
- certaines images héritées peuvent rendre la Mosaïque visuellement répétitive.

## 10. Parking / prochaine reprise

À rouvrir seulement sur décision explicite :

1. **tableau de bord / statistiques**, d’abord sous forme d’étude et maquette ;
2. **robot bleu au cœur rouge dans l’interface elle-même**, en remplacement éventuel de la plume ;
3. **signature de code / SmartScreen** ;
4. réflexion sur la répétition des couvertures héritées ;
5. accessibilité et benchmark si l’usage réel les rend nécessaires.

Voir le parking détaillé : [idees-et-finitions.md](idees-et-finitions.md).

---

## Statut

**Projet temporairement clos au jalon 0.9.4 installé sur Zenith Ice.**  
La prochaine reprise doit partir du produit installé, de ce document et du parking, sans réouvrir par défaut les décisions déjà validées.
