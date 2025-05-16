import tkinter as tk
import numpy as np
from tkinter import filedialog, Menu
from PIL import Image, ImageTk
from scipy.signal import convolve2d

#var globales
fenetre_principale = None
canvas = None
image_selectionnee = None
image_affichee = None
matrice_pixels = None 
matrice_pixels_apercu = None
dialogue_effet = None
formats = "*.png;*.jpg;*.jpeg;*.bmp;*.gif"
historique = []
img2_pixels = []


#callbacks
def callback_filtre_couleur(filtre=""):
    sauvegarder_etat()
    if filtre=="vert":
        filtre_vert()
    elif filtre=="gris":
        filtre_gris()
    refresh(matrice_pixels)

def callback_fenetre_effet(filtre=""):
    global dialogue_effet

    dialogue_effet = tk.Toplevel(fenetre_principale)
    frame_boutons = tk.Frame(dialogue_effet)
    frame_boutons.pack(side=tk.BOTTOM, pady=10)

    if filtre=="luminosité":     
        dialogue_effet.title("Luminosité")
        slider = tk.Scale(dialogue_effet, orient=tk.HORIZONTAL, length=200, from_=0.1, to=3.0, resolution=0.05, label="Gamma (luminosité)", command=correction_gamma)
        slider.set(1.0)
        slider.pack(pady=20)
        tk.Button(frame_boutons, text="Appliquer", command=lambda: correction_gamma(slider.get())).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_boutons, text="Annuler", command=dialogue_effet.destroy).pack(side=tk.LEFT, padx=10)

    if filtre == "contratse":
        dialogue_effet.title("Contraste")
        slider1 = tk.Scale(dialogue_effet, from_=0.1, to=3.0, orient=tk.HORIZONTAL, length=200, resolution=0.1, label="Contraste", command=lambda x: sigmoide(slider1.get(), slider2.get())) 
        slider1.set(1.0)
        slider1.pack(pady=20)
        slider2 = tk.Scale(dialogue_effet, from_=0.1, to=3.0, orient=tk.HORIZONTAL, length=200, resolution=0.1, label="Pente", command=lambda x: sigmoide(slider1.get(), slider2.get())) 
        slider2.set(1.0)
        slider2.pack(pady=20)
        tk.Button(frame_boutons, text="Appliquer", command=appliquer).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_boutons, text="Annuler", command=discard).pack(side=tk.LEFT, padx=10)

    elif filtre == "flou":
        dialogue_effet.title("Flou Gaussien")
        slider = tk.Scale(dialogue_effet, from_=1, to=5, orient=tk.HORIZONTAL,
                          length=200, resolution=1,
                          command=filtre_Flou)
        slider.set(1)
        slider.pack(pady=20)
        tk.Button(frame_boutons, text="Appliquer", command=appliquer).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_boutons, text="Annuler", command=discard).pack(side=tk.LEFT, padx=10)


#fonctions application
def ouvrir():
    global image_selectionnee
    global matrice_pixels_apercu
    global matrice_pixels

    fichier = filedialog.askopenfilename(filetypes=[("Images", formats)])
    if not fichier:
        return
    image_selectionnee = Image.open(fichier).convert("RGB")
    largeur, hauteur = image_selectionnee.size
    matrice_pixels = [[image_selectionnee.getpixel((x, y)) for x in range(largeur)]for y in range(hauteur)]
    matrice_pixels_apercu = matrice_pixels.copy()
    refresh(matrice_pixels_apercu)
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

#fonction affichage

def refresh(matrice):
    global canvas
    global image_affichee
    hauteur = len(matrice_pixels_apercu)
    largeur = len(matrice_pixels_apercu[0])
    image = Image.new("RGB", (largeur, hauteur))
    for y in range(hauteur):
        for x in range(largeur):
                pixel = matrice_pixels_apercu[y][x]
                image.putpixel((x, y), pixel)
    image.thumbnail((400, 400))
    image_affichee = ImageTk.PhotoImage(image)
    if canvas == None: 
        canvas = tk.Canvas(fenetre_principale)
        canvas.config(width=400, height=400)
        canvas.create_image(0, 0, anchor=tk.NW, image=image_affichee)
        canvas.pack()
    else:
        canvas.delete("all")
        canvas.config(width=400, height=400)
        canvas.create_image(0, 0, anchor=tk.NW, image=image_affichee)


