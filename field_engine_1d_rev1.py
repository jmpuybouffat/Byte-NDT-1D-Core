import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURATION CONSTRUCTEUR ---
M = 32              # Nombre d'éléments
d = 0.5             # Largeur élément (mm)
g = 0.1             # Gap (mm)
s = d + g           # Pitch (mm)
freq = 5.0          # Fréquence (MHz)
c_vitesse = 5900    # Vitesse (m/s) - ex: Acier Longitudinal

# --- CALCUL DES COORDONNÉES ---
Mb = (M - 1) / 2
m = np.arange(1, M + 1)
elements_y = (m - 1 - Mb) * s  # Position exacte des centres
aperture = M * d + (M - 1) * g

# --- GRILLE DE VISUALISATION (L'ÉCHELLE) ---
y_max, z_max = 60, 40 # Dimensions de la fenêtre (mm)
res_y, res_z = 300, 200 # Résolution du Tenseur
yy, zz = np.meshgrid(np.linspace(-y_max/2, y_max/2, res_y), 
                     np.linspace(0, z_max, res_z))

# --- CALCUL DES RETARDS (STEERING) ---
angle_deg = 20 # Angle de tir souhaité
delays = (elements_y * np.sin(np.radians(angle_deg))) / (c_vitesse / 1000)
delays -= np.min(delays)

# --- GÉNÉRATION DU TENSEUR ---
def compute_full_field(yy, zz, ey, delays, f, c):
    k = 2 * np.pi * f / (c / 1000)
    omega = 2 * np.pi * f
    field = np.zeros_like(yy, dtype=complex)
    for i, pos_y in enumerate(ey):
        r = np.sqrt((yy - pos_y)**2 + zz**2)
        # Ajout du terme de directivité de l'élément individuel (diffraction de fente)
        # sinc(k * d/2 * sin(theta))
        theta = np.arctan2((yy - pos_y), zz)
        directivity = np.sinc((k * d / 2 * np.sin(theta)) / np.pi)
        
        phase = 1j * (k * r - (omega * delays[i]))
        field += directivity * (1 / np.sqrt(r + 0.1)) * np.exp(phase)
    return field

tensor = compute_full_field(yy, zz, elements_y, delays, freq, c_vitesse)

# --- AFFICHAGE ---
plt.figure(figsize=(12, 7))
plt.imshow(np.abs(tensor), extent=[-y_max/2, y_max/2, z_max, 0], cmap='hot')
plt.title(f'Byte NDT - Caractérisation PAUT {M} élém. (Angle: {angle_deg}°)')
plt.xlabel('Distance Latérale (mm)')
plt.ylabel('Profondeur (mm)')
plt.colorbar(label='Pression relative')
plt.show()