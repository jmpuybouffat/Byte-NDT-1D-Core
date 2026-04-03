import numpy as np
from config_sonde import SONDE_CONFIG, get_pitch

def generate_field_tensor(angle_deg, profondeur_max=40, largeur_max=60):
    # Récupération des paramètres
    M = SONDE_CONFIG["nb_elements"]
    s = get_pitch()
    f = SONDE_CONFIG["frequence_mhz"]
    c = SONDE_CONFIG["vitesse_acier"]
    
    # Grille TPU (Tensor Processing Unit)
    y = np.linspace(-largeur_max/2, largeur_max/2, 300)
    z = np.linspace(0, profondeur_max, 200)
    yy, zz = np.meshgrid(y, z)
    
    # Coordonnées des centres des éléments
    Mb = (M - 1) / 2
    elements_y = (np.arange(M) - Mb) * s
    
    # Calcul des lois de retards (Steering)
    delays = (elements_y * np.sin(np.radians(angle_deg))) / (c / 1000)
    delays -= np.min(delays)
    
    # Moteur de sommation cohérente
    k = 2 * np.pi * f / (c / 1000)
    omega = 2 * np.pi * f
    field = np.zeros_like(yy, dtype=complex)
    
    for i, pos_y in enumerate(elements_y):
        r = np.sqrt((yy - pos_y)**2 + zz**2)
        # Ajout de la phase et du retard
        phase = 1j * (k * r - (omega * delays[i]))
        field += (1 / np.sqrt(r + 0.1)) * np.exp(phase)
        
    return field, yy, zz