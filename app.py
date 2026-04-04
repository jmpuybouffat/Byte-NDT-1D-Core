import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURATION & LANGUE ---
st.set_page_config(page_title="Byte NDT Expert System", layout="wide")
lang = st.radio("Langue / Language", ["FR", "EN"], horizontal=True)

# Dictionnaire de traduction
texts = {
    "title": "🛡️ Byte NDT : Système Expert (Schmeer & GTD) - LSB 941" if lang == "FR" else "🛡️ Byte NDT: Expert System (Schmeer & GTD) - LSB 941",
    "sidebar_beam": "Configuration Faisceau" if lang == "FR" else "Beam Setup",
    "sidebar_defect": "Géométrie de l'Indication" if lang == "FR" else "Indication Geometry",
    "mode_choice": "Visualisation : Profondeur (Z) ou Parcours (S) ?" if lang == "FR" else "View: Depth (Z) or Sound Path (S)?",
    "btn": "🚀 Calculer l'Interaction Physique" if lang == "FR" else "🚀 Calculate Physical Interaction"
}

st.title(texts["title"])

# --- BARRE LATÉRALE ---
st.sidebar.header(texts["sidebar_beam"])
angle_deg = st.sidebar.slider("Angle (°)", 0, 75, 45)
angle_rad = np.radians(angle_deg)

st.sidebar.markdown("---")
st.sidebar.header(texts["sidebar_defect"])
defect_type = st.sidebar.selectbox("Type", ["Aucun", "Inclusion (Born)", "Entaille (EDM / Kirchhoff + GTD)"])

# Paramètres EDM réels (L, l, e)
if "EDM" in defect_type:
    def_z = st.sidebar.slider("Profondeur Z (mm)", 0, 200, 100)
    def_h = st.sidebar.slider("Hauteur Entaille / Height (mm)", 0.5, 5.0, 2.0)
    def_thick = st.sidebar.slider("Épaisseur air / Gap (mm)", 0.1, 0.3, 0.1)
else:
    def_z = st.sidebar.slider("Profondeur Z (mm)", 0, 200, 100)
    def_h = 1.0

view_mode = st.radio(texts["mode_choice"], ["Profondeur / Depth (Z)", "Parcours / Sound Path (S)"], horizontal=True)

# --- MOTEUR PHYSIQUE SIMPLIFIÉ (Somme de tout) ---
if st.button(texts["btn"]):
    # Grille de calcul
    x = np.linspace(-50, 50, 200)
    z = np.linspace(0, 200, 400)
    X, Z = np.meshgrid(x, z)
    
    # Faisceau théorique (Gaussien + Atténuation)
    beam = np.exp(-((X - Z*np.tan(angle_rad))**2) / (10**2)) * np.exp(-Z/100)
    
    # Interaction
    signal = beam.copy()
    if defect_type != "Aucun":
        # Réflexion (Kirchhoff)
        mask_center = (np.abs(X) < 1) & (np.abs(Z - def_z) < def_h/2)
        signal[mask_center] *= 5.0
        
        # Effet de bord (GTD) : Points de diffraction haut et bas
        if "EDM" in defect_type:
            edge_top = (np.abs(X) < 1.5) & (np.abs(Z - (def_z - def_h/2)) < 1)
            edge_bottom = (np.abs(X) < 1.5) & (np.abs(Z - (def_z + def_h/2)) < 1)
            signal[edge_top] += 2.0
            signal[edge_bottom] += 2.0

    # Conversion dB
    amp_db = 20 * np.log10(signal / (np.max(signal) + 1e-12))

    # --- AFFICHAGE ---
    fig, ax = plt.subplots(figsize=(10, 8))
    
    display_z = Z if "Profondeur" in view_mode else Z / np.cos(angle_rad)
    label_y = "Profondeur / Depth Z (mm)" if "Profondeur" in view_mode else "Parcours / Sound Path S (mm)"

    im = ax.imshow(amp_db, extent=[-50, 50, np.max(display_z), 0], cmap='magma', vmin=-20, vmax=0, aspect='auto')
    
    # Isocontours normatifs
    contours = ax.contour(amp_db, levels=[-12, -6], extent=[-50, 50, np.max(display_z), 0], colors=['white', 'yellow'])
    ax.clabel(contours, inline=True, fontsize=10, fmt='%1.0f dB')
    
    plt.colorbar(im, label="Amplitude (dB)")
    ax.set_ylabel(label_y)
    ax.set_xlabel("Position X (mm)")
    
    st.pyplot(fig)

    # RAPPORT DE DIAGNOSTIC
    st.markdown("### 📊 Rapport d'Indication / Inspection Report")
    col1, col2, col3 = st.columns(3)
    sound_path = def_z / np.cos(angle_rad)
    col1.metric("Position Z", f"{def_z} mm")
    col2.metric("Sound Path (S)", f"{sound_path:.1f} mm")
    col3.metric("Dimension (-6dB)", f"{def_h} mm")
