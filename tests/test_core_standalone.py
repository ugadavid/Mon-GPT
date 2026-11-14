"""Ce fichier ne dépend ni de ChatGPT, ni du stockage, ni de Tk."""
import unittest
from mon_gpt.core import Catalog


class StandaloneTests(unittest.TestCase):
    def test_generic_organization_and_search(self):
        catalog = Catalog()
        project = catalog.add("Études", "project")
        item = catalog.add("Une référence générique")
        item.metadata = {"Équipe": "Fiction"}
        catalog.attach(item.id, [project.id])
        self.assertEqual(catalog.search("equipe", project=project.id), [item])
        self.assertEqual(catalog.search("fiction"), [item])

    def test_relation_types_are_enforced(self):
        catalog = Catalog()
        project = catalog.add("Projet", "project")
        item = catalog.add("Fiche générique")
        for action in (lambda: catalog.move(item.id, project.id), lambda: catalog.attach(project.id, [project.id]), lambda: catalog.add("Fiche", parent=project.id), lambda: catalog.reorder(item.id, 1)):
            with self.assertRaises(ValueError):
                action()
