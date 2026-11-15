# Importer depuis Mon GPT Collector

Mon GPT<3 **0.9.0** accepte exclusivement le JSON **v2** du Collector. Le Collector Chrome reste en **0.8.2**, sans modification.

## Un ajout, distinct d’une restauration

Dans **Fichier → Importer depuis Mon GPT Collector (JSON)…**, choisir l’export. L’assistant analyse le fichier sans modifier le catalogue. **Restaurer le catalogue…** conserve sa fonction différente : remplacer le catalogue par une sauvegarde Mon GPT, après sauvegarde préalable.

Les projets sans conversation sont conservés par défaut. Les discussions sans projet sont placées dans **À classer**. Aucun message, résumé, tag, catégorie ou note n’est inventé ; les illustrations héritent des règles existantes. Aucun lien ChatGPT n’est ouvert lors de l’analyse, de l’import ou du démarrage.

## Choisir les destinations

L’onglet **Projets** affiche chaque source séparément : nom, clé abrégée, nombre de fils observés, décision et destination. Sélectionner une ligne pour lire sa clé complète et modifier le choix, puis **Appliquer le choix**. Le compteur et l’aperçu sont recalculés avant tout enregistrement.

- **Créer séparément** : un dossier local par clé inconnue, même si les noms sont identiques. Le nom observé est conservé ; un nom absent demande un titre local explicite.
- **Associer à un existant** : choisir un projet local par chemin et identifiant interne. Les noms identiques sont proposés en premier, mais aucun rapprochement n’est appliqué sans votre choix.
- **Fusionner vers un projet de l’export** : choisir une autre source destinée à être créée ou associée. Les clés individuelles sont toutes conservées, dirigées vers le même projet local. Aucune suppression de dossier ni intervention dans ChatGPT.
- **Ignorer cet import** : aucun nouveau mapping pour cette source. Ses fils restent à classer s’ils n’ont pas d’autre destination retenue. Ce choix concerne cet import seulement.

Les homonymes et collisions de noms locaux sont signalés en pastel. Une case confirme globalement leurs créations séparées : il n’est pas nécessaire de répéter des dizaines de confirmations. Les lignes et destinations restent distinctes grâce aux identifiants. Une fusion circulaire ou vers une source ignorée est refusée.

Les clés déjà connues reprennent leur correspondance mémorisée. Un changement de nom distant ne renomme jamais un projet local. Si le dossier local a été supprimé, l’assistant exige une nouvelle décision visible ; il ne le recrée pas silencieusement.

## Vérifier, confirmer, reprendre

L’onglet **Discussions** présente les titres observés, UUID abrégés, projets source, destinations et états. Une fiche déjà présente indique **Déjà présent · inchangé** et son classement local réel. Un titre absent est signalé comme provisoire. Recherche, filtres et pages de 60 lignes limitent le nombre de lignes rendues. Sélectionner une ligne pour lire le texte complet. Ctrl+F rejoint la recherche ; Tab, Espace, Entrée et Échap utilisent les contrôles habituels.

**Vérifier l’import** affiche le bilan et la confirmation finale. **Revenir aux choix** conserve les décisions. Annuler, Échap ou fermer avant confirmation ne crée ni dossier, ni sauvegarde, ni préférence d’import. Les modifications d’une fiche en cours sont protégées par le dialogue d’enregistrement existant.

**Confirmer et importer** prépare une sauvegarde ZIP complète, images personnelles comprises, puis remplace atomiquement le catalogue validé. Durant cet enregistrement, attendre le bilan. Une erreur conserve les objets actifs et le catalogue antérieur ; la sauvegarde déjà créée reste disponible. L’arbre, les compteurs, la vue active et l’aperçu sont rafraîchis après réussite. Les filtres courants restent actifs : retirer les filtres pour voir tous les nouveaux fils si nécessaire.

