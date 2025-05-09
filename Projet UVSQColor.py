import tkinter as tk
import numpy as np
from tkinter import filedialog, Menu
from PIL import Image, ImageTk


fenetre_principale = None
canvas = None
image_originale = None
image_affichee = None
matrice_pixels = None
matrice_affichage = None
dialogue_effet = None
historique = []

def ouvrir():
    global image_originale, matrice_pixels

    fichier = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    if not fichier:
        return
    image_originale = Image.open(fichier).convert("RGB")
    largeur, hauteur = image_originale.size
    matrice_pixels = [[image_originale.getpixel((x, y)) for x in range(largeur)]for y in range(hauteur)]
    refresh()

    menu_effets.entryconfig("Filtre vert", state="normal")
    menu_effets.entryconfig("Niveaux de gris", state="normal")
    menu_fichier.entryconfig("Enregistrer", state="normal")
    menu_effets.entryconfig("Luminosité", state="normal")
    menu_effets.entryconfig("Flou gaussien", state="normal")
    menu_effets.entryconfig("Annuler", state="normal")

def refresh():
    global image_affichee, matrice_pixels

    hauteur = len(matrice_pixels)
    largeur = len(matrice_pixels[0])
    image_modifiee = Image.new("RGB", (largeur, hauteur))
    for y in range(hauteur):
            for x in range(largeur):
                couleur = matrice_pixels[y][x]
                image_modifiee.putpixel((x, y), couleur)
    image_affichee = ImageTk.PhotoImage(image_modifiee)

    canvas.config(width=largeur, height=hauteur)
    canvas.create_image(0, 0, anchor=tk.NW, image=image_affichee)
    fenetre_principale.pack_propagate(False)

def sauvegarder_etat():
    global historique, matrice_pixels
    copie = [row[:] for row in matrice_pixels]
    historique.append(copie)

def undo():
    global historique, matrice_pixels
    if historique:
        matrice_pixels = historique.pop()
        refresh()

def filtre_couleur(filtre=""):
    global matrice_pixels
    sauvegarder_etat()
    
    if filtre == "vert":
        for i in range(len(matrice_pixels)):
            for j in range(len(matrice_pixels[0])):
                r, g, b = matrice_pixels[i][j]
                matrice_pixels[i][j] = (0, g, 0)

    elif filtre == "gris":
        for y in range(len(matrice_pixels)):
            for x in range(len(matrice_pixels[0])):
                r, g, b = matrice_pixels[y][x]
                gris = int(0.299 * r + 0.587 * g + 0.114 * b)
                matrice_pixels[y][x] = (gris, gris, gris)
    refresh()

def correction_gamma(valeur):
    global matrice_affichage
    gamma = float(valeur)
    max_value = 255.0
    for y in range(len(matrice_affichage)):
        for x in range(len(matrice_affichage[0])):
            r, g, b = matrice_affichage[y][x]
            matrice_affichage[y][x] = (
                int(max_value * (r / max_value) ** gamma),
                int(max_value * (g / max_value) ** gamma),
                int(max_value * (b / max_value) ** gamma)
            )
    refresh()

def applique_effet():
    global matrice_pixels, matrice_affichage
    sauvegarder_etat()
    matrice_pixels = [row[:] for row in matrice_affichage]
    refresh()
    dialogue_effet.destroy()

def annule_effet():
    global matrice_affichage
    matrice_affichage = [row[:] for row in matrice_pixels]
    refresh()
    dialogue_effet.destroy()

