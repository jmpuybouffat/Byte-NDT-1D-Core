import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURATION INTERFACE ---
st.set_page_config(page_title="Byte NDT - LSB 941 Expert", layout="wide")
lang = st.radio("Language / Langue", ["FR", "EN"], horizontal=True)

t = {
    "title": "🛡️ Byte NDT : Expertise Physique Intégrée (Born, Kirchhoff & GTD)",
    "setup": "Configuration Examen",
    "angle": "Angle de tir (°)",
    "mode": "Vue : Profondeur (Z) ou Parcours (S) ?",
    "defect": "Indication (EDM / Void)",
    "type": "Type de défaut",
    "dim": "Dimensions (L, h, e)",
    "orient": "Désorientation (°)",
    "btn": "🚀 GÉNÉRER LE DIAGNOSTIC",
    "report": "📊 Rapport Métrologique"
} if lang == "FR" else {
    "title": "🛡️ Byte NDT: Integrated Physical Expertise (Born, Kirchhoff & GTD)",
    "setup": "Exam Setup",
    "angle": "Beam Angle (°)",
    "mode": "View: Depth (Z) or Sound Path (S)?",
    "defect": "Indication (EDM / Void)",
    "type": "Defect Type",
    "dim": "Dimensions (L, h, e)",
    "orient": "Misorientation (°)",
    "btn": "🚀 GENERATE DIAGNOSIS",
    "report": "📊 Metrology Report"
}

st.title(t["title"])

# --- PARAMÈTRES (S'AFFICHENT DANS LA BARRE LATÉRALE) ---
st.sidebar.header(t["setup"])
angle_deg = st.sidebar.slider(t["angle"], 0, 75, 45)
angle_rad = np.radians(angle_deg)

view_mode = st.radio(t["mode"], ["Z (Depth)", "S (Sound Path)"], horizontal=True)

st.sidebar.markdown("---")
st.sidebar.header(t["defect"])
def_type = st.sidebar.selectbox(t["type"], ["Entaille (EDM - Kirchhoff/GTD)", "Inclusion (Void - Born)"])
def_z = st.sidebar.slider("Profondeur Z (mm)", 0, 200, 100)
def_h = st.sidebar.slider("Hauteur / Height (mm)", 0.5, 10.0, 3.0)
def_tilt = st.sidebar.slider(t["orient"], -20, 20, 0)

# --- MOTEUR PHYSIQUE AUTONOME ---
if st.button(t["btn"]):
    # Création de la grille (indépendante de tout fichier externe)
    x = np.linspace(-60, 60, 250)
    z = np.linspace(0, 200, 400)
    X, Z = np.meshgrid(x, z)
    
    # 1. Faisceau incident
    beam = np.exp(-((X - Z*np.tan(angle_rad))**2) / (15**2)) * np.exp(-Z/150)
    signal = beam.copy()
    
    # 2. Modélisation de l'Indication
    if "Entaille" in def_type:
        # Kirchhoff (Face) + GTD (Bords)
        tilt_factor = np.cos(np.radians(def_tilt))
        mask_face = (np.abs(X - def_z*np.tan(angle_rad)) < 3) & (np.abs(Z - def_z) < def_h/2)
        signal[mask_face] *= (6.0 * tilt_factor)
        
        # GTD : On simule les deux pointes de l'entaille (Double tache)
        for edge_off in [-def_h/2, def_h/2]:
            ez = def_z + edge_off
            ex = ez * np.tan(angle_rad)
            mask_edge = (np.abs(X - ex) < 4) & (np.abs(Z - ez) < 2)
            signal[mask_edge] += 4.0
    else:
        # Born (Inclusion sphérique)
        dist = np.sqrt((X - def_z*np.tan(angle_rad))**2 + (Z - def_z)**2)
        signal[dist < 2] *= 3.5

    # 3. Conversion dB
    amp_db = 20 * np.log10(signal / (np.max(signal) + 1e-12))

    # --- AFFICHAGE ---
    fig, ax = plt.subplots(figsize=(10, 8))
    y_plot = Z if "Z" in view_mode else Z / np.cos(angle_rad)
    ylabel = "Depth Z (mm)" if "Z" in view_mode else "Sound Path S (mm)"

    im = ax.imshow(amp_db, extent=[-60, 60, np.max(y_plot), 0], cmap='magma', vmin=-25, vmax=0, aspect='auto')
    ax.contour(amp_db, levels=[-12, -6], extent=[-60, 60, np.max(y_plot), 0], colors=['white', 'yellow'], linewidths=1.5)
    
    plt.colorbar(im, label="Amplitude (dB)")
    ax.set_ylabel(ylabel)
    st.pyplot(fig)

    # --- RAPPORT ---
    st.markdown(f"### {t['report']}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Depth Z", f"{def_z} mm")
    c2.metric("Sound Path S", f"{def_z / np.cos(angle_rad):.1f} mm")
    c3.metric("Height (h)", f"{def_h} mm")
