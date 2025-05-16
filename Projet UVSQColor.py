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
    tk.Button(frame_boutons, text="Appliquer", command=appliquer).pack(side=tk.LEFT, padx=10)
    tk.Button(frame_boutons, text="Annuler", command=discard).pack(side=tk.LEFT, padx=10)
    if filtre=="luminosité":     
        dialogue_effet.title("Luminosité")
        slider = tk.Scale(dialogue_effet, orient=tk.HORIZONTAL, length=200, from_=0.1, to=3.0, resolution=0.1, digits=2, label="Gamma (luminosité)", command=correction_gamma)
        slider.set(1.0)
        slider.pack(pady=20)
    if filtre == "contraste":
        dialogue_effet.title("Contraste")
        slider1 = tk.Scale(dialogue_effet, from_=0.1, to=3.0, orient=tk.HORIZONTAL, length=200, resolution=0.1, label="Contraste", command=lambda x: sigmoide(slider1.get(), slider2.get())) 
        slider1.set(1.0)
        slider1.pack(pady=20)
        slider2 = tk.Scale(dialogue_effet, from_=0.1, to=3.0, orient=tk.HORIZONTAL, length=200, resolution=0.1, label="Pente", command=lambda x: sigmoide(slider1.get(), slider2.get())) 
        slider2.set(1.0)
        slider2.pack(pady=20)
    elif filtre == "flou":
        dialogue_effet.title("Flou Gaussien")
        slider = tk.Scale(dialogue_effet, from_=1, to=10, orient=tk.HORIZONTAL, length=200, resolution=1, command=filtre_Flou)
        slider.set(1)
        slider.pack(pady=20)



#fonctions application
def ouvrir():
    global image_selectionnee
    global matrice_pixels_apercu
    global matrice_pixels

    fichier = filedialog.askopenfilename(filetypes=[("Images", formats)])
    if not fichier:
        return
    image_pil = Image.open(fichier)
    image_pil = image_pil.convert('RGB') 
    matrice_pixels = np.array(image_pil)
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
    image = Image.fromarray(matrice, 'RGB')
    image.thumbnail((300, 300))
    image_affichee = ImageTk.PhotoImage(image)
    if canvas == None: 
        canvas = tk.Canvas(fenetre_principale)
        canvas.config(width=300, height=300)
        canvas.create_image(0, 0, anchor=tk.NW, image=image_affichee)
        canvas.pack()
    else:
        canvas.delete("all")
        canvas.config(width=300, height=300)
        canvas.create_image(0, 0, anchor=tk.NW, image=image_affichee)


#retour en arrière

def sauvegarder_etat():
    global historique
    if matrice_pixels is not None:
        historique.append(np.copy(matrice_pixels))

def undo():
    global historique
    global matrice_pixels
    global matrice_pixels_apercu
    if historique:
        matrice_pixels = historique.pop()
        matrice_pixels_apercu = np.copy(matrice_pixels)
        refresh(matrice_pixels_apercu)


#application filtre

def appliquer():
    global matrice_pixels
    global matrice_pixels_apercu
    sauvegarder_etat()
    if matrice_pixels_apercu is not None:
        matrice_pixels = matrice_pixels_apercu.copy()
        dialogue_effet.destroy()

def discard():
    global matrice_pixels
    global matrice_pixels_apercu
    if matrice_pixels is not None:
        matrice_pixels_apercu = matrice_pixels.copy()
        refresh(matrice_pixels_apercu)
        dialogue_effet.destroy()  

#logique derrière les filtres
        
def filtre_vert():
    global matrice_pixels
    sauvegarder_etat()
    matrice_pixels[:, :, 0] = 0
    matrice_pixels[:, :, 2] = 0 
    refresh(matrice_pixels)

def filtre_gris():
    global matrice_pixels
    sauvegarder_etat()
    luminance = np.dot(matrice_pixels[...,:3], [0.299, 0.587, 0.114]).astype(np.uint8)
    matrice_pixels = np.stack([luminance]*3, axis=-1)
    refresh(matrice_pixels)

def correction_gamma(valeur):
    global matrice_pixels_apercu
    gamma = float(valeur)
    sauvegarder_etat()
    norm = matrice_pixels / 255.0
    matrice_pixels_apercu = np.clip((norm ** gamma) * 255, 0, 255).astype(np.uint8)
    refresh(matrice_pixels_apercu)
    
def filtre_Flou(intensite):
    global matrice_pixels_apercu
    intensite = int(intensite)
    kernel = creer_kernel(intensite)
    flou_image = np.empty_like(matrice_pixels, dtype=np.float32)
    for i in range(3):
        flou_image[:, :, i] = convolve2d(matrice_pixels[:, :, i], kernel, mode='same', boundary='symm')
    matrice_pixels_apercu = np.clip(flou_image, 0, 255).astype(np.uint8)
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
    c = float(c)
    k = float(k)
    norm = matrice_pixels / 255.0
    s = 1 / (1 + np.exp(-k * c * (norm - 0.5)))
    matrice_pixels_apercu = np.clip(s * 255, 0, 255).astype(np.uint8)
    refresh(matrice_pixels_apercu)

def fusionner():
    global matrice_pixels
    sauvegarder_etat()
    chemin = filedialog.askopenfilename(filetypes=[("Images", formats)])
    if not chemin:
        return
    image2 = Image.open(chemin).convert("RGB")
    largeur1, hauteur1 = matrice_pixels.shape[1], matrice_pixels.shape[0]
    image2 = image2.resize((largeur1, hauteur1))
    image2_np = np.array(image2)
    matrice_pixels = ((matrice_pixels.astype(np.uint16) + image2_np.astype(np.uint16)) // 2).astype(np.uint8)
    refresh(matrice_pixels)


def filtre_detection_bords():
    global matrice_pixels
    sauvegarder_etat()

    image_niveaux_gris = np.dot(matrice_pixels[..., :3], [0.299, 0.587, 0.114])
    sobel_x = np.array([[1, 0, -1],
                        [2, 0, -2],
                        [1, 0, -1]])
    sobel_y = np.array([[1, 2, 1],
                        [0, 0, 0],
                        [-1, -2, -1]])
    filtre_vertical = convolve2d(image_niveaux_gris, sobel_x, mode='same', boundary='symm')
    filtre_horizontal = convolve2d(image_niveaux_gris, sobel_y, mode='same', boundary='symm')
    intensite = np.sqrt(filtre_vertical**2 + filtre_horizontal**2)
    intensite = np.clip(intensite, 0, 255).astype(np.uint8)
    matrice_pixels = np.stack([intensite]*3, axis=-1)
    refresh(matrice_pixels)

#fichiers
def enregistrer():
    if matrice_pixels is None:
        return
    image_finale = Image.fromarray(matrice_pixels.astype(np.uint8), 'RGB')
    fichier = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Images", formats)], title="Enregistrer l'image")
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
