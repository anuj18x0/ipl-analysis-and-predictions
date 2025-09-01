import streamlit as st
import os
import sys

# Simple diagnostic page to debug deployment issues
st.title(" Deployment Diagnostics")

st.write("## System Information")
st.write(f"Python version: {sys.version}")
st.write(f"Current working directory: {os.getcwd()}")

st.write("## File Structure Check")
required_paths = [
    'src/',
    'src/pages/',
    'src/predictions/',
    'scripts/',
    'Model/',
    'Datasets/'
]

for path in required_paths:
    if os.path.exists(path):
        st.success(f" {path} exists")
    else:
        st.error(f" {path} missing")

st.write("## Environment Variables")
env_vars = ['DELIVERIES_CSV_URL', 'SCORE_MODEL_COMPRESSED_URL', 'WINNER_MODEL_URL']
for var in env_vars:
    value = os.getenv(var, 'NOT SET')
    if value != 'NOT SET':
        st.success(f" {var}: {value[:50]}...")
    else:
        st.warning(f" {var}: {value}")

st.write("## Import Test")
try:
    from src.pages import homePage
    st.success(" src.pages.homePage imported successfully")
except Exception as e:
    st.error(f" Import error: {str(e)}")

try:
    from scripts.download_large_files import download_large_files
    st.success(" scripts.download_large_files imported successfully")
except Exception as e:
    st.error(f" Import error: {str(e)}")

st.write("## Ready for main app!")
