import sys
import unittest

sys.path.insert(0, "src")
from nettoyage import nettoyer_prix, normaliser_nom, verifier_stock
from comparaison import comparer
from panier import calculer_panier
from rapprochement import detecter_aberrants, tokeniser, trouver_produit


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

  def test_comparatif_produit_exclusif_absent(self):
    index = {
        "P99": {
            "Marché Lagune": {"en_stock": True, "prix_paye": 1000},
        }
    }
    journal = []
    resultats = comparer(index, {"P99": "Produit exclusif"}, journal)
    self.assertEqual(resultats, [])
    self.assertIn("non comparable", journal[0])

  def test_comparatif_egalite(self):
    index = {
        "P16": {
            "Marché Lagune": {"en_stock": True, "prix_paye": 1000},
            "Baobab Shop": {"en_stock": True, "prix_paye": 1000},
            "Comptoir Ivoire": {"en_stock": True, "prix_paye": 1200},
        }
    }
    resultats = comparer(index, {"P16": "Produit égalité"}, [])
    self.assertEqual(
        resultats[0]["meilleures_boutiques_liste"],
        ["Marché Lagune", "Baobab Shop"],
    )

  def test_prix_aberrant_mis_a_none(self):
    index = {
        "P01": {
            "Marché Lagune": {
                "id_source": "ML-1021",
                "prix_paye": 1000000,
            },
            "Baobab Shop": {"id_source": "B-01", "prix_paye": 100000},
            "Comptoir Ivoire": {"id_source": "CI-01", "prix_paye": 110000},
        }
    }
    detecter_aberrants(index, [])
    self.assertIsNone(index["P01"]["Marché Lagune"]["prix_paye"])

  def test_panier_lagune_incomplet(self):
    index = {
        "P04": {
            "Baobab Shop": {"en_stock": True, "prix_paye": 75000},
        },
        "P12": {
            "Marché Lagune": {"en_stock": True, "prix_paye": 300000},
        },
    }
    panier = calculer_panier(index, {"P04": 1, "P12": 1})
    self.assertIsNone(panier["totaux_par_boutique"]["Marché Lagune"])
    self.assertEqual(panier["articles_manquants"]["Marché Lagune"], ["P04"])


if __name__ == "__main__":
  unittest.main()