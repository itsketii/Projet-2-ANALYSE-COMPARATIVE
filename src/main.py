import csv
import os
from collecte import charger_lagune, charger_baobab, charger_comptoir
from nettoyage import nettoyer
from rapprochement import charger_catalogue, construire_index, detecter_aberrants
from comparaison import comparer, exporter_csv
from synthese import calculer_victoires, calculer_ecarts_moyens, top_gains
from panier import calculer_panier


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

    victoires = calculer_victoires(resultats_comparatif)
    ecarts_moyens = calculer_ecarts_moyens(resultats_comparatif)
    top_fcfa, top_pct = top_gains(resultats_comparatif)
    
    panier = calculer_panier(index)
    paniers_ens = {
        enseigne: (
            total,
            panier["articles_manquants"].get(enseigne, []),
        )
        for enseigne, total in panier["totaux_par_boutique"].items()
    }
    total_opt = panier["total_optimise"]

    with open("output/journal_nettoyage.txt", "w", encoding="utf-8") as f:
        for message in journal:
            f.write(message + "\n")

    print("\n" + "=" * 65)
    print("       RAPPORT DE SYNTHÈSE - ANALYSE COMPARATIVE DE PRIX")
    print("=" * 65)
    print(f" Produits comparables analysés : {len(resultats_comparatif)}")
    print(f" Anomalies & alertes dans le journal : {len(journal)}")
    
    print("\n [1] VICTOIRES PAR ENSEIGNE (Meilleur prix)")
    print("-" * 65)
    for ens, nb in victoires.items():
        print(f"   • {ens:<20} : {nb:>2} produits les moins chers")

    print("\n [2] ÉCART MOYEN PAR RAPPORT AU PRIX MINIMUM (%)")
    print("-" * 65)
    for ens, (moy, nb) in ecarts_moyens.items():
        print(f"   • {ens:<20} : +{moy:>5.2f}%  (sur {nb} produits comparés)")

    print("\n [3] TOP 3 DES GAINS EN FCFA")
    print("-" * 65)
    for r in top_fcfa:
        print(f"   • [{r['produit_id']}] {r['produit']}")
        print(f"     Écart : +{r['ecart_fcfa']:,} FCFA (+{r['ecart_pct']}%) | Meilleure offre : {r['meilleure_boutique']}")

    print("\n [4] TOP 3 DES GAINS EN POURCENTAGE (%)")
    print("-" * 65)
    for r in top_pct:
        print(f"   • [{r['produit_id']}] {r['produit']}")
        print(f"     Écart : +{r['ecart_pct']}% (+{r['ecart_fcfa']:,} FCFA) | Meilleure offre : {r['meilleure_boutique']}")

    print("\n [5] COÛT DU PANIER DE RENTRÉE")
    print("-" * 65)
    for ens, (total, manquants) in paniers_ens.items():
        if total is not None:
            print(f"   • {ens:<20} : {total:>10,d} FCFA")
        else:
            print(f"   • {ens:<20} : Incomplet (manque {len(manquants)} article(s))")
    print(f"   • {'Panier Optimal (Mix)':<20} : {total_opt:>10,d} FCFA  (Économie max)")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()