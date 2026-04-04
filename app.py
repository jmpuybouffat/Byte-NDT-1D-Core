import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURATION INTERFACE ---
st.set_page_config(page_title="Byte NDT - Expert System", layout="wide")

# Système de langue
lang = st.radio("Langue / Language", ["FR", "EN"], horizontal=True)

texts = {
    "title": "🛡️ Byte NDT : Système Expert (GTD & Schmeer) - LSB 941",
    "setup": "Configuration de l'Examen",
    "angle": "Angle du faisceau (°)",
    "mode": "Mode de Vue : Profondeur (Z) ou Parcours (S) ?",
    "defect": "Géométrie de l'Indication",
    "type": "Nature du défaut",
    "depth": "Profondeur Z (mm)",
    "height": "Hauteur de l'entaille (mm)",
    "btn": "🚀 Calculer l'Interaction Physique",
    "report": "📊 Rapport de Diagnostic / Inspection Report"
} if lang == "FR" else {
    "title": "🛡️ Byte NDT: Expert System (GTD & Schmeer) - LSB 941",
    "setup": "Examination Setup",
    "angle": "Beam Angle (°)",
    "mode": "View Mode: Depth (Z) or Sound Path (S)?",
    "defect": "Indication Geometry",
    "type": "Defect Nature",
    "depth": "Depth Z (mm)",
    "height": "Notch Height (mm)",
    "btn": "🚀 Calculate Physical Interaction",
    "report": "📊 Inspection Report"
}

st.title(texts["title"])

# --- BARRE LATÉRALE (INPUTS) ---
st.sidebar.header(texts["setup"])
angle_deg = st.sidebar.slider(texts["angle"], 0, 75, 45)
angle_rad = np.radians(angle_deg)

view_mode = st.radio(texts["mode"], ["Z (Profondeur/Depth)", "S (Parcours/Sound Path)"], horizontal=True)

st.sidebar.markdown("---")
st.sidebar.header(texts["defect"])
def_type = st.sidebar.selectbox(texts["type"], ["Aucun", "Inclusion (Born)", "Entaille (EDM / Kirchhoff + GTD)"])
def_z = st.sidebar.slider(texts["depth"], 0, 200, 100) # Échelle 200mm demandée
def_h = st.sidebar.slider(texts["height"], 0.5, 10.0, 3.0) if "EDM" in def_type else 2.0

# --- MOTEUR PHYSIQUE (CONVERGENCE DES HYPOTHÈSES) ---
if st.button(texts["btn"]):
    # Création de la grille de calcul (Position X, Profondeur Z)
    x_grid = np.linspace(-50, 50, 200)
    z_grid = np.linspace(0, 200, 400)
    X, Z = np.meshgrid(x_grid, z_grid)
    
    # 1. Modélisation du faisceau (Gaussien + Atténuation de Sommerfeld)
    beam = np.exp(-((X - Z*np.tan(angle_rad))**2) / (12**2)) * np.exp(-Z/150)
    signal = beam.copy()
    
    if def_type != "Aucun":
        # 2. Hypothèse de Kirchhoff (Réflexion de face sur l'EDM)
        mask_face = (np.abs(X - def_z*np.tan(angle_rad)) < 2) & (np.abs(Z - def_z) < def_h/2)
        signal[mask_face] *= 4.0
        
        # 3. Hypothèse GTD (Échos de bords / Edge Waves)
        # On simule les deux points de diffraction (Haut et Bas de l'entaille)
        if "EDM" in def_type:
            for offset in [-def_h/2, def_h/2]:
                edge_z = def_z + offset
                edge_x = edge_z * np.tan(angle_rad)
                edge_mask = (np.abs(X - edge_x) < 3) & (np.abs(Z - edge_z) < 2)
                signal[edge_mask] += 3.0 # Signature de diffraction

    # 4. Conversion en dB (Langage Opérateur)
    amp_db = 20 * np.log10(signal / (np.max(signal) + 1e-12))

    # --- AFFICHAGE MÉTROLOGIQUE ---
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Choix de l'axe Y : Géométrie (Z) ou Appareil (S)
    y_axis_data = Z if "Z (" in view_mode else Z / np.cos(angle_rad)
    ylabel = "Profondeur Z (mm)" if "Z (" in view_mode else "Sound Path S (mm)"

    im = ax.imshow(amp_db, extent=[-50, 50, np.max(y_axis_data), 0], cmap='magma', vmin=-20, vmax=0, aspect='auto')
    
    # Isocontours à -6dB et -12dB (Aide au Sizing)
    ax.contour(amp_db, levels=[-12, -6], extent=[-50, 50, np.max(y_axis_data), 0], colors=['white', 'yellow'], linewidths=1)
    
    plt.colorbar(im, label="Amplitude (dB)")
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Position X (mm)")
    st.pyplot(fig)

    # --- RAPPORT DE MESURE ---
    st.markdown(f"### {texts['report']}")
    c1, c2, c3 = st.columns(3)
    sound_path = def_z / np.cos(angle_rad)
    c1.metric("Depth Z", f"{def_z} mm")
    c2.metric("Sound Path S", f"{sound_path:.1f} mm")
    c3.metric("Height / Hauteur", f"{def_h} mm")
