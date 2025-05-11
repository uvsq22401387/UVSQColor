import tkinter as tk
import numpy as np
from tkinter import filedialog, Menu
from PIL import Image, ImageTk
from scipy.signal import convolve2d


fenetre_principale = None
canvas = None
image_selectionnee = None 
image_matrice = None 
image_matrice_apercu = None
image_affichee = None 
dialogue_effet = None
formats = "*.png;*.jpg;*.jpeg;*.bmp;*.gif"
historique = []
historique_annulation =[]
img2_pixels = []

def ouvrir():
    global image_selectionnee
    global image_matrice

    fichier = filedialog.askopenfilename(filetypes=[("Images", formats)])
    if not fichier:
        return
    image_selectionnee = Image.open(fichier).convert("RGB")
    largeur, hauteur = image_selectionnee.size
    image_matrice = [[image_selectionnee.getpixel((x, y)) for x in range(largeur)]for y in range(hauteur)]
    refresh()
    activer_boutons()

def activer_boutons():
    sous_menu_filtres.entryconfig("Filtre vert", state="normal")
    sous_menu_filtres.entryconfig("Niveaux de gris", state="normal")
    sous_menu_filtres.entryconfig("Détection de bords", state="normal")
    sous_menu_ajustements.entryconfig("Luminosité", state="normal")
    sous_menu_ajustements.entryconfig("Contraste", state="normal")
    sous_menu_flou.entryconfig("Flou gaussien", state="normal")
    menu_fichier.entryconfig("Enregistrer", state="normal")
    menu_effets.entryconfig("Fusionner", state="normal")

def refresh():
    global image_affichee

    hauteur = len(image_matrice)
    largeur = len(image_matrice[0])
    image = Image.new("RGB", (largeur, hauteur))
    for y in range(hauteur):
            for x in range(largeur):
                pixel = image_matrice[y][x]
                image.putpixel((x, y), pixel)

    image_affichee = ImageTk.PhotoImage(image)
    canvas.config(width=largeur, height=hauteur)
    canvas.create_image(0, 0, anchor=tk.NW, image=image_affichee)

def sauvegarder_etat():
    global historique
    global historique_annulation
    copie = [row[:] for row in image_matrice]
    historique.append(copie)
    historique_annulation.clear

def undo():
    global historique
    global historique_annulation
    global image_matrice
    if historique:
        historique_annulation.append([row[:] for row in image_matrice])
        image_matrice = historique.pop()
        refresh()

def redo():
    global historique
    global image_matrice
    global historique_annulation
    if historique_annulation:
        sauvegarder_etat()
        image_matrice = historique_annulation.pop()
        refresh()

def fenetre_effet(fenetre=""):
    global dialogue_effet
    global image_matrice_apercu

    image_matrice_apercu = [ligne[:] for ligne in image_matrice]

    dialogue_effet = tk.Toplevel(fenetre_principale)
    frame_slider = tk.Frame(dialogue_effet)
    frame_slider.pack(pady=10)
    frame_boutons = tk.Frame(dialogue_effet)
    frame_boutons.pack(side=tk.BOTTOM, pady=10)
    dialogue_effet.grab_set()

    if fenetre==0:     
        dialogue_effet.title("Luminosité")
        slider = tk.Scale(frame_slider, from_=0.1, to=3.0, orient=tk.HORIZONTAL, resolution=0.1, digits=2)
        slider.set(1.0)
        slider.pack(pady=20)
        tk.Button(frame_boutons, text="Aperçu", command=lambda: apercu(slider.get(),None, 0)).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_boutons, text="Appliquer", command=lambda: correction_gamma(slider.get())).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_boutons, text="Annuler", command=dialogue_effet.destroy).pack(side=tk.LEFT, padx=10)

    elif fenetre==1:
        dialogue_effet.title("Flou Gaussien")
        slider = tk.Scale(frame_slider, from_=1, to=10, orient=tk.HORIZONTAL, resolution=1, digits=0, label="Intensité du flou Gaussien")
        slider.set(1)
        slider.pack(pady=20)
        tk.Button(frame_boutons, text="Aperçu", command=lambda: apercu(slider.get(),None, 1)).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_boutons, text="Appliquer", command=lambda: appliquer_flou_gaussien(slider.get())).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_boutons, text="Annuler", command=dialogue_effet.destroy).pack(side=tk.LEFT, padx=10)

    elif fenetre == 2:
        dialogue_effet.title("Contraste")

        slider_contraste = tk.Scale(frame_slider, from_=0.1, to=5.0, resolution=0.1, orient=tk.HORIZONTAL, label="Contraste")
        slider_contraste.set(1.0)
        slider_contraste.pack(pady=20)

        slider_pente = tk.Scale(frame_slider, from_=1, to=20, resolution=1, orient=tk.HORIZONTAL, label="Pente")
        slider_pente.set(10)
        slider_pente.pack(pady=20)

        tk.Button(frame_boutons, text="Aperçu", command=lambda: apercu(slider_contraste.get(),slider_pente.get(), 2)).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_boutons, text="Appliquer", command=lambda: sigmoide(slider_contraste.get(), slider_pente.get())).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_boutons, text="Annuler", command=dialogue_effet.destroy).pack(side=tk.LEFT, padx=10)

