import streamlit as st
import requests
import os

# ---- Config ----
API_UPLOAD_URL = "http://127.0.0.1:8000/upload"
API_QUERY_URL = "http://127.0.0.1:8000/query"
UPLOAD_FOLDER = "uploaded_files"

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---- Streamlit Page Setup ----
st.set_page_config(page_title="Readalyzer", layout="centered")

# ---- Centered Title ----
st.markdown("<h1 style='text-align: center;'>Readalyzer</h1>", unsafe_allow_html=True)

# ---- Sidebar: Upload Documents ----
st.sidebar.header("Upload Documents")
uploaded_file = st.sidebar.file_uploader(
    "Upload a document (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"]
)

if uploaded_file:
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with open(file_path, "rb") as f:
        files = {"file": (uploaded_file.name, f)}
        upload_resp = requests.post(API_UPLOAD_URL, files=files)

    if upload_resp.status_code == 200:
        st.sidebar.success(f"{uploaded_file.name} uploaded and indexed!")
    else:
        st.sidebar.error(f"Failed to upload {uploaded_file.name}: {upload_resp.text}")

# ---- Chat UI ----
st.subheader("💬 Feel free to drop your question about the PDF")
user_query = st.text_input("Type your question:")

if st.button("Ask AI"):
    if not user_query:
        st.warning("Please enter a question.")
    else:
        try:
            response = requests.post(API_QUERY_URL, json={"query": user_query})
            if response.status_code == 200:
                answer = response.json().get("response", "No response available.")
                st.markdown(f"**AI Response:** {answer}")
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")
