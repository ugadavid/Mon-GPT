# Mon GPT<3

Interface et documentation en français. Ne publier que des exemples fictifs.

## Frontière d'architecture obligatoire

`mon_gpt/core.py` contient uniquement les modèles et règles génériques d'organisation : projets, fiches, relations, champs communs et recherche. Il ne doit importer ni l'interface, ni le stockage, ni l'adaptateur ChatGPT. Les identifiants internes restent stables et indépendants des identifiants des sources.

Les URL, identités de conversation et règles propres à ChatGPT appartiennent à `chatgpt.py`. Les informations spécifiques ne doivent pas migrer dans les fiches génériques. Le stockage orchestre les formats ; l'interface orchestre les interactions. Préserver ces frontières pour permettre l'extraction future du socle sans réécriture métier. Aucun système de plugins anticipé.

Lancer `python -m unittest discover -s tests -v` et la recette Windows avant publication. Ne pas versionner les données utilisateur.

MG-002 : préserver l'ouverture directe depuis la Liste et les créations intégrées. Utiliser les tokens de `theme.py`. Le schéma métier 1 reste strict ; les préférences UI restent dans `interface.json`, hors catalogue. Vues Détaillée/Mosaïque, couvertures et imports attendent une mission validée. Les trois PNG de référence dans `missions/MG-002-maquettes` ne doivent pas être modifiés ou embarqués dans le code.

MG-003a autorise l’évolution explicite au schéma 2 : identité visuelle des projets, migration 1→2 avec copie préalable, galerie locale et import d’images. Les sauvegardes ZIP complètes incluent les ressources personnelles référencées ; les anciens JSON restent lisibles. Le résolveur `identity.py` reste indépendant de ChatGPT, de Tk et du stockage. Les vues Détaillée/Mosaïque restent hors périmètre. Préserver la présentation MG-002b hors fiche projet et seule illustration contextuelle du bandeau.