def filtre_couleur(filtre=""):
    global image_matrice
    sauvegarder_etat()

    if filtre == "vert":
        for i in range(len(image_matrice)):
            for j in range(len(image_matrice[0])):
                r, g, b = image_matrice[i][j]
                image_matrice[i][j] = (0, g, 0)

    elif filtre == "gris":
        for y in range(len(image_matrice)):
            for x in range(len(image_matrice[0])):
                r, g, b = image_matrice[y][x]
                gris = int(0.299 * r + 0.587 * g + 0.114 * b)
                image_matrice[y][x] = (gris, gris, gris)
    refresh()

def correction_gamma(valeur):
    global image_matrice
    sauvegarder_etat()
    gamma = float(valeur)
    max_value = 255.0
    for y in range(len(image_matrice)):
        for x in range(len(image_matrice[0])):
            r, g, b = image_matrice[y][x]
            image_matrice[y][x] = (
                int(max_value * (r / max_value) ** gamma),
                int(max_value * (g / max_value) ** gamma),
                int(max_value * (b / max_value) ** gamma)
            )
    refresh()
    dialogue_effet.destroy()

    
def appliquer_flou_gaussien(intensite):
    global image_matrice
    sauvegarder_etat()

    kernel = np.array([
        [1, 2, 1],
        [2, 4, 2],
        [1, 2, 1]
    ], dtype=np.float32)
    kernel /= kernel.sum()

    image_np = np.array(image_matrice, dtype=np.uint8)
    flou_image = image_np.copy()

    for i in range(int(intensite)):
        for j in range(3):
            flou_image[:, :, j] = convolve2d(flou_image[:, :, j], kernel, mode='same', boundary='symm')

    image_matrice = [[tuple(pixel) for pixel in row] for row in flou_image]

    refresh()
    dialogue_effet.destroy()


def sigmoide(c, k):
    global image_matrice

    sauvegarder_etat()
    image_matrice = [[(
        int(1/(1+np.exp(-k*c*(r/255.0-0.5)))*255),
        int(1/(1+np.exp(-k*c*(g/255.0-0.5)))*255),
        int(1/(1+np.exp(-k*c*(b/255.0-0.5)))*255)
    ) for (r, g, b) in row] for row in image_matrice]

    refresh() 
    dialogue_effet.destroy()

def apercu(param1, param2, filtre):
    sauvegarder_etat()
    if filtre==0:
        correction_gamma(param1)
    elif filtre==1:
        appliquer_flou_gaussien(param1)
    elif filtre==2:
        sigmoide(param1, param2)
    refresh()
    fenetre_principale.after(1000, undo)
    fenetre_principale.after(1100, lambda: historique_annulation.pop() if historique_annulation else None)
    fenetre_principale.after(1500, lambda:fenetre_effet(filtre))

def fusionner():
    global image_matrice, img2_pixels
    sauvegarder_etat()
    chemin = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    if not chemin:
        return

    image2 = Image.open(chemin).convert("RGB")
    largeur1, hauteur1 = len(image_matrice[0]), len(image_matrice)
    largeur2, hauteur2 = image2.size

    if (largeur1, hauteur1) != (largeur2, hauteur2):
        image2 = image2.resize((largeur1, hauteur1))

    img2_pixels = [[image2.getpixel((x, y)) for x in range(largeur1)] for y in range(hauteur1)]

    for y in range(hauteur1):
        for x in range(largeur1):
            r1, g1, b1 = image_matrice[y][x]
            r2, g2, b2 = img2_pixels[y][x]
            image_matrice[y][x] = (
                (r1 + r2) // 2,
                (g1 + g2) // 2,
                (b1 + b2) // 2
            )
    refresh()


