# Configuration de la sonde 1D pour Byte NDT
SONDE_CONFIG = {
    "nb_elements": 32,      # M
    "largeur_elem": 0.5,    # d (mm)
    "gap": 0.1,             # g (mm)
    "frequence_mhz": 5.0,   # f
    "vitesse_acier": 5900,  # c (m/s) pour ondes L
}

def get_pitch():
    return SONDE_CONFIG["largeur_elem"] + SONDE_CONFIG["gap"]

def get_aperture():
    s = get_pitch()
    return (SONDE_CONFIG["nb_elements"] - 1) * s + SONDE_CONFIG["largeur_elem"]