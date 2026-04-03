import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from tensor_generator import generate_field_tensor

# Configuration de la page
st.set_page_config(page_title="Byte NDT - Interface Opérateur", layout="wide")

# --- STYLE ET TRADUCTION ---
lang = st.radio("Sélectionnez la langue / Select Language", ["FR", "EN"], horizontal=True)

if lang == "FR":
    title = "🛡️ Système d'Expertise Ultrasonore - Racine LSB 941"
    header_beam = "Configuration du Faisceau"
    label_angle = "Angle de tir (°)"
    header_defect = "Caractérisation de l'Indication"
    label_type = "Type de défaut"
    label_pos_x = "Position Latérale X (mm)"
    label_pos_z = "Profondeur Z (mm)"
    label_size = "Taille (mm)"
    btn_run = "🚀 Lancer le Diagnostic"
    msg_sizing = "💡 Note : L'isocontour jaune définit la zone de Sizing à -6dB."
    footer_npy = "Données .NPY prêtes pour le Machine Learning Global."
else:
    title = "🛡️ Ultrasonic Expert System - LSB 941 Root"
    header_beam = "Beam Configuration"
    label_angle = "Beam Angle (°)"
    header_defect = "Indication Characterization"
    label_type = "Defect Type"
    label_pos_x = "Lateral Position X (mm)"
    label_pos_z = "Depth Z (mm)"
    label_size = "Defect Size (mm)"
    btn_run = "🚀 Start Diagnosis"
    msg_sizing = "💡 Note: The yellow isocontour defines the -6dB Sizing area."
    footer_npy = "Data .NPY ready for Global Machine Learning."

st.title(title)

# --- BARRE LATÉRALE ---
st.sidebar.header(header_beam)
angle = st.sidebar.slider(label_angle, 0, 75, 45)

st.sidebar.markdown("---")
st.sidebar.header(header_defect)
defect_options = ["Aucun / None", "Inclusion (Void - Born)", "Entaille (EDM - Kirchhoff)"]
defect_type = st.sidebar.selectbox(label_type, defect_options)

# MISE À JOUR PROFONDEUR : On passe à 200 mm
if defect_type != "Aucun / None":
    def_x = st.sidebar.slider(label_pos_x, -50, 50, 0)
    def_z = st.sidebar.slider(label_pos_z, 0, 200, 100) # Profondeur jusqu'à 200 mm
    def_size = st.sidebar.slider(label_size, 0.5, 10.0, 2.0)

# --- CALCUL ET AFFICHAGE ---
if st.button(btn_run):
    with st.spinner('Simulation...'):
        # On génère le faisceau (ajusté pour la nouvelle profondeur)
        tensor, yy, zz = generate_field_tensor(angle)
        
        # Logique de détection
        if defect_type != "Aucun / None":
            dist = np.sqrt((yy - def_x)**2 + (zz - (def_z/5))**2) # Scale ajusté pour l'affichage
            mask = dist < (def_size/2)
            tensor[mask] = np.max(np.abs(tensor)) * 2.5

        # Conversion en dB
        amplitude = np.abs(tensor)
        A_max = np.max(amplitude)
        amplitude_db = 20 * np.log10(amplitude / (A_max + 1e-12))

        # Affichage Expert
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # L'échelle de profondeur (extent) est mise à jour à 200 mm
        im = ax.imshow(amplitude_db, extent=[-50, 50, 200, 0], cmap='viridis', vmin=-20, vmax=0)
        plt.colorbar(im, label="Amplitude (dB)")

        # Isocontours normatifs
        contours = ax.contour(amplitude_db, levels=[-12, -6, -3], 
                              extent=[-50, 50, 200, 0], 
                              colors=['white', 'yellow', 'red'])
        ax.clabel(contours, inline=True, fontsize=10, fmt='%1.0f dB')

        ax.set_title(f"Simulation PAUT @ {angle}° - Depth 200mm")
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Depth / Profondeur (mm)")
        
        st.pyplot(fig)
        st.info(msg_sizing)
        st.success(f"✅ {footer_npy}")