def filtre_detection_bords():
    global image_matrice
    sauvegarder_etat()

    image_numpy  = np.array(image_matrice, dtype=np.uint8)
    image_niveaux_gris  = np.dot(image_numpy [..., :3], [0.299, 0.587, 0.114])  
    sobel_x = np.array([[1, 0, -1],
                        [2, 0, -2],
                        [1, 0, -1]])
    sobel_y = np.array([[1, 2, 1],
                        [0, 0, 0],
                        [-1, -2, -1]])

    filtre_vertical = convolve2d(image_niveaux_gris , sobel_x, mode='same', boundary='symm')
    filtre_horizontal = convolve2d(image_niveaux_gris , sobel_y, mode='same', boundary='symm')
    intesite = np.sqrt(filtre_vertical**2 + filtre_horizontal**2)
    intesite = np.clip(intesite, 0, 255).astype(np.uint8)

    image_matrice = [[(val, val, val) for val in ligne] for ligne in intesite]
    refresh()

def enregistrer():
    if not image_matrice or not image_selectionnee:
        return

    hauteur = len(image_matrice)
    largeur = len(image_matrice[0])
    image_finale = Image.new("RGB", (largeur, hauteur))
    for i in range(hauteur):
        for j in range(largeur):
            image_finale.putpixel((j, i), image_matrice[i][j])

    fichier = filedialog.asksaveasfilename(defaultextension=".png",
                                        filetypes=[("Images", formats)],
                                        title="Enregistrer l'image")
    if fichier:
        image_finale.save(fichier)


fenetre_principale = tk.Tk()
fenetre_principale.title("UVSQolor")
fenetre_principale.bind('<Control-z>', lambda event: undo())
fenetre_principale.bind('<Control-s>', lambda event:enregistrer())
fenetre_principale.bind('<Control-n>', lambda event: ouvrir())
fenetre_principale.bind('<Control-y>', lambda event: redo())

canvas = tk.Canvas(fenetre_principale)
canvas.pack()

barre_menu = Menu(fenetre_principale)
fenetre_principale.config(menu=barre_menu)
menu_fichier = Menu(barre_menu, tearoff=0)
menu_fichier.add_command(label="Ouvrir", command=ouvrir)
menu_fichier.add_command(label="Enregistrer", command=enregistrer, state="disabled")
barre_menu.add_cascade(label="Fichier", menu=menu_fichier)

menu_effets = Menu(barre_menu, tearoff=0)
menu_effets.add_command(label="Fusionner", command=fusionner, state="disabled")



sous_menu_filtres = Menu(menu_effets, tearoff=0)
sous_menu_filtres.add_command(label="Filtre vert", command=lambda: filtre_couleur("vert"), state="disabled")
sous_menu_filtres.add_command(label="Niveaux de gris", command=lambda: filtre_couleur("gris"), state="disabled")
sous_menu_filtres.add_command(label="Détection de bords", command=filtre_detection_bords, state="disabled")
menu_effets.add_cascade(label="Filtres", menu=sous_menu_filtres)

sous_menu_ajustements = Menu(menu_effets, tearoff=0)
sous_menu_ajustements.add_command(label="Luminosité", command=lambda: fenetre_effet(0), state="disabled")
sous_menu_ajustements.add_command(label="Contraste", command=lambda: fenetre_effet(2), state="disabled")
menu_effets.add_cascade(label="Ajustements", menu=sous_menu_ajustements)

sous_menu_flou = Menu(menu_effets, tearoff=0)
sous_menu_flou.add_command(label="Flou gaussien", command=lambda: fenetre_effet(1), state="disabled")
menu_effets.add_cascade(label="Flou", menu=sous_menu_flou)
barre_menu.add_cascade(label="Effets", menu=menu_effets)

barre_menu.add_command(label="↶", command=undo)
barre_menu.add_command(label="↷", command=redo)


fenetre_principale.mainloop()
