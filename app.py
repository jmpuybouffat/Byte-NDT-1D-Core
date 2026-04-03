# --- CALCUL EN DB ---
amplitude = np.abs(tensor)
A_max = np.max(amplitude)
# On évite la division par zéro
amplitude_db = 20 * np.log10(amplitude / A_max + 1e-10)

# --- AFFICHAGE EXPERT ---
fig, ax = plt.subplots(figsize=(10, 7))

# Fond coloré en dB (limité à -20dB pour la clarté)
im = ax.imshow(amplitude_db, extent=[-30, 30, 40, 0], cmap='viridis', vmin=-20, vmax=0)
plt.colorbar(im, label="Amplitude (dB / Référence)")

# AJOUT DES COURBES DE NIVEAU (Isocontours)
# On dessine spécifiquement les lignes -3, -6 et -12 dB
contours = ax.contour(amplitude_db, levels=[-12, -6, -3], 
                      extent=[-30, 30, 40, 0], colors=['white', 'yellow', 'red'],
                      linewidths=1.5)
ax.clabel(contours, inline=True, fontsize=10, fmt='%1.0f dB')

ax.set_title("Cartographie de Pression en dB avec Isocontours")
st.pyplot(fig)