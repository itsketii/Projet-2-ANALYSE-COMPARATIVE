PANIER_RENTREE = {
    "P04": 1,
    "P12": 1,
    "P14": 2,
    "P15": 1,
    "P28": 1,
}


def calculer_panier(index, panier=PANIER_RENTREE):
    """Calcule le total par boutique et le total optimisé article par article."""
    boutiques = sorted(
        {source for produit in index.values() for source in produit}
    )
    totaux = {boutique: 0 for boutique in boutiques}
    articles_manquants = {boutique: [] for boutique in boutiques}
    articles = []
    total_optimise = 0

    for produit_id, quantite in panier.items():
        sources = index.get(produit_id, {})
        prix_disponibles = {
            boutique: info["prix_paye"]
            for boutique, info in sources.items()
            if info.get("en_stock") and info.get("prix_paye") is not None
        }
        articles.append({
            "produit_id": produit_id,
            "quantite": quantite,
            "prix_par_boutique": prix_disponibles,
        })

        for boutique in boutiques:
            prix = prix_disponibles.get(boutique)
            if prix is not None:
                totaux[boutique] += prix * quantite
            else:
                articles_manquants[boutique].append(produit_id)

        if prix_disponibles:
            total_optimise += min(prix_disponibles.values()) * quantite

    totaux_calculables = {
        boutique: total if not articles_manquants[boutique] else None
        for boutique, total in totaux.items()
    }
    economies = {
        boutique: total - total_optimise
        for boutique, total in totaux_calculables.items()
        if total is not None
    }

    return {
        "totaux_par_boutique": totaux_calculables,
        "articles": articles,
        "articles_manquants": articles_manquants,
        "total_optimise": total_optimise,
        "economie_vs_meilleur_boutique": economies,
    }
