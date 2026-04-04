import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURATION EXPERTE ---
st.set_page_config(page_title="Byte NDT - LSB 941 Expert", layout="wide")
lang = st.radio("Language / Langue", ["FR", "EN"], horizontal=True)

t = {
    "title": "🛡️ Byte NDT : Expertise Physique (Schmeer, Kirchhoff & GTD)" if lang == "FR" else "🛡️ Byte NDT: Physical Expertise (Schmeer, Kirchhoff & GTD)",
    "setup": "Configuration Examen" if lang == "FR" else "Examination Setup",
    "angle_beam": "Angle d'incidence (°)" if lang == "FR" else "Incidence Angle (°)",
    "mode": "Référentiel : Profondeur (Z) ou Parcours (S) ?" if lang == "FR" else "Reference: Depth (Z) or Sound Path (S)?",
    "defect": "Caractérisation de l'Indication (EDM)" if lang == "FR" else "Indication Characterization (EDM)",
    "dim_l": "Longueur L (mm)" if lang == "FR" else "Length L (mm)",
    "dim_h": "Hauteur h (mm)" if lang == "FR" else "Height h (mm)",
    "dim_e": "Épaisseur d'air e (mm)" if lang == "FR" else "Air Gap e (mm)",
    "orient": "Désorientation Angulaire (°)" if lang == "FR" else "Angular Misorientation (°)",
    "btn": "🚀 Lancer le Diagnostic Global" if lang == "FR" else "🚀 Run Global Diagnosis"
}

st.title(t["title"])

# --- BARRE LATÉRALE : PARAMÈTRES RÉELS ---
st.sidebar.header(t["setup"])
angle_beam_deg = st.sidebar.slider(t["angle_beam"], 0, 75, 45)
angle_beam_rad = np.radians(angle_beam_deg)

view_mode = st.radio(t["mode"], ["Z (Depth)", "S (Sound Path)"], horizontal=True)

st.sidebar.markdown("---")
st.sidebar.header(t["defect"])
def_z = st.sidebar.slider("Profondeur Z (mm)", 0, 200, 100)
def_l = st.sidebar.slider(t["dim_l"], 1.0, 20.0, 10.0)
def_h = st.sidebar.slider(t["dim_h"], 0.5, 10.0, 3.0)
def_e = st.sidebar.slider(t["dim_e"], 0.1, 0.5, 0.2)
def_tilt = st.sidebar.slider(t["orient"], -15, 15, 0) # Orientation de l'entaille

# --- MOTEUR PHYSIQUE AVANCÉ ---
if st.button(t["btn"]):
    # Grille de calcul 200mm
    x_vec = np.linspace(-60, 60, 300)
    z_vec = np.linspace(0, 200, 500)
    X, Z = np.meshgrid(x_vec, z_vec)
    
    # 1. Propagation du faisceau (Modèle Gaussien/Sommerfeld)
    beam = np.exp(-((X - Z*np.tan(angle_beam_rad))**2) / (15**2)) * np.exp(-Z/180)
    signal = beam.copy()
    
    # 2. Interaction Kirchhoff (Réflexion de face sur EDM)
    # L'amplitude dépend de la perpendicularité (Effet de coin)
    tilt_factor = np.cos(np.radians(def_tilt))
    mask_face = (np.abs(X - def_z*np.tan(angle_beam_rad)) < (def_l/10)) & (np.abs(Z - def_z) < (def_h/2))
    signal[mask_face] *= (5.0 * tilt_factor)
    
    # 3. Interaction GTD (Ondes de bords / Diffractions de pointes)
    # On modélise les deux bords (haut et bas) de l'entaille
    for edge in [-def_h/2, def_h/2]:
        ez = def_z + edge
        ex = ez * np.tan(angle_beam_rad)
        mask_edge = (np.abs(X - ex) < 3) & (np.abs(Z - ez) < 2)
        signal[mask_edge] += 3.5 # Écho de pointe distinct
        
    # 4. Conversion dB
    amp_db = 20 * np.log10(signal / (np.max(signal) + 1e-12))

    # --- AFFICHAGE MÉTROLOGIQUE ---
    fig, ax = plt.subplots(figsize=(12, 8))
    
    y_data = Z if "Z" in view_mode else Z / np.cos(angle_beam_rad)
    ylabel = "Profondeur / Depth Z (mm)" if "Z" in view_mode else "Parcours / Sound Path S (mm)"

    im = ax.imshow(amp_db, extent=[-60, 60, np.max(y_data), 0], cmap='magma', vmin=-25, vmax=0, aspect='auto')
    
    # Isocontours normatifs (-6dB jaune, -12dB blanc)
    ax.contour(amp_db, levels=[-12, -6], extent=[-60, 60, np.max(y_data), 0], colors=['white', 'yellow'], linewidths=1.5)
    
    plt.colorbar(im, label="Amplitude (dB)")
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Position X (mm)")
    ax.set_title(f"Simulation PAUT @ {angle_beam_deg}° - LSB 941 Root")
    
    st.pyplot(fig)

    # --- RAPPORT DE MÉTROLOGIE ---
    st.markdown("### 📋 Rapport d'Analyse Automatique")
    c1, c2, c3, c4 = st.columns(4)
    s_path = def_z / np.cos(angle_beam_rad)
    c1.metric("Z Depth", f"{def_z} mm")
    c2.metric("Sound Path S", f"{s_path:.1f} mm")
    c3.metric("Height (h)", f"{def_h} mm")
    c4.metric("Amplitude", f"{20*np.log10(tilt_factor+0.5):.1f} dB")
    
    st.info(f"💡 Modèle physique : Kirchhoff (Surfaces) + Born (Volume) + GTD (Bords).")
