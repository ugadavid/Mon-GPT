# MG-007 — Intégrer les 24 nouvelles illustrations à la galerie

**Statut : mission à réaliser ; validation utilisateur après recette.**  
**Base GitHub vérifiée :** `origin/main`, commit `51dc63f24cd4810f63cf184bbb5ae6743a118496` (« ajout illustrations MG-007 »), après MG-006 v0.6.0 validée (**117 tests réussis**).  
**Source :** `missions/MG-007-illustrations/` contient **exactement 24 PNG** en quatre séries (6 + 6 + 10 + 2). La galerie existante possède **7 couvertures** dans `mon_gpt/assets/covers/`. **Objectif : 31 couvertures sélectionnables au total.**

## 1. Une intégration, pas une création graphique

Les images ont été créées et déposées **par David**. Les utiliser **toutes les 24**, sans les redessiner, régénérer, remplacer, écarter ni produire d'autres variantes. **Conserver les 24 PNG originaux inchangés** dans `missions/MG-007-illustrations/`. Ils sont déjà présents sur le dépôt : utiliser les fichiers locaux de CODEX-VM après `git pull` ; **ne pas transférer à nouveau leurs gros blobs dans le chat ou via GitHub**.

**Réutiliser exactement la galerie et les sélecteurs déjà développés pour les projets et les fils** : `ProjectVisualFields`, `VisualLayer`, `COVERS`, `ImageLibrary.open`, le bandeau et les trois vues. Aucune nouvelle galerie, aucun nouveau bouton, aucune nouvelle couche UX.

## 2. Correspondance des 24 fichiers à vérifier sur place

Les fichiers ont des noms horodatés et non descriptifs. Voici la **correspondance de création attendue** : **Codex doit regarder chaque fichier localement et confirmer visuellement chaque association** avant nommage. Ne pas se fier seulement aux numéros, signaler les ambiguïtés éventuelles.

| Série (début du nom) | Ordre des fichiers suffixés -1, -2, etc. | Thèmes attendus |
|---|---:|---|
| `Image ChatGPT 15 nov. 2026, 11_11_…` | 1–6 | **Écriture (variante)** ; **Gaming** ; **Études** ; **Administratif** ; **Langues étrangères** ; **Développement informatique** |
| `Image ChatGPT 15 nov. 2026, 11_17_…` | 1–6 | **Travaux (bâtiment)** ; **Musique** ; **Graphisme** ; **Réflexion** ; **Institutions** ; **Santé** |
| `Image ChatGPT 15 nov. 2026, 11_38_…` | 1–10 | **Cuisine & gastronomie** ; **Finances & budget** ; **Maison & décoration** ; **Jardinage & nature** ; **Photographie & vidéo** ; **Cinéma & séries** ; **Sport & activités physiques** ; **Famille & vie personnelle** ; **Sciences & recherche** ; **Événements & fêtes** |
| `Image ChatGPT 15 nov. 2026, 11_47_…` | 1–2 | **Travail & entrepreneuriat** ; **Animaux** |

**Important :** les heures exactes varient au sein des lots. Par exemple `11_11_24-1.png` et `11_11_26-2.png`. Faire l'inventaire **des noms complets réels**, à partir du répertoire local. Il est possible que certaines scènes de production ne correspondent pas exactement au thème suggéré : l'indiquer, mais ne supprimer aucune source ni inventer un remplacement.

**Libellés courts en français** dans la galerie (Gaming, Études, Santé, Animaux…). Noms techniques et horodatages invisibles pour l'utilisateur. **Clés `pack:` stables et explicites ASCII**, par exemple `pack:gaming`, `pack:etudes`, `pack:administratif`, `pack:langues`, `pack:developpement`, `pack:travaux`, etc. Pour l'Écriture nouvelle, utiliser **`pack:ecriture_carnet` ou équivalent**, sans remplacer l'actuel `pack:ecriture`.

## 3. Optimisation du pack et préservation

Les 24 PNG sources pèsent chacun environ 2–3 Mo. Ne pas les ajouter tels quels au pack d'exécution :

