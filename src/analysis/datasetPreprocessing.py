import pandas as pd
import os

# Global variables for cached data
_matches_df = None
_deliveries_df = None

def ensure_large_files_exist():
    """Ensure large files are downloaded before loading data"""
    # Note: Score model is now in Git LFS, only CSV and winner model need downloading
    if not os.path.exists("Datasets/deliveries_2008-2024.csv") or not os.path.exists("Model/winner_prediction_model.pkl"):
        print("📥 Downloading large files...")
        from scripts.download_large_files import download_large_files
        download_large_files()

def load_matches_data():
    """Load and preprocess matches data (lazy loading)"""
    global _matches_df
    if _matches_df is None:
        ensure_large_files_exist()
        print("📊 Loading matches data...")
        _matches_df = pd.read_csv("Datasets/matches_2008-2024.csv")
        _matches_df.columns = _matches_df.columns.str.strip()
        _matches_df = trimSpaceInValues(_matches_df)
        _matches_df = latest_teams(_matches_df, ['team1', 'team2', 'winner'])
        unique_stadium(_matches_df)
    return _matches_df

def load_deliveries_data():
    """Load and preprocess deliveries data (lazy loading)"""
    global _deliveries_df
    if _deliveries_df is None:
        ensure_large_files_exist()
        print("🏏 Loading deliveries data...")
        _deliveries_df = pd.read_csv("Datasets/deliveries_2008-2024.csv")
        _deliveries_df.columns = _deliveries_df.columns.str.strip()
        _deliveries_df = trimSpaceInValues(_deliveries_df)
        _deliveries_df = latest_teams(_deliveries_df, ['batting_team', 'bowling_team'])
        
        # Replacing the empty values in the 'extra_types' with 'None' when it is normal deliveries
        _deliveries_df.loc[_deliveries_df["extras_type"].str.strip() == "", "extras_type"] = "None"
    return _deliveries_df

# Public interface (backward compatibility)
def get_matches_data():
    return load_matches_data()

def get_deliveries_data():
    return load_deliveries_data()

# For backward compatibility with existing code
@property 
def new_matchesDF():
    return load_matches_data()

@property
def new_deliveriesDF():
    return load_deliveries_data()


# Updating the team names
def latest_teams(df, cols):
    # mapping old to latest
    team_name_map = {
        "Deccan Chargers": "Sunrisers Hyderabad",
        "Delhi Daredevils": "Delhi Capitals",
        "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
        "Punjab Kings": "Kings XI Punjab",
        "Rising Pune Supergiants": "Rising Pune Supergiant",
    }

    # Replace old team names with the latest names
    for col in cols:
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not found in DataFrame")
        df[col] = df[col].replace(team_name_map)

    return df


# Updating the venue names
def unique_stadium(matches_df):
    venue_map = {
        "Arun Jaitley Stadium, Delhi": "Arun Jaitley Stadium",
        "Brabourne Stadium, Mumbai": "Brabourne Stadium",
        "Dr DY Patil Sports Academy, Mumbai": "Dr DY Patil Sports Academy",
        "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam": "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium",
        "Eden Gardens, Kolkata": "Eden Gardens",
        "Himachal Pradesh Cricket Association Stadium, Dharamsala": "Himachal Pradesh Cricket Association Stadium",
        "M.Chinnaswamy Stadium": "M Chinnaswamy Stadium",
        "M Chinnaswamy Stadium, Bengaluru": "M Chinnaswamy Stadium",
        "M Chinnaswamy Stadium, Bengalore": "M Chinnaswamy Stadium",
        "MA Chidambaram Stadium, Chepauk": "MA Chidambaram Stadium",
        "MA Chidambaram Stadium, Chepauk, Chennai": "MA Chidambaram Stadium",
        "Maharashtra Cricket Association Stadium, Pune": "Maharashtra Cricket Association Stadium",
        "Punjab Cricket Association Stadium, Mohali": "Punjab Cricket Association IS Bindra Stadium",
        "Punjab Cricket Association IS Bindra Stadium": "Punjab Cricket Association IS Bindra Stadium",
        "Punjab Cricket Association IS Bindra Stadium, Mohali": "Punjab Cricket Association IS Bindra Stadium",
        "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh": "Punjab Cricket Association IS Bindra Stadium",
        "Rajiv Gandhi International Stadium, Uppal": "Rajiv Gandhi International Stadium",
        "Rajiv Gandhi International Stadium, Uppal, Hyderabad": "Rajiv Gandhi International Stadium",
        "Sawai Mansingh Stadium, Jaipur": "Sawai Mansingh Stadium",
        "Wankhede Stadium, Mumbai": "Wankhede Stadium",
    }
    matches_df["venue"] = matches_df["venue"].replace(venue_map)


def trimSpaceInValues(df):
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].str.strip()
    return df


# Note: Data is now loaded lazily through functions above.
# This ensures files are downloaded before loading during cloud deployment.
