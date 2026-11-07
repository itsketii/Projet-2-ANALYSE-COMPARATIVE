def calculer_victoires(resultats):
    """Compte les victoires de chaque boutique, égalités incluses."""
    victoires = {
        "Marché Lagune": 0,
        "Baobab Shop": 0,
        "Comptoir Ivoire": 0,
    }
    for resultat in resultats:
        for boutique in resultat.get("meilleures_boutiques_liste", []):
            if boutique in victoires:
                victoires[boutique] += 1
    return victoires


def calculer_ecarts_moyens(resultats):
    """Calcule l'écart moyen de chaque boutique par rapport au prix minimal."""
    ecarts = {
        "Marché Lagune": [],
        "Baobab Shop": [],
        "Comptoir Ivoire": [],
    }
    mapping_cles = {
        "Marché Lagune": "prix_lagune",
        "Baobab Shop": "prix_baobab",
        "Comptoir Ivoire": "prix_comptoir",
    }

    for resultat in resultats:
        prix_min = resultat["prix_min"]
        if prix_min == 0:
            continue

        for boutique, cle in mapping_cles.items():
            prix_boutique = resultat.get(cle)
            if prix_boutique != "" and prix_boutique is not None:
                ecart = ((prix_boutique - prix_min) / prix_min) * 100
                ecarts[boutique].append(ecart)

    resultats_moyens = {}
    for boutique, valeurs in ecarts.items():
        moyenne = sum(valeurs) / len(valeurs) if valeurs else 0.0
        resultats_moyens[boutique] = (round(moyenne, 2), len(valeurs))
    return resultats_moyens


def top_gains(resultats):
    """Retourne les trois plus grands écarts en FCFA et en pourcentage."""
    top_fcfa = sorted(
        resultats,
        key=lambda resultat: resultat["ecart_fcfa"],
        reverse=True,
    )[:3]
    top_pct = sorted(
        resultats,
        key=lambda resultat: resultat["ecart_pct"],
        reverse=True,
    )[:3]
    return top_fcfa, top_pct


def calculer_synthese(resultats):
    """Regroupe les indicateurs principaux de l'analyse comparative."""
    top_fcfa, top_pct = top_gains(resultats)
    return {
        "victoires": calculer_victoires(resultats),
        "ecarts_moyens": calculer_ecarts_moyens(resultats),
        "top_gains_fcfa": top_fcfa,
        "top_gains_pct": top_pct,
    }
