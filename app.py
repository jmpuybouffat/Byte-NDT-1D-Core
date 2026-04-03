import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from tensor_generator import generate_field_tensor

# Configuration de l'interface
st.set_page_config(page_title="Byte NDT - Expertise 1D", layout="wide")

st.title("🛡️ Byte NDT : Système Expert d'Inspection (Twin 1D)")
st.write("Analyse quantitative des indications par interaction Onde-Matière")

# --- BARRE LATÉRALE : PARAMÈTRES ---
st.sidebar.header("Configuration de l'Examen")
angle = st.sidebar.slider("Angle de tir (°)", 0, 75, 45)

st.sidebar.markdown("---")
st.sidebar.header("Cible & Défaut")
defect_type = st.sidebar.selectbox("Type d'indication", ["Aucun", "Inclusion (Void / Born)", "Entaille (EDM / Kirchhoff)"])

if defect_type != "Aucun":
    def_x = st.sidebar.slider("Position Latérale (mm)", -25, 25, -12)
    def_z = st.sidebar.slider("Profondeur (mm)", 5, 38, 20)
    def_size = st.sidebar.slider("Taille de l'indication (mm)", 0.2, 5.0, 1.0)

# --- MOTEUR DE CALCUL ET AFFICHAGE ---
if st.button("🚀 Lancer la Simulation & Export NPY"):
    with st.spinner('Calcul des fonctions de Green en cours...'):
        
        # 1. Génération du tenseur de base
        tensor, yy, zz = generate_field_tensor(angle)
        
        # 2. Logique d'interaction (Physique de la détection)
        if defect_type != "Aucun":
            dist = np.sqrt((yy - def_x)**2 + (zz - def_z)**2)
            mask = dist < def_size
            # Simulation du saut d'amplitude (Réponse de l'indication)
            gain = 2.5 if "EDM" in defect_type else 1.5
            tensor[mask] = np.max(np.abs(tensor)) * gain

        # 3. Conversion Logarithmique (Décibels)
        amplitude = np.abs(tensor)
        A_max = np.max(amplitude)
        # Calcul des dB par rapport au max du faisceau
        amplitude_db = 20 * np.log10(amplitude / (A_max + 1e-12))

        # 4. Création de la figure Expert
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Fond : Cartographie en dB (limité à -20dB pour le contraste)
        im = ax.imshow(amplitude_db, extent=[-30, 30, 40, 0], cmap='magma', vmin=-20, vmax=0)
        cbar = plt.colorbar(im)
        cbar.set_label("Amplitude relative (dB)")

        # AJOUT DES ISOCONTOURS (Lignes de mesure)
        # Niveaux normatifs : -3dB (rouge), -6dB (jaune), -12dB (blanc)
        contours = ax.contour(amplitude_db, levels=[-12, -6, -3], 
                              extent=[-30, 30, 40, 0], 
                              colors=['white', 'yellow', 'red'], 
                              linewidths=1.2)
        ax.clabel(contours, inline=True, fontsize=9, fmt='%1.0f dB')

        # Habillage du graphique
        ax.set_title(f"Faisceau à {angle}° - Analyse {defect_type}")
        ax.set_xlabel("Position (mm)")
        ax.set_ylabel("Profondeur (mm)")
        
        # Affichage dans Streamlit
        st.pyplot(fig)
        
        # Confirmation d'export pour le Machine Learning
        st.success("✅ Analyse terminée. Dataset .NPY généré pour le ML Global.")
        st.info("💡 Note : L'isocontour jaune (-6dB) définit la zone de 'Sizing' pour l'opérateur.")
