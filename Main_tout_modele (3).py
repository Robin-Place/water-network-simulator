# -*- coding: utf-8 -*-

from Classes_tout_modele import Canalisation, Noeud
from Affichage_tout_modele import Affichage_reseau
import numpy as np
import matplotlib.pyplot as plt
import numpy.linalg as la
from time import time
from Inversion_matrice_symetrique import resoudre_systeme_symetrique_numpy

class Controleur:
    
    def __init__(self, reseau, modele, methode_res, precision, H0, k, n):
        self.modele = modele
        self.methode_res = methode_res
        self.precision = precision
        self.H0 = H0
        self.k = k
        self.n = n
        
        self.lire_reseau(reseau)
        self.initialisation_reseau()

    
    def lire_fichier(self, nom_du_fichier):
        try:
            with open(nom_du_fichier, 'r', encoding='utf-8') as fichier:
                donnees = fichier.readlines()
                donnees_nettoyees = "Type de fichier non reconnu"
                if "connec" in nom_du_fichier:
                    # [num_noeaud_1, num_noeud_2]
                    donnees_nettoyees = [list(map(lambda x: int(x)-1, ligne.strip().split(" "))) for ligne in donnees[2:]]
                elif "noeuds0" in nom_du_fichier:
                    # [x, y, z]
                    donnees_nettoyees = [list(map(lambda x: float(x)/1000, ligne.strip().split(' '))) for ligne in donnees[2:]]
                elif "noeuds2" in nom_du_fichier:
                    # [x, y, z]
                    donnees_nettoyees = [list(map(lambda x: float(x), ligne.strip().split('\t'))) for ligne in donnees[2:]]
                elif "debit" in nom_du_fichier:
                    # debit
                    donnees_nettoyees = [int(ligne.strip()) for ligne in donnees[1:]]
                elif "Diam0" in nom_du_fichier:
                    # diamètre
                    donnees_nettoyees = [float(ligne.strip()) for ligne in donnees[1:]]
                elif "Diam2" in nom_du_fichier:
                    # diamètre
                    donnees_nettoyees = [float(ligne.strip())/100 for ligne in donnees[1:]]
                return donnees_nettoyees
        except FileNotFoundError:
            return "Erreur : Le fichier est introuvable."
        except Exception as e:
            return f"Une erreur est survenue : {e}"
    
    
    def lire_reseau(self, fichiers_reseau):
        reseau = []
        for fichier in fichiers_reseau:
            reseau.append(self.lire_fichier(fichier))
        self.info_connexions, self.info_noeuds, self.info_debits, self.info_diametres = reseau
        
    
    def affiche_reseau(self, num=False):
        fig, ax = plt.subplots()
        for c in self.canalisations:
            c.affichage(ax)
        for n in self.noeuds:
            n.affichage(num)
        plt.show()
    
    
    def initialisation_reseau(self):
        self.noeuds = []
        self.canalisations = []
        for n in range(len(self.info_noeuds)):
            self.noeuds.append(Noeud(n, self.info_noeuds[n], self.info_debits[n]))
    
        for c in range(len(self.info_connexions)):
            noeud1, noeud2 = [self.noeuds[num] for num in self.info_connexions[c]]
            self.canalisations.append(Canalisation(c, self.info_diametres[c], [noeud1, noeud2]))
            noeud1.ajouter_canalisation_voisine(self.canalisations[c])
            noeud2.ajouter_canalisation_voisine(self.canalisations[c])
        
    
    def calcul_potentiels_lineaire(self): # Modèle de pertes linéaires
        Q = [[e/1000] for e in self.info_debits[1:]] # Matrice colonne des débits des self.noeuds 1 à -1
        M = np.zeros((len(self.noeuds)-1, len(self.noeuds)-1)) # Matrice des coefficients - à inverser
        for n in range(1, len(self.noeuds)):
            c_v = self.noeuds[n].canalisations_voisines
            somme_Y = 0
            for c in c_v:
                Y = 1/c.K(self.k) # admittance Y = 1/Z
                somme_Y += Y
                n2 = c.noeud1 if c.noeud1 != self.noeuds[n] else c.noeud2 # n2 noeud voisin différent du noeud de base
                if n2.num == 0: # H0 considéré comme connu donc passe dans Q
                    Q[n-1][0] -= self.H0*Y
                else:
                    M[n-1][n2.num-1] += Y
            if n2.num != 0:
                M[n-1][n-1] = -somme_Y
        if self.methode_res == 'Numpy':
            self.potentiels = np.linalg.solve(M, Q)
        elif self.methode_res == 'LDLT':
            self.potentiels = resoudre_systeme_symetrique_numpy(M, Q)
        self.potentiels = [self.H0] + [float(e[0]) for e in self.potentiels] # Matrice ligne de H avec H0
        
        # Calcul de Qf0 pour vérification et maj de debits[0]
        c_v = self.noeuds[0].canalisations_voisines
        Qf0 = 0 
        for c in c_v:
            Y = 1/c.K(self.k)
            n2 = c.noeud1 if c.noeud1 != self.noeuds[0] else c.noeud2
            Qf0 += (self.potentiels[n2.num] - self.H0)/c.K(self.k)
        if round(Qf0*1000) != -sum(self.info_debits[1:]): # vérification Qf0 = -somme(debits)
            print(f"ERREUR du modèle : Qf0 = {Qf0*1000} != -somme(debits) = {-sum(self.info_debits[1:])}")
        else :
            if __name__ == "__main__": 
                print(f"Cohérence du modèle : -Qf0 = {-Qf0*1000} = somme(debits) = {sum(self.info_debits[1:])}")
        self.info_debits[0] = Qf0
    
    def fonction_HW(self, deltaH, D, L):
        return 100*(D**4.87*abs(deltaH)/(10.69*L))**(1/1.85)
    
    
    def jacobienne_numerique(self, H, Q):
        epsilon = 1e-8
        fcts = []
        J = np.zeros((len(H), len(H)))
        for i in range(len(H)):
            noeud = self.noeuds[i+1]
            c_v = noeud.canalisations_voisines
            fi = 0
            for c in c_v:
                noeud2 = c.noeud2 if c.noeud2 != noeud else c.noeud1
                H_n1 = H[noeud.num-1]
                H_n2 = H[noeud2.num-1] if noeud2.num != 0 else self.H0
                f = self.fonction_HW(H_n2 - H_n1, c.D, c.L) if H_n2 > H_n1 else -self.fonction_HW(H_n2 - H_n1, c.D, c.L)
                fi += f
                f_dHn1 = self.fonction_HW(H_n2 - (H_n1 + epsilon), c.D, c.L) if H_n2 > H_n1 else -self.fonction_HW(H_n2 - (H_n1 + epsilon), c.D, c.L)
                J[i][noeud.num-1] += (f_dHn1 - f)/epsilon
                if noeud2.num != 0:
                    f_dHn2 = self.fonction_HW((H_n2 + epsilon) - H_n1, c.D, c.L) if H_n2 > H_n1 else -self.fonction_HW((H_n2 + epsilon) - H_n1, c.D, c.L)
                    J[i][noeud2.num-1] += (f_dHn2 - f)/epsilon
            fcts.append(fi-Q[i])
        return np.array(fcts), np.array(J)
    
        
    def calcul_potentiels_non_lineaire(self): # Modèle de pertes linéaires
        Q = np.array(self.info_debits[1:])/1000 # Matrice colonne des débits des self.noeuds 1 à -1
        H = np.array([self.H0*(len(self.noeuds)-(i+1))/len(self.noeuds) for i in range(len(self.noeuds)-1)]) # Matrice des potentiels
        ecart = 1
        
        while ecart > self.precision:
            f,J = self.jacobienne_numerique(H, Q)
            if self.methode_res == 'Numpy' :
                dH = -la.solve(J, f)
            elif self.methode_res == 'LDLT' :
                dH = -resoudre_systeme_symetrique_numpy(J, f)
            H += dH
            ecart = la.norm(dH)
        
        # Calcul de Qf0 pour vérification et maj de debits[0]
        c_v = self.noeuds[0].canalisations_voisines
        Qf0 = 0
        for c in c_v:
            noeud2 = c.noeud2 if c.noeud2 != self.noeuds[0] else c.noeud1
            Qf0 -= self.fonction_HW(H[noeud2.num-1]-self.H0, c.D, c.L)
        if round(Qf0*1000) != -sum(self.info_debits[1:]): # vérification Qf0 = -somme(debits)
            print(f"ERREUR du modèle : Qf0 = {Qf0*1000} != -somme(debits) = {-sum(self.info_debits[1:])}")
        else : 
            print(f"Cohérence du modèle : -Qf0 = {-Qf0*1000} = somme(debits) = {sum(self.info_debits[1:])}")
        self.potentiels = np.array([self.H0] + list(H))
        self.info_debits[0] = int(Qf0*1000)
    
    
    def calcul_debits_lineaire(self):
        for c in self.canalisations:
            num_v1, num_v2 = c.noeud1.num, c.noeud2.num
            c.debit = (self.potentiels[num_v2] - self.potentiels[num_v1])/c.K(self.k) # Q = f^(-1)(deltaH)
            c.v = c.debit/c.section # Calcul de la vitesse
    
    
    def calcul_debits_non_lineaire(self):
        for c in self.canalisations:
            Q = self.fonction_HW(c.noeud1.potentiel - c.noeud2.potentiel, c.D, c.L)
            c.debit = Q if c.noeud1.potentiel > c.noeud2.potentiel else -Q
            c.v = c.debit/c.section # Calcul de la vitesse      
    
    
    def calcul_pressions(self, constantes):
        for c in self.canalisations:
            c.tronconnage(self.n, constantes, self.modele, potentiels=self.potentiels)
        for n in self.noeuds:
            n.calcul_pression()
    
    
    def resolution(self):
        
        # Mises en place du réseau
        self.initialisation_reseau()
        
        # Calcul des potentiels + maj débit noeud 0
        if self.modele == 'Linéaire':
            self.calcul_potentiels_lineaire()
        elif self.modele == 'Non Linéaire':
            self.calcul_potentiels_non_lineaire()

        for i in range(len(self.noeuds)):
            self.noeuds[i].potentiel = self.potentiels[i]
            
        self.noeuds[0].debit = self.info_debits[0]
    
        # Calcul des débits
        if self.modele == 'Linéaire':
            self.calcul_debits_lineaire()
        elif self.modele == 'Non Linéaire':
            self.calcul_debits_non_lineaire()
    
        # Calcul des pressions dans chaque tronçon
        rho = 1000; g = 9.81
        if self.modele == 'Linéaire':
            constantes = (self.k, rho, g) # nécessaires pour le tronconnage
        elif self.modele == 'Non Linéaire':
            constantes = (rho, g) # nécessaires pour le tronconnage
        self.calcul_pressions(constantes)
        
        
        
        
