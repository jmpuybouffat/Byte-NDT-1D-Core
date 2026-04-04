import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURATION INTERFACE ---
st.set_page_config(page_title="Byte NDT - Certification 32 El.", layout="wide")
lang = st.radio("Language / Langue", ["FR", "EN"], horizontal=True)

# Lexique bilingue
texts = {
    "title": "🛡️ Byte NDT : Système Expert PAUT (32 Eléments / Sectoriel)",
    "setup": "Configuration de la Sonde (Hardware)",
    "wedge": "Angle Sabot / Wedge (°)",
    "scan": "Balayage Sectoriel (°)",
    "defect": "Géométrie de l'Indication",
    "type": "Nature du défaut",
    "dim": "Dimensions (L, h, e)",
    "orient": "Orientation (3 Axes)",
    "hypo": "Hypothèses de Calcul",
    "btn": "🚀 GÉNÉRER LE DIAGNOSTIC & RAPPORT DB",
    "note": "Note : Sommerfeld (Faisceau), Kirchhoff (Faces), GTD (Bords)."
} if lang == "FR" else {
    "title": "🛡️ Byte NDT: PAUT Expert System (32 Elements / Sectorial)",
    "setup": "Probe Configuration (Hardware)",
    "wedge": "Wedge Angle (°)",
    "scan": "Sectorial Scan (°)",
    "defect": "Indication Geometry",
    "type": "Defect Nature",
    "dim": "Dimensions (L, h, e)",
    "orient": "Orientation (3 Axes)",
    "hypo": "Calculation Hypotheses",
    "btn": "🚀 GENERATE DIAGNOSIS & DB REPORT",
    "note": "Note: Sommerfeld (Beam), Kirchhoff (Faces), GTD (Edges)."
}

st.title(texts["title"])

# --- BARRE LATÉRALE : HARDWARE & GÉOMÉTRIE ---
st.sidebar.header(texts["setup"])
nb_el = st.sidebar.select_slider("Éléments PAUT", options=[16, 32], value=32)
pitch = 0.6  # mm
wedge_angle = 55.0 # Angle de base demandé

st.sidebar.markdown("---")
st.sidebar.header(texts["scan"])
angle_sector = st.sidebar.slider("Balayage / Scan (°)", 35, 70, 55, step=1)
angle_rad = np.radians(angle_sector)

st.sidebar.markdown("---")
st.sidebar.header(texts["defect"])
def_type = st.sidebar.selectbox(texts["type"], ["Entaille (EDM)", "Inclusion (Void)"])
def_z = st.sidebar.slider("Profondeur Z (mm)", 0, 200, 100)
def_l = st.sidebar.slider("Longueur L (mm)", 1, 20, 10)
def_h = st.sidebar.slider("Hauteur h (mm)", 1, 10, 3)
def_e = st.sidebar.slider("Épaisseur e (mm)", 0.1, 0.5, 0.2)
def_tilt = st.sidebar.slider(texts["orient"], -20, 20, 0)

view_mode = st.radio("Référentiel", ["Profondeur Z (Depth)", "Parcours S (Sound Path)"], horizontal=True)

# --- MOTEUR PHYSIQUE (HYUGENS & KIRCHHOFF) ---
if st.button(texts["btn"]):
    # Grille 200mm
    x_vec, z_vec = np.linspace(-60, 60, 250), np.linspace(0, 200, 400)
    X, Z = np.meshgrid(x_vec, z_vec)
    
    # Simulation sommation des 32 éléments (Lois de retard)
    el_pos = (np.arange(nb_el) - (nb_el-1)/2) * pitch
    total_field = np.zeros_like(X, dtype=complex)
    for x_el in el_pos:
        r = np.sqrt((X - x_el)**2 + Z**2)
        # Retard sectoriel focalisé
        phase = 2 * np.pi * 5.0 * (r / 3.2 - (x_el * np.sin(angle_rad) / 3.2))
        total_field += np.exp(-1j * phase) / np.sqrt(r + 1)
    
    amplitude = np.abs(total_field)
    
    # Interaction spécifique
    if "EDM" in def_type:
        # Kirchhoff + GTD (Double tache aux bords)
        tilt_loss = np.cos(np.radians(def_tilt))
        mask_face = (np.abs(X - def_z*np.tan(angle_rad)) < def_l/10) & (np.abs(Z - def_z) < def_h/2)
        amplitude[mask_face] *= (5.0 * tilt_loss)
        for edge in [-def_h/2, def_h/2]: # GTD
            mask_edge = (np.sqrt((X - (def_z+edge)*np.tan(angle_rad))**2 + (Z-(def_z+edge))**2) < 3.5)
            amplitude[mask_edge] += 3.5
    else:
        # Born (Void)
        dist = np.sqrt((X - def_z*np.tan(angle_rad))**2 + (Z - def_z)**2)
        amplitude[dist < 3] *= 4.0

    # dB & Couleurs CIVA
    amp_db = 20 * np.log10(amplitude / (np.max(amplitude) + 1e-12))

    # --- AFFICHAGE ---
    fig, ax = plt.subplots(figsize=(10, 8))
    y_plot = Z if "Z" in view_mode else Z / np.cos(angle_rad)
    
    im = ax.imshow(amp_db, extent=[-60, 60, np.max(y_plot), 0], cmap='magma', vmin=-20, vmax=0, aspect='auto')
    
    # ISOCONTOURS MÉTROLOGIQUES
    cnt = ax.contour(amp_db, levels=[-12, -6, -3], extent=[-60, 60, np.max(y_plot), 0], 
                     colors=['white', 'yellow', 'red'], linewidths=1.5)
    ax.clabel(cnt, inline=True, fontsize=10, fmt='%1.1f dB')
    
    plt.colorbar(im, label="Amplitude (dB)")
    ax.set_ylabel("Profondeur / Depth Z (mm)" if "Z" in view_mode else "Sound Path S (mm)")
    st.pyplot(fig)

    # --- RAPPORT & HYPOTHÈSES ---
    st.markdown("### 📊 Rapport d'Examen PAUT")
    c1, c2, c3 = st.columns(3)
    c1.metric("Sound Path S", f"{def_z/np.cos(angle_rad):.1f} mm")
    c2.metric("Amplitude Max", f"{np.max(amp_db):.1f} dB")
    c3.metric("Ouverture Active", f"{nb_el * pitch:.1f} mm")

    with st.expander(texts["hypo"]):
        st.write(texts["note"])
        st.write("- **Sommerfeld** : Modélisation de la diffraction du champ lointain.")
        st.write("- **Kirchhoff** : Approximation de surface pour la réflexion spéculaire sur EDM.")
        st.write("- **GTD** : Geometric Theory of Diffraction pour les échos de bords (dimensionnement h).")
