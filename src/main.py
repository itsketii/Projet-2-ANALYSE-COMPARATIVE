import csv
import os
from collecte import charger_lagune, charger_baobab, charger_comptoir
from nettoyage import nettoyer
from rapprochement import charger_catalogue, construire_index, detecter_aberrants
from comparaison import comparer, exporter_csv


def main():
    journal = []

    lignes_brutes = (
        charger_lagune("data/marche_lagune.csv") +
        charger_baobab("data/baobab_shop.json") +
        charger_comptoir("data/comptoir_ivoire.xlsx")
    )

    lignes_propres = nettoyer(lignes_brutes, journal)

    catalogue_path = "data/catalogue_reference.csv"
    catalogue = charger_catalogue(catalogue_path)

    noms_catalogue = {}
    with open(catalogue_path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f, delimiter=","):
            noms_catalogue[row["produit_id"]] = row["nom"]

    index = construire_index(lignes_propres, catalogue, journal)

    detecter_aberrants(index, journal)

    resultats_comparatif = comparer(index, noms_catalogue, journal)

    os.makedirs("output", exist_ok=True)
    exporter_csv(resultats_comparatif, "output/comparatif.csv")

    with open("output/journal_nettoyage.txt", "w", encoding="utf-8") as f:
        for message in journal:
            f.write(message + "\n")

    print("Pipeline exécuté avec succès !")
    print(f"Produits comparables générés : {len(resultats_comparatif)}")
    print(f"Entrées totales dans le journal : {len(journal)}")


if __name__ == "__main__":
    main()