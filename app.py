import streamlit as st
import os
from pathlib import Path
from src.pages import homePage
from src.pages import exploratoryDataAnalysis
from src.pages import playerAnalysis
from src.pages import batter_vs_bowlerAnalysis
from src.pages import teamAnalysis
from src.pages import team_vs_teamAnalysis
from src.pages import matches
from src.predictions import winnerPrediction
from src.predictions import scorePrediction

# Set up page config first (must be first Streamlit command)
st.set_page_config(
    page_title="IPL ANALYSIS",
    page_icon="",
    initial_sidebar_state="expanded",
    layout="wide",
)

# Bootstrap CSS
st.markdown(
    '''
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
    ''',
    unsafe_allow_html=True,
)

# Initialize session state for file download status
if 'files_checked' not in st.session_state:
    st.session_state.files_checked = False
if 'files_ready' not in st.session_state:
    st.session_state.files_ready = False

def check_and_download_files():
    if st.session_state.files_checked:
        return st.session_state.files_ready
    
    required_files = [
        'Datasets/deliveries_2008-2024.csv',
        'Model/winner_prediction_model.pkl'
    ]
    
    # Check if score model exists (either compressed or decompressed)
    score_model_exists = (
        os.path.exists('Model/predict_ipl_score_best_rf.pkl') or 
        os.path.exists('Model/predict_ipl_score_compressed.pkl.bz2')
    )
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if not score_model_exists:
        missing_files.append('Score prediction model')
    
    if missing_files:
        st.info(f" Setting up {len(missing_files)} files... This will take 3-4 minutes.")
        st.write(" Files needed:", missing_files)
        
        progress_placeholder = st.empty()
        progress_placeholder.info(" Downloading files...")
        
        try:
            # Only run download if we actually need files
            need_download = any(not os.path.exists(f) for f in required_files[:2])
            
            if need_download:
                from scripts.download_large_files import download_large_files
                download_large_files()
            
            # Handle score model decompression if compressed file exists
            if os.path.exists('Model/predict_ipl_score_compressed.pkl.bz2') and not os.path.exists('Model/predict_ipl_score_best_rf.pkl'):
                progress_placeholder.info(" Decompressing score model...")
                import bz2
                
                with bz2.open('Model/predict_ipl_score_compressed.pkl.bz2', 'rb') as f:
                    model_data = f.read()
                
                with open('Model/predict_ipl_score_best_rf.pkl', 'wb') as f:
                    f.write(model_data)
            
            progress_placeholder.success(" All files ready!")
            st.session_state.files_ready = True
            
        except Exception as e:
            progress_placeholder.error(f" Error during setup: {str(e)}")
            st.info("Please check if the Google Drive URLs are accessible.")
            st.session_state.files_ready = False
    else:
        st.session_state.files_ready = True
    
    st.session_state.files_checked = True
    return st.session_state.files_ready

# Pages that need data files
PAGES_NEEDING_FILES = {
    "Exploratory Data Analysis", 
    "Team Analysis", 
    "Team v/s Team", 
    "Batter v/s Bowler", 
    "Player Analysis", 
    "Match Scorecard",
    "Predict Score", 
    "Predict Win Probability"
}

PAGES = {
    "HOME": homePage,
    "Exploratory Data Analysis": exploratoryDataAnalysis,
    "Team Analysis": teamAnalysis,
    "Team v/s Team": team_vs_teamAnalysis,
    "Batter v/s Bowler": batter_vs_bowlerAnalysis,
    "Player Analysis": playerAnalysis,
    "Match Scorecard": matches,
    "Predict Score": scorePrediction,
    "Predict Win Probability": winnerPrediction
}

# Sidebar navigation
st.sidebar.title("NAVIGATION")
selection = st.sidebar.radio("Select a Page", list(PAGES.keys()))

# Show home page immediately, download files only when needed
if selection == "HOME":
    page = PAGES[selection]
    page.app()
elif selection in PAGES_NEEDING_FILES:
    # Check files only when user selects a page that needs them
    if check_and_download_files():
        page = PAGES[selection]
        page.app()
    else:
        st.error(" Files not ready. Please try refreshing the page.")
else:
    page = PAGES[selection]
    page.app()
