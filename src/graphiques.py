import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt


def graphique_produit(index, pid, chemin="output/graphique_produit.png"):
  """Génère un histogramme comparant le prix d'un produit dans les différentes enseignes."""
  os.makedirs(os.path.dirname(chemin), exist_ok=True)
  fiche = index.get(pid, {})
  sources = []
  prix = []
  for src, info in fiche.items():
    if info.get("prix_paye") is not None:
      sources.append(src)
      prix.append(info["prix_paye"])

  if not prix:
    return

  min_prix = min(prix)
  couleurs = ["#4e79a7" if p != min_prix else "#59a14f" for p in prix]

  plt.figure(figsize=(8, 5))
  plt.bar(sources, prix, color=couleurs, width=0.5)
  plt.title(f"Comparaison des prix payés pour le produit {pid}")
  plt.ylabel("Prix payé (FCFA)")
  plt.grid(axis="y", linestyle="--", alpha=0.7)
  plt.savefig(chemin, dpi=120, bbox_inches="tight")
  plt.close()


def graphique_historique(hist, pid, chemin="output/graphique_historique.png"):
  """Génère la courbe d'évolution annuelle d'un produit avec une bande grisée pour le Black Friday."""
  os.makedirs(os.path.dirname(chemin), exist_ok=True)
  plt.figure(figsize=(10, 5))

  sources_tracees = 0
  dates = []
  for (source, p), series in hist.items():
    if p == pid:
      dates = [
          mdates.date2num(datetime.strptime(d, "%Y-%m-%d"))
          for d, _ in series
      ]
      prixs = [pr for _, pr in series]
      plt.plot(dates, prixs, label=source, linewidth=2)
      sources_tracees += 1

  if sources_tracees > 0 and dates:
    # Bande grisée pour la semaine du Black Friday
    plt.axvspan(
        float(mdates.date2num(datetime(2025, 11, 24))),
        float(mdates.date2num(datetime(2025, 11, 30))),
        color="gray",
        alpha=0.3,
        label="Semaine Black Friday",
    )
    plt.xticks(dates[::30], rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.title(f"Évolution annuelle des prix et impact Black Friday - {pid}")
    plt.xlabel("Date")
    plt.ylabel("Prix (FCFA)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(chemin, dpi=120, bbox_inches="tight")
  plt.close()