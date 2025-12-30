import subprocess
import threading
import time
import os
import signal
import requests
from dotenv import load_dotenv
import streamlit as st
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from python_server.database import engine, MessageLog, get_db
from python_server.config import Config

# Load environment variables
load_dotenv()
default_key = os.getenv("BARK_DEVICE_KEY", "")

# Global process handle
process = None
process_lock = threading.Lock()

def start_server():
    global process
    with process_lock:
        if process is None or process.poll() is not None:
            # Start uvicorn server in a subprocess
            # We don't pipe stdout/stderr so logs show up in the terminal for debugging
            cmd = ["python", "-m", "uvicorn", "python_server.main:app", "--host", Config.HOST, "--port", str(Config.PORT)]
            process = subprocess.Popen(cmd)
            
            # Wait a moment to see if it crashes immediately (e.g., port already in use)
            time.sleep(2)
            if process.poll() is not None:
                st.error("Bark server failed to start. Check your terminal for errors (is port 8080 already in use?)")
                process = None
            else:
                st.success("Bark server started.")
        else:
            st.info("Server is already running.")

def stop_server():
    global process
    with process_lock:
        if process and process.poll() is None:
            # Terminate the process gracefully
            if os.name == "nt":
                subprocess.call(["taskkill", "/F", "/T", "/PID", str(process.pid)])
            else:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            process.wait()
            st.success("Bark server stopped.")
            process = None
        else:
            st.info("Server is not running.")

def get_logs(limit: int = 100):
    Session = sessionmaker(bind=engine)
    with Session() as session:
        logs = session.query(MessageLog).order_by(MessageLog.id.desc()).limit(limit).all()
        return logs

st.title("Bark Server Control Panel")
col1, col2 = st.columns(2)
with col1:
    if st.button("Start Server"):
        start_server()
with col2:
    if st.button("Stop Server"):
        stop_server()

# README download
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "rb") as f:
        st.download_button(
            label="Download README.md",
            data=f,
            file_name="README.md",
            mime="text/markdown"
        )
else:
    st.warning("README.md not found.")

st.divider()

st.subheader("Send Notification")
with st.form("send_push_form"):
    push_key = st.text_input("Device Key", value=default_key)
    push_title = st.text_input("Title", value="Bark")
    push_body = st.text_area("Body", placeholder="Enter your message here...")
    
    submitted = st.form_submit_button("Send Push")
    if submitted:
        if not push_key or not push_body:
            st.error("Device Key and Body are required.")
        else:
            try:
                # Use localhost if host is 0.0.0.0 (Windows client fix)
                target_host = Config.HOST if Config.HOST != "0.0.0.0" else "127.0.0.1"
                url = f"http://{target_host}:{Config.PORT}/{push_key}/{push_title}/{push_body}"
                
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    st.success("Notification sent successfully!")
                else:
                    st.error(f"Failed to send: {response.text}")
            except Exception as e:
                st.error(f"Error connecting to server: {e}")

st.subheader("Message Log")
log_limit = st.slider("Number of entries to show", min_value=10, max_value=200, value=50, step=10)
logs = get_logs(log_limit)
if logs:
    # Prepare data for display
    data = [{
        "ID": log.id,
        "Timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log.timestamp)),
        "Device Key": log.device_key,
        "Title": log.title,
        "Body": log.body,
        "Status": log.status,
    } for log in logs]
    st.table(data)
else:
    st.info("No logs available.")

st.divider()

st.subheader("Raw Event Logs (log.log)")
log_file = Path(Config.PROJECT_ROOT) / "log.log"
st.code(f"Log File Path: {log_file.absolute()}")

if log_file.exists():
    with open(log_file, "r", encoding="utf-8") as f:
        # Read last 100 lines
        lines = f.readlines()
        last_lines = lines[-100:]
        st.text_area("Last 100 lines", value="".join(last_lines), height=300)
    
    with open(log_file, "rb") as f:
        st.download_button(
            label="Download log.log",
            data=f,
            file_name="log.log",
            mime="text/plain"
        )
else:
    st.warning("log.log file not found yet. It will be created once the server starts logging events.")
