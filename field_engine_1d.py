import numpy as np

def get_pa_delays_interface(M, s, ang_wedge, ang_steel, DT0, DF, c_wedge, c_steel):
    """
    Calcule les lois de retards (Delay Laws) à travers l'interface Sabot/Acier.
    C'est la base du pilotage électronique du faisceau.
    """
    Mb = (M - 1) / 2
    m = np.arange(1, M + 1)
    e = (m - 1 - Mb) * s  # Position des éléments
    
    # Calcul des angles d'incidence et réfraction (Snell-Descartes)
    # Note: ang_steel est l'angle voulu dans la pièce
    ang_inc = np.arcsin((c_wedge / c_steel) * np.sin(np.radians(ang_steel)))
    
    # Calcul simplifié du trajet pour le steering
    # Pour la focalisation (DF), on utilise la différence de marche temporelle
    dt_elements = DT0 + e * np.sin(np.radians(ang_wedge))
    
    # Temps de parcours (microsecondes)
    t = (1000 * dt_elements / (c_wedge * np.cos(ang_inc)))
    td = np.max(t) - t # Transformation en retards positifs
    return td

def compute_pressure_tensor(grid_y, grid_z, elements_y, z_interface, delays, freq, c_steel):
    """
    Génère le TENSEUR de pression acoustique.
    Sortie : Matrice complexe (Amplitude + Phase) pour le Machine Learning.
    """
    k = 2 * np.pi * freq / (c_steel / 1000) # Nombre d'onde
    omega = 2 * np.pi * freq
    
    # Initialisation du tenseur (Grille Y x Grille Z)
    pressure_tensor = np.zeros_like(grid_y, dtype=complex)
    
    for i, ey in enumerate(elements_y):
        # Calcul de la distance élément -> point de grille (R)
        r = np.sqrt((grid_y - ey)**2 + (grid_z - z_interface)**2)
        
        # Phase incluant le retard PAUT (delay)
        # P = (1/sqrt(r)) * exp(j * (k*r - omega*tau))
        phase = 1j * (k * r - (omega * delays[i]))
        pressure_tensor += (1 / np.sqrt(r + 0.1)) * np.exp(phase)
        
    return pressure_tensor

# --- EXEMPLE D'UTILISATION POUR GÉNÉRER UN TENSEUR ---
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # 1. PARAMÈTRES DE LA SIMULATION
    M, pitch, f_mhz = 32, 0.6, 5.0
    c_steel = 3240  # Vitesse ondes de cisaillement (m/s)
    
    # 2. GÉNÉRATION DE LA GRILLE (Le "TPU")
    y = np.linspace(0, 60, 200) # 60 mm de large
    z = np.linspace(0, 40, 150) # 40 mm de profondeur
    yy, zz = np.meshgrid(y, z)
    
    # 3. CALCUL DES LOIS DE RETARDS (Angle 45°)
    delays = np.linspace(0, 2, M) # Simulation simple de retard pour test
    elements_y = np.linspace(20, 40, M)
    
    # 4. GÉNÉRATION DU TENSEUR
    tensor = compute_pressure_tensor(yy, zz, elements_y, 0, delays, f_mhz, c_steel)
    
    print("✅ Tenseur calculé avec succès.")

    # 5. EXPORTATION POUR FPGA (Format binaire)
    # On enregistre l'amplitude pour le traitement Verilog
    np.abs(tensor).astype(np.float32).tofile("pressure_tensor.bin")
    print("💾 Fichier 'pressure_tensor.bin' généré pour simulation FPGA.")

    # 6. VISUALISATION
    plt.figure(figsize=(10, 6))
    plt.imshow(np.abs(tensor), extent=[0, 60, 40, 0], cmap='magma')
    plt.colorbar(label='Amplitude (Relative)')
    plt.title('Byte NDT - Visualisation du Champ de Pression (TPU Core)')
    plt.xlabel('Largeur Y (mm)')
    plt.ylabel('Profondeur Z (mm)')
    plt.show()
    
    print("Moteur de Tenseurs initialisé. Prêt pour l'exportation FPGA.")