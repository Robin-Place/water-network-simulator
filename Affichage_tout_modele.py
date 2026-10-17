# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.scrolledtext as sc
import numpy as np 


class Affichage_reseau(tk.Tk):
    
    def __init__(self, controleur, hauteur=630, largeur=1260, l_canva=740, l_legende=20):
        super().__init__()
        self.title("Simulation réseau")
        self.geometry(f"{largeur}x{hauteur}")
        self.resizable(False, False)
        
        self.controleur = controleur
        self.hauteur = hauteur
        self.l_legende = l_legende
        self.l_canva = l_canva
        
        self.id_noeuds = {}
        self.id_troncons = {}
        self.id_textes = {}
        
        self.P_min = 2
        self.P_max = 6
        
        self.carte = tk.Canvas(width = l_canva, height = hauteur, bg='light blue')
        self.carte.pack(side=tk.LEFT)
        
        tk.Button(self, text='Afficher/Retirer les numéros des noeuds et canalisations', command=self.maj_affichage_num).pack(fill='x')
        
        self.choix = tk.StringVar(value='Aucun') 
        self.choix.trace_add("write", lambda *args:self.actualiser_affichage())
        for e in ['Aucun', 'Altitudes', 'Potentiels', 'Pressions', 'Débits']:
            tk.Radiobutton(self, text=e, value = e, variable = self.choix).pack(fill='x')
        
        self.scrolledtext = sc.ScrolledText(self, width=largeur-l_canva, height=20)
        self.scrolledtext.pack(side=tk.TOP)
        
        self.texte_visible = False
        tk.Button(self, text='Effacer le ScrolledText', command=lambda:self.scrolledtext.delete("2.0", tk.END)).pack(fill='x')
        
        self.scrolledtext.insert(tk.END, '*** Cliquer sur un élément pour afficher ses informations ***\n')
        self.scrolledtext.tag_config("alerte_verte", foreground="green", font=("Helvetica", 13))
        self.scrolledtext.tag_config("alerte_rouge", foreground="red", font=("Helvetica", 13))
        
        self.tooltip = tk.Label(self.carte, text="", bg="white")
        
        frame_H0 = tk.Frame(self)
        frame_H0.pack(side=tk.TOP, anchor='w', padx=5, pady=5)
       
        tk.Label(frame_H0, text="Nombre de tronçons :").pack(side=tk.LEFT)
        self.entry_troncons = tk.Entry(frame_H0, width=8)
        self.entry_troncons.insert(0, int(self.controleur.n))
        self.entry_troncons.pack(side=tk.LEFT, padx=5)
       
        tk.Label(frame_H0, text="H0 (m) :").pack(side=tk.LEFT)
        self.entry_H0 = tk.Entry(frame_H0, width=8)
        self.entry_H0.insert(0, int(self.controleur.H0))
        self.entry_H0.pack(side=tk.LEFT, padx=5)
        tk.Button(frame_H0, text="Valider", command=self.modifier_parametres).pack(side=tk.LEFT, padx=20)
        
        frame_P = tk.Frame(self)
        frame_P.pack(side=tk.TOP, anchor='w', padx=5, pady=5)
        tk.Button(frame_P, text="Valider", command=self.modifier_consignes).pack(side=tk.RIGHT, padx=20)
        
        frame_P_min = tk.Frame(frame_P)
        frame_P_min.pack(side=tk.TOP, anchor='w', padx=5, pady=5)
        
        tk.Label(frame_P_min, text="Pression min consigne (atm) :").pack(side=tk.LEFT)
        self.entry_P_min = tk.Entry(frame_P_min, width=8)
        self.entry_P_min.insert(0, int(self.P_min))
        self.entry_P_min.pack(side=tk.LEFT, padx=5)
       
        frame_P_max = tk.Frame(frame_P)
        frame_P_max.pack(anchor='w', padx=5, pady=5)
        
        tk.Label(frame_P_max, text="Pression max consigne (atm) :").pack(side=tk.LEFT)
        self.entry_P_max = tk.Entry(frame_P_max, width=8)
        self.entry_P_max.insert(0, int(self.P_max))
        self.entry_P_max.pack(side=tk.LEFT, padx=5)
        
        
        self.initialiser_affichage()
        self.afficher_reseau()
    
    
    def afficher_reseau(self):
        rayon = min([3/2*self.hauteur/100, 3/2*(self.l_canva-2*self.l_legende)/100])
        margex = 4*(self.l_canva-2*self.l_legende)/100 + 2*self.l_legende
        margey = 4*self.hauteur/100
        self.coo_canva(self.l_canva-2*self.l_legende, margex, margey)
        self.afficher_canalisations()
        self.afficher_noeuds(rayon)
    
    
    def afficher_noeuds(self, rayon):
        for noeud in self.controleur.noeuds:
            noeud.id = self.carte.create_oval(noeud.x_c-rayon, noeud.y_c-rayon, noeud.x_c+rayon, noeud.y_c+rayon, fill="lightgrey", outline='white', width=1)
            self.id_noeuds[noeud.id] = noeud
            self.carte.create_text(noeud.x_c, noeud.y_c, text=f'{noeud.num}', fill="white", state='hidden', tags='Texte')
            self.carte.tag_bind(noeud.id, '<Button-1>', self.clique_noeud_1)
            self.carte.tag_bind(noeud.id, '<Button-3>', self.clique_noeud_3)
            self.carte.tag_bind(noeud.id, '<Enter>', self.survol_noeud)
            self.carte.tag_bind(noeud.id, '<Leave>', self.cacher_tooltip)
    
    
    def afficher_canalisations(self):
        for canalisation in self.controleur.canalisations:
            noeud1 = canalisation.noeud1
            noeud2 = canalisation.noeud2
            n = len(canalisation.troncons)
            for i in range(n):
                troncon = canalisation.troncons[i]
                x1 = noeud1.x_c + i/n*(noeud2.x_c-noeud1.x_c)
                y1 = noeud1.y_c + i/n*(noeud2.y_c-noeud1.y_c)
                x2 = noeud1.x_c + (i+1)/n*(noeud2.x_c-noeud1.x_c)
                y2 = noeud1.y_c + (i+1)/n*(noeud2.y_c-noeud1.y_c)
                x = (x1+x2)/2
                y = (y1+y2)/2
                troncon.id = self.carte.create_line(x1, y1, x2, y2, width=troncon.c.D*20, fill='lavender')
                self.id_troncons[troncon.id] = troncon
                self.carte.tag_bind(troncon.id, '<Button-1>', self.clique_canalisation_1)
                self.carte.tag_bind(troncon.id, '<Button-3>', self.clique_canalisation_3)
                self.carte.tag_bind(troncon.id, '<Enter>', self.survol_canalisation)
                self.carte.tag_bind(troncon.id, '<Leave>', self.cacher_tooltip)
                if i == n//2:
                    self.carte.create_text(x, y, text=f'{canalisation.num}', font='bald', fill='white', state='hidden', tags='Texte')
                self.dessiner_fleche(noeud1.x_c, noeud1.y_c, noeud2.x_c, noeud2.y_c, canalisation.debit, troncon.couleur_D)
    
    def coo_canva(self, l_canva, margex, margey):
        for noeud in self.controleur.noeuds:
            noeud.x_c = margex + 92/100*l_canva*noeud.x/10
            noeud.y_c = margey + 92/100*self.hauteur*abs(noeud.y-4.5)/9
            
    
    def clique_noeud_1(self, event):
        ident = self.carte.find_withtag("current")[0]
        noeud = self.id_noeuds[ident]
        self.scrolledtext.insert(tk.END, f'\nNoeud n°{noeud.num} :\nPotentiel : {noeud.potentiel} \nPression : {noeud.P} atm\nDébit de fuite : {noeud.debit} L/s\nCoordonnées (km) : {[round(e, 9) for e in noeud.coo]}\n')
        
    
    def clique_noeud_3(self, event):
        ident = self.carte.find_withtag("current")[0]
        noeud = self.id_noeuds[ident]
        self.popup_modifier_debit(noeud)
        
    
    def clique_canalisation_1(self, event):
        ident = self.carte.find_withtag("current")[0]
        troncon = self.id_troncons[ident]
        self.scrolledtext.insert(tk.END, f'\nCanalisation n°{troncon.c.num}, troncon n°{troncon.num}/{troncon.n} :\nPotentiel : {troncon.potentiel} m\nPression : {troncon.pression} atm\nDébit : {abs(troncon.c.debit)*1000} L/s\nDiamètre : {troncon.c.D} m\nDénivelé de la canalisation: {abs(troncon.c.noeud1.z-troncon.c.noeud2.z)*1000} m\n')
        
    
    def clique_canalisation_3(self, event):
        ident = self.carte.find_withtag("current")[0]
        troncon = self.id_troncons[ident]
        self.popup_modifier_diametre(troncon.c)
        

    def popup_modifier_diametre(self, canalisation):
        popup = tk.Toplevel(self)
        popup.title(f"Modifier la canalisation n°{canalisation.num}")
        popup.geometry("350x200")
        popup.resizable(False, False)
        
        tk.Label(popup, text=f"Canalisation n°{canalisation.num}").pack(pady=(10, 0))
        tk.Label(popup, text=f"Diamètre actuel : {canalisation.D:.2f} m").pack()
        
        frame = tk.Frame(popup)
        frame.pack(pady=10)
        tk.Label(frame, text="Nouveau diamètre (m) :").pack(side=tk.LEFT)
        entry = tk.Entry(frame, width=10)
        entry.insert(0, str(round(canalisation.D, 2)))
        entry.pack(side=tk.LEFT, padx=5)

        bouton_valider = tk.Button(popup, text="Valider", command= lambda *args:valider(popup)).pack()
        message = tk.Label(popup, text="", fg="red")
        message.pack()
        
        bouton_supprimer = tk.Button(popup, text="Supprimer la canalisation", command=lambda *args:supprimer(popup)).pack()
        
        
        def valider(fenetre):
            try:
                nouveau_D = float(entry.get())
                if nouveau_D <= 0:
                    raise ValueError
                self.controleur.info_diametres[canalisation.num] = nouveau_D
                self.carte.delete('all')
                self.maj_affichage()
                self.scrolledtext.insert(tk.END, f"\nDiamètre de la canalisation {canalisation.num} mis à jour : {nouveau_D} m\n", "alerte_verte" )
                fenetre.destroy()
            except ValueError:
                message.config(text="Valeur invalide : on attend un nombre > 0", fg="red")
        
        
        def supprimer(fenetre):
            pass
            del self.controleur.info_connexions[canalisation.num]
            self.carte.delete('all')
            self.maj_affichage()
            self.scrolledtext.insert(tk.END, f"\nCanalisation {canalisation.num} supprimée\n", "alerte_verte" )
            fenetre.destroy()
        

    def popup_modifier_debit(self, noeud):
        popup = tk.Toplevel(self)
        popup.title(f"Modifier le noeud n°{noeud.num}")
        popup.geometry("350x150")
        popup.resizable(False, False)
        
        tk.Label(popup, text=f"Noeud n°{noeud.num}").pack(pady=(10, 0))
        tk.Label(popup, text=f"Débit de fuite actuel : {noeud.debit:.2f} L/s").pack()
        
        frame = tk.Frame(popup)
        frame.pack(pady=10)
        tk.Label(frame, text="Nouveau débit de fuite (L/s) :").pack(side=tk.LEFT)
        entry = tk.Entry(frame, width=10)
        entry.insert(0, str(round(noeud.debit, 2)))
        entry.pack(side=tk.LEFT, padx=5)
        message = tk.Label(popup, text="", fg="red")
        message.pack()

        bouton_valider = tk.Button(popup, text="Valider", command= lambda *args:valider(popup)).pack()
        
        
        def valider(fenetre):
            try:
                nouveau_D = float(entry.get())
                self.controleur.info_debits[noeud.num] = nouveau_D
                self.carte.delete('all')
                self.maj_affichage()
                self.scrolledtext.insert(tk.END, f"\nDébit du noeud {noeud.num} mis à jour : {nouveau_D} L/s\n", "alerte_verte" )
                fenetre.destroy()
            except ValueError:
                message.config(text="Valeur invalide : on attend un nombre", fg="red")
        
        
    def modifier_parametres(self):
        try:
            nouveau_H = int(self.entry_H0.get())
            nouveau_n = int(self.entry_troncons.get())
            if (nouveau_H < 0) or (nouveau_n<0):
                raise ValueError
            self.controleur.H0 = nouveau_H
            self.controleur.n = nouveau_n
            self.carte.delete('all')
            self.maj_affichage()
            self.scrolledtext.insert(tk.END, f"\nValeurs de H0 et n mises à jour : H0 = {nouveau_H}, n = {nouveau_n}\n", "alerte_verte" )
        except ValueError:
            self.scrolledtext.insert(tk.END,"\nValeur incorrecte : veuillez entrer un nombre\n", "alerte_rouge")
    

    def couleur_echelle(self, valeur, v_min, v_max):
        ratio = (valeur - v_min) / (v_max - v_min)        
        r = int(255 * ratio)
        g = 0
        b = int(255 * (1 - ratio))
        return f'#{r:02x}{g:02x}{b:02x}'
  
        
    def initialiser_affichage(self):
        
        # Altitudes
        A = [noeud.z*1000 for noeud in self.controleur.noeuds]
        for c in self.controleur.canalisations:
            for t in c.troncons:
                A.append(t.coo[2]*1000)
        A_min = min(A); A_max = max(A)
        self.info_A = [A, A_min, A_max]
        for noeud in self.controleur.noeuds:
            noeud.couleur_A = self.couleur_echelle(noeud.z*1000, A_min, A_max)
        for c in self.controleur.canalisations:
            for t in c.troncons:
                t.couleur_A = self.couleur_echelle(t.coo[2]*1000, A_min, A_max)
        
        # Potentiels    
        H = [noeud.potentiel for noeud in self.controleur.noeuds]
        for c in self.controleur.canalisations:
            for t in c.troncons:
                H.append(t.potentiel)
        H_min = min(H); H_max = max(H)
        self.info_H = [H, H_min, H_max]
        for noeud in self.controleur.noeuds:
            noeud.couleur_H = self.couleur_echelle(noeud.potentiel, H_min, H_max)
        for c in self.controleur.canalisations:
            for t in c.troncons:
                t.couleur_H = self.couleur_echelle(t.potentiel, H_min, H_max)
        
        # Pressions et Débits
        P = []; D = []
        for c in self.controleur.canalisations:
            for t in c.troncons:
                P.append(t.pression)
                D.append(abs(t.c.debit))
        P_min = min(P); P_max = max(P)
        D_min = min(D); D_max = max(D)
        self.info_P = [P, P_min, P_max]
        self.info_D = [D, D_min, D_max]
        for c in self.controleur.canalisations:
            for t in c.troncons:
                t.couleur_P = self.couleur_echelle(t.pression, P_min, P_max)
                t.couleur_D = self.couleur_echelle(abs(t.c.debit), D_min, D_max)
        for n in self.controleur.noeuds:
            if self.P_min < n.P and n.P < self.P_max:
                n.couleur_P = f'#{0:02x}{255:02x}{0:02x}'
            else:
                n.couleur_P = f'#{255:02x}{0:02x}{0:02x}'
        

    def actualiser_affichage(self):
        mode = self.choix.get() # 'Aucun', 'Potentiels', 'Pressions' ou 'Débits'       
        
        if mode == 'Aucun':
            self.carte.delete("legende")
            for noeud in self.controleur.noeuds:
                self.carte.itemconfig(noeud.id, fill='lightgrey')
            for c in self.controleur.canalisations:
                for t in c.troncons:
                    self.carte.itemconfig(t.id, fill='lavender')
            self.carte.itemconfig("Fleche", state='hidden')
        
        elif mode == 'Altitudes':
            self.carte.delete("legende")
            for noeud in self.controleur.noeuds:
                self.carte.itemconfig(noeud.id, fill=noeud.couleur_A)
            for c in self.controleur.canalisations:
                for t in c.troncons:
                    self.carte.itemconfig(t.id, fill=t.couleur_A)
            self.carte.itemconfig("Fleche", state='hidden')
            self.dessiner_legende(self.info_A[1], self.info_A[2])
        
        elif mode == 'Potentiels':
            self.carte.delete("legende")
            for noeud in self.controleur.noeuds:
                self.carte.itemconfig(noeud.id, fill=noeud.couleur_H)
            for c in self.controleur.canalisations:
                for t in c.troncons:
                    self.carte.itemconfig(t.id, fill=t.couleur_H)
            self.carte.itemconfig("Fleche", state='hidden')
            self.dessiner_legende(self.info_H[1], self.info_H[2])

        elif mode == 'Pressions':
            self.carte.delete("legende")
            for noeud in self.controleur.noeuds:
                self.carte.itemconfig(noeud.id, fill=noeud.couleur_P)
            for c in self.controleur.canalisations:
                for t in c.troncons:
                    self.carte.itemconfig(t.id, fill=t.couleur_P)
            self.carte.itemconfig("Fleche", state='hidden')
            self.dessiner_legende(self.info_P[1], self.info_P[2])
        
        elif mode == 'Débits':
            self.carte.delete("legende")
            for noeud in self.controleur.noeuds:
                self.carte.itemconfig(noeud.id, fill='lightgrey')
            for c in self.controleur.canalisations:
                for t in c.troncons:
                    self.carte.itemconfig(t.id, fill=t.couleur_D)
            self.carte.itemconfig("Fleche", state='disabled')
            self.dessiner_legende(self.info_D[1], self.info_D[2])

            
    def dessiner_legende(self, v_min, v_max):
        x0, y0 = 20, 20
        
        for i in range(self.hauteur-2*x0):
            ratio = i / self.hauteur
            couleur = self.couleur_echelle(v_max - (v_max-v_min)*ratio, v_min, v_max)
            self.carte.create_line(x0, y0+i, x0+self.l_legende, y0+i, fill=couleur, tags="legende")
        
        # Ajouter les textes
        self.carte.create_text(x0+self.l_legende/2, y0-10, text=f"{v_max:.2f}", tags="legende", fill="black")
        self.carte.create_text(x0+self.l_legende/2, y0 + self.hauteur - 2*x0 +10, text=f"{v_min:.2f}", tags="legende", fill="black")
                
    
    def maj_affichage_num(self):
        self.texte_visible = not self.texte_visible
        etat = 'disabled' if self.texte_visible else 'hidden'
        self.carte.itemconfig("Texte", state=etat)
    
    
    def dessiner_fleche(self, x1, y1, x2, y2, debit, couleur):
        if debit < 0:
            x1, y1, x2, y2 = x2, y2, x1, y1            
        
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2        
        angle = np.arctan2(y2 - y1, x2 - x1)
        taille = 16 # Taille de la flèche
        
        p1 = (xm + taille * np.cos(angle), ym + taille * np.sin(angle))
        p2 = (xm - taille * np.cos(angle - 0.5), ym - taille * np.sin(angle - 0.5))
        p3 = (xm - taille * np.cos(angle + 0.5), ym - taille * np.sin(angle + 0.5))
        
        self.carte.create_polygon(p1, p2, p3, fill=couleur, outline='black', tags="Fleche", state='hidden')
   
    
    def maj_affichage(self, calcul=True):
       self.controleur.resolution() if calcul else None
       self.initialiser_affichage()
       self.afficher_reseau()
       self.actualiser_affichage()
      
    
    def survol_noeud(self, event):
        ident = self.carte.find_withtag("current")[0]
        noeud = self.id_noeuds[ident]
        texte = f"Noeud n°{noeud.num}\nH : {noeud.potentiel:.2f} n\nP : {round(noeud.P, 3)} atm \nQ : {noeud.debit} L/s"
        self.tooltip.config(text=texte)
        x = event.x - 100 if event.x > self.l_canva - 120 else event.x + 10
        y = event.y - 60 if event.y > self.hauteur - 80 else event.y + 10
        self.tooltip.place(x=x, y=y)
    
    
    def survol_canalisation(self, event):
        ident = self.carte.find_withtag("current")[0]
        troncon = self.id_troncons[ident]
        c = troncon.c
        texte = f"Canalisation n°{c.num} \nQ : {abs(c.debit)*1000:.2f} L/s \nD : {c.D:.2f} m \nL : {c.L/1000:.2f} m \n\nTronçon n°{troncon.num}/{troncon.n} \nH : {troncon.potentiel:.2f} m \nP : {troncon.pression:.3f} atm"
        self.tooltip.config(text=texte)
        x = event.x - 100 if event.x > self.l_canva - 120 else event.x + 10
        y = event.y - 120 if event.y > self.hauteur - 150 else event.y + 10
        self.tooltip.place(x=x, y=y)
    
    
    def cacher_tooltip(self, event):
        self.tooltip.place_forget()
    
    
    def modifier_consignes(self):
        self.P_min = float(self.entry_P_min.get())
        self.P_max = float(self.entry_P_max.get())
        self.scrolledtext.insert(tk.END, f"\nValeurs de P_min et P_max mises à jour : P_min = {self.P_min}, n = {self.P_max}\n", "alerte_verte" )
        self.maj_affichage(calcul=False)
     
