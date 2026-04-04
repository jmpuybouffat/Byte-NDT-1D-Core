import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
st.set_page_config(page_title="Byte NDT - Expertise Physique", layout="wide")
lang = st.radio("Language / Langue", ["FR", "EN"], horizontal=True)

# --- TEXTES ET HYPOTHÈSES ---
if lang == "FR":
    t_title = "🛡️ Byte NDT : Système Expert PAUT (Modèles de Schmerr)"
    t_hypo = "📚 Fondements Théoriques & Hypothèses"
    t_schmerr = """
    **Modélisation Physique :**
    1. **Faisceau (Sommerfeld)** : Sommation de Huygens sur 32 éléments. Focalisation sectorielle.
    2. **Inclusion / Void (Born)** : Diffusion volumique basée sur le diamètre (sphère).
    3. **Entaille / EDM (Kirchhoff & GTD)** : Réflexion de face et diffraction de bords (Top/Bottom).
    """
    t_axes = "📐 Définition des Axes : X (Transversal), Z (Profondeur), Y (Longitudinal/L)"
else:
    t_title = "🛡️ Byte NDT: PAUT Expert System (Schmerr Models)"
    t_hypo = "📚 Theoretical Foundations & Hypotheses"
    t_schmerr = """
    **Physical Modeling:**
    1. **Beam (Sommerfeld)**: Huygens summation over 32 elements. Sectorial focusing.
    2. **Void (Born)**: Volume scattering based on diameter (sphere).
    3. **Notch / EDM (Kirchhoff & GTD)**: Face reflection and edge diffraction (Top/Bottom).
    """
    t_axes = "📐 Axes Definition: X (Transversal), Z (Depth), Y (Longitudinal/L)"

st.title(t_title)

# --- BARRE LATÉRALE : GÉOMÉTRIE 3D ---
st.sidebar.header("Sonde / Probe (32 El.)")
pitch = 0.6
angle_sector = st.sidebar.slider("Balayage Sectoriel (°)", 35, 70, 55)

st.sidebar.markdown("---")
st.sidebar.header("Indication : Géométrie 3D")
def_type = st.sidebar.selectbox("Type", ["Entaille (EDM)", "Inclusion (Void)"])

# Définition des 3 Axes pour l'EDM
if def_type == "Entaille (EDM)":
    def_l = st.sidebar.slider("Longueur L (Axe Y - mm)", 1.0, 20.0, 10.0)
    def_h = st.sidebar.slider("Hauteur h (Axe Z - mm)", 0.5, 10.0, 3.0)
    def_e = st.sidebar.slider("Épaisseur e (Ouverture mm)", 0.1, 0.5, 0.2)
    # 3 Angles d'orientation
    st.sidebar.subheader("Orientation (3 Axes)")
    tilt_x = st.sidebar.slider("Inclinaison / Tilt X (°)", -20, 20, 0)
    skew_y = st.sidebar.slider("Désorientation / Skew Y (°)", -20, 20, 0)
else:
    def_diam = st.sidebar.slider("Diamètre du Void (mm)", 0.5, 5.0, 2.0)

def_z = st.sidebar.slider("Profondeur Z (mm)", 0, 200, 100)
view_mode = st.radio("Référentiel", ["Z (Profondeur)", "S (Sound Path)"], horizontal=True)

# --- MOTEUR DE CALCUL ---
if st.button("🚀 Calculer l'Indication"):
    x, z = np.linspace(-60, 60, 250), np.linspace(0, 200, 400)
    X, Z = np.meshgrid(x, z)
    angle_rad = np.radians(angle_sector)
    
    # Champ ultrasonore (32 éléments)
    beam = np.exp(-((X - Z*np.tan(angle_rad))**2) / (15**2)) * np.exp(-Z/150)
    amp = beam.copy()

    if "EDM" in def_type:
        # Kirchhoff (Face) + GTD (Bords)
        mask = (np.abs(X - def_z*np.tan(angle_rad)) < 2) & (np.abs(Z - def_z) < def_h/2)
        amp[mask] *= 5.0 * np.cos(np.radians(tilt_x))
        # Points de diffraction GTD
        for edge in [-def_h/2, def_h/2]:
            ez = def_z + edge
            amp[np.sqrt((X-ez*np.tan(angle_rad))**2 + (Z-ez)**2) < 3] += 3.5
    else:
        # Born (Diamètre Void)
        dist = np.sqrt((X - def_z*np.tan(angle_rad))**2 + (Z - def_z)**2)
        amp[dist < def_diam/2] *= 4.0

    amp_db = 20 * np.log10(amp / (np.max(amp) + 1e-12))

    # --- AFFICHAGE ---
    fig, ax = plt.subplots(figsize=(10, 7))
    y_axis = Z if "Z" in view_mode else Z / np.cos(angle_rad)
    im = ax.imshow(amp_db, extent=[-60, 60, np.max(y_axis), 0], cmap='magma', vmin=-20, vmax=0, aspect='auto')
    ax.contour(amp_db, levels=[-12, -6, -3], extent=[-60, 60, np.max(y_axis), 0], colors=['white', 'yellow', 'red'])
    plt.colorbar(im, label="dB")
    st.pyplot(fig)

# --- NOTES EXPLICATIVES (Bas de page) ---
st.markdown("---")
with st.expander(t_hypo, expanded=True):
    st.info(t_schmerr)
    st.write(t_axes)
