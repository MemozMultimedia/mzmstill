
import streamlit as st
import cv2

import numpy as np
import tempfile
import zipfile
import os
import base64
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="MZM Stillz Pro", layout="wide")

# ✨ LUXURY MODERN UI WITH GLOW EFFECTS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

.stApp { background: #050508 !important; color: #f0f0f0; font-family: 'Inter', sans-serif; }

/* Fix Logo Space */
.main-header { 
    display: flex; 
    flex-direction: column; 
    align-items: center; 
    padding-top: 40px; 
    margin-bottom: 25px; 
}

.block-container { padding-top: 0rem !important; }

.card { 
    background: rgba(255, 255, 255, 0.02); 
    border: 1px solid rgba(255, 255, 255, 0.05); 
    border-radius: 12px; 
    padding: 15px; 
    margin-bottom: 15px; 
}

.img-container { 
    border-radius: 8px; 
    overflow: hidden; 
    border: 1px solid rgba(255,255,255,0.05); 
    background: #000; 
    margin-bottom: 12px; 
}

/* GLOSSY GLOW BUTTONS */
.download-btn { 
    display: inline-block; 
    padding: 8px 12px; 
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%); 
    color: #fff !important; 
    text-decoration: none !important; 
    border-radius: 8px; 
    font-size: 0.85rem; 
    font-weight: 600;
    text-align: center; 
    width: 100%; 
    border: 1px solid rgba(255,255,255,0.1);
    transition: 0.3s all ease; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    position: relative;
    overflow: hidden;
}

.download-btn:hover { 
    background: rgba(255,255,255,0.2); 
    border-color: rgba(255,255,255,0.5);
    box-shadow: 0 0 20px rgba(255,255,255,0.15); 
    transform: translateY(-2px);
}

.download-btn::after {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
    transform: rotate(45deg);
    transition: 0.5s;
}

.download-btn:hover::after {
    left: 100%;
}

.stButton>button {
    background: white !important;
    color: black !important;
    font-weight: 800 !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 0.6rem !important;
}
</style>
""", unsafe_allow_html=True)

# FUNCTIONS
def get_sharpness(img):
    return cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()

def get_image_download_link(img, filename, text):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="{filename}" class="download-btn">{text}</a>'
    return href

# HEADER
st.markdown('<div class="main-header">', unsafe_allow_html=True)
if os.path.exists("MZM.PNG"): st.image("MZM.PNG", width=120)
st.markdown('<h1 style="font-size: 2.8rem; margin:0; letter-spacing:-1.5px; font-weight:800;">MZM Stillz</h1>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# UI
uploaded_file = st.file_uploader("", type=["mov","mp4","avi"], label_visibility="collapsed")

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    
    c1, c2 = st.columns([1.2, 1])
    with c1: 
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.video(tfile.name)
        # Recognizable Full Screen Button using built-in Streamlit functionality or CSS hint
        st.caption("Tip: 📺 Use the control bar above for Full Screen.")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        num = st.slider("Stills Density", 4, 32, 12)
        if st.button("⚡ GENERATE MASTER STILLS", use_container_width=True):
            with st.status("Neural Processing...", expanded=False):
                cap = cv2.VideoCapture(tfile.name)
                frames, scores = [], []
                count = 0
                while True:
                    ret, frame = cap.read()
                    if not ret: break
                    if count % 8 == 0:
                        frames.append(frame)
                        scores.append(get_sharpness(frame))
                    count += 1
                cap.release()
                idx = np.argsort(scores)[-num:]
                st.session_state['stills'] = [frames[i] for i in idx]
                st.session_state['file_name'] = os.path.splitext(uploaded_file.name)[0]
        st.markdown('</div>', unsafe_allow_html=True)

if 'stills' in st.session_state:
    st.markdown("--- ")
    zip_path = f"{st.session_state['file_name']}_mzm.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        for i, f in enumerate(st.session_state['stills']):
            p = f"frame_{i}.png"; cv2.imwrite(p, f); z.write(p); os.remove(p)
    
    with open(zip_path, "rb") as f:
        st.download_button("📥 DOWNLOAD COMPLETE PACKAGE (ZIP)", f, file_name=zip_path, type="primary", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, frame in enumerate(st.session_state['stills']):
        with cols[i % 4]:
            st.markdown('<div class="img-container">', unsafe_allow_html=True)
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            st.image(pil_img, use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown(get_image_download_link(pil_img, f"still_{i}.png", f"⤓ Still {i+1}"), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
