# MG-012 — Fenêtre Licences et crédits

**17 novembre 2026 · Mon GPT<3 0.9.4 · Windows / CODEX-VM.**

## Livraison ciblée

**Aide → Licences et crédits…**, entre Gestes et raccourcis et À propos, ouvre une fenêtre native redimensionnable utilisant `InformationWindow` et le thème existant. Trois onglets : **Composants**, **Notices locales**, **Périmètre**. Aucun logo, nouvel asset, framework ou changement général d’apparence. La version applicative 0.9.4 est conservée ; aucune nouvelle version cible n’est imposée par MG-012.

Le tableau présente Python, Tcl, Tk et Pillow, leurs fonctions, licences et **versions installées interrogées à l’exécution**. La sélection donne les explications complètes dans une zone défilante. Entrée ou Consulter les notices ouvre le texte local correspondant ; une liste permet de changer de notice. Texte sélectionnable, Ctrl+A/Ctrl+C et navigation Tab ; bouton de source officielle facultatif et explicite. Périmètre présente le statut de Trucabule et les limites de l’inventaire.

La fenêtre est réutilisée si elle existe déjà. Échap, Fermer et la croix utilisent le cycle de vie existant, avec retour du focus. Une notice absente produit un message local lisible, sans téléchargement automatique.

## Sources et vérification documentaire

Départ propre sur `main`, `e437c3f`, puis synchronisation en avance rapide vers **`697af47`** contenant MG-012 et les cadrages. `AGENTS.md` et la mission lus. Aucun travail local préexistant à déplacer. Les manifestes et imports confirment la seule dépendance Python tierce d’exécution déclarée : `Pillow==13.0.0`. Python/Tk est un prérequis séparé. Aucun installateur versionné constaté dans ce périmètre.