def fenetre_effet(fenetre=""):
    global dialogue_effet, matrice_affichage

    matrice_affichage = [row[:] for row in matrice_pixels]

    dialogue_effet = tk.Toplevel(fenetre_principale)
    frame_boutons = tk.Frame(dialogue_effet)
    frame_boutons.pack(side=tk.BOTTOM, pady=10)
    dialogue_effet.geometry("300x150")
    dialogue_effet.grab_set()

    if fenetre=="luminosité":     
        dialogue_effet.title("Luminosité")
        slider = tk.Scale(dialogue_effet, from_=0.1, to=3.0, orient=tk.HORIZONTAL, resolution=0.1, digits=2, command=correction_gamma)
        slider.set(1.0)
        slider.pack(pady=20)
        tk.Button(frame_boutons, text="Appliquer", command=applique_effet).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_boutons, text="Annuler", command=annule_effet).pack(side=tk.LEFT, padx=10)

    elif fenetre=="flou":
        dialogue_effet.title("Flou Gaussien")
        slider = tk.Scale(dialogue_effet, from_=1, to=10, orient=tk.HORIZONTAL, resolution=1, digits=0, label="Intensité du flou Gaussien")
        slider.set(1)
        slider.pack(pady=20)
        tk.Button(frame_boutons, text="Appliquer", command=lambda: appliquer_flou_gaussien(slider.get())).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_boutons, text="Annuler", command=dialogue_effet.destroy).pack(side=tk.LEFT, padx=10)

def appliquer_flou_gaussien(intensite):
    global matrice_pixels
    sauvegarder_etat()
    for _ in range(int(intensite)):
        hauteur = len(matrice_pixels)
        largeur = len(matrice_pixels[0])
        noyau = [
            [1, 2, 1],
            [2, 4, 2],
            [1, 2, 1]
        ]
        facteur = 16
        nouvelle_matrice = [[(0, 0, 0) for _ in range(largeur)] for _ in range(hauteur)]
        for y in range(1, hauteur - 1):
            for x in range(1, largeur - 1):
                r_total = g_total = b_total = 0
                for j in range(-1, 2):
                    for i in range(-1, 2):
                        r, g, b = matrice_pixels[y + j][x + i]
                        poids = noyau[j + 1][i + 1]
                        r_total += r * poids
                        g_total += g * poids
                        b_total += b * poids
                nouvelle_matrice[y][x] = (
                    r_total // facteur,
                    g_total // facteur,
                    b_total // facteur
                )
        matrice_pixels = nouvelle_matrice
    refresh()
    dialogue_effet.destroy()

def enregistrer():
    if not matrice_pixels:
        return

    hauteur = len(matrice_pixels)
    largeur = len(matrice_pixels[0])
    image_finale = Image.new("RGB", (largeur, hauteur))
    for i in range(hauteur):
        for j in range(largeur):
            image_finale.putpixel((j, i), matrice_pixels[i][j])

    fichier = filedialog.asksaveasfilename(defaultextension=".png",
                                        filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg;*.jpeg"), ("BMP", "*.bmp"), ("GIF", "*.gif")],
                                        title="Enregistrer l'image")
    if fichier:
        image_finale.save(fichier)


fenetre_principale = tk.Tk()
fenetre_principale.title("UVSQolor")

canvas = tk.Canvas(fenetre_principale)
canvas.pack()

barre_menu = Menu(fenetre_principale)
fenetre_principale.config(menu=barre_menu)
menu_fichier = Menu(barre_menu, tearoff=0)
menu_fichier.add_command(label="Ouvrir", command=ouvrir)
menu_fichier.add_command(label="Enregistrer", command=enregistrer, state="disabled")
barre_menu.add_cascade(label="Fichier", menu=menu_fichier)

menu_effets = Menu(barre_menu, tearoff=0)
menu_effets.add_command(label="Filtre vert", command=lambda: filtre_couleur("vert"), state="disabled")
menu_effets.add_command(label="Niveaux de gris", command=lambda: filtre_couleur("gris"), state="disabled")
menu_effets.add_command(label="Luminosité", command=lambda: fenetre_effet("luminosité"), state="disabled")
menu_effets.add_command(label="Flou gaussien", command=lambda: fenetre_effet("flou"), state="disabled")
menu_effets.add_command(label="Annuler", command=undo, state="disabled")
barre_menu.add_cascade(label="Effets", menu=menu_effets)

fenetre_principale.mainloop()
