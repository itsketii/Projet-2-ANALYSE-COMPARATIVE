import sys
import unittest

sys.path.insert(0, "src")
from nettoyage import nettoyer_prix, normaliser_nom, verifier_stock
from rapprochement import tokeniser, trouver_produit


class TestCasLimites(unittest.TestCase):

  def test_nettoyer_prix(self):
    self.assertEqual(nettoyer_prix("102\u202f900 FCFA"), 102900)
    self.assertIsNone(nettoyer_prix("Prix sur demande"))
    self.assertIsNone(nettoyer_prix(""))
    self.assertIsNone(nettoyer_prix(None))
    self.assertEqual(nettoyer_prix(12500), 12500)
    self.assertEqual(nettoyer_prix("279 300"), 279300)

  def test_normaliser_nom(self):
    self.assertEqual(
        normaliser_nom("  souris   sans fil  "), "souris sans fil"
    )
    self.assertEqual(normaliser_nom("CLÉ USB"), "cle usb")

  def test_verifier_stock(self):
    self.assertFalse(verifier_stock({"stock_brut": "Rupture"}))
    self.assertFalse(verifier_stock({"stock_brut": 0}))
    self.assertTrue(verifier_stock({"stock_brut": "Stock limité"}))
    self.assertTrue(verifier_stock({"stock_brut": 5}))

  def test_rapprochement_fautes(self):
    catalogue = {
        "P01": {"samsung", "galaxy", "a15", "128", "gb"},
        "P02": {"samsung", "galaxy", "a25", "128", "gb"},
    }
    # Test faute de frappe et ordre inversé
    tokens1 = tokeniser("Samsun Galaxy A15 128Go")
    pid1, _ = trouver_produit(tokens1, catalogue)
    self.assertEqual(pid1, "P01")

    tokens2 = tokeniser("Galaxy A15 128GB - Samsung")
    pid2, _ = trouver_produit(tokens2, catalogue)
    self.assertEqual(pid2, "P01")


if __name__ == "__main__":
  unittest.main()