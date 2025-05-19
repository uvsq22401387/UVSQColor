import tkinter as tk
from tkinter import Menu
from Assets.fcts4edit import *

def lancer_application():
    global fenetre_principale, menu_fichier, menu_effets, sous_menu_filtres, sous_menu_ajustements, sous_menu_flou
    fenetre_principale =tk.Tk()
    fenetre_principale.title("UVSQolor")
    fenetre_principale.bind('<Control-z>', lambda event: undo())
    fenetre_principale.bind('<Control-y>', lambda event: redo())
    fenetre_principale.bind('<Control-s>', lambda event: enregistrer())
    fenetre_principale.bind('<Control-n>', lambda event: ouvrir())

    barre_menu = Menu(fenetre_principale)
    fenetre_principale.config(menu=barre_menu)

    menu_fichier = Menu(barre_menu, tearoff=0)
    menu_fichier.add_command(label="Ouvrir", command=handle_ouverture_activation)
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
    sous_menu_flou.add_command(label="Flou Classique", command=lambda: callback_fenetre_effet("flou"), state="disabled")
    sous_menu_flou.add_command(label="Flou Gaussien", command=lambda: callback_fenetre_effet("flou gauss"), state="disabled")
    menu_effets.add_cascade(label="Flou", menu=sous_menu_flou)

    barre_menu.add_cascade(label="Effets", menu=menu_effets)
    barre_menu.add_command(label="↶", command=undo)
    barre_menu.add_command(label="↷", command=redo)

    fenetre_principale.mainloop()

def handle_ouverture_activation():
    if ouvrir():
        activer_boutons(fenetre_principale, menu_fichier, menu_effets, sous_menu_filtres, sous_menu_ajustements, sous_menu_flou)

if __name__ == "__main__":
    lancer_application()