#retour en arrière

def sauvegarder_etat():
    global historique
    copie = [row[:] for row in matrice_pixels]
    historique.append(copie)

def undo():
    global historique
    global matrice_pixels
    global matrice_pixels_apercu
    if historique:
        matrice_pixels = historique.pop()
        matrice_pixels_apercu = matrice_pixels.copy()
        refresh(matrice_pixels_apercu)

#application filtre

def appliquer():
    global matrice_pixels
    global matrice_pixels_apercu
    sauvegarder_etat()
    if matrice_pixels_apercu != None:
        matrice_pixels = matrice_pixels_apercu.copy()
        dialogue_effet.destroy()

def discard():
    global matrice_pixels
    global matrice_pixels_apercu
    if matrice_pixels != None:
        matrice_pixels_apercu = matrice_pixels.copy()
        refresh(matrice_pixels_apercu)
        dialogue_effet.destroy()  

#logique derrière les filtres
        
def filtre_vert():
    for i in range(len(matrice_pixels)):
        for j in range(len(matrice_pixels[0])):
            r, g, b = matrice_pixels[i][j]
            matrice_pixels[i][j] = (0, g, 0)
    refresh(matrice_pixels)

def filtre_gris():
    for y in range(len(matrice_pixels)):
        for x in range(len(matrice_pixels[0])):
            r, g, b = matrice_pixels[y][x]
            gris = int(0.299 * r + 0.587 * g + 0.114 * b)
            matrice_pixels[y][x] = (gris, gris, gris)
    refresh(matrice_pixels)

def correction_gamma(valeur):
    global matrice_pixels_apercu
    sauvegarder_etat()
    gamma = float(valeur)
    max_value = 255.0
    copie = [row[:] for row in matrice_pixels]
    for y in range(len(copie)):
        for x in range(len(copie[0])):
            r, g, b = copie[y][x]
            copie[y][x] = (
                int(max_value * (r / max_value) ** gamma),
                int(max_value * (g / max_value) ** gamma),
                int(max_value * (b / max_value) ** gamma)
            )
    matrice_pixels_apercu = copie.copy()
    refresh(matrice_pixels_apercu)
    
def filtre_Flou(intensite):
    global matrice_pixels_apercu
    intensite = int(intensite)

    kernel = creer_kernel(intensite)

    image_np = np.array(matrice_pixels, dtype=np.uint8)
    flou_image = image_np.copy()
    for i in range(3):
        flou_image[:, :, i] = convolve2d(flou_image[:, :, i], kernel, mode='same', boundary='symm')
    matrice_pixels_apercu = [[tuple(pixel) for pixel in row] for row in flou_image]
    refresh(matrice_pixels_apercu)

def creer_kernel(intensite=None):
    taille_kernel = 3 + 2*(intensite-1)
    if taille_kernel % 2 == 0:
        taille_kernel += 1
    centre = taille_kernel // 2

    kernel = np.zeros((taille_kernel, taille_kernel), dtype=np.float32)
    for i in range(taille_kernel):
        for j in range(taille_kernel):
            x = i - centre
            y = j - centre
            kernel[i, j] = np.exp(-(x*x + y*y)/(2 * intensite * intensite))

    kernel /= kernel.sum()
    return kernel

def sigmoide(c, k):
    global matrice_pixels_apercu

    sauvegarder_etat()
    matrice_pixels_apercu = [[(
        int(1/(1+np.exp(-k*c*(r/255.0-0.5)))*255),
        int(1/(1+np.exp(-k*c*(g/255.0-0.5)))*255),
        int(1/(1+np.exp(-k*c*(b/255.0-0.5)))*255)
    ) for (r, g, b) in row] for row in matrice_pixels]

    refresh() 

