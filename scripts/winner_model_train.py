
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle

matches = pd.read_csv('matches_2008-2024.csv')

data = matches.dropna(subset=['winner'])
data = data[data['result'] != 'tie']
data = data[data['result'] != 'no result']

current_teams = [
    'Chennai Super Kings',
    'Kolkata Knight Riders',
    'Punjab Kings',
    'Delhi Capitals',
    'Rajasthan Royals',
    'Sunrisers Hyderabad',
    'Mumbai Indians',
    'Royal Challengers Bengaluru',
    'Lucknow Super Giants',
    'Gujarat Titans',
]

team_name_map = {
    'Delhi Daredevils': 'Delhi Capitals',
    'Deccan Chargers': 'Sunrisers Hyderabad',
    'Kings XI Punjab': 'Punjab Kings',
    'Rising Pune Supergiants': 'Rising Pune Supergiant',
    'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
}
for col in ['team1', 'team2', 'toss_winner', 'winner']:
    data[col] = data[col].replace(team_name_map)

# Filter to only include matches between current teams
data = data[(data['team1'].isin(current_teams)) & (data['team2'].isin(current_teams))]
data = data[data['winner'].isin(current_teams)]

# Home ground mapping for each team
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

# Create home advantage features
def is_home_ground(row, team_col):
    team = row[team_col]
    venue = row['venue']
    if team in team_home_venues:
        return 1 if venue in team_home_venues[team] else 0
    return 0

data['team1_is_home'] = data.apply(lambda row: is_home_ground(row, 'team1'), axis=1)
data['team2_is_home'] = data.apply(lambda row: is_home_ground(row, 'team2'), axis=1)
data['has_home_advantage'] = (data['team1_is_home'] | data['team2_is_home']).astype(int)

data['toss_winner_is_winner'] = (data['toss_winner'] == data['winner']).astype(int)

# Recent season (last 5 years)
data['is_recent_season'] = (data['season'] >= data['season'].max() - 5).astype(int)

# Head-to-head record features
def calculate_head_to_head_stats(data):
    """Calculate head-to-head win rates for each team combination"""
    h2h_stats = {}
    
    for idx, row in data.iterrows():
        team1, team2 = row['team1'], row['team2']
        winner = row['winner']
        
        # Create matchup key (sorted to handle both team1 vs team2 and team2 vs team1)
        matchup = tuple(sorted([team1, team2]))
        
        if matchup not in h2h_stats:
            h2h_stats[matchup] = {team1: 0, team2: 0, 'total': 0}
        
        h2h_stats[matchup][winner] += 1
        h2h_stats[matchup]['total'] += 1
    
    return h2h_stats

# Calculate historical head-to-head stats
h2h_stats = calculate_head_to_head_stats(data)

def get_team1_h2h_winrate(row):
    """Get team1's historical win rate against team2"""
    team1, team2 = row['team1'], row['team2']
    matchup = tuple(sorted([team1, team2]))
    
    if matchup in h2h_stats and h2h_stats[matchup]['total'] > 0:
        return h2h_stats[matchup].get(team1, 0) / h2h_stats[matchup]['total']
    return 0.5  # Default to 50% if no history

data['team1_h2h_winrate'] = data.apply(get_team1_h2h_winrate, axis=1)

# Batting/Bowling first performance
def calculate_bat_bowl_first_stats(data):
    """Calculate win rates when batting or bowling first"""
    stats = {}
    
    for team in current_teams:
        # When batting first (team1)
        bat_first_matches = data[data['team1'] == team]
        bat_first_wins = len(bat_first_matches[bat_first_matches['winner'] == team])
        bat_first_total = len(bat_first_matches)
        
        # When bowling first (team2) 
        bowl_first_matches = data[data['team2'] == team]
        bowl_first_wins = len(bowl_first_matches[bowl_first_matches['winner'] == team])
        bowl_first_total = len(bowl_first_matches)
        
        stats[team] = {
            'bat_first_winrate': bat_first_wins / bat_first_total if bat_first_total > 0 else 0.5,
            'bowl_first_winrate': bowl_first_wins / bowl_first_total if bowl_first_total > 0 else 0.5
        }
    
    return stats

bat_bowl_stats = calculate_bat_bowl_first_stats(data)

def get_team1_bat_first_winrate(row):
    team1 = row['team1']
    return bat_bowl_stats.get(team1, {}).get('bat_first_winrate', 0.5)

def get_team2_bowl_first_winrate(row):
    team2 = row['team2']
    return bat_bowl_stats.get(team2, {}).get('bowl_first_winrate', 0.5)

data['team1_bat_first_winrate'] = data.apply(get_team1_bat_first_winrate, axis=1)
data['team2_bowl_first_winrate'] = data.apply(get_team2_bowl_first_winrate, axis=1)

# Team1 vs Team2 at Venue feature
data['team1_vs_team2_venue'] = data['team1'] + '_vs_' + data['team2'] + '_at_' + data['venue']

features = [
    'team1', 'team2', 'toss_winner', 'toss_decision', 'venue', 'season',
    'toss_winner_is_winner', 'team1_is_home', 'team2_is_home', 'has_home_advantage', 
    'is_recent_season', 'team1_h2h_winrate', 'team1_bat_first_winrate', 'team2_bowl_first_winrate'
]
X = data[features]
y = data['winner']

X = pd.get_dummies(X, columns=['team1', 'team2', 'toss_winner', 'toss_decision', 'venue'])

# Keep original team names for labels
team_labels = sorted(y.unique())
print("Team labels:", team_labels)

# Convert target to categorical codes but preserve the mapping
y_categorical = y.astype('category')
y_codes = y_categorical.cat.codes

X_train, X_test, y_train, y_test = train_test_split(X, y_codes, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=300, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

print('Accuracy:', accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

print('\nProbability predictions for first 5 samples:')
for i in range(min(5, len(y_pred_proba))):
    actual_team = team_labels[y_test.iloc[i]]
    print(f'\nActual winner: {actual_team}')
    print('Win probabilities:')
    for j, team in enumerate(team_labels):
        prob = y_pred_proba[i][j]
        print(f'  {team}: {prob:.3f} ({prob*100:.1f}%)')

with open('winner_prediction_model.pkl', 'wb') as f:
    pickle.dump((model, X.columns.tolist(), team_labels), f)

print('\nModel saved! Use predict_proba() method to get winning probabilities.')
