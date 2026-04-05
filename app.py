import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURATION & BILINGUISME ---
st.set_page_config(page_title="Byte NDT - PAUT Beam Pure", layout="wide")
lang = st.radio("Langue / Language", ["FR", "EN"], horizontal=True)

t = {
    "title": "🎓 Byte NDT : Simulateur Faisceau Pur (Contrôle Total)",
    "params": "⚙️ Sonde IMASONIC",
    "nb_el": "Nb éléments (Nx)",
    "pitch": "Pitch (Px - mm)",
    "gap": "Gap (IEx - mm)",
    "freq": "Fréquence (MHz)",
    "steering": "🎯 Pilotage du Faisceau",
    "mode_ang": "Balayage Angulaire (Angle + Profondeur)",
    "mode_cart": "Point Focal Libre (Fx, Fz)",
    "angle": "Angle de tir (°)",
    "focus_x": "Position Latérale Fx (mm)",
    "focus_z": "Profondeur Focus Fz (mm)",
    "env": "Milieu de propagation",
    "vel": "Vitesse (m/s)"
} if lang == "FR" else {
    "title": "🎓 Byte NDT: Pure Beam Simulator (Full Control)",
    "params": "⚙️ IMASONIC Probe",
    "nb_el": "Nb elements (Nx)",
    "pitch": "Pitch (Px - mm)",
    "gap": "Gap (IEx - mm)",
    "freq": "Frequency (MHz)",
    "steering": "🎯 Beam Steering",
    "mode_ang": "Angular Sweep (Angle + Depth)",
    "mode_cart": "Free Focal Point (Fx, Fz)",
    "angle": "Steering Angle (°)",
    "focus_x": "Lateral Position Fx (mm)",
    "focus_z": "Focal Depth Fz (mm)",
    "env": "Propagation Medium",
    "vel": "Velocity (m/s)"
}

st.title(t["title"])

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.header(t["params"])
    nb_el = st.select_slider(t["nb_el"], options=[8, 16, 32, 64], value=32)
    pitch = st.slider(t["pitch"], 0.1, 2.0, 0.6, 0.1)
    gap = st.slider(t["gap"], 0.0, 0.5, 0.1, 0.05)
    f_mhz = st.slider(t["freq"], 1.0, 10.0, 5.0, 0.5)
    
    st.header(t["steering"])
    # LE DOUBLE MODE EST ICI : L'utilisateur ne perd plus aucun outil
    mode = st.radio("", [t["mode_ang"], t["mode_cart"]])
    
    if mode == t["mode_ang"]:
        angle_deg = st.slider(t["angle"], -70, 70, 45)
        fz = st.slider(t["focus_z"], 10.0, 120.0, 50.0, 1.0)
        fx = fz * np.tan(np.radians(angle_deg))
    else:
        fx = st.slider(t["focus_x"], -50.0, 50.0, 20.0, 1.0)
        fz = st.slider(t["focus_z"], 10.0, 120.0, 50.0, 1.0)
    
    st.header(t["env"])
    v_st = st.number_input(t["vel"], value=3240)

# --- MOTEUR DE CALCUL PHYSIQUE ---
v_mm_s = v_st * 1000.0 
f_hz = f_mhz * 1e6
omega = 2 * np.pi * f_hz
k = omega / v_mm_s
lambda_mm = v_mm_s / f_hz
element_width = pitch - gap

# Grille de calcul
x_grid = np.linspace(-60, 60, 250)
z_grid = np.linspace(0.1, 100, 250)
X, Z = np.meshgrid(x_grid, z_grid)

# Loi de retards stricte vers le point (Fx, Fz)
elements_x = (np.arange(nb_el) - (nb_el - 1) / 2) * pitch
dist_focal_centre = np.sqrt(fx**2 + fz**2)
retards = (dist_focal_centre - np.sqrt((fx - elements_x)**2 + fz**2)) / v_mm_s

# Sommation de Huygens + Directivité
pressure = np.zeros_like(X, dtype=complex)
for i in range(nb_el):
    r = np.sqrt((X - elements_x[i])**2 + Z**2)
    theta = np.arcsin(np.clip((X - elements_x[i]) / r, -1.0, 1.0))
    term = (np.pi * element_width / lambda_mm) * np.sin(theta)
    term = np.where(term == 0, 1e-9, term) 
    directivity = np.sin(term) / term
    
    phase = k * r - omega * retards[i]
    pressure += directivity * (1 / np.sqrt(r)) * np.exp(1j * phase)

amp = np.abs(pressure)
amp_db = 20 * np.log10(amp / np.max(amp))

# --- AFFICHAGE ---
fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor('white')

ax.set_xlim(-60, 60)
ax.set_ylim(100, 0)

im = ax.imshow(amp_db, extent=[-60, 60, 100, 0], cmap='magma', vmin=-24, vmax=0, aspect='auto')
cnt = ax.contour(amp_db, levels=[-12, -6, -3], extent=[-60, 60, 100, 0], colors=['silver', 'gold', 'red'], linewidths=0.8)

# Dessin de la sonde IMASONIC
for i, el_x in enumerate(elements_x):
    ax.add_patch(plt.Rectangle((el_x - element_width/2, -2), element_width, 2, color='cornflowerblue', clip_on=False))

# Ligne d'axe et Marqueur Focale
ax.plot([0, fx], [0, fz], color='white', linestyle='--', alpha=0.4)
ax.plot(fx, fz, marker='+', color='white', markersize=15, markeredgewidth=2)

ax.set_xlabel("Position Latérale X (mm)")
ax.set_ylabel("Profondeur Z (mm)")
plt.colorbar(im, label="Amplitude (dB)", shrink=0.7)

st.pyplot(fig)
