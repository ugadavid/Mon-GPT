# Mon GPT<3

Interface et documentation en français. Ne publier que des exemples fictifs.

## Frontière d'architecture obligatoire

`mon_gpt/core.py` contient uniquement les modèles et règles génériques d'organisation : projets, fiches, relations, champs communs et recherche. Il ne doit importer ni l'interface, ni le stockage, ni l'adaptateur ChatGPT. Les identifiants internes restent stables et indépendants des identifiants des sources.

Les URL, identités de conversation et règles propres à ChatGPT appartiennent à `chatgpt.py`. Les informations spécifiques ne doivent pas migrer dans les fiches génériques. Le stockage orchestre les formats ; l'interface orchestre les interactions. Préserver ces frontières pour permettre l'extraction future du socle sans réécriture métier. Aucun système de plugins anticipé.

Lancer `python -m unittest discover -s tests -v` et la recette Windows avant publication. Ne pas versionner les données utilisateur.