if __name__ == "__main__": 

    # Lecture des données
    petit_reseau = ["connec0.txt", "noeuds0.txt", "debit0.txt", "Diam0.txt"]
    grand_reseau = ["connec2.txt", "noeuds2.txt", "debit2.txt", "Diam2.txt"]
    
    
    # Définition des paramètres
    modele = 'Non Linéaire' # 'Linéaire'
    methode_res = 'Numpy' # 'Numpy'
    precision = 1e-8 # Modèle non linéaire
    H0 = 200
    k = 2 # Modèle linéaire
    n = 9 # Nombre de tronçons par canalisation
    
    
    # Création du controleur
    controleur_LDLT = Controleur(grand_reseau, modele, 'LDLT', precision, H0, k, n)
    controleur_Numpy = Controleur(grand_reseau, modele, 'Numpy', precision, H0, k, n)
    controleur = controleur_LDLT if methode_res == 'LDLT' else controleur_Numpy
    
    
    # Affichage des données
    
    t0 = time()
    controleur_LDLT.resolution()
    t1 = time()
    controleur_Numpy.resolution()
    t2 = time()
    
    print(f"\nTemps d'exéctions : \nAlgorithme LDL^T : {t1-t0} s\nMéthode numpy.linalg.solve() : {t2-t1} s\n")
    
    aff = Affichage_reseau(controleur)
    aff.mainloop()