def fusionner():
    global matrice_pixels, img2_pixels
    sauvegarder_etat()
    chemin = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    if not chemin:
        return

    image2 = Image.open(chemin).convert("RGB")
    largeur1, hauteur1 = len(matrice_pixels[0]), len(matrice_pixels)
    largeur2, hauteur2 = image2.size

    if (largeur1, hauteur1) != (largeur2, hauteur2):
        image2 = image2.resize((largeur1, hauteur1))

    img2_pixels = [[image2.getpixel((x, y)) for x in range(largeur1)] for y in range(hauteur1)]

    for y in range(hauteur1):
        for x in range(largeur1):
            r1, g1, b1 = matrice_pixels[y][x]
            r2, g2, b2 = img2_pixels[y][x]
            matrice_pixels[y][x] = (
                (r1 + r2) // 2,
                (g1 + g2) // 2,
                (b1 + b2) // 2
            )
    refresh(matrice_pixels)


def filtre_detection_bords():
    global matrice_pixels
    sauvegarder_etat()

    image_numpy  = np.array(matrice_pixels, dtype=np.uint8)
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

    matrice_pixels = [[(val, val, val) for val in ligne] for ligne in intesite]
    refresh(matrice_pixels)

#fichiers

def enregistrer():
    if not matrice_pixels or not image_selectionnee:
        return

    hauteur = len(matrice_pixels)
    largeur = len(matrice_pixels[0])
    image_finale = Image.new("RGB", (largeur, hauteur))
    for i in range(hauteur):
        for j in range(largeur):
            image_finale.putpixel((j, i), matrice_pixels[i][j])

    fichier = filedialog.asksaveasfilename(defaultextension=".png",
                                        filetypes=[("Images", formats)],
                                        title="Enregistrer l'image")
    if fichier:
        image_finale.save(fichier)

#interface

fenetre_principale = tk.Tk()
fenetre_principale.title("UVSQolor")
fenetre_principale.bind('<Control-z>', lambda event: undo())
fenetre_principale.bind('<Control-s>', lambda event:enregistrer())
fenetre_principale.bind('<Control-n>', lambda event: ouvrir())


barre_menu = Menu(fenetre_principale)
fenetre_principale.config(menu=barre_menu)
menu_fichier = Menu(barre_menu, tearoff=0)
menu_fichier.add_command(label="Ouvrir", command=ouvrir)
menu_fichier.add_command(label="Enregistrer", command=enregistrer, state="disabled")
barre_menu.add_cascade(label="Fichier", menu=menu_fichier)

menu_effets = Menu(barre_menu, tearoff=0)
menu_effets.add_command(label="Fusionner", command=fusionner, state="disabled")

sous_menu_filtres = Menu(menu_effets, tearoff=0)
sous_menu_filtres.add_command(label="Filtre vert", command=lambda: callback_filtre_couleur("vert"), state="disabled")
sous_menu_filtres.add_command(label="Niveaux de gris", command=lambda: callback_filtre_couleur("gris"), state="disabled")
sous_menu_filtres.add_command(label="Détection de bords", command=filtre_detection_bords, state="disabled")
menu_effets.add_cascade(label="Filtres", menu=sous_menu_filtres)

sous_menu_ajustements = Menu(menu_effets, tearoff=0)
sous_menu_ajustements.add_command(label="Luminosité", command=lambda: callback_fenetre_effet("luminosité"), state="disabled")
sous_menu_ajustements.add_command(label="Contraste", command=lambda: callback_fenetre_effet("contraste"), state="disabled")
menu_effets.add_cascade(label="Ajustements", menu=sous_menu_ajustements)

sous_menu_flou = Menu(menu_effets, tearoff=0)
sous_menu_flou.add_command(label="Flou gaussien", command=lambda: callback_fenetre_effet("flou"), state="disabled")
menu_effets.add_cascade(label="Flou", menu=sous_menu_flou)
barre_menu.add_cascade(label="Effets", menu=menu_effets)

barre_menu.add_command(label="↶", command=undo)


fenetre_principale.mainloop()