Sources de revue consultées sur `ugadavid/trucabule-revue-technique`, révision distante observée **`c2d5ff748f9c8319531297c99e51c7cd99d25b62`** : [RT-001](https://github.com/ugadavid/trucabule-revue-technique/blob/c2d5ff748f9c8319531297c99e51c7cd99d25b62/reports/RT-001/rapport.md), [inventaire des licences](https://github.com/ugadavid/trucabule-revue-technique/blob/c2d5ff748f9c8319531297c99e51c7cd99d25b62/reports/RT-001/inventaire-licences.md), [note de décision](https://github.com/ugadavid/trucabule-revue-technique/blob/c2d5ff748f9c8319531297c99e51c7cd99d25b62/decisions/2026-11-17-licences-et-diffusion.md), [RT-002, surface technologique](https://github.com/ugadavid/trucabule-revue-technique/blob/c2d5ff748f9c8319531297c99e51c7cd99d25b62/reports/RT-002/inventaire-technologies.md). RT-001 demeure **PARTIEL**, aucune licence générale choisie. Aucun autre dépôt modifié, aucun document privé de revue recopié dans Mon-GPT.

| Composant | Version observée | Texte inclus et contrôle |
|---|---|---|
| Python | 3.13.17 | `LICENSE.txt` complet du runtime Windows installé : licence source [v3.13.17](https://github.com/python/cpython/blob/v3.13.17/LICENSE) vérifiée comme préfixe, puis avis additionnels Windows conservés. PSF-2.0, BeOpen, CNRI, CWI et 0BSD des exemples restent présents. |
| Tcl | 8.6.15 | [license.terms de core-8-6-15](https://github.com/tcltk/tcl/blob/core-8-6-15/license.terms) officiel complet. |
| Tk | 8.6.15 | [license.terms de core-8-6-15](https://github.com/tcltk/tk/blob/core-8-6-15/license.terms) officiel complet, identique au texte installé. Les termes ne sont pas remplacés par ceux de Tcl ou Python. |
| Pillow | 13.0.0 | `licenses/LICENSE` complet de la wheel Windows x64 / CPython 3.13 installée : [texte source MIT-CMU 13.0.0](https://github.com/python-pillow/Pillow/blob/13.0.0/LICENSE) vérifié comme préfixe, puis tous les avis supplémentaires de cette wheel. Aucune simplification en « MIT ». |

Les fichiers sont dans [`mon_gpt/notices`](../../mon_gpt/notices/README.md). Les textes ne sont ni résumés ni traduits ; fins de ligne normalisées et fin de ligne finale assurée. Le manifeste [`sources.json`](../../mon_gpt/notices/sources.json) indique provenance, références officielles et SHA-256 des textes UTF-8/LF. La bibliothèque graphique et les notices de la wheel sont distinguées : cela ne prétend pas que chaque sous-composant est utilisé par Mon GPT.

La licence générale du code **Trucabule n’est pas encore fixée**, ce qui est expliqué dans la fenêtre. Aucune licence générale, titularité individuelle, partenariat, autorisation sur les illustrations ou conformité globale n’est inventé. Les notices locales de référence sont distinguées des versions installées, qui peuvent varier chez l’utilisateur.

## Frontières préservées

`credits.py` porte seulement les références et la lecture documentaire locale ; `credits_ui.py` porte la présentation. Le menu et `open_information` réutilisent le cycle de vie existant. **Aucun changement au moteur, catalogue, préférences, schémas, stockage, imports, illustrations ou Collector.** Pas de migration, packaging, installateur ou mutualisation. L’affichage ne requiert aucun accès réseau ; seul le bouton explicite de source lance le navigateur.

## Vérifications

**203 tests Python réussis en 242,444 s** : 199 historiques conservés et quatre nouveaux tests MG-012. **43 tests JavaScript réussis** sur le Collector inchangé. `compileall` et vérification Git des espaces réussis.

```powershell
python -m unittest discover -s tests -v
python -m compileall -q mon_gpt tests/test_credits.py
cd companions/chatgpt-collector
npm test
```

[Journal Python](tests-python.txt) · [Journal JavaScript](tests-javascript.txt) · [Bilan de recette fictive](bilan-recette.json).

Les nouveaux tests contrôlent les empreintes des quatre notices, les attributions historiques, les versions réellement affichées, l’ordre du menu, la consultation intégrale des quatre fichiers, le blocage du réseau et l’absence d’ouverture de navigateur sans commande explicite. Ils vérifient aussi réutilisation sans doublon, fermeture/réouverture, Échap, focus, texte en lecture seule mais copiable, Ctrl+A/Copie, Tab, défilement jusqu’au dernier avis, source officielle explicitement invoquée et absence de modification des préférences/catalogue en mémoire ou sur disque. Une notice manquante ne déclenche aucun accès réseau. Trois dimensions Tk réelles sont exercées : **860×640**, **600×500**, **1100×760**, avec boutons et zone de lecture utilisables. La taille minimale de cette seule fenêtre est 600×500 ; le thème et les autres fenêtres ne changent pas.

### Recette Windows native

Exécution de `python -m mon_gpt --data-dir .recette/MG012 --simulate-open` dans un catalogue isolé contenant **un projet et une discussion fictifs**, fenêtre principale 1000×680. Ouverture depuis le menu Aide dans l’ordre demandé ; tableau des versions constaté ; sélection de Pillow, consultation de sa notice locale et défilement vers ses avis supplémentaires ; lecture du périmètre complet et fermeture réelle par bouton Fermer puis par **Échap** après réouverture. Aucun lien externe ni fil ChatGPT ouvert. Les trois captures sont brutes, issues de la vraie fenêtre Windows, sans retouche :

- [Composants, rôles, versions et licences](01-composants.png)
- [Notice Pillow locale et copiable](02-notices-locales.png)
- [Périmètre : Trucabule, compagnon et futur packaging](03-perimetre.png)

Après consultation et fermeture des crédits, **catalogue et `interface.json` sont identiques octet pour octet** à leurs copies de référence ; journal d’erreurs vide et aucune ouverture de fil. Aucun réseau n’est nécessaire à la consultation : textes lus depuis les fichiers locaux, scénario automatisé exécuté avec connexion socket interdite. La connexion Windows n’a pas été désactivée pour la recette visuelle.

**Limite du pilotage natif :** l’essai de redimensionnement au bord via le pilote de souris n’a pas changé les dimensions capturées. Ce geste n’est donc pas déclaré validé manuellement ; les changements réels de géométrie et la lisibilité minimale sont vérifiés par les tests Tk sous Windows aux trois tailles ci-dessus. Copie, répétition sans doublon et retour précis du focus sont également contrôlés par les tests Tk, distinctement de la recette visuelle.

Les textes officiels gardent leurs espaces finaux ; les attributs Git du seul répertoire de notices évitent leur normalisation et les faux avertissements sur ce contenu repris intégralement. Les données et fichiers temporaires de recette restent ignorés ; seuls notices, tests, rapport et captures fictives sont publiés.

## Limites et point d’arrêt

Les notices sont des références complètes pour les versions vérifiées, pas une extraction universelle de chaque installation possible. Si une autre version est installée, ses propres notices doivent aussi être consultées. Les composants, DLL, codecs, runtimes et ressources d’une **future distribution binaire** devront être inventoriés et contrôlés sur l’artefact effectivement livré. MG-012 ne certifie pas cet inventaire et n’achève pas RT-001. Les droits des ressources graphiques restent hors de ce petit ajout documentaire.

**STOP après publication de MG-012, en attente de validation utilisateur.**
