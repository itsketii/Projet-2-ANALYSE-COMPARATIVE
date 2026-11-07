import unicodedata
import os

def noter(journal, source, id_source, probleme, action):
    journal.append(f"[{source}] {id_source} : {probleme} → {action}")

def nettoyer_prix(brut):
    if brut is None:
        return None
    if isinstance(brut, (int, float)):
        return int(brut)
    chiffres = "".join(c for c in str(brut) if c.isdigit())
    if not chiffres:
        return None
    return int(chiffres)

def normaliser_nom(texte):
    if not texte:
        return ""
    texte = " ".join(str(texte).lower().split())
    nfd = unicodedata.normalize("NFD", texte)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")

def calculer_prix_paye(l, prix_net):
    if prix_net is None:
        return None
    
    source = l["source"]
    if source == "Marché Lagune":
        return prix_net
    elif source == "Baobab Shop":
        return prix_net + l.get("livraison", 0)
    elif source == "Comptoir Ivoire":
        remise = l.get("remise_pct", 0)
        return round(prix_net * (1 - remise / 100))
    return prix_net

def verifier_stock(l):
    stock_brut = l.get("stock_brut")
    if isinstance(stock_brut, str):
        return stock_brut.strip().lower() in ["en stock", "stock limité"]
    elif isinstance(stock_brut, (int, float)):
        return stock_brut > 0
    return False

def nettoyer(lignes, journal):
    propres = []
    vus = set()
    
    for l in lignes:
        source = l["source"]
        id_src = l["id_source"]
        
        identifiant = (source, id_src)
        if identifiant in vus:
            noter(journal, source, id_src, "doublon détecté", "ligne ignorée")
            continue
        vus.add(identifiant)
        
        prix_net = nettoyer_prix(l["prix_brut"])
        if prix_net is None:
            noter(journal, source, id_src, f"prix invalide ou absent ({l['prix_brut']})", "prix_paye = None")
        
        prix_paye = calculer_prix_paye(l, prix_net)
        
        en_stock = verifier_stock(l)
        if not en_stock:
            noter(journal, source, id_src, "produit en rupture", "en_stock = False")
            
        nom_norm = normaliser_nom(l["nom_brut"])
        
        l_propre = {
            "source": source,
            "id_source": id_src,
            "nom_brut": l["nom_brut"],
            "nom_norm": nom_norm,
            "prix_paye": prix_paye,
            "en_stock": en_stock,
            "livraison": l.get("livraison", 0),
            "remise_pct": l.get("remise_pct", 0)
        }
        propres.append(l_propre)
        
    return propres

if __name__ == "__main__":
    from collecte import charger_lagune, charger_baobab, charger_comptoir
    
    journal = []
    lignes_brutes = (
        charger_lagune("data/marche_lagune.csv") +
        charger_baobab("data/baobab_shop.json") +
        charger_comptoir("data/comptoir_ivoire.xlsx")
    )
    
    lignes_propres = nettoyer(lignes_brutes, journal)
    
    print(f"Total lignes propres : {len(lignes_propres)}")
    print(f"Nombre d'anomalies dans le journal : {len(journal)}")
    print("\nExemple d'entrée du journal :")
    for j in journal[:5]:
        print(" -", j)

    os.makedirs("output", exist_ok=True)
    with open("output/journal_nettoyage.txt", "w", encoding="utf-8") as f_out:
        for ligne in journal:
            f_out.write(ligne + "\n")
    print("\nJournal sauvegardé dans output/journal_nettoyage.txt")    