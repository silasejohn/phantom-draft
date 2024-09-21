from league_stats import create_multi_league_df, unique_teams, find_leagues_given_team

# Create a multi-league dataframe
multi_league_df = create_multi_league_df()
print(multi_league_df.head())

important_teams = ['PSG Talon', 'Fukuoka SoftBank HAWKS gaming', 'Vikings Esports', 'GAM Esports', '100 Thieves', 'MAD Lions KOI', 'paiN Gaming', 'Movistar R7']

# create a dictionary with team names as keys and leagues as values
team_leagues = {}

# add keys to the dictionary with values of a empty list
for team in important_teams:
    team_leagues[team] = find_leagues_given_team(multi_league_df, team)
    print(f"{team} has participated in the following leagues: {team_leagues[team]}")

print(team_leagues)
    