- Sur CODEX-VM, inspecter format, lisibilité, dimensions et ratio avec Pillow. Convertir en **24 JPEG optimisés** dans `mon_gpt/assets/covers/` en qualité convenable (autour de 85–90), de préférence **1200 × 675**, **16:9**.
- **Pas de recadrage destructeur** : si les PNG ne sont pas exactement au ratio 16:9, contenir l'image entière sur un fond adapté plutôt que couper la composition. Comparer quelques originaux et JPEG obtenus, éviter le flou et les artefacts.
- Les originaux sous `missions/` restent bit pour bit identiques ; les 24 JPEG sont de nouveaux actifs légers. Pas de téléchargement externe, pas d'images générées ici.
- Préserver absolument les **7 images et clés historiques** : `pack:soleil`, `pack:ecriture`, `pack:voyage`, `pack:montagne`, `pack:laboratoire`, `pack:creation`, `pack:technique`. Aucun catalogue existant ne doit changer d'image.
- Les 24 nouvelles clés s'ajoutent à `identity.COVERS`. `ImageLibrary.open` sait déjà charger les JPEG `pack:` correspondants ; réutiliser ce chemin. Garder la galerie hors connexion.

## 4. Résultat à obtenir dans l'application

- **31 couvertures sélectionnables**, sans doublon de clé, vignette manquante ou image cassée ; galerie navigable au clavier, à la souris et à la molette jusqu'à la toute dernière vignette, en format **1000×680** comme en **1360×820**.
- Le même choix accessible pour **projets ET fils** grâce aux sélecteurs partagés de MG-006. Sélection, `Utiliser`, `Enregistrer/Ctrl+S` et retour à l'aperçu fonctionnent comme avant.
- `Revenir à l'héritage` sur un fil reste indépendant d'icône et couleur ; `Par défaut` sur projet revient au soleil.
- Nouvelle couverture immédiatement visible dans **bandeau, Détaillée et Mosaïque**, entière et non déformée, puis encore visible après fermeture/réouverture. Aucun changement de nom, d'URL, de notes, de rattachements ou de tags.
- Les préférences d'interface, filtres, sélection et reprise de session fonctionnent sans modification.

**Hors périmètre :** aucune modification de `schema:3`, migration, ZIP, import personnel, classement, déduplication ChatGPT, gestion de l'héritage, icônes/couleurs, contenu/tailles des cartes, présentation des vues, menu principal ou extension Chrome. **Pas de repasse artistique** ; on fera une vraie passe plus tard.

## 5. Tests et recette, preuves

**Conserver les 117 tests de MG-006**, ajouter quelques assertions portant seulement sur : 24 nouveaux noms et JPEG, 31 entrées de galerie, intégrité des dimensions, compatibilité des sept `pack:` précédents, choix et sauvegarde projet/fil, héritage, affichage dans les vues, navigation de la galerie et relecture.

Sur la **vraie application Tk** sur CODEX-VM, avec des données **fictives** :
1. Parcourir la galerie entière jusqu'à la dernière des **31 couvertures**, en format normal et compact, en utilisant souris et clavier ;
2. Affecter une nouvelle image à un **projet**, une autre à un **fil** du même projet, enregistrer : elles diffèrent en Mosaïque et dans le bandeau ;
3. Vérifier côte à côte une ancienne couverture `pack:ecriture` et la nouvelle variante Écriture ; ne perdre aucun ancien choix ;
4. Tester `Revenir à l'héritage` d'un fil, puis une restauration et relecture standard, sans modification du stockage existant ;
5. Vérifier que les JPEG chargent hors réseau et sans couper les scènes.

Livrer :
- **24 JPEG optimisés** sous `mon_gpt/assets/covers/` ;
- les **24 entrées supplémentaires** de `COVERS` et, si indispensable, un réglage minimal de défilement pour 31 choix ;
- `reports/MG-007/rapport.md` avec la **table de correspondance des 24 fichiers complets** (source → thème observé → clé → JPEG), dimensions et poids source/compressé ; noter explicitement toute association incertaine ;
- **3 ou 4 captures natives** : galerie au début, galerie à la fin, deux nouvelles couvertures dans un projet/fil, Mosaïque si pertinent ;
- README/version actualisés sobrement si nécessaire, nombre de tests, limites et commande de lancement.

Commit/push sur `origin/main` ; confirmer SHA distant et dépôt propre. **Pas de validation automatique par Codex** : attendre notre recette.

**Critère final :** les 24 illustrations que David a déposées apparaissent toutes dans la galerie existante, pour projets et fils, sans perte des sept anciennes ni modification du fonctionnement.
