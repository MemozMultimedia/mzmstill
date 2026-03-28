
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

# ✨ ULTRA-MODERN PRODUCTIVITY UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

.stApp { background: #050508 !important; color: #f0f0f0; font-family: 'Inter', sans-serif; }

/* Compact Header */
.main-header { display: flex; flex-direction: column; align-items: center; margin-bottom: 15px; }
.block-container { padding-top: 1rem !important; }

/* Productivity Cards */
.card { 
    background: rgba(255, 255, 255, 0.02); 
    border: 1px solid rgba(255, 255, 255, 0.05); 
    border-radius: 12px; 
    padding: 15px; 
    margin-bottom: 10px; 
}

/* Modern Image Grid */
.img-container { 
    border-radius: 8px; 
    overflow: hidden; 
    border: 1px solid rgba(255,255,255,0.1); 
    background: #000; 
    margin-bottom: 10px; 
    transition: 0.3s; 
}
.img-container:hover { border-color: #fff; transform: translateY(-2px); }

/* Glassmorphism Buttons */
.stButton>button { 
    border-radius: 6px !important; 
    font-weight: 600 !important; 
    transition: 0.2s; 
}
.download-btn { 
    display: inline-block; 
    padding: 5px 10px; 
    background: rgba(255,255,255,0.1); 
    color: #fff; 
    text-decoration: none; 
    border-radius: 4px; 
    font-size: 0.8rem; 
    text-align: center; 
    width: 100%; 
}
.download-btn:hover { background: #fff; color: #000; }
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
if os.path.exists("MZM.PNG"): st.image("MZM.PNG", width=100)
st.markdown('<h1 style="font-size: 2rem; margin:0; letter-spacing:-1px; font-weight:800;">MZM Stillz</h1>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# WORKFLOW
uploaded_file = st.file_uploader("", type=["mov","mp4","avi"], label_visibility="collapsed")

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    
    c1, c2 = st.columns([1.2, 1])
    with c1: 
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.video(tfile.name)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        num = st.slider("Density", 4, 32, 12)
        if st.button("EXTRACT MASTER STILLS", use_container_width=True):
            with st.status("Scanning Optics...", expanded=False):
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
    st.subheader("🖼 Selection Library")
    
    # Package Download
    zip_path = f"{st.session_state['file_name']}_stills.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        for i, f in enumerate(st.session_state['stills']):
            p = f"frame_{i}.png"
            cv2.imwrite(p, f)
            z.write(p)
            os.remove(p)
    
    with open(zip_path, "rb") as f:
        st.download_button("📦 DOWNLOAD ALL (ZIP)", f, file_name=zip_path, type="primary", use_container_width=True)

    # Image List / Grid
    cols = st.columns(4)
    for i, frame in enumerate(st.session_state['stills']):
        with cols[i % 4]:
            st.markdown('<div class="img-container">', unsafe_allow_html=True)
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            st.image(pil_img, use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            # Individual Download
            st.markdown(get_image_download_link(pil_img, f"still_{i}.png", f"⤓ Still {i+1}"), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
