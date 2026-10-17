"""Génère un aperçu calculé de la démonstration, sans ouvrir l'interface."""

import contextlib
import io
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from Main_tout_modele import Controleur


def main():
    fichiers = [str(ROOT / "data" / "demo" / f"{p}0.txt") for p in ("connec", "noeuds", "debit", "Diam")]
    c = Controleur(fichiers, "Non Linéaire", "LDLT", 1e-8, 80, 2, 9)
    with contextlib.redirect_stdout(io.StringIO()):
        c.resolution()
    fig, ax = plt.subplots(figsize=(11, 6.6))
    fig.subplots_adjust(left=.12, right=.86, bottom=.17, top=.84)
    fig.suptitle("Simulation d'un réseau d'eau potable", fontsize=20, fontweight="bold", ha="left", x=.08)
    consommation = sum(c.info_debits[1:])
    ax.set_title(f"Réseau du projet : {len(c.noeuds)} nœuds, {len(c.canalisations)} canalisations, consommation de {consommation:g} L/s", fontsize=11, loc="left", pad=20)
    for canal in c.canalisations:
        a, b = canal.noeud1, canal.noeud2
        ax.plot([a.x, b.x], [a.y, b.y], color="#98aaa9", linewidth=1.5 + 8*canal.D, zorder=1)
        debit = canal.debit
        origine, arrivee = (a, b) if debit >= 0 else (b, a)
        ax.annotate("", xy=(origine.x + .59*(arrivee.x-origine.x), origine.y + .59*(arrivee.y-origine.y)), xytext=(origine.x + .43*(arrivee.x-origine.x), origine.y + .43*(arrivee.y-origine.y)), arrowprops={"arrowstyle": "->", "color": "#253f3e", "lw": 1.8})
        ax.annotate(f"{abs(debit)*1000:.2f} L/s", ((a.x+b.x)/2, (a.y+b.y)/2), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=9, bbox={"facecolor": "white", "edgecolor": "none", "pad": 2})
    points = ax.scatter([n.x for n in c.noeuds], [n.y for n in c.noeuds], c=[n.potentiel for n in c.noeuds], cmap="viridis", s=360, edgecolors="white", linewidths=2, zorder=3)
    decalages = [(-5, -39), (0, -39), (-24, 22), (-28, -43), (30, 20), (32, 24)]
    for n in c.noeuds:
        ax.text(n.x, n.y, str(n.num), ha="center", va="center", color="black" if n.num == 0 else "white", fontsize=10, fontweight="bold", zorder=4)
        label = "Source" if n.num == 0 else f"Consommation : {n.debit:g} L/s"
        ax.annotate(f"{label}\nH = {n.potentiel:.3f} m", (n.x, n.y), xytext=decalages[n.num], textcoords="offset points", ha="center", fontsize=9)
    fig.colorbar(points, ax=ax, shrink=.75, label="Charge hydraulique H (m)")
    ax.set(xlabel="Coordonnée x (km)", ylabel="Coordonnée y (km)", aspect="equal")
    ax.margins(x=.15, y=.42)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(.08, .035, "Newton-Raphson · solveur LDLᵀ · H₀ = 80 m\nIllustration calculée sur les données du projet fournies par Robin PLACE ; sujet et données : Florent Prunier.", fontsize=8, color="#5b6667")
    fichier = ROOT / "docs" / "demo-reseau.png"
    fig.savefig(fichier, dpi=160, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(fichier)


if __name__ == "__main__":
    main()
