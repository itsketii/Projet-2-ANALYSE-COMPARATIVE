import csv
import time
from pathlib import Path
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
from graphiques import graphique_produit, graphique_historique


RACINE_PROJET = Path(__file__).resolve().parent.parent
DOSSIER_DONNEES = RACINE_PROJET / "data"
DOSSIER_SORTIE = RACINE_PROJET / "output"


def main():
    journal = []

    lignes_brutes = (
        charger_lagune(DOSSIER_DONNEES / "marche_lagune.csv") +
        charger_baobab(DOSSIER_DONNEES / "baobab_shop.json") +
        charger_comptoir(DOSSIER_DONNEES / "comptoir_ivoire.xlsx")
    )

    lignes_propres = nettoyer(lignes_brutes, journal)

    catalogue_path = DOSSIER_DONNEES / "catalogue_reference.csv"
    catalogue = charger_catalogue(catalogue_path)

    noms_catalogue = {}
    with open(catalogue_path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f, delimiter=","):
            noms_catalogue[row["produit_id"]] = row["nom"]

    index = construire_index(lignes_propres, catalogue, journal)

    detecter_aberrants(index, journal)

    resultats_comparatif = comparer(index, noms_catalogue, journal)

    DOSSIER_SORTIE.mkdir(exist_ok=True)
    exporter_csv(resultats_comparatif, DOSSIER_SORTIE / "comparatif.csv")

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

    t0 = time.perf_counter()
    hist = charger_historique(DOSSIER_DONNEES / "historique_prix.csv", journal)
    t1 = time.perf_counter()
    temps_index = t1 - t0

    t2 = time.perf_counter()
    bf_resultats = analyser_black_friday(hist)
    t3 = time.perf_counter()
    temps_indexe = t3 - t2

    t4 = time.perf_counter()
    mesurer_analyse_naive(hist)
    t5 = time.perf_counter()
    temps_naif = t5 - t4

    mois_resultats = mois_le_moins_cher(hist)

    graphique_produit(index, "P12", DOSSIER_SORTIE / "comparaison_P12.png")
    graphique_historique(hist, "P11", DOSSIER_SORTIE / "historique_P11.png")

    with open(
        DOSSIER_SORTIE / "black_friday.csv",
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["source", "produit_id", "variation_pct"],
            delimiter=";",
        )
        writer.writeheader()
        writer.writerows(variations_black_friday(hist))

    with open(DOSSIER_SORTIE / "journal_nettoyage.txt", "w", encoding="utf-8") as f:
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
    for ens, (var, nb) in bf_resultats.items():
        print(f"   • {ens:<20} : {var:>+6.1f}%  (sur {nb} produits)")
    for ens, data_mois in mois_resultats.items():
        if data_mois:
            mois_min = min(data_mois, key=lambda mois: data_mois[mois])
            print(f"   • {ens:<20} : mois le moins cher {mois_min} ({data_mois[mois_min]}% de la moyenne annuelle)")

    print("\n [7] TEMPS D'EXÉCUTION")
    print("-" * 65)
    print(f"   • Lecture + indexation : {temps_index:.6f} s")
    print(f"   • Analyse indexée      : {temps_indexe:.6f} s")
    print(f"   • Approche naïve       : {temps_naif:.6f} s")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()