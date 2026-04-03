import streamlit as st
from tensor_generator import generate_field_tensor
import matplotlib.pyplot as plt
import numpy as np

st.title("Byte NDT - Visualiseur 1D")
angle = st.slider("Angle de tir", 0, 70, 20)

if st.button("Générer le faisceau"):
    tensor, yy, zz = generate_field_tensor(angle)
    fig, ax = plt.subplots()
    ax.imshow(np.abs(tensor), extent=[-30, 30, 40, 0], cmap='hot')
    st.pyplot(fig)