"""Lancement sur un réseau original ou sur le petit exemple synthétique fourni."""

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def fichiers_reseau(dossier, numero):
    return [dossier / f"{prefix}{numero}.txt" for prefix in ("connec", "noeuds", "debit", "Diam")]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Simulation pédagogique de réseau d'eau potable.")
    groupe = parser.add_mutually_exclusive_group(required=True)
    groupe.add_argument("--demo", action="store_true", help="Réseau synthétique fourni (4 nœuds).")
    groupe.add_argument("--data-dir", type=Path, help="Dossier contenant les 4 fichiers du réseau original.")
    parser.add_argument("--network", choices=("0", "2"), default="2", help="Suffixe des fichiers originaux.")
    parser.add_argument("--modele", choices=("lineaire", "non-lineaire"), default="non-lineaire")
    parser.add_argument("--solveur", choices=("numpy", "ldlt"), default="numpy")
    parser.add_argument("--charge-source", type=float, help="Charge à la source (m) : 80 en démo, 200 sur le réseau original.")
    parser.add_argument("--sans-interface", action="store_true", help="Calcul et bilan dans le terminal.")
    args = parser.parse_args(argv)

    dossier = ROOT / "data" / "demo" if args.demo else args.data_dir.resolve()
    fichiers = fichiers_reseau(dossier, "0" if args.demo else args.network)
    manquants = [str(f) for f in fichiers if not f.is_file()]
    if manquants:
        parser.error("Fichiers manquants :\n" + "\n".join(manquants))

    # Imports après la lecture des options : --help fonctionne sans dépendances.
    from Main_tout_modele import Controleur

    controleur = Controleur(
        [str(f) for f in fichiers],
        "Linéaire" if args.modele == "lineaire" else "Non Linéaire",
        "Numpy" if args.solveur == "numpy" else "LDLT",
        1e-8, args.charge_source if args.charge_source is not None else (80 if args.demo else 200), 2, 9,
    )
    controleur.resolution()
    print(f"Réseau : {len(controleur.noeuds)} nœuds, {len(controleur.canalisations)} canalisations")
    for noeud in controleur.noeuds:
        print(f"Nœud {noeud.num} : charge = {noeud.potentiel:.6f} m ; pression calculée = {noeud.P:.3f} atm")
    if not args.sans_interface:
        from Affichage_tout_modele import Affichage_reseau
        Affichage_reseau(controleur).mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
