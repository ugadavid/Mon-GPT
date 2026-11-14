import ast
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from mon_gpt.core import Catalog
from mon_gpt.chatgpt import ChatGPT, parse_url
from mon_gpt.storage import Store, encode, decode

ID = "00000000-0000-4000-8000-000000000001"
URL = f"https://chatgpt.com/c/{ID}"


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(self.temp.name)
        self.cat = Catalog()
        self.adapter = ChatGPT(self.cat)

    def project(self, name, parent=None):
        return self.cat.add(name, "project", parent)

    def test_hierarchy_move_cycles_and_safe_deletion(self):
        a = self.project("Racine")
        b = self.project("Sous-projet", a.id)
        c = self.project("Troisième niveau", b.id)
        for parent in (a.id, c.id):
            with self.assertRaises(ValueError):
                self.cat.move(a.id, parent)
        self.cat.move(c.id, a.id)
        self.assertEqual(c.parent, a.id)
        r, _ = self.adapter.ingest("Fil fictif", URL)
        self.cat.attach(r.id, [a.id])
        self.cat.delete(a.id)
        self.assertIsNone(b.parent)
        self.assertIsNone(c.parent)
        self.assertIn(r.id, self.cat.records)
        self.assertEqual(r.projects, [])

    def test_manual_order_survives_sort_and_restart(self):
        z, e, a = [self.project(n) for n in ("Zèbre", "École", "abricot")]
        self.cat.reorder(a.id, -1)
        manual = [r.id for r in self.cat.children()]
        self.assertEqual([r.title for r in self.cat.children(alphabetical=True)], ["abricot", "École", "Zèbre"])
        self.store.save(self.cat, self.adapter)
        reloaded, _ = self.store.load()
        self.assertEqual([r.id for r in reloaded.children()], manual)

    def test_multiple_locations_and_unfiled(self):
        a, b = self.project("A"), self.project("B")
        r, _ = self.adapter.ingest("Fictif", URL)
        self.cat.attach(r.id, [a.id, b.id, a.id])
        r.notes = "Note partagée"
        for project in (a, b):
            self.assertEqual([x for x in self.cat.search(project=project.id) if x.kind == "item"][0].notes, "Note partagée")
        self.cat.attach(r.id, [b.id])
        self.cat.attach(r.id, [])
        self.assertEqual(self.cat.search(unfiled=True), [r])
        self.assertIn(r, self.cat.search())

    def test_identity_and_url_safety(self):
        r, created = self.adapter.ingest("Titre préservé", URL)
        r.notes = "Notes préservées"
        same, created2 = self.adapter.ingest("Autre titre", f"https://chatgpt.com/g/g-fiction/c/{ID.upper()}?a=1#fragment")
        self.assertTrue(created)
        self.assertFalse(created2)
        self.assertIs(r, same)
        self.assertEqual(r.title, "Titre préservé")
        self.assertEqual(r.notes, "Notes préservées")
        for bad in ("http://chatgpt.com/c/" + ID, "https://chatgpt.com.evil/c/" + ID, "https://chatgpt.com@evil.com/c/" + ID, "file:///C:/x", "javascript:alert(1)", URL + "/extra", "https://chatgpt.com:443/c/" + ID, "https://chatgpt.com/c/invalide"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                parse_url(bad)

    def test_generic_search_french_metadata_and_unique_results(self):
        a = self.project("Été")
        b = self.project("Second", a.id)
        r = self.cat.add("Œuvre générique")
        a.metadata = {"Équipe": "Créativité"}
        r.metadata = {"Méthode": "Révision"}
        r.tags, r.categories = ["Étude"], ["Idées"]
        r.description, r.notes = "Résumé", "À vérifier"
        self.cat.attach(r.id, [a.id, b.id])
        for query, expected in [("ETE", a), ("equipe", a), ("CREATIVITE", a), ("methode", r), ("REVISION", r), ("oeuvre", r), ("resume", r), ("verifier", r)]:
            self.assertIn(expected, self.cat.search(query))
        items = [x for x in self.cat.search(project=a.id, tag="etude", category="idees") if x.kind == "item"]
        self.assertEqual(items, [r])

    def populated(self):
        a = self.project("Fiction")
        b = self.project("Laboratoire", a.id)
        a.notes, a.tags, a.categories, a.metadata = "Projet fictif", ["Bleu"], ["Essai"], {"Équipe": "Imaginaire"}
        r, _ = self.adapter.ingest("Fil inventé", URL)
        r.notes, r.description, r.tags, r.categories, r.metadata = "Notes", "Résumé", ["Été"], ["Idées"], {"Clé": "Valeur"}
        self.cat.attach(r.id, [a.id, b.id])

    def test_complete_export_restore_and_prebackup(self):
        self.populated()
        original = encode(self.cat, self.adapter)
        destination = Path(self.temp.name) / "export.json"
        self.store.export(destination, self.cat, self.adapter)
        imported = encode(*self.store.read(destination))
        self.assertEqual(original, imported)
        self.project("État avant restauration")
        before = encode(self.cat, self.adapter)
        cat, adapter, backup = self.store.restore(imported, self.cat, self.adapter)
        self.assertEqual(encode(cat, adapter), original)
        self.assertEqual(encode(*self.store.read(backup)), before)
        self.assertEqual(encode(*self.store.load()), original)

    def test_invalid_restore_leaves_file_intact(self):
        self.populated()
        self.store.save(self.cat, self.adapter)
        original = self.store.path.read_bytes()
        candidate = encode(self.cat, self.adapter)
        variants = []
        for key, value in [("schema", 200), ("chatgpt", []), ("records", [{}])]:
            bad = copy.deepcopy(candidate)
            bad[key] = value
            variants.append(bad)
        bad = copy.deepcopy(candidate)
        bad["records"][0]["parent"] = bad["records"][1]["id"]
        variants.append(bad)
        bad = copy.deepcopy(candidate)
        bad["records"][0]["metadata"] = {"a": 5}
        variants.append(bad)
        bad = copy.deepcopy(candidate)
        del bad["records"][0]["id"]
        variants.append(bad)
        for bad in variants:
            with self.assertRaises(ValueError):
                self.store.restore(bad, self.cat, self.adapter)
            self.assertEqual(self.store.path.read_bytes(), original)
        self.assertEqual(list(Path(self.temp.name).glob("avant-restauration*")), [])

    def test_atomic_failure_does_not_truncate_and_corrupt_load_is_error(self):
        self.populated()
        self.store.save(self.cat, self.adapter)
        original = self.store.path.read_bytes()
        with patch("mon_gpt.storage.os.replace", side_effect=OSError("Panne simulée")):
            with self.assertRaises(OSError):
                self.store.save(self.cat, self.adapter)
        self.assertEqual(original, self.store.path.read_bytes())
        self.store.path.write_text("{cassé", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.store.load()
        self.assertEqual(self.store.path.read_text(encoding="utf-8"), "{cassé")

    def test_core_has_no_application_dependencies(self):
        source = Path("mon_gpt/core.py").read_text(encoding="utf-8")
        imports = [node for node in ast.walk(ast.parse(source)) if isinstance(node, (ast.Import, ast.ImportFrom))]
        allowed = {"dataclasses", "datetime", "uuid", "unicodedata"}
        for node in imports:
            modules = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names]
            self.assertTrue(set(modules) <= allowed)

    def test_single_writer_lock(self):
        self.store.acquire()
        self.addCleanup(self.store.lock.close)
        with self.assertRaises(ValueError):
            Store(self.temp.name).acquire()


if __name__ == "__main__":
    unittest.main()
