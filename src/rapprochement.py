import csv
import re
import statistics
import unicodedata

SYNONYMES = {
    "go": "gb",
    "to": "tb",
    "fridge": "refrigerateur",
    "frigo": "refrigerateur",
    "clim": "climatiseur",
    "1hp": "1cv",
    "1.5hp": "1.5cv",
    "samsun": "samsung",
    "128go": "128gb",
    "256go": "256gb",
}

MOTS_VIDES = {
    "pc",
    "portable",
    "laptop",
    "electric",
    "et",
    "de",
    "la",
    "le",
    "les",
    "des",
    "du",
}


def tokeniser(nom_norm):
  """Transforme un nom normalisé en un ensemble de mots-clés (tokens nettoyés)."""
  if not nom_norm:
    return set()

  s = re.sub(r"(\d),(\d)", r"\1.\2", str(nom_norm))

  mots_bruts = re.findall(r"\d+\.\d+|[a-z]+\d+|\d+|[a-z]+", s.lower())

  tokens = set()
  for mot in mots_bruts:
    mot_nettoye = SYNONYMES.get(mot, mot)
    if mot_nettoye not in MOTS_VIDES:
      tokens.add(mot_nettoye)

  return tokens


def charger_catalogue(chemin):
  """Charge le catalogue de référence et renvoie un dict {produit_id: set_de_tokens}."""
  catalogue = {}
  with open(chemin, encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f, delimiter=","):
      pid = row.get("id") or row.get("produit_id")
      nom = row.get("designation") or row.get("nom")
      if pid and nom:
        nom_norm = " ".join(str(nom).lower().split())
        catalogue[pid] = tokeniser(nom_norm)
  return catalogue


def trouver_produit(tokens_ligne, catalogue):
  """Trouve le produit_id du catalogue le plus proche en utilisant l'indice de Jaccard."""
  meilleur_pid = None
  meilleur_score = 0.0
  deuxieme_score = 0.0

  for pid, tokens_cat in catalogue.items():
    if not tokens_cat:
      continue
    intersection = len(tokens_ligne & tokens_cat)
    union = len(tokens_ligne | tokens_cat)
    score = intersection / union if union > 0 else 0.0

    if score > meilleur_score:
      deuxieme_score = meilleur_score
      meilleur_score = score
      meilleur_pid = pid
    elif score > deuxieme_score:
      deuxieme_score = score

  if meilleur_score >= 0.2 and (meilleur_score - deuxieme_score) >= 0.05:
    return meilleur_pid, meilleur_score

  return None, meilleur_score


def construire_index(lignes, catalogue, journal):
  """Associe chaque ligne nettoyée à un produit_id et construit l'index final."""
  index = {}
  for l in lignes:
    tokens = tokeniser(l["nom_norm"])
    pid, score = trouver_produit(tokens, catalogue)

    if not pid:
      journal.append(
          f"[{l['source']}] {l['id_source']} : produit non rapproché (nom ="
          f" {l['nom_brut']})"
      )
      continue

    source = l["source"]
    if source in index.setdefault(pid, {}):
      journal.append(
          f"[{source}] {pid} : conflit de doublon multi-ligne pour la même"
          " boutique"
      )
    else:
        index[pid][source] = l

  return index


def detecter_aberrants(index, journal):
  """Détecte les prix aberrants par rapport à la médiane du produit."""
  for pid, sources in index.items():
    prix_valides = [
        info["prix_paye"]
        for info in sources.values()
        if info["prix_paye"] is not None
    ]
    if len(prix_valides) >= 3:
      med = statistics.median(prix_valides)
      for source, info in sources.items():
        prix = info["prix_paye"]
        if prix is not None and (prix > 3 * med or prix < med / 3):
          journal.append(
              f"[{source}] {info['id_source']} ({pid}) : prix aberrant ({prix}"
              f" vs médiane {med})"
          )
          info["prix_paye"] = None



if __name__ == "__main__":
    from collecte import charger_lagune, charger_baobab, charger_comptoir
    from nettoyage import nettoyer

    journal = []
    lignes_brutes = (
        charger_lagune("data/marche_lagune.csv") +
        charger_baobab("data/baobab_shop.json") +
        charger_comptoir("data/comptoir_ivoire.xlsx")
    )
    lignes_propres = nettoyer(lignes_brutes, journal)

    catalogue = charger_catalogue("data/catalogue_reference.csv")
    index = construire_index(lignes_propres, catalogue, journal)

    detecter_aberrants(index, journal)

    print(f"Nombre de produits dans l'index : {len(index)}")
    print(f"Nombre total d'entrées dans le journal : {len(journal)}")

    print("\nExemple d'index pour le produit P01 :")
    if "P01" in index:
        for source, data in index["P01"].items():
            print(f" - {source} : {data['nom_brut']} | Prix payé : {data['prix_paye']} FCFA")