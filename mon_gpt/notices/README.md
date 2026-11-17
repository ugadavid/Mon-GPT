# Notices locales — MG-012

Textes de référence vérifiés le **17 novembre 2026**, consultables hors ligne via Aide → Licences et crédits… Les textes originaux sont conservés intégralement, dans leur langue, sans substitution par une traduction ou un résumé. Seules les fins de ligne sont normalisées en LF et une fin de ligne finale est assurée. Les espaces finaux d’origine sont conservés ; `.gitattributes` désactive les alertes d’espaces finaux et la conversion automatique des fins de ligne dans ces seuls textes. `sources.json` donne leur provenance et leur SHA-256 UTF-8/LF.

| Fichier | Provenance / version exacte |
|---|---|
| `python-3.13.17-windows.txt` | `LICENSE.txt` intégral de l’installation CPython 3.13.17 Windows x64 observée ; commence par le [LICENSE de v3.13.17](https://github.com/python/cpython/blob/v3.13.17/LICENSE), puis conserve les avis propres à cette distribution Windows. PSF-2.0, historique BeOpen/CNRI/CWI, 0BSD des exemples et avis complémentaires restent inclus. |
| `tcl-8.6.15.txt` | [Tcl core-8-6-15 / license.terms](https://github.com/tcltk/tcl/blob/core-8-6-15/license.terms), téléchargé depuis cette référence officielle. |
| `tk-8.6.15.txt` | [Tk core-8-6-15 / license.terms](https://github.com/tcltk/tk/blob/core-8-6-15/license.terms), identique au texte de l’installation observée. Tcl et Tk ont des termes distincts. |
| `pillow-13.0.0-windows.txt` | Fichier `pillow-13.0.0.dist-info/licenses/LICENSE` complet de la wheel Windows x64 / CPython 3.13 installée : [licence source 13.0.0 MIT-CMU](https://github.com/python-pillow/Pillow/blob/13.0.0/LICENSE) vérifiée comme préfixe, puis tous les avis de ses sous-composants, sans suppression des sections non utilisées par l’application. |

Les versions du tableau de l’application sont interrogées à l’exécution, sans réseau. Ces notices demeurent des **références datées** : une installation différente peut fournir d’autres avis. Elles ne prouvent ni la liste ni les obligations d’un futur assemblage autonome. Les bibliothèques et runtimes sont actuellement installés séparément ; aucun fichier de code, DLL ou codec n’est redistribué par cet ajout documentaire.

Ne pas attribuer ces licences au code Trucabule, aux images ou aux autres ressources. **La licence générale du code Trucabule n’est pas encore fixée.** RT-001 reste partiel ; les droits des ressources et les artefacts effectivement redistribués restent à contrôler séparément. Collector et Puppeteer ne sont pas des composants d’exécution du bureau.

Pour une mise à jour : vérifier version, fichier officiel et attributions, conserver le texte complet, actualiser `sources.json` et les références de `credits.py`, puis refaire tests et recette. Les avis originaux restent consultables dans les fichiers, même sans l’interface.
