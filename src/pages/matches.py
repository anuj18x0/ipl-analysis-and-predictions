import pandas as pd
import streamlit as st
from ..analysis.datasetPreprocessing import load_matches_data, load_deliveries_data


def app():
    st.markdown(
        """
    <h1 style='text-align:center; color: #4ef037;'><strong> 🏏 MATCHES 🤾‍♂️ </strong></h1>
    <hr style="border-top: 3px solid #4ef037;">
    """,
        unsafe_allow_html=True,
    )
    # Load the data using the lazy loading functions
    matches = load_matches_data()
    deliveries = load_deliveries_data()

    # Streamlit App
    st.title("IPL Match Scorecard")

    # Filters for match selection
    years = [str(y) for y in range(2008, 2025)]  # Limit years to 2008-2024
    selected_year = st.selectbox("Select Year", years)

    # Filter matches based on year
    matches_year = matches[matches["season"] == int(selected_year)]
    teams = sorted(set(matches_year["team1"]).union(set(matches_year["team2"])))

    team1 = st.selectbox("Select Team 1", teams)
    team2 = st.selectbox("Select Team 2", [t for t in teams if t != team1])

    # Get matches between the selected teams
    match_info = matches_year[((matches_year["team1"] == team1) & (matches_year["team2"] == team2)) |
                            ((matches_year["team1"] == team2) & (matches_year["team2"] == team1))]

    if match_info.empty:
        st.warning("No match data available for the selected teams and year.")
        st.stop()

    # Allow user to select a match if multiple exist
    match_dates = match_info["date"].astype(str).unique()
    selected_match_date = st.selectbox("Select Match Date", match_dates)

    # Get the selected match details
    selected_match = match_info[match_info["date"].astype(str) == selected_match_date].iloc[0]
    match_id = selected_match["id"]
    match_date = selected_match["date"]
    team1_name = selected_match["team1"]
    team2_name = selected_match["team2"]

    # Filter deliveries for the selected match
    match_data = deliveries[deliveries["match_id"] == match_id]
    inning1 = match_data[match_data["inning"] == 1]
    inning2 = match_data[match_data["inning"] == 2]

    st.subheader("Player of the Match")
    st.write(selected_match["player_of_match"])

    # Function to calculate batting stats
    def batting_scorecard(df):
        batting = df.groupby("batter", sort=False).agg(
            Runs=("batsman_runs", "sum"),
            Balls=("batsman_runs", "count")
        ).reset_index()
        
        # Merge with dismissal info
        dismissals = df[df["player_dismissed"].notna()][["player_dismissed", "dismissal_kind"]]
        dismissals.columns = ["batter", "Dismissal"]
        
        batting = batting.merge(dismissals, on="batter", how="left")
        batting["Dismissal"].fillna("Not Out", inplace=True)
        
        batting["Strike Rate"] = (batting["Runs"] / batting["Balls"]) * 100
        return batting

    # Function to calculate bowling stats
    def bowling_scorecard(df):
        bowling = df.groupby("bowler").agg(
            Overs=("over", lambda x: len(set(x))),
            Runs=("total_runs", "sum"),
            Wickets=("is_wicket", "sum")
        ).reset_index()
        bowling["Economy"] = bowling["Runs"] / bowling["Overs"]
        return bowling

    # Function to get final score
    def get_final_score(df, team_name):
        if df.empty:
            return f"{team_name}: No data available"
        total_runs = df["total_runs"].sum()
        total_wickets = df["is_wicket"].sum()
        overs = df["over"].max() + 1
        return f"{team_name}: {total_runs}/{total_wickets} in {overs} Overs"

    st.header(f"{team1} vs {team2} ({selected_year}) - {match_date}")

    st.subheader("Final Scores")
    if not inning1.empty:
        st.write(get_final_score(inning1, team1_name))
    else:
        st.write(f"{team1_name}: No data available")
    if not inning2.empty:
        st.write(get_final_score(inning2, team2_name))
    else:
        st.write(f"{team2_name}: No data available")

    st.subheader("Batting Scorecard")
    if not inning1.empty:
        st.write(f"{team1_name}")
        st.dataframe(batting_scorecard(inning1))
    if not inning2.empty:
        st.write(f"{team2_name}")
        st.dataframe(batting_scorecard(inning2))

    st.subheader("Bowling Scorecard")
    if not inning1.empty:
        st.write(f"{team2_name}")
        st.dataframe(bowling_scorecard(inning1))
    if not inning2.empty:
        st.write(f"{team1_name}")
        st.dataframe(bowling_scorecard(inning2))