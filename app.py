import streamlit as st
import cv2
import os
import subprocess
import time

# --- STEP 1: AUTO-CONNECT TO TAILSCALE ---
def start_tailscale():
    auth_key = st.secrets["TAILSCALE_AUTHKEY"]
    if not os.path.exists("/dev/net/tun"):
        # This part handles the cloud environment setup
        subprocess.run(["sudo", "tailscale", "up", "--authkey", auth_key, "--hostname=streamlit-app"], check=True)

# Run tailscale connection once at start
try:
    start_tailscale()
except Exception as e:
    st.error(f"Tailscale Connection Failed: {e}")

# --- STEP 2: DASHBOARD UI ---
st.set_page_config(page_title="India SafeHome SaaS", layout="wide")
st.title("📹 Home Live Feed (Secure Tunnel)")

# Replace with your REAL internal camera IP
# Example: rtsp://username:password@192.168.1.10:554/stream1
RTSP_URL = st.sidebar.text_input("Camera RTSP Link", type="password")

if st.button("Start Monitor"):
    if not RTSP_URL:
        st.warning("Please enter your RTSP link in the sidebar.")
    else:
        st.success("Connected via Tailscale Tunnel")
        placeholder = st.empty()
        cap = cv2.VideoCapture(RTSP_URL)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                st.error("Lost connection to home camera.")
                break
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            placeholder.image(frame, channels="RGB", use_container_width=True)
            time.sleep(0.03) # Match FPS