Réimporter le même export après fermeture, relance ou restauration ne crée aucun doublon. L’identité d’une discussion est son UUID, jamais son titre. **Tous les champs des fiches existantes restent inchangés**, y compris URL locale, classement, ordre, dates et repères graphiques. Cette version ne propose pas d’ajouter les nouveaux rattachements aux fiches déjà connues. Un export enrichi ajoute seulement les nouvelles identités.

## Validation et erreurs

L’enveloppe et chaque ligne sont strictes : champs, types, dates UTC, preuves, clés, UUID, hôte exact `chatgpt.com`, URL observées et cohérence des rattachements. Aucun format v1 ni format futur accepté. Les doublons dans les tableaux, même identiques, et les champs JSON dupliqués sont refusés : corriger l’export, plutôt que choisir arbitrairement une ligne.

**Aucune ligne invalide n’est omise.** Une anomalie refuse l’intégralité du fichier ; l’onglet Anomalies donne les lignes concernées, les motifs et l’action de correction. Il n’y a pas d’import partiel dans cette version. Limites : 6 Mio de fichier, 1 000 projets, 5 000 discussions, 10 URL/contextes par fil ; les bornes du catalogue et des sauvegardes existantes restent applicables. Lecture, planification et sauvegarde sont effectuées en arrière-plan sans opérations Tk dans le worker.

## Persistance et architecture

`collector_import.py` porte la lecture, la validation et la planification ChatGPT, sans Tk ni navigateur. `import_ui.py` orchestre l’assistant ; `storage.py` valide et enregistre la transaction. **`core.py` et `identity.py` restent inchangés** : aucune clé source dans `Record`, ses métadonnées ou ses champs communs.

Évolution minimale et explicite du catalogue : le **schéma 4** ajoute au même document atomique `chatgpt_projects`, une table `{projectKey: idProjetLocal}` appartenant à l’adaptateur ChatGPT. Plusieurs clés peuvent viser le même UUID interne. Le tableau `chatgpt` des conversations reste inchangé. Aucune table parallèle indépendante ; les sauvegardes JSON et ZIP ainsi que les restaurations transportent ces mappings.

Les catalogues 1, 2 et 3 restent lisibles selon leurs règles strictes. Un catalogue sans mapping continue d’être écrit au schéma 3 ; l’ajout de la première correspondance produit le schéma 4. Avant réécriture d’un schéma antérieur, une copie exacte `avant-migration-vN-DATE.json` est conservée, en plus du ZIP complet `avant-import-DATE.zip`. Une ancienne application ne sait pas lire le schéma 4 : utiliser la sauvegarde antérieure pour revenir à celle-ci.

La table accepte au maximum 10 000 correspondances persistées. Une destination supprimée est conservée comme témoin UUID pour réclamer une résolution au prochain import ; une destination existante doit toujours être un projet. Les préférences restent dans `interface.json`, sans décisions d’import.

## Lancement et recette isolée

Depuis PowerShell :

```powershell
& 'C:\Users\codex\Documents\Projets\mon-gpt\lancer.cmd'
```

Pour une recette fictive séparée, depuis le dépôt :

```powershell
python -m mon_gpt --data-dir .recette/MG009-demo --simulate-open
```

Le scénario Windows du fichier fourni peut être reproduit en deux processus, avec un **nouveau** dossier isolé :

```powershell
python tools/recipe_mg009.py --source missions/MG-009-imports/mon-gpt-observations.json --data-dir .recette/MG009-verification --phase first
python tools/recipe_mg009.py --source missions/MG-009-imports/mon-gpt-observations.json --data-dir .recette/MG009-verification --phase second
```

Ce pilote ouvre les vrais composants Tk et exerce les méthodes de l’assistant ; il ne simule pas des clics dans le sélecteur Windows. Le sélecteur, les gestes clavier/souris et les captures sont vérifiés séparément sur fixtures. Ses résultats publics ne doivent contenir que des compteurs et assertions, jamais les titres, noms, clés ou URL du fichier personnel.
