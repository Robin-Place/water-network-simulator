# -*- coding: utf-8 -*-

import numpy as np

# =======================================
# Algorithme LDLT - Résolution de Système
# =======================================

# 1. UTILITAIRES DE MATRICES

def creer_matrice_nulle(n, p):
    """Crée une matrice n lignes par p colonnes remplie de 0.0."""
    return [[0.0 for _ in range(p)] for _ in range(n)]



# 2. ALGORITHMES CŒURS : FACTORISATION (LDL^T)

def factorisation_ldl(A):
    """
    Effectue la factorisation A = L * D * L^T.
    Retourne (L, D) où L est triangulaire inférieure unitaire et D est diagonale.
    """
    n = len(A)
    L = creer_matrice_nulle(n, n)
    D = creer_matrice_nulle(n, n)
    
    for i in range(n):
        L[i][i] = 1.0  
    
    for j in range(n):
        # Calcul de D[j][j]
        somme_D = sum((L[j][k] ** 2) * D[k][k] for k in range(j))
        D[j][j] = A[j][j] - somme_D
        
        if D[j][j] == 0:
            raise ValueError("La matrice est singulière ou nécessite un pivotement.")
        
        # Calcul de L[i][j] pour i > j
        for i in range(j + 1, n):
            somme_L = sum(L[i][k] * L[j][k] * D[k][k] for k in range(j))
            L[i][j] = (A[i][j] - somme_L) / D[j][j]
            
    return L, D



# 3. ALGORITHMES DE RÉSOLUTION

def resolution_descente(L, b):
    """ Étape 1 : Résout L * y = b par substitution avant (Descente) """
    n = len(L)
    y = [0.0] * n
    for i in range(n):
        somme = sum(L[i][k] * y[k] for k in range(i))
        y[i] = b[i] - somme
    return y


def resolution_diagonale(D, y):
    """ Étape 2 : Résout D * z = y par simple division scalaire """
    n = len(D)
    z = [0.0] * n
    for i in range(n):
        z[i] = y[i] / D[i][i]
    return z


def resolution_remontee(L, z):
    """ Étape 3 : Résout L^T * x = z par substitution arrière (Remontée) """
    n = len(L)
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        # Les coefficients de L^T à la ligne i correspondent à L[k][i] pour k > i
        somme = sum(L[k][i] * x[k] for k in range(i + 1, n))
        x[i] = z[i] - somme
    return x



# 4. ORCHESTRATEUR GLOBAL

def resoudre_systeme_symetrique(A, b):
    """
    Résout le système linéaire A * x = b en exploitant la symétrie via LDL^T.
    Évite l'inversion explicite de la matrice. O(n²) opérations après factorisation.
    """
    # 1. Factorisation
    L, D = factorisation_ldl(A)
    
    # 2. Descente, Diagonale, Remontée
    y = resolution_descente(L, b)
    z = resolution_diagonale(D, y)
    x = resolution_remontee(L, z)
    
    return np.array(x)




# =========================================
# Version Optimisée avec Numpy (Vectorisée)
# =========================================

def factorisation_ldl_numpy(A):
    """ Effectue la factorisation A = L * D * L^T de manière vectorisée. """
    n = A.shape[0]
    L = np.eye(n)          
    D_diag = np.zeros(n)   
    
    for j in range(n):
        v = (L[j, :j] ** 2) * D_diag[:j]
        D_diag[j] = A[j, j] - np.sum(v)
        
        if D_diag[j] == 0:
            raise ValueError("La matrice est singulière ou nécessite un pivotement.")
        
        if j < n - 1:
            somme_L = L[j+1:, :j] @ (L[j, :j] * D_diag[:j])
            L[j+1:, j] = (A[j+1:, j] - somme_L) / D_diag[j]
            
    return L, np.diag(D_diag)


def resolution_descente_numpy(L, b):
    """ Étape 1 vectorisée : L * y = b """
    n = L.shape[0]
    y = np.zeros(n)
    for i in range(n):
        y[i] = b[i] - L[i, :i] @ y[:i]
    return y


def resolution_diagonale_numpy(D, y):
    """ Étape 2 vectorisée : D * z = y """
    d_diag = np.diag(D) # Extraction du vecteur diagonal
    return y / d_diag


def resolution_remontee_numpy(L, z):
    """ Étape 3 vectorisée : L^T * x = z """
    n = L.shape[0]
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        # L[i+1:, i] correspond à la colonne de L, soit la ligne de L^T
        x[i] = z[i] - L[i + 1:, i] @ x[i + 1:]
    return x



# ORCHESTRATEUR GLOBAL (Version Numpy)

def resoudre_systeme_symetrique_numpy(A, b):
    """
    Résout de manière optimisée et vectorisée le système A * x = b via LDL^T.
    """
    # 1. Factorisation
    L, D = factorisation_ldl_numpy(A)
    
    # 2. Enchaînement des résolutions triangulaires/diagonales
    y = resolution_descente_numpy(L, b)
    z = resolution_diagonale_numpy(D, y)
    x = resolution_remontee_numpy(L, z)
    
    return x