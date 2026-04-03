import matplotlib.pyplot as plt
import numpy as np
import os
from tensor_generator import generate_field_tensor

# Création du dossier pour le Machine Learning
if not os.path.exists("dataset_byte_ndt"):
    os.makedirs("dataset_byte_ndt")

print("🚀 Byte NDT : Lancement de la génération du Dataset Tensoriel...")

# Simulation d'un balayage sectoriel pour l'IA (ex: de 10° à 60°)
angles = [10, 20, 30, 40, 45, 50, 60]

for ang in angles:
    tensor, yy, zz = generate_field_tensor(ang)
    
    # 1. Sauvegarde du TENSEUR BRUT (Format binaire NumPy)
    # C'est la "Vérité Terrain" pour l'IA et le FPGA
    np.save(f"dataset_byte_ndt/tensor_{ang}deg.npy", tensor)
    
    # 2. Sauvegarde de l'IMAGE (Pour l'humain et la formation)
    plt.figure(figsize=(8, 5))
    plt.imshow(np.abs(tensor), extent=[-30, 30, 40, 0], cmap='magma')
    plt.title(f"Byte NDT - Signature Acoustique ({ang} deg)")
    plt.axis('off')
    plt.savefig(f"dataset_byte_ndt/visual_{ang}deg.png")
    plt.close()
    
    print(f"✅ Angle {ang}° généré : Image + Tenseur enregistrés.")

print("\n📈 Dataset prêt. Route du Machine Learning ouverte.")