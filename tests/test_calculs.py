"""Contrôles numériques indépendants des jeux de données universitaires."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

import numpy as np
from Inversion_matrice_symetrique import (
    factorisation_ldl_numpy,
    resoudre_systeme_symetrique,
    resoudre_systeme_symetrique_numpy,
)
from Main_tout_modele import Controleur


ROOT = Path(__file__).resolve().parents[1]


class TestSolveur(unittest.TestCase):
    def test_factorisation_reconstruit_la_matrice(self):
        matrice = np.array([[4., 1., 2.], [1., 5., 1.], [2., 1., 6.]])
        L, D = factorisation_ldl_numpy(matrice)
        np.testing.assert_allclose(L @ D @ L.T, matrice, atol=1e-12)

    def test_solution_comparee_a_numpy(self):
        rng = np.random.default_rng(42)
        for n in (1, 3, 12):
            B = rng.normal(size=(n, n))
            A = B @ B.T + np.eye(n)
            b = rng.normal(size=n)
            for signe in (-1, 1):
                with self.subTest(n=n, signe=signe):
                    attendue = np.linalg.solve(signe * A, b)
                    np.testing.assert_allclose(resoudre_systeme_symetrique_numpy(signe * A, b), attendue, atol=1e-11)
                    np.testing.assert_allclose(resoudre_systeme_symetrique((signe * A).tolist(), b.tolist()), attendue, atol=1e-11)

    def test_second_membre_colonne(self):
        A = np.array([[4., 1.], [1., 3.]])
        b = np.array([[1.], [2.]])
        x = resoudre_systeme_symetrique_numpy(A, b)
        np.testing.assert_allclose(A @ x, b.ravel(), atol=1e-12)

    def test_pivot_nul_signale(self):
        with self.assertRaises(ValueError):
            resoudre_systeme_symetrique_numpy(np.zeros((2, 2)), np.ones(2))


class TestReseau(unittest.TestCase):
    def test_reseau_original_bilan_de_la_source(self):
        fichiers = [str(ROOT / f"{p}2.txt") for p in ("connec", "noeuds", "debit", "Diam")]
        for modele in ("Linéaire", "Non Linéaire"):
            for solveur in ("Numpy", "LDLT"):
                with self.subTest(modele=modele, solveur=solveur):
                    c = Controleur(fichiers, modele, solveur, 1e-8, 200, 2, 9)
                    with contextlib.redirect_stdout(io.StringIO()):
                        c.resolution()
                    self.assertEqual(len(c.noeuds), 30)
                    self.assertEqual(len(c.canalisations), 50)
                    self.assertAlmostEqual(-c.noeuds[0].debit, sum(c.info_debits[1:]), places=6)

    def test_reseau_demo_conserve_les_debits(self):
        fichiers = [str(ROOT / "data" / "demo" / f"{p}0.txt") for p in ("connec", "noeuds", "debit", "Diam")]
        solutions = {}
        for modele in ("Linéaire", "Non Linéaire"):
            for solveur in ("Numpy", "LDLT"):
                with self.subTest(modele=modele, solveur=solveur):
                    c = Controleur(fichiers, modele, solveur, 1e-8, 80, 2, 9)
                    with contextlib.redirect_stdout(io.StringIO()):
                        c.resolution()
                    self.assertTrue(np.isfinite(c.potentiels).all())
                    bilans = np.zeros(len(c.noeuds))
                    for canal in c.canalisations:
                        # Convention historique du débit : le modèle linéaire est orienté à l'inverse.
                        debit = -canal.debit if modele == "Linéaire" else canal.debit
                        bilans[canal.noeud1.num] -= debit
                        bilans[canal.noeud2.num] += debit
                    np.testing.assert_allclose(bilans[1:], np.array([8., 12., 10.]) / 1000, atol=1e-7)
                    self.assertAlmostEqual(bilans[0], -0.030, places=7)
                    self.assertAlmostEqual(c.noeuds[0].debit, -30., places=6)
                    solutions[(modele, solveur)] = c.potentiels
            np.testing.assert_allclose(solutions[(modele, "Numpy")], solutions[(modele, "LDLT")], atol=1e-6)

    def test_noeud_alimente_directement_solution_analytique(self):
        with tempfile.TemporaryDirectory() as dossier:
            root = Path(dossier)
            textes = {"connec0.txt": "demo\nsource et client\n1 2\n", "noeuds0.txt": "demo\nx y z\n0 0 0\n1000 0 0\n", "debit0.txt": "L/s\n-10\n10\n", "Diam0.txt": "m\n0.2\n"}
            for nom, texte in textes.items():
                (root / nom).write_text(texte, encoding="utf-8")
            fichiers = [str(root / nom) for nom in textes]
            for solveur in ("Numpy", "LDLT"):
                with self.subTest(solveur=solveur):
                    c = Controleur(fichiers, "Linéaire", solveur, 1e-8, 80, 2, 9)
                    c.resolution()
                    # Q=10 L/s, K=2*1000/(0.2*100)=100, donc H1=80-100*0.01=79 m.
                    self.assertAlmostEqual(c.potentiels[1], 79.)


if __name__ == "__main__":
    unittest.main()
