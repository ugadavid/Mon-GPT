# MG-012 — Fenêtre « Licences et crédits » depuis le menu Aide

**17 novembre 2026 — Mission de réalisation ciblée.**  
**Statut : GO pour MG-012 uniquement.**  
**Application : Mon GPT<3 0.9.4, dépôt `ugadavid/Mon-GPT`.**  
**Langue de l’interface et du rapport : français.**

> Mission autonome pour Codex. Lire les instructions `AGENTS.md`, confirmer branche, état Git, version et fichiers effectivement présents. Respecter les changements concurrents. Le but est une petite finition documentaire **dans l’application existante**, avant la future grande passe graphique et la distribution Windows. Ni changement de licence générale, ni refonte graphique, ni installateur.

## Contexte vérifié au cadrage

- Le menu **Aide** dans `mon_gpt/ui.py` contient déjà **Gestes et raccourcis** et **À propos de Mon GPT<3**.
- Ces deux entrées ouvrent leurs fenêtres via `mon_gpt/information_ui.py` (`InformationWindow`, `HelpWindow`, `AboutWindow`, `open_information`), avec composants/thèmes existants.
- `requirements.txt` déclare **Pillow==13.0.0** comme dépendance Python tierce d'exécution ; Python, Tkinter/Tcl/Tk et modules standards ne sont pas des paquets PyPI installés par l'utilisateur dans ce dépôt de sources.
- L’extension **Mon GPT Collector 0.8.2** est un compagnon distinct, en Chrome MV3. Son `puppeteer-core==25.17.0` est une dépendance **de tests/développement**, et non une bibliothèque exécutée par l’extension distribuée.
- La revue des droits est documentée dans [RT-001](https://github.com/ugadavid/trucabule-revue-technique/blob/main/reports/RT-001/rapport.md), [inventaire](https://github.com/ugadavid/trucabule-revue-technique/blob/main/reports/RT-001/inventaire-licences.md), et la [note de décision](https://github.com/ugadavid/trucabule-revue-technique/blob/main/decisions/2026-11-17-licences-et-diffusion.md). **RT-001 est PARTIEL ; aucun choix de licence pour le code Trucabule n'a été validé.**
- [RT-002](https://github.com/ugadavid/trucabule-revue-technique/blob/main/reports/RT-002/inventaire-technologies.md) renseigne la surface réelle des bibliothèques. À relire comme source et non comme permission de mutualiser/refactoriser.

Confirmer ce contexte sur le snapshot réel avant de modifier. Une divergence doit être documentée, non masquée.

## Objectif fonctionnel

Ajouter **Aide → Licences et crédits…**, ouvrant une **troisième fenêtre native**, sobre et lisible, dans le langage visuel actuel. Cette fenêtre doit permettre au destinataire de comprendre les composants tiers pertinents et d'accéder aux avis/licences correspondants sans devoir chercher sur Internet.

### Contenu souhaité

1. Un court texte d'introduction : application Mon GPT<3, utilisation de composants libres/tiers et remerciement aux auteurs et contributeurs, sans insinuer un partenariat ou un parrainage.
2. Une liste/table lisible avec composant, fonction générale, licence, version **lorsqu'elle est connue**, et lien vers sa documentation/texte officiel. Vérifier chaque mention exacte : notamment **Python/PSF et licences historiques pertinentes**, **Tcl/Tk sous ses propres termes**, **Pillow 13.0.0 / MIT-CMU**, en tenant compte de RT-001.
3. Une zone ou un bouton « Consulter les notices » permettant de lire les **textes de licence effectivement requis et inclus localement** ; pas une simple URL externe qui rendrait la lecture impossible hors connexion. Utiliser de préférence un répertoire documentaire ou un petit fichier de notices maintenable. Conserver les avis complets et copyrights nécessaires, sans inventer ni tronquer les textes officiels.
4. Une section distincte « Composants non intégrés à cette application » **uniquement si elle éclaire vraiment** le périmètre : le Collector Chrome est un produit compagnon ; Puppeteer est réservé aux tests et ne doit pas être présenté comme une dépendance de l'application de bureau. Éviter une liste de tous les outils de développement qui rendrait l'écran illisible.
5. Une phrase prudente au sujet de Trucabule : auteur/distributeur du logiciel ; **la licence générale de son code n'est pas encore fixée**. Ne pas inventer une licence MIT, Apache, MPL ou GPL pour le logiciel lui-même ; ne pas présenter un dépôt public comme preuve d'ouverture sous licence.
6. **Aucun logo ni nouvelle illustration**. Aucun emplacement publicitaire ou mention obligatoire de Trucabule dans les applications d'autrui.

Les mentions doivent refléter le **produit tel qu'il fonctionne actuellement depuis les sources**. Un éventuel futur exécutable autonome pourrait redistribuer des runtimes, DLL et codecs supplémentaires : **ne pas prétendre que l'écran certifie leur inventaire final**. Préparer une présentation facile à compléter au moment du packaging Windows, mais ne pas anticiper de packaging dans MG-012.

### Ergonomie et navigation

- Entrée dans le menu Aide, ordre logique : « Gestes et raccourcis », « Licences et crédits… », « À propos… », sauf convention UI existante plus pertinente.
- Reprendre `InformationWindow` et les couleurs/tokens existants autant que possible, **sans modifier globalement le thème**.
- Fenêtre redimensionnable, texte lisible avec défilement, liens/boutons clavier-souris ; textes de licences affichables et copiables ou consultables localement ; gestion du focus, Échap/Fermer ; réouverture sans fenêtres identiques en double.
- La fenêtre ne doit modifier ni catalogue, ni préférences, ni données métier. Aucun réseau nécessaire pour afficher les crédits ou les textes locaux ; les liens externes restent facultatifs.
- Ne pas mélanger la future « grande passe graphique » avec cette petite fonctionnalité.

## Sources et exactitude documentaire

- Lire le **texte de licence officiel adapté à la version** et ses attributions, plutôt que déduire une licence de la seule famille d'outil.
- Distinguer utilisation d'une bibliothèque, redistribution de ses fichiers, runtime installé séparément, code propre et outils de développement.
- Si une attribution ou un texte exact reste douteux, consigner le point dans le rapport et indiquer « à confirmer », au lieu de produire une affirmation de conformité.
- Réaliser seulement les copies de textes légalement nécessaires/appropriées, et éviter les copies de code des composants.
- Les obligations d'une **future distribution binaire** seront à vérifier lors de la mission d'installateur ; MG-012 ne vaut ni certification juridique ni audit complet des DLL/codecs.

## Vérifications et critères de recette

- Tester ouverture via le menu, fermeture, Échap, répétition d'ouverture, focus, redimensionnement, défilement, lisibilité hors ligne.
- Vérifier exactitude des composants, versions, types de dépendance, URL et notices locales par rapport aux sources ; vérifier qu'aucune licence du code Trucabule n'a été attribuée implicitement.
- Contrôler que le Collector et `puppeteer-core` ne sont pas présentés comme composants exécutés par Mon GPT desktop.
- Tester que l'écran ne modifie ni données métier ni préférences.
- Exécuter `python -m unittest discover -s tests -v`, les vérifications statiques pertinentes et une **recette Windows réelle** sur données fictives isolées, conformément à `AGENTS.md`. Ne pas confondre tests simulés avec validation visuelle réelle ; signaler précisément tout contrôle impossible.
- Documenter brièvement l'écran dans le README et/ou `docs/`, avec rapport `reports/MG-012/rapport.md` et, si pertinent, captures fictives limitées.

## Publicité, livraison et point d'arrêt

Dans **Mon-GPT seulement**, les modifications de code, tests, documents et notices nécessaires à MG-012 sont autorisées ; après vérification, commit/push sur `origin/main` selon les consignes du dépôt, sans push forcé ni écrasement de contributions concurrentes. Publier aussi un résultat PARTIEL ou bloqué, clairement qualifié. Vérifier le SHA distant et l'état Git.

**STOP après MG-012.** Aucune modification du Collector, aucune licence générale choisie, aucune passe graphique majeure, aucun exécutable/installeur, aucune migration de données, aucune refonte de l'architecture ou mutualisation des autres applications.

La fonctionnalité attendue est simplement : **une belle petite fenêtre « Licences et crédits » fiable, lisible et prête à accompagner la distribution future.**
