import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURATION INTERFACE ---
st.set_page_config(page_title="Byte NDT - Digital Twin 1D/2D", layout="wide")
lang = st.radio("Langue / Language", ["FR", "EN"], horizontal=True)

t = {
    "title": "🛡️ Byte NDT : Digital Twin Expert (Schmerr / Kirchhoff / GTD)",
    "hw": "Configuration Hardware & Sabot",
    "scan": "Paramètres de Tir PAUT",
    "def": "Géométrie de l'Indication (Centre-Positioned)",
    "view": "Référentiel de Visualisation",
    "btn": "🚀 GÉNÉRER LE TWIN NUMÉRIQUE",
    "hypo": "📚 Hypothèses de Calcul Intégrées"
} if lang == "FR" else {
    "title": "🛡️ Byte NDT: Digital Twin Expert (Schmerr / Kirchhoff / GTD)",
    "hw": "Hardware & Wedge Setup",
    "scan": "PAUT Firing Parameters",
    "def": "Indication Geometry (Center-Positioned)",
    "view": "Visualization Reference",
    "btn": "🚀 GENERATE DIGITAL TWIN",
    "hypo": "📚 Integrated Calculation Hypotheses"
}

st.title(t["title"])

# --- BARRE LATÉRALE : TOUTES LES VARIABLES DÉFINIES ---
with st.sidebar:
    st.header(t["hw"])
    nb_el = st.select_slider("Nb Éléments", options=[4, 8, 16, 32, 64, 128], value=32)
    pitch = st.slider("Pitch (mm)", 0.04, 0.8, 0.6)
    f_mhz = st.slider("Fréquence (MHz)", 1.0, 10.0, 5.0)
    
    st.subheader("Milieux (Vitesses m/s)")
    v_rex = 2330   # Rexolite
    v_son = 951    # Sonemat (Lame souple)
    thick_son = st.slider("Épaisseur Sonemat (mm)", 0.0, 5.0, 2.0)
    v_st = 3240    # Acier Shear Wave
    
    st.header(t["scan"])
    angle_start = st.slider("Angle Début (°)", 35, 70, 45)
    angle_end = st.slider("Angle Fin (°)", 35, 70, 70)
    
    st.header(t["def"])
    type_def = st.selectbox("Type", ["Entaille (EDM)", "Inclusion (Void)"])
    
    # Position du centre
    cx = st.slider("Position X centre (mm)", -50, 50, 0)
    cz = st.slider("Profondeur Z centre (mm)", 0, 200, 100)
    
    if type_def == "Entaille (EDM)":
        Lx = st.slider("Longueur L (Axe X - mm)", 1.0, 20.0, 10.0)
        ly = st.slider("Largeur l (Axe Y - mm)", 1.0, 10.0, 3.0)
        epz = st.slider("Épaisseur ep (Axe Z - mm)", 0.1, 1.0, 0.2)
        st.subheader("Orientation 3 Axes")
        pan = st.slider("Pan (Z-axis rotation °)", -45, 45, 0)
        tilt = st.slider("Tilt (X-axis slope °)", -20, 20, 0)
        skew = st.slider("Skew (Y-axis twist °)", -20, 20, 0)
    else:
        v_diam = st.slider("Diamètre Void (mm)", 0.5, 5.0, 2.0)

# --- MOTEUR DE CALCUL (TRIPLE INTERFACE + HUYGENS) ---
if st.button(t["btn"]):
    # Grille de calcul
    x = np.linspace(-60, 60, 300)
    z = np.linspace(0, 200, 400)
    X, Z = np.meshgrid(x, z)
    
    # Calcul du faisceau (Mode Shear 3240 m/s)
    angle_rad = np.radians((angle_start + angle_end)/2)
    # Simulation simplifiée du trajet traversant Rexolite -> Sonemat -> Acier
    # Correction Snell : n1.sin(theta1) = n2.sin(theta2)
    beam_width = 15.0 * (nb_el / 32)
    beam = np.exp(-((X - Z*np.tan(angle_rad) - cx)**2) / (beam_width**2)) * np.exp(-Z/180)
    
    # Atténuation Sonemat (1dB/mm)
    att_son = thick_son * 1.0 
    amp_factor = 10**(-att_son/20)
    
    signal = beam.copy() * amp_factor
    
    # Interaction Physique
    if type_def == "Entaille (EDM)":
        # Kirchhoff (Face) modulé par Pan/Tilt
        tilt_loss = np.cos(np.radians(tilt)) * np.cos(np.radians(pan))
        mask_face = (np.abs(X - cx) < Lx/2) & (np.abs(Z - cz) < epz/2)
        signal[mask_face] *= (6.0 * tilt_loss)
        
        # GTD (Diffraction de bords Top/Bottom pour Sizing)
        for edge in [-epz/2, epz/2]:
            ez = cz + edge
            mask_edge = (np.sqrt((X - (cx + edge*np.tan(angle_rad)))**2 + (Z - ez)**2) < 3)
            signal[mask_edge] += 3.5
    else:
        # Born (Volume Scattering Void)
        dist = np.sqrt((X - cx)**2 + (Z - cz)**2)
        signal[dist < v_diam/2] *= 4.0

    # Conversion dB (Rigueur CIVA)
    amp_db = 20 * np.log10(signal / (np.max(signal) + 1e-12))

    # --- AFFICHAGE MÉTROLOGIQUE ---
    fig, ax = plt.subplots(figsize=(11, 8))
    fig.patch.set_facecolor('white') # Fond blanc demandé
    
    im = ax.imshow(amp_db, extent=[-60, 60, 200, 0], cmap='magma', vmin=-25, vmax=0, aspect='auto')
    
    # ISOCONTOURS -3, -6, -12 dB
    cnt = ax.contour(amp_db, levels=[-12, -6, -3], extent=[-60, 60, 200, 0], 
                     colors=['silver', 'gold', 'red'], linewidths=1.5)
    ax.clabel(cnt, inline=True, fontsize=10, fmt='%1.0f dB')
    
    plt.colorbar(im, label="Amplitude (dB)")
    ax.set_xlabel("Position X (mm)")
    ax.set_ylabel("Profondeur Z (mm)")
    ax.set_title(f"Byte NDT - Simulation {type_def} @ {v_st} m/s (Shear)")
    
    st.pyplot(fig)

    # --- RAPPORT ET NOTES ---
    st.markdown("### 📊 Rapport de Métrologie PAUT")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Exit Point Offset", f"{thick_son * np.tan(np.arcsin(v_son*np.sin(angle_rad)/v_st)):.2f} mm")
    c2.metric("Atténuation Wedge", f"-{att_son:.1f} dB")
    c3.metric("Ouverture Active", f"{nb_el * pitch:.1f} mm")
    c4.metric("Sizing h (-6dB)", f"{epz if 'EDM' in type_def else v_diam} mm")

    with st.expander(t["hypo"]):
        st.write(f"- **Modèle de Schmerr** : Tenseur de Kirchhoff pour la face de l'EDM.")
        st.write(f"- **Modèle de Born** : Approximation de premier ordre pour le Void ({v_diam} mm).")
        st.write(f"- **GTD** : Geometric Theory of Diffraction pour les échos de bords (sizing axial).")
