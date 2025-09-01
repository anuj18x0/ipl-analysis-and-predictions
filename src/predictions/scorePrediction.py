import pickle
import pandas as pd
import streamlit as st


def app():
    st.markdown('''
    <h1 style='text-align:center; color: #ffcd19;'><strong>💠 SCORE PREDICTION FOR THE 1st INNING 💠</strong></h1>
    <hr style="border-top: 3px solid #ffcd19;">
    ''', unsafe_allow_html=True)

    # Load Saved Model - now uses decompressed model
    try:
        model = pickle.load(open('Model/predict_ipl_score_best_rf.pkl', 'rb'))
    except (FileNotFoundError, pickle.UnpicklingError) as e:
        st.error(f"❌ Score prediction model not available")
        st.info("📦 The model is being downloaded and decompressed. This feature will be available once the process completes.")
        st.warning("⚡ Try other features like Winner Prediction, Team Analysis, or Player Analysis in the meantime!")
        return

    TEAMS = ['Chennai Super Kings', 'Delhi Capitals', 'Kings XI Punjab',
             'Kolkata Knight Riders', 'Mumbai Indians', 'Rajasthan Royals',
             'Royal Challengers Bangalore', 'Sunrisers Hyderabad', 'Gujarat Titans', 'Lucknow Super Giants']

    # Batting Team & Bowling Team
    col1, col2 = st.columns(2)
    with col1:
        batting_team = st.selectbox('Batting Team At The Moment', TEAMS)
    with col2:
        bowling_team = st.selectbox('Bowling Team At The Moment', TEAMS)

    if bowling_team == batting_team:
        st.error("Bowling and Batting Team Can't Be Same")
    else:

        encoded_batting_team = [1 if batting_team ==
                                TEAM else 0 for TEAM in TEAMS]
        encoded_bowling_team = [1 if bowling_team ==
                                TEAM else 0 for TEAM in TEAMS]

        # Current Runs
        current_runs = st.number_input('Enter Current Score of Batting Team..')

        # Wickets Out
        wickets_left = st.number_input(
            'Enter Number of Wickets Left For Batting Team..')
        wickets_out = 10-wickets_left

        # Overs Spent
        over = st.number_input('Current Over of The Match..')

        # Runs In Last 5
        run_lst_5 = st.number_input(
            'How Many Runs Batting Team Has Scored In Last 5 Overs ?')

        # Wickets In Last 5
        wicket_lst_5 = st.number_input(
            'Number of  Wickets Taken By Bowling Team In The Last 5 Overs ?')

        # DATA
        # st.write(batting_team,bowling_team)
        # st.write(encoded_batting_team)
        # st.write(encoded_bowling_team)
        # st.write(current_runs)
        # st.write(wickets_out)
        # st.write(over)
        # st.write(run_lst_5)
        # st.write(wicket_lst_5)

        data = [int(wickets_out), over, int(run_lst_5), int(wicket_lst_5), int(current_runs)]
        data.extend(encoded_batting_team)
        data.extend(encoded_bowling_team)

        print(data)

        st.write('---')
        st.write('Encoded Input Data:', pd.DataFrame([data]))
        # Generating Predictions
        Generate_pred = st.button("Predict Score")
        if Generate_pred:

            pred = model.predict([data])
            st.subheader(f'The Predicted Score Will Be Between { int(pred)-5} - {int(pred)+5}')