import csv
import statistics
from collections import defaultdict


def charger_historique(chemin, journal):
    """Lit l'historique une seule fois et l'indexe par enseigne et produit."""
    historique = {}
    nombre_lignes = 0
    anomalies = 0

    with open(chemin, encoding="utf-8-sig", newline="") as fichier:
        for ligne in csv.DictReader(fichier):
            nombre_lignes += 1
            try:
                date = ligne["date"]
                source = ligne["source"]
                produit_id = ligne["produit_id"]
                prix = int(ligne["prix_fcfa"])
            except (KeyError, TypeError, ValueError):
                anomalies += 1
                continue

            historique.setdefault((source, produit_id), []).append((date, prix))

    journal.append(
        f"[Historique] {nombre_lignes} lignes lues, {anomalies} anomalie(s)"
    )
    return historique


def _variations_black_friday(hist, debut, fin):
    variations = []
    for (source, produit_id), prix_dates in hist.items():
        prix_annuels = [prix for _, prix in prix_dates]
        prix_black_friday = [
            prix for date, prix in prix_dates if debut <= date <= fin
        ]
        if not prix_black_friday or not prix_annuels:
            continue

        moyenne_annuelle = statistics.mean(prix_annuels)
        moyenne_black_friday = statistics.mean(prix_black_friday)
        variation_pct = (moyenne_black_friday / moyenne_annuelle - 1) * 100
        variations.append({
            "source": source,
            "produit_id": produit_id,
            "variation_pct": variation_pct,
        })
    return variations


def analyser_black_friday(
    hist,
    debut="2025-11-24",
    fin="2025-11-30",
):
    """Compare la semaine Black Friday à la moyenne annuelle par produit."""
    variations_par_source = defaultdict(list)
    for variation in _variations_black_friday(hist, debut, fin):
        variations_par_source[variation["source"]].append(
            variation["variation_pct"]
        )

    return {
        source: (
            round(statistics.mean(variations), 2),
            len(variations),
        )
        for source, variations in variations_par_source.items()
    }


def variations_black_friday(
    hist,
    debut="2025-11-24",
    fin="2025-11-30",
):
    """Retourne les variations Black Friday détaillées pour l'export CSV."""
    return _variations_black_friday(hist, debut, fin)


def mois_le_moins_cher(hist):
    """Calcule l'indice mensuel moyen, 100 représentant la moyenne annuelle."""
    indices_par_source = defaultdict(lambda: defaultdict(list))
    for (source, _), prix_dates in hist.items():
        moyenne_annuelle = statistics.mean(prix for _, prix in prix_dates)
        if moyenne_annuelle == 0:
            continue

        prix_par_mois = defaultdict(list)
        for date, prix in prix_dates:
            prix_par_mois[date[:7]].append(prix)

        for mois, prix_mois in prix_par_mois.items():
            indice = statistics.mean(prix_mois) / moyenne_annuelle * 100
            indices_par_source[source][mois].append(indice)

    return {
        source: {
            mois: round(statistics.mean(indices), 2)
            for mois, indices in mois_indices.items()
        }
        for source, mois_indices in indices_par_source.items()
    }


def mesurer_analyse_naive(hist, debut="2025-11-24", fin="2025-11-30"):
    """Mesure une analyse O(K x N) en filtrant toutes les lignes à chaque couple."""
    lignes = [
        (source, produit_id, date, prix)
        for (source, produit_id), prix_dates in hist.items()
        for date, prix in prix_dates
    ]
    couples = list(hist)
    variations = []
    for source, produit_id in couples:
        prix_couple = [
            prix for src, pid, _, prix in lignes
            if src == source and pid == produit_id
        ]
        prix_black_friday = [
            prix for src, pid, date, prix in lignes
            if src == source
            and pid == produit_id
            and debut <= date <= fin
        ]
        if prix_black_friday:
            variations.append(
                statistics.mean(prix_black_friday)
                / statistics.mean(prix_couple)
                * 100
            )
    return variations

