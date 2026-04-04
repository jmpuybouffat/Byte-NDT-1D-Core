import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURATION BILINGUE ---
st.set_page_config(page_title="Byte NDT Expert", layout="wide")
lang = st.radio("Langue / Language", ["FR", "EN"], horizontal=True)

# Lexique technique
texts = {
    "title": "🛡️ Byte NDT : Système Expert Ultrasonore (GTD & Schmeer)" if lang == "FR" else "🛡️ Byte NDT: Ultrasonic Expert System (GTD & Schmeer)",
    "view_mode": "Visualisation : Profondeur (Z) ou Parcours (Sound Path S) ?" if lang == "FR" else "View Mode: Depth (Z) or Sound Path (S)?",
    "calc_btn": "🚀 Calculer l'Interaction Physique" if lang == "FR" else "🚀 Calculate Physical Interaction",
    "report": "📊 Rapport de Diagnostic / Inspection Report" if lang == "FR" else "📊 Inspection Report"
}

st.title(texts["title"])

# --- PARAMÈTRES OPÉRATEUR ---
st.sidebar.header("Setup" if lang == "EN" else "Configuration")
angle_deg = st.sidebar.slider("Angle (°)", 0, 75, 45)
angle_rad = np.radians(angle_deg)

st.sidebar.markdown("---")
st.sidebar.header("Indication")
def_type = st.sidebar.selectbox("Type", ["Aucun", "Inclusion (Born)", "Entaille (EDM / Kirchhoff + GTD)"])

# Paramètres EDM réels (Z étendu à 200mm)
def_z = st.sidebar.slider("Profondeur Z / Depth Z (mm)", 0, 200, 100)
if "EDM" in def_type:
    def_h = st.sidebar.slider("Hauteur Entaille / Notch Height (mm)", 0.5, 10.0, 3.0)
else:
    def_h = 2.0

view_mode = st.radio(texts["view_mode"], ["Z (Profondeur/Depth)", "S (Parcours/Sound Path)"], horizontal=True)

# --- MOTEUR PHYSIQUE ---
if st.button(texts["calc_btn"]):
    # Grille 200mm
    x = np.linspace(-50, 50, 200)
    z = np.linspace(0, 200, 400)
    X, Z = np.meshgrid(x, z)
    
    # Faisceau
    beam = np.exp(-((X - Z*np.tan(angle_rad))**2) / (12**2)) * np.exp(-Z/150)
    signal = beam.copy()
    
    if def_type != "Aucun":
        # 1. Kirchhoff (Réflexion face)
        mask_face = (np.abs(X - def_z*np.tan(angle_rad)) < 2) & (np.abs(Z - def_z) < def_h/2)
        signal[mask_face] *= 4.0
        
        # 2. GTD (Échos de bords / Edge Waves)
        if "EDM" in def_type:
            top_z, bot_z = def_z - def_h/2, def_z + def_h/2
            edge_top = (np.abs(X - top_z*np.tan(angle_rad)) < 3) & (np.abs(Z - top_z) < 2)
            edge_bot = (np.abs(X - bot_z*np.tan(angle_rad)) < 3) & (np.abs(Z - bot_z) < 2)
            signal[edge_top] += 3.0
            signal[edge_bot] += 3.0

    # Conversion dB
    amp_db = 20 * np.log10(signal / (np.max(signal) + 1e-12))

    # --- AFFICHAGE ---
    fig, ax = plt.subplots(figsize=(10, 8))
    
    if "S (" in view_mode:
        y_axis = Z / np.cos(angle_rad)
        ylabel = "Parcours Ultrasonore / Sound Path S (mm)"
    else:
        y_axis = Z
        ylabel = "Profondeur / Depth Z (mm)"

    im = ax.imshow(amp_db, extent=[-50, 50, np.max(y_axis), 0], cmap='magma', vmin=-20, vmax=0, aspect='auto')
    
    # Isocontours normatifs
    contours = ax.contour(amp_db, levels=[-12, -6], extent=[-50, 50, np.max(y_axis), 0], colors=['white', 'yellow'])
    ax.clabel(contours, inline=True, fontsize=10, fmt='%1.0f dB')
    
    plt.colorbar(im, label="Amplitude (dB)")
    ax.set_ylabel(ylabel)
    ax.set_xlabel("X (mm)")
    st.pyplot(fig)

    # --- RAPPORT ---
    st.markdown(f"### {texts['report']}")
    c1, c2, c3 = st.columns(3)
    s_path = def_z / np.cos(angle_rad)
    c1.metric("Depth Z", f"{def_z} mm")
    c2.metric("Sound Path S", f"{s_path:.1f} mm")
    c3.metric("Estimated Size (-6dB)", f"{def_h} mm")
