import csv
import json
import openpyxl


def charger_lagune(chemin):
    lignes = []
    with open(chemin, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f, delimiter=";"):
            lignes.append({
                "source": "Marché Lagune",
                "id_source": row["reference"],
                "nom_brut": row["designation"],
                "prix_brut": row["prix"],
                "livraison": 0,
                "remise_pct": 0,
                "stock_brut": row["disponibilite"],
            })
    return lignes


def charger_baobab(chemin):
    lignes = []
    with open(chemin, "r", encoding="utf-8") as f:
        data = json.load(f)
        for item in data.get("items", []):
            lignes.append({
                "source": "Baobab Shop",
                "id_source": item.get("sku"),
                "nom_brut": item.get("title"),
                "prix_brut": item.get("pricing", {}).get("amount"),
                "livraison": item.get("pricing", {}).get("delivery_fee", 0),
                "remise_pct": 0,
                "stock_brut": item.get("stock"),
            })
    return lignes


def charger_comptoir(chemin): 
    lignes = []
    wb = openpyxl.load_workbook(chemin)
    ws = wb.active if wb.active is not None else wb.worksheets[0]
    
    for ligne in ws.iter_rows(min_row=4, values_only=True):
        code, article, rayon, prix, remise, qte, date = ligne
        if code is None:
            continue

        lignes.append({
            "source": "Comptoir Ivoire",
            "id_source": code,
            "nom_brut": article,
            "prix_brut": prix,
            "livraison": 0,
            "remise_pct": remise if remise is not None else 0,
            "stock_brut": qte
        })
    return lignes


if __name__ == "__main__":
    for nom, f in [("Lagune", charger_lagune("data/marche_lagune.csv")),
                   ("Baobab", charger_baobab("data/baobab_shop.json")),
                   ("Comptoir", charger_comptoir("data/comptoir_ivoire.xlsx"))]:
        print(nom, len(f), f[0])