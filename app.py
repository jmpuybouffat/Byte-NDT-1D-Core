import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(page_title="Byte NDT - Digital Twin 3D", layout="wide")
st.title("🛡️ Byte NDT : Digital Twin 3D (Expert Mode)")

# --- BARRE LATÉRALE : PARAMÈTRES RÉELS ---
with st.sidebar:
    st.header("Sonde & Milieu")
    v_st = 3240 # Shear wave
    angle_deg = st.slider("Angle de tir (°)", 35, 75, 45)
    
    st.header("Indication EDM (3D)")
    cx = st.slider("Position X (mm)", -40, 40, 20)
    cy = st.slider("Position Y (mm)", -40, 40, 0)
    cz = st.slider("Profondeur Z (mm)", 0, 200, 80)
    
    L = st.slider("Longueur L (mm)", 1, 20, 10)
    h = st.slider("Hauteur h (mm)", 1, 10, 5)
    
    st.subheader("Orientation (Axes Pan/Tilt/Skew)")
    tilt = st.slider("Tilt (°)", -30, 30, 0)
    pan = st.slider("Pan (°)", -30, 30, 0)

# --- CALCUL DU TWIN 3D (PRESSION & GÉOMÉTRIE) ---
def generate_3d_twin():
    # 1. Création de l'EDM (Boîte 3D)
    # On définit les sommets de l'entaille
    x_rect = [cx-L/2, cx+L/2, cx+L/2, cx-L/2, cx-L/2]
    y_rect = [cy-2, cy-2, cy+2, cy+2, cy-2] # largeur fixe pour visi
    z_rect = [cz-h/2, cz-h/2, cz+h/2, cz+h/2, cz-h/2]

    # 2. Simulation du Faisceau (Volume de Pression)
    # On génère un cône de pression pour visualiser le faisceau réel
    z_beam = np.linspace(0, 200, 20)
    x_beam = z_beam * np.tan(np.radians(angle_deg))
    y_beam = np.zeros_like(z_beam)

    fig = go.Figure()

    # AJOUT DU FAISCEAU (Cône de propagation)
    fig.add_trace(go.Scatter3d(
        x=x_beam, y=y_beam, z=z_beam,
        mode='lines',
        line=dict(color='orange', width=10),
        name="Axe du Faisceau (Pressure Path)"
    ))

    # AJOUT DE L'EDM (L'indication physique)
    fig.add_trace(go.Mesh3d(
        x=[cx-L/2, cx+L/2, cx+L/2, cx-L/2, cx-L/2, cx+L/2, cx+L/2, cx-L/2],
        y=[cy-1, cy-1, cy+1, cy+1, cy-1, cy-1, cy+1, cy+1],
        z=[cz-h/2, cz-h/2, cz-h/2, cz-h/2, cz+h/2, cz+h/2, cz+h/2, cz+h/2],
        color='red', opacity=0.8, name="EDM Notch"
    ))

    # CONFIGURATION DU RÉFÉRENTIEL X, Y, Z
    fig.update_layout(
        scene=dict(
            xaxis_title='X (Transversal)',
            yaxis_title='Y (Longitudinal)',
            zaxis_title='Z (Profondeur)',
            zaxis=dict(range=[200, 0]), # Inversion pour la profondeur
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=1.5)
        ),
        margin=dict(r=0, l=0, b=0, t=40),
        title="Visualisation interactive du Twin (Faisceau vs Indication)"
    )
    return fig

st.plotly_chart(generate_3d_twin(), use_container_width=True)

st.info("💡 Utilisez votre souris pour faire pivoter la vue. Vérifiez la collision faisceau/EDM.")
