from league_stats import create_multi_league_df, create_single_split_team_df
from team_stats import find_leagues_given_team, find_splits_given_team
from LeagueTeam import LeagueTeam

# Create a multi-league dataframe
multi_league_df = create_multi_league_df()
print(multi_league_df.head())

important_teams = ['PSG Talon', 'Fukuoka SoftBank HAWKS gaming', 'Vikings Esports', 'GAM Esports', '100 Thieves', 'MAD Lions KOI', 'paiN Gaming', 'Movistar R7']

# create a dictionary with team names as keys and leagues as values
team_leagues = {}
team_splits = {}

# add keys to the dictionary with values of a empty list
for team in important_teams:
    team_leagues[team] = find_leagues_given_team(multi_league_df, team)
    print(f"{team} has participated in the following leagues: {team_leagues[team]}")
    team_splits[team] = find_splits_given_team(multi_league_df, team)
    print(f"{team} has participated in the following splits: {team_splits[team]}")

# for every team and each split they have been in, create a dataframe, export to csv and store in /data/team_data
for team in important_teams:
    for split in team_splits[team]:
        df = create_single_split_team_df(multi_league_df, team, split)
        filename = f"{team}_{split}.csv"
        df.to_csv(f"data/team_data/{filename}", index=False)


# print(team_leagues)
# print(team_splits)


    

