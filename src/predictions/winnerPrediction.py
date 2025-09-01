import pickle
import pandas as pd
import streamlit as st
import numpy as np


def app():
    st.markdown('''
    <h1 style='text-align:center; color: #700961;'><strong> 🎲 PREDICTING WIN PROBABILITY FOR A TEAM 🎲</strong></h1>
    <hr style="border-top: 3px solid #700961;">
    ''', unsafe_allow_html=True)

    TEAMS = [
        'Chennai Super Kings',
        'Kolkata Knight Riders', 
        'Punjab Kings',
        'Delhi Capitals',
        'Rajasthan Royals',
        'Sunrisers Hyderabad',
        'Mumbai Indians',
        'Royal Challengers Bengaluru',
        'Lucknow Super Giants',
        'Gujarat Titans'
    ]

    VENUES = [
        'M Chinnaswamy Stadium',
        'Punjab Cricket Association Stadium, Mohali',
        'Feroz Shah Kotla',
        'Wankhede Stadium',
        'Eden Gardens',
        'Sawai Mansingh Stadium',
        'Rajiv Gandhi International Stadium, Uppal',
        'MA Chidambaram Stadium, Chepauk',
        'Dr DY Patil Sports Academy',
        'Newlands',
        "St George's Park",
        'Kingsmead',
        'SuperSport Park',
        'Buffalo Park',
        'New Wanderers Stadium',
        'De Beers Diamond Oval',
        'OUTsurance Oval',
        'Brabourne Stadium',
        'Sardar Patel Stadium, Motera',
        'Barabati Stadium',
        'Brabourne Stadium, Mumbai',
        'Vidarbha Cricket Association Stadium, Jamtha',
        'Himachal Pradesh Cricket Association Stadium',
        'Nehru Stadium',
        'Holkar Cricket Stadium',
        'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium',
        'Subrata Roy Sahara Stadium',
        'Maharashtra Cricket Association Stadium',
        'Shaheed Veer Narayan Singh International Stadium',
        'JSCA International Stadium Complex',
        'Sheikh Zayed Stadium',
        'Sharjah Cricket Stadium',
        'Dubai International Cricket Stadium',
        'Punjab Cricket Association IS Bindra Stadium, Mohali',
        'Saurashtra Cricket Association Stadium',
        'Green Park',
        'M.Chinnaswamy Stadium',
        'Punjab Cricket Association IS Bindra Stadium',
        'Rajiv Gandhi International Stadium',
        'MA Chidambaram Stadium',
        'Arun Jaitley Stadium',
        'MA Chidambaram Stadium, Chepauk, Chennai',
        'Wankhede Stadium, Mumbai',
        'Narendra Modi Stadium, Ahmedabad',
        'Arun Jaitley Stadium, Delhi',
        'Zayed Cricket Stadium, Abu Dhabi',
        'Dr DY Patil Sports Academy, Mumbai',
        'Maharashtra Cricket Association Stadium, Pune',
        'Eden Gardens, Kolkata',
        'Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh',
        'Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow',
        'Rajiv Gandhi International Stadium, Uppal, Hyderabad',
        'M Chinnaswamy Stadium, Bengaluru',
        'Barsapara Cricket Stadium, Guwahati',
        'Sawai Mansingh Stadium, Jaipur',
        'Himachal Pradesh Cricket Association Stadium, Dharamsala',
        'Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur',
        'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam'
    ]

    # Load historical data for calculating head-to-head and bat/bowl first stats
    try:
        matches_df = pd.read_csv('Datasets/matches_2008-2024.csv')
        
        # Apply same preprocessing as training
        team_name_map = {
            'Delhi Daredevils': 'Delhi Capitals',
            'Deccan Chargers': 'Sunrisers Hyderabad',
            'Kings XI Punjab': 'Punjab Kings',
            'Rising Pune Supergiants': 'Rising Pune Supergiant',
            'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
        }
        for col in ['team1', 'team2', 'toss_winner', 'winner']:
            matches_df[col] = matches_df[col].replace(team_name_map)
        
        matches_df = matches_df[(matches_df['team1'].isin(TEAMS)) & (matches_df['team2'].isin(TEAMS))]
        matches_df = matches_df[matches_df['winner'].isin(TEAMS)]
        matches_df = matches_df.dropna(subset=['winner'])
        matches_df = matches_df[matches_df['result'] != 'tie']
        matches_df = matches_df[matches_df['result'] != 'no result']
        
    except FileNotFoundError:
        st.error("Datasets/matches_2008-2024.csv not found!")
        return

    # Load Saved Model
    try:
        with open('Model/winner_prediction_model.pkl', 'rb') as f:
            model, feature_columns, team_labels = pickle.load(f)
    except FileNotFoundError:
        st.error("Winner prediction model not found! Please train the model first by running winner_model_train.py")
        return
    except (ValueError, pickle.UnpicklingError) as e:
        # Fallback for older model format or corrupted file
        try:
            with open('winner_prediction_model.pkl', 'rb') as f:
                model, feature_columns = pickle.load(f)
            team_labels = None
        except (FileNotFoundError, pickle.UnpicklingError):
            st.error(f"Error loading winner prediction model: {str(e)}")
            st.info("The model file may be corrupted or incompatible. Please retrain the model.")
            return

    # Home ground mapping
    team_home_venues = {
        'Chennai Super Kings': ['MA Chidambaram Stadium, Chepauk', 'MA Chidambaram Stadium, Chepauk, Chennai', 'MA Chidambaram Stadium'],
        'Mumbai Indians': ['Wankhede Stadium', 'Wankhede Stadium, Mumbai', 'Dr DY Patil Sports Academy', 'Dr DY Patil Sports Academy, Mumbai', 'Brabourne Stadium', 'Brabourne Stadium, Mumbai'],
        'Royal Challengers Bengaluru': ['M Chinnaswamy Stadium', 'M.Chinnaswamy Stadium', 'M Chinnaswamy Stadium, Bengaluru'],
        'Kolkata Knight Riders': ['Eden Gardens', 'Eden Gardens, Kolkata'],
        'Delhi Capitals': ['Feroz Shah Kotla', 'Arun Jaitley Stadium', 'Arun Jaitley Stadium, Delhi'],
        'Rajasthan Royals': ['Sawai Mansingh Stadium', 'Sawai Mansingh Stadium, Jaipur'],
        'Punjab Kings': ['Punjab Cricket Association Stadium, Mohali', 'Punjab Cricket Association IS Bindra Stadium, Mohali', 'Punjab Cricket Association IS Bindra Stadium', 'Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh', 'Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur'],
        'Sunrisers Hyderabad': ['Rajiv Gandhi International Stadium, Uppal', 'Rajiv Gandhi International Stadium', 'Rajiv Gandhi International Stadium, Uppal, Hyderabad', 'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium', 'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam'],
        'Lucknow Super Giants': ['Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow'],
        'Gujarat Titans': ['Narendra Modi Stadium, Ahmedabad', 'Sardar Patel Stadium, Motera']
    }

    # Helper functions for calculating features
    def calculate_h2h_winrate(team1, team2, matches_df):
        """Calculate team1's win rate against team2"""
        h2h_matches = matches_df[
            ((matches_df['team1'] == team1) & (matches_df['team2'] == team2)) |
            ((matches_df['team1'] == team2) & (matches_df['team2'] == team1))
        ]
        if len(h2h_matches) == 0:
            return 0.5
        team1_wins = len(h2h_matches[h2h_matches['winner'] == team1])
        return team1_wins / len(h2h_matches)

    def calculate_bat_first_winrate(team, matches_df):
        """Calculate team's win rate when batting first"""
        bat_first_matches = matches_df[matches_df['team1'] == team]
        if len(bat_first_matches) == 0:
            return 0.5
        wins = len(bat_first_matches[bat_first_matches['winner'] == team])
        return wins / len(bat_first_matches)

    def calculate_bowl_first_winrate(team, matches_df):
        """Calculate team's win rate when bowling first"""
        bowl_first_matches = matches_df[matches_df['team2'] == team]
        if len(bowl_first_matches) == 0:
            return 0.5
        wins = len(bowl_first_matches[bowl_first_matches['winner'] == team])
        return wins / len(bowl_first_matches)

    # Team Selection
    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox('Team 1', TEAMS)
    with col2:
        team2 = st.selectbox('Team 2', TEAMS)

    if team1 == team2:
        st.error("Team 1 and Team 2 Can't Be Same")
        return

    # Match Details
    col3, col4 = st.columns(2)
    with col3:
        toss_winner = st.selectbox('Toss Winner', [team1, team2])
    with col4:
        toss_decision = st.selectbox('Toss Decision', ['bat', 'field'])

    venue = st.selectbox('Venue', VENUES)
    season = st.number_input('Season (Year)', min_value=2008, max_value=2024, value=2024)

    # Calculate features
    team1_is_home = 1 if venue in team_home_venues.get(team1, []) else 0
    team2_is_home = 1 if venue in team_home_venues.get(team2, []) else 0
    has_home_advantage = 1 if (team1_is_home or team2_is_home) else 0
    
    team1_h2h_winrate = calculate_h2h_winrate(team1, team2, matches_df)
    team1_bat_first_winrate = calculate_bat_first_winrate(team1, matches_df)
    team2_bowl_first_winrate = calculate_bowl_first_winrate(team2, matches_df)

    # Show additional info
    if team1_is_home:
        st.success(f"🏠 **{team1}** has home advantage")
    elif team2_is_home:
        st.info(f"🏠 **{team2}** has home advantage")
    else:
        st.warning("⚪ Neutral venue")
    
    st.metric("Head-to-Head Record", f"{team1}: {team1_h2h_winrate:.1%} vs {team2}: {1-team1_h2h_winrate:.1%}")

    # Create input data for prediction
    input_data = {
        'team1': team1,
        'team2': team2,
        'toss_winner': toss_winner,
        'toss_decision': toss_decision,
        'venue': venue,
        'season': season,
        'toss_winner_is_winner': 0,  # Will be calculated later
        'team1_is_home': team1_is_home,
        'team2_is_home': team2_is_home,
        'has_home_advantage': has_home_advantage,
        'is_recent_season': 1 if season >= 2019 else 0,
        'team1_h2h_winrate': team1_h2h_winrate,
        'team1_bat_first_winrate': team1_bat_first_winrate,
        'team2_bowl_first_winrate': team2_bowl_first_winrate
    }

    # Create DataFrame
    input_df = pd.DataFrame([input_data])
    
    # One-hot encode to match training data format
    input_encoded = pd.get_dummies(input_df, columns=['team1', 'team2', 'toss_winner', 'toss_decision', 'venue'])
    
    # Align with training features
    for col in feature_columns:
        if col not in input_encoded.columns:
            input_encoded[col] = 0
    
    # Ensure same column order as training
    input_encoded = input_encoded.reindex(columns=feature_columns, fill_value=0)

    st.write('---')
    
    # Generate Predictions
    if st.button("Predict Win Probability"):
        try:
            # Get probabilities
            probabilities = model.predict_proba(input_encoded)[0]
            prediction = model.predict(input_encoded)[0]
            
            # Create probability display
            st.subheader("🏆 Win Probabilities:")
            
            # Method 1: If we have team_labels, use them
            if team_labels is not None:
                prob_dict = {}
                for i, prob in enumerate(probabilities):
                    if i < len(team_labels):
                        prob_dict[team_labels[i]] = prob
                
                # Get probabilities for selected teams
                team1_prob = prob_dict.get(team1, 0)
                team2_prob = prob_dict.get(team2, 0)
                
                # If either team probability is 0, it means the team wasn't in training data
                if team1_prob == 0 and team2_prob == 0:
                    st.error("Neither team found in model training data!")
                    return
                
                # Normalize probabilities to sum to 1 for the two teams
                total_prob = team1_prob + team2_prob
                if total_prob > 0:
                    team1_prob = team1_prob / total_prob
                    team2_prob = team2_prob / total_prob
                else:
                    team1_prob = team2_prob = 0.5
                    
            else:
                # Method 2: Fallback - assume binary classification
                if len(probabilities) == 2:
                    team1_prob = probabilities[0]
                    team2_prob = probabilities[1]
                else:
                    # Multi-class - use the highest probabilities
                    sorted_probs = sorted(enumerate(probabilities), key=lambda x: x[1], reverse=True)
                    team1_prob = sorted_probs[0][1]
                    team2_prob = sorted_probs[1][1] if len(sorted_probs) > 1 else 0
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label=f"🏏 {team1}",
                    value=f"{team1_prob:.1%}"
                )
            
            with col2:
                st.metric(
                    label=f"🏏 {team2}",
                    value=f"{team2_prob:.1%}"
                )
            
            # Show winner
            if team1_prob > team2_prob:
                st.success(f"🥇 **{team1}** is predicted to win with {team1_prob:.1%} probability!")
                winner_confidence = team1_prob - team2_prob
            else:
                st.success(f"🥇 **{team2}** is predicted to win with {team2_prob:.1%} probability!")
                winner_confidence = team2_prob - team1_prob
            
            # Confidence indicator
            if winner_confidence > 0.3:
                st.info("🔥 High confidence prediction!")
            elif winner_confidence > 0.1:
                st.warning("⚖️ Moderate confidence prediction")
            else:
                st.error("🤔 Low confidence - very close match!")
            
            # Bar chart
            chart_data = pd.DataFrame({
                'Team': [team1, team2],
                'Win Probability': [team1_prob, team2_prob]
            })
            st.bar_chart(chart_data.set_index('Team'))
            
            # Additional insights
            st.subheader("📊 Match Insights:")
            
            st.metric("Batting First Win Rate", f"{team1}: {team1_bat_first_winrate:.1%}")
            
            st.metric("Bowling First Win Rate", f"{team2}: {team2_bowl_first_winrate:.1%}")
            
            toss_impact = "Advantage" if toss_winner == (team1 if team1_prob > team2_prob else team2) else "Disadvantage"
            st.metric("Toss Impact", f"Toss winner has {toss_impact}")
                
        except Exception as e:
            st.error(f"Prediction error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
