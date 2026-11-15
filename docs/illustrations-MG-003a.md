# Les six univers de MG-003a

Illustrations originales générées pour Mon GPT<3 le 15 novembre 2026 avec l’outil intégré **imagegen** et le [skill imagegen](C:/Users/codex/.codex/skills/.system/imagegen/SKILL.md). Aucun stock téléchargé ni maquette d’interface transformée en couverture. Les trois PNG de référence n’ont été ni modifiés ni réembarqués.

Fichiers livrés : `mon_gpt/assets/covers/ecriture.jpg`, `voyage.jpg`, `montagne.jpg`, `laboratoire.jpg`, `creation.jpg`, `technique.jpg`. Six paysages 1200×675, JPEG qualité 90, environ 1,77 Mo au total. Les sorties originales sont conservées hors dépôt ; seuls le redimensionnement/recadrage 16:9 et l’encodage ont été appliqués pour le pack applicatif. Les icônes sont dessinées par code et ne dépendent pas de cette génération.

## Prompts utilisés

Écriture :

> Use case: illustration-story. Asset type: original landscape project cover for Mon GPT<3 local app, 16:9 wide. Create one refined editorial gouache and cut-paper illustration, full bleed, warm ivory paper grain, pine green, sage, muted terracotta, honey light. Scene: an inviting writer's desk near an open window onto a rolling green garden; an open notebook, fountain pen, quiet cup and a small plant. Large clear silhouettes, lovely composition readable even as a tiny thumbnail, subtle hand-crafted texture, elegant restrained details, calm personal atelier mood. No text, lettering, logos, watermark, UI, collage or grid. One complete original illustration.

Pour chacun des cinq autres fichiers, le prompt commun suivant a été utilisé en remplaçant `{scene}` par la scène correspondante :

> Use case: illustration-story. Asset type: original project cover for Mon GPT<3, full bleed 16:9 landscape. Scene: {scene}. Style: refined editorial gouache and cut-paper illustration, warm ivory paper grain, pine green, sage, muted terracotta, honey light. Large clear silhouettes, lovely composition readable as a tiny thumbnail, subtle hand-crafted texture, elegant restrained details, calm personal atelier mood. One complete original illustration. No text, lettering, logos, watermark, UI, collage or grid.

| Fichier | Scène exacte |
| --- | --- |
| voyage.jpg | a winding coastal path above a turquoise cove, terracotta Mediterranean buildings, one little sailboat, umbrella pine and a warm low sun |
| montagne.jpg | majestic alpine peaks, a still jade lake, pines and a small terracotta cabin; generous sky and layered ridges, a sense of quiet exploration |
| laboratoire.jpg | a sunlit botanical research atelier, elegant glass flasks, microscope, botanical leaves and specimen jars on a pale workbench; warm curious handcrafted atmosphere |
| creation.jpg | an artist's atelier table with ceramic vase, brushes, terracotta pigment bowls and rich colored paper shapes, soft sage window light; bold playful balanced composition |
| technique.jpg | an elegant inventor's wooden desk with a small brass mechanical model, a circuit board, precise tools and a glowing lamp, muted petrol blue backdrop and warm honey highlights |

Ces prompts décrivent les couvertures réellement livrées. Le pack doit rester fourni avec le code pour permettre l’usage et la restauration hors connexion. Aucun appel à imagegen n’est nécessaire au lancement de Mon GPT<3.

## Ajout MG-003b : Prairie au soleil

`soleil.jpg` est une illustration locale originale 1200×675, redessinée par code dans le langage du paysage historique : soleil miel, prairie et collines sauge, trois arbres et livre ouvert. Elle se régénère avec `python -m examples.create_solar_cover` (Pillow). Aucune photo externe ni nouvelle image de référence ; les six JPEG précédents restent inchangés. Le rendu du bandeau conserve toute cette scène, au même titre que les autres couvertures.
