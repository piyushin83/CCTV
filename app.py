import streamlit as st
import cv2
import os
import subprocess
import requests
import tarfile

# --- TAILSCALE MANUAL INSTALLER (Bypasses packages.txt errors) ---
def setup_tailscale():
    auth_key = st.secrets["TAILSCALE_AUTHKEY"]
    
    # Check if tailscale is already running
    if os.path.exists("/tmp/tailscaled.sock"):
        return

    st.info("Setting up secure tunnel...")
    
    # Download Tailscale binary directly
    ts_version = "1.56.1" # Stable version
    url = f"https://pkgs.tailscale.com/stable/tailscale_{ts_version}_amd64.tgz"
    
    if not os.path.exists("tailscale"):
        r = requests.get(url, stream=True)
        with open("ts.tgz", "wb") as f:
            f.write(r.raw.read())
        with tarfile.open("ts.tgz") as tar:
            tar.extractall()
        # Move binaries to a simpler path
        os.rename(f"tailscale_{ts_version}_amd64", "ts_bin")

    # Start Tailscale Daemon in background
    subprocess.Popen(["./ts_bin/tailscaled", "--tun=userspace-networking", "--socks5-server=localhost:1055"])
    
    # Connect to your network
    subprocess.run(["./ts_bin/tailscale", "up", "--authkey", auth_key, "--hostname=streamlit-cloud-app"], check=True)
    st.success("Tunnel Active!")

# Try to connect
try:
    if "TAILSCALE_AUTHKEY" in st.secrets:
        setup_tailscale()
except Exception as e:
    st.error(f"Tunnel Error: {e}")

# --- MAIN APP ---
st.title("📹 India SafeHome CCTV")
rtsp_url = st.sidebar.text_input("Enter Home RTSP (e.g. rtsp://192.168.1.10...)", type="password")

if rtsp_url:
    cap = cv2.VideoCapture(rtsp_url)
    frame_placeholder = st.empty()
    while True:
        ret, frame = cap.read()
        if not ret:
            st.warning("Waiting for stream...")
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame, channels="RGB")
