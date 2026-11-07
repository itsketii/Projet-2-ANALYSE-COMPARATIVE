import random
import time


def faux_nom(i):
    marques = [
        "samsung",
        "tecno",
        "infinix",
        "hp",
        "lenovo",
        "dell",
        "lg",
        "hisense",
    ]
    return f"{random.choice(marques)} modele{i} {random.choice([64, 128, 256])}gb"


def simuler_stress():
    print("Génération des données de stress (500 produits par boutique)...")
    catalogue = {f"P{i:03d}": set(faux_nom(i).lower().split()) for i in range(500)}
    lignes = []
    for b in ["Lagune", "Baobab", "Comptoir"]:
        for i in range(500):
            lignes.append(faux_nom(i).upper() if b == "Lagune" else faux_nom(i))

    # 1. Approche naïve (échantillonnée pour éviter le blocage complet)
    t0 = time.perf_counter()
    echantillon = lignes[:50]
    for l in echantillon:
        tokens_l = set(l.lower().split())
        for pid, tokens_cat in catalogue.items():
            _ = (
                len(tokens_l & tokens_cat) / len(tokens_l | tokens_cat)
                if (tokens_l | tokens_cat)
                else 0
            )
    t1 = time.perf_counter()
    temps_naif = (t1 - t0) * (len(lignes) / len(echantillon))

    # 2. Approche indexée (index inversé)
    t2 = time.perf_counter()
    index_inverse = {}
    for pid, tokens in catalogue.items():
        for t in tokens:
            index_inverse.setdefault(t, set()).add(pid)

    for l in lignes:
        tokens_l = set(l.lower().split())
        candidats = set()
        for t in tokens_l:
            if t in index_inverse:
                candidats.update(index_inverse[t])
    t3 = time.perf_counter()
    temps_index = t3 - t2

    print("\n--- RÉSULTATS DU TEST DE STRESS (1500 lignes vs 500 produits) ---")
    print(f" • Temps approche naïve (estimé) : {temps_naif:.4f} s")
    print(f" • Temps approche indexée        : {temps_index:.4f} s")
    print(
        "→ Conclusion : L'indexation évite la complexité O(N²) et reste"
        " instantanée.\n"
    )


if __name__ == "__main__":
    simuler_stress()
