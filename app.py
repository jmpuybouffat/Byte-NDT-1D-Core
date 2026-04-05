import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(page_title="Byte NDT - Digital Twin", layout="wide")
st.title("🛡️ Byte NDT : Digital Twin Expert (Huygens + 3D)")

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.header("⚙️ Sonde & Sabot")
    nb_el = st.select_slider("Nb Éléments", options=[16, 32, 64, 128], value=32)
    pitch = st.slider("Pitch (mm)", 0.1, 1.0, 0.6)
    
    st.subheader("Milieux & Réfraction")
    v_rex = 2330
    v_son = 951
    thick_son = st.slider("Épaisseur Sonemat (mm)", 0.0, 5.0, 2.0)
    v_st = 3240 # Shear wave
    angle_tir = st.slider("Angle de tir Acier (°)", 35, 75, 45)

    st.header("🎯 Géométrie EDM (3D)")
    cx = st.slider("Position X (mm)", -40, 40, 20)
    cy = st.slider("Position Y (mm)", -20, 20, 0)
    cz = st.slider("Profondeur Z (mm)", 10, 200, 80)
    
    L = st.slider("Longueur L (Axe Y)", 1.0, 20.0, 10.0)
    h = st.slider("Hauteur h (Axe Z)", 1.0, 10.0, 5.0)
    ep = 0.5 # Epaisseur de l'entaille
    
    st.subheader("Orientation")
    tilt = st.slider("Tilt X (°)", -20, 20, 0)
    pan = st.slider("Pan Z (°)", -20, 20, 0)

# --- MOTEUR PHYSIQUE ---
# Grille de calcul
x_grid = np.linspace(-60, 60, 300)
z_grid = np.linspace(0, 200, 400)
X, Z = np.meshgrid(x_grid, z_grid)

angle_rad = np.radians(angle_tir)
beam_width = 15.0 * (nb_el / 32)

# Faisceau théorique
beam = np.exp(-((X - Z*np.tan(angle_rad) - cx)**2) / (beam_width**2)) * np.exp(-Z/180)

# Atténuation Sonemat
att_son = thick_son * 1.0
amp_factor = 10**(-att_son/20)
signal = beam.copy() * amp_factor

# Interaction Kirchhoff & GTD
tilt_loss = np.cos(np.radians(tilt)) * np.cos(np.radians(pan))
mask_face = (np.abs(X - cx) < ep) & (np.abs(Z - cz) < h/2)
signal[mask_face] *= (6.0 * tilt_loss)

for edge in [-h/2, h/2]:
    ez = cz + edge
    mask_edge = (np.sqrt((X - (cx + edge*np.tan(angle_rad)))**2 + (Z - ez)**2) < 3)
    signal[mask_edge] += 3.5

amp_db = 20 * np.log10(signal / (np.max(signal) + 1e-12))

# --- AFFICHAGE DOUBLE TWIN ---
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("📊 Vue Expert (B-Scan & GTD)")
    fig2d, ax = plt.subplots(figsize=(8, 9))
    fig2d.patch.set_facecolor('white')
    im = ax.imshow(amp_db, extent=[-60, 60, 200, 0], cmap='magma', vmin=-25, vmax=0, aspect='auto')
    cnt = ax.contour(amp_db, levels=[-12, -6, -3], extent=[-60, 60, 200, 0], colors=['silver', 'gold', 'red'], linewidths=1.5)
    ax.clabel(cnt, inline=True, fontsize=10, fmt='%1.0f dB')
    ax.set_xlabel("Position X (mm)")
    ax.set_ylabel("Profondeur Z (mm)")
    st.pyplot(fig2d)

with col2:
    st.subheader("🌐 Référentiel 3D Interactif")
    fig3d = go.Figure()
    
    # Trace du Faisceau (Ligne Orange)
    z_line = np.linspace(0, 200, 10)
    x_line = z_line * np.tan(angle_rad)
    fig3d.add_trace(go.Scatter3d(x=x_line, y=np.zeros(10), z=z_line, mode='lines', line=dict(color='orange', width=8), name="Axe Faisceau"))
    
    # EDM (Cube Rouge)
    fig3d.add_trace(go.Mesh3d(
        x=[cx-ep, cx+ep, cx+ep, cx-ep, cx-ep, cx+ep, cx+ep, cx-ep],
        y=[cy-L/2, cy-L/2, cy+L/2, cy+L/2, cy-L/2, cy-L/2, cy+L/2, cy+L/2],
        z=[cz-h/2, cz-h/2, cz-h/2, cz-h/2, cz+h/2, cz+h/2, cz+h/2, cz+h/2],
        color='red', opacity=0.8, name="EDM"
    ))
    
    fig3d.update_layout(scene=dict(
        xaxis_title='X (Transversal)', yaxis_title='Y (Longitudinal)', zaxis_title='Z (Profondeur)',
        zaxis=dict(range=[200, 0]), aspectmode='manual', aspectratio=dict(x=1, y=1, z=1.5)
    ), margin=dict(r=0, l=0, b=0, t=0))
    st.plotly_chart(fig3d, use_container_width=True)

st.markdown("---")
st.markdown(f"**Calculs de surface :** Atténuation Sonemat intégrée : **-{att_son:.1f} dB** | Décalage Exit Point estimé : **{thick_son * np.tan(np.arcsin(v_son*np.sin(angle_rad)/v_st)):.2f} mm**")
