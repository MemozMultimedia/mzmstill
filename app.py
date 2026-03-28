
import streamlit as st
import cv2
import numpy as np
import tempfile
import zipfile
import os
from PIL import Image

st.set_page_config(page_title="MZM Stillz Pro", layout="wide")

# CSS
st.markdown("""
<style>
.stApp { background: #050505; color: white; }
.logo-container { display: flex; justify-content: center; padding: 20px; }
.centered-text { text-align: center; }
</style>
""", unsafe_allow_html=True)

# Centered Logo
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
if os.path.exists("MZM.PNG"):
    st.image("MZM.PNG", width=200)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<h1 class="centered-text">MZM Stillz</h1>', unsafe_allow_html=True)

# Rest of the app logic...
uploaded_file = st.file_uploader("", type=["mov","mp4","avi"])
if uploaded_file:
    st.video(uploaded_file)
