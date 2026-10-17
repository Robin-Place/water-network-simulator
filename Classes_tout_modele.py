# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

class Canalisation:
    
    def __init__(self, num, D, noeuds_voisins):
        self.num = num
        self.D = D
        self.noeud1, self.noeud2 = noeuds_voisins
        self.L = self.calcul_L(self.noeud1.coo, self.noeud2.coo)*1000
        self.section = np.pi*(D/2)**2
    
    
    def __str__(self):
        return f"Canalisation {self.num} de longueur {round(self.L, 2)}m, de section {self.section}m², reliant le noeud {self.noeud1.num} et {self.noeud2.num}, et d'admittance {1/self.K(1)}"


    def affichage(self, ax):
        ax.plot([self.noeud1.x, self.noeud2.x], [self.noeud1.y, self.noeud2.y], linewidth=15*self.D)
        plt.text((self.noeud1.x + self.noeud2.x)/2, (self.noeud1.y + self.noeud2.y)/2, f"{self.num}", fontsize=10, fontweight='bold', ha='center', va='center')


    def calcul_L(self, co1, co2):
        return np.sqrt((co1[0]-co2[0])**2+ (co1[1]-co2[1])**2+ (co1[2]-co2[2])**2)


    def K(self, k, portion=1):
        return k*portion*self.L/(self.D*100) # Modèle de pertes linéaires
    
    
    def tronconnage(self, nombre, constantes, modele, potentiels=[]):
        self.troncons = []
        for i in range(1, nombre+1):
            self.troncons.append(Troncon(self, i, nombre, constantes, modele, potentiels=potentiels))
        


class Noeud:
    
    def __init__(self, num, coo, debit):
        self.num = num
        self.coo = coo
        self.x = coo[0]
        self.y = coo[1]
        self.z = coo[2]
        self.debit = debit
        self.canalisations_voisines = []
        
    
    def __str__(self):
        return f"Noeud {self.num} situé en ({self.x}, {self.y}, {self.z}), ayant un débit de fuite de {self.debit} L/s, reliant les canalisations {[c.num for c in self.canalisations_voisines]}"
        
    
    def ajouter_canalisation_voisine(self, canalisation):
        self.canalisations_voisines.append(canalisation)
        
        
    def affichage(self, num):
        plt.scatter(self.x, self.y, s=abs(self.debit), color='black', zorder=2)
        if num:
            plt.text(self.x, self.y, f"{self.num}", fontsize=12, color="red", ha='center', va='center', fontweight='bold')

    
    def calcul_pression(self):
        P = 0
        for c in self.canalisations_voisines:
            if self == c.noeud1:
                P += c.troncons[0].pression
            else:
                P += c.troncons[-1].pression
        self.P = P/len(self.canalisations_voisines)


class Troncon:
    
    def __init__(self, canalisation, numero, nombre, constantes, modele, potentiels=[]):
        self.c = canalisation
        self.num = numero
        self.n = nombre
        self.coo = list(np.array(self.c.noeud1.coo) + np.array([e*self.num/(self.n+1) for e in (np.array(self.c.noeud2.coo)-np.array(self.c.noeud1.coo))]))
        self.potentiel = 0
        if modele == 'Linéaire':
            k, rho, g = constantes
            self.potentiel = potentiels[self.c.noeud1.num] + self.c.K(k, portion=self.num/(self.n+1))*self.c.debit # deltaH = f(Q)
        elif modele == 'Non Linéaire':
            rho, g = constantes
            dH = 10.69*self.num*self.c.L/self.n*(abs(self.c.debit/100))**1.85/self.c.D**4.87 # dH = f(Q)
            self.potentiel = self.c.noeud1.potentiel + dH if self.c.noeud2.potentiel > self.c.noeud1.potentiel else self.c.noeud1.potentiel - dH
        self.pression = rho*g*(self.potentiel - (self.c.v)**2/(2*g) - self.coo[2]*1000)/101325 # théorème de Bernoulli : P = rho*g*(H -v**2/2g - z)

