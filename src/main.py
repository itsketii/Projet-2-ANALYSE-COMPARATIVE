import csv
import os
import time
from collecte import charger_lagune, charger_baobab, charger_comptoir
from nettoyage import nettoyer
from rapprochement import charger_catalogue, construire_index, detecter_aberrants
from comparaison import comparer, exporter_csv
from synthese import calculer_victoires, calculer_ecarts_moyens, top_gains
from panier import calculer_panier
from historique import (
    analyser_black_friday,
    charger_historique,
    mesurer_analyse_naive,
    mois_le_moins_cher,
    variations_black_friday,
)


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

    # 8. Historique et mesure de complexité
    t0 = time.perf_counter()
    historique = charger_historique("data/historique_prix.csv", journal)
    t1 = time.perf_counter()

    t2 = time.perf_counter()
    black_friday = analyser_black_friday(historique)
    t3 = time.perf_counter()

    t4 = time.perf_counter()
    mesurer_analyse_naive(historique)
    t5 = time.perf_counter()

    mois_indices = mois_le_moins_cher(historique)
    variations_detaillees = variations_black_friday(historique)
    with open("output/black_friday.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["source", "produit_id", "variation_pct"],
            delimiter=";",
        )
        writer.writeheader()
        writer.writerows(variations_detaillees)

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
    print("\n [6] BLACK FRIDAY ET MOMENT D'ACHAT")
    print("-" * 65)
    for ens, (variation, nb) in black_friday.items():
        print(f"   • {ens:<20} : {variation:+.2f}%  (sur {nb} produits)")
    for ens, indices in mois_indices.items():
        mois_min = min(indices, key=lambda mois: indices[mois])
        print(
            f"   • {ens:<20} : mois le moins cher {mois_min} "
            f"({indices[mois_min]:.2f}% de la moyenne annuelle)"
        )

    print("\n [7] TEMPS D'EXÉCUTION")
    print("-" * 65)
    print(f"   • Lecture + indexation : {t1 - t0:.6f} s")
    print(f"   • Analyse indexée      : {t3 - t2:.6f} s")
    print(f"   • Analyse naïve        : {t5 - t4:.6f} s")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()