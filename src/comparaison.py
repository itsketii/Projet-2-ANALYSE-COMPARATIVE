import csv
import statistics


def prix_exploitables(fiche):
    """Extrait un dictionnaire {source: prix_paye} pour les lignes en stock et avec un prix valide."""
    exploitables = {}
    for source, info in fiche.items():
        if info.get("en_stock") and info.get("prix_paye") is not None:
            exploitables[source] = info["prix_paye"]
    return exploitables


def comparer(index, noms_catalogue, journal):
    """Compare les prix par produit et génère les indicateurs (min, max, moyenne, écarts)."""
    resultats = []
    
    for pid, fiche in index.items():
        nom_produit = noms_catalogue.get(pid, pid)
        p = prix_exploitables(fiche)
        
        if len(p) < 2:
            raisons = []
            for src, info in fiche.items():
                if not info.get("en_stock"):
                    raisons.append(f"{src}: rupture")
                elif info.get("prix_paye") is None:
                    raisons.append(f"{src}: prix absent")
                else:
                    raisons.append(f"{src}: un seul prix exploitable")
            journal.append(f"[Comparatif] {pid} ({nom_produit}) : non comparable ({', '.join(raisons)})")
            continue
            
        prix_min = min(p.values())
        prix_max = max(p.values())
        prix_moyen = round(statistics.mean(p.values()))
        
        meilleures_boutiques = [s for s, val in p.items() if val == prix_min]
        meilleure_boutique_str = " / ".join(meilleures_boutiques)
        
        ecart_fcfa = prix_max - prix_min
        ecart_pct = round((ecart_fcfa / prix_min) * 100, 1) if prix_min > 0 else 0.0
        economie_vs_moyenne_pct = round(((prix_moyen - prix_min) / prix_moyen) * 100, 1) if prix_moyen > 0 else 0.0
        
        ligne_res = {
            "produit_id": pid,
            "produit": nom_produit,
            "prix_lagune": p.get("Marché Lagune", ""),
            "prix_baobab": p.get("Baobab Shop", ""),
            "prix_comptoir": p.get("Comptoir Ivoire", ""),
            "meilleure_boutique": meilleure_boutique_str,
            "meilleures_boutiques_liste": meilleures_boutiques,
            "prix_min": prix_min,
            "prix_moyen": prix_moyen,
            "ecart_fcfa": ecart_fcfa,
            "ecart_pct": ecart_pct,
            "economie_vs_moyenne_pct": economie_vs_moyenne_pct
        }
        resultats.append(ligne_res)
        
    return resultats


def exporter_csv(lignes, chemin):
    """Exporte les résultats comparatifs dans un fichier CSV avec séparateur point-virgule."""
    if not lignes:
        return
    colonnes_exclues = {"meilleures_boutiques_liste"}
    colonnes = [c for c in lignes[0] if c not in colonnes_exclues]
    with open(chemin, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=colonnes, delimiter=";")
        writer.writeheader()
        for ligne in lignes:
            writer.writerow({cle: valeur for cle, valeur in ligne.items() if cle in colonnes})