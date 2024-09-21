from league_stats import create_multi_league_df, create_single_league_df, export_df_to_csv, create_single_split_team_df
from team_stats import find_leagues_given_team, find_splits_given_team, find_unique_players_and_positions_given_team
import pandas as pd
import os

# Create a multi-league dataframe
multi_league_df = create_multi_league_df()

# Create a single league dataframe for each league 
# and export to a csv file in the data/league_data folder
leagues = multi_league_df['league'].unique()
for league in leagues:
    league_df = create_single_league_df(multi_league_df, league)
    export_df_to_csv(league_df, f'data/league_data/{league}_league.csv')

important_teams = ['PSG Talon', 'Fukuoka SoftBank HAWKS gaming', 'Vikings Esports', 'GAM Esports', '100 Thieves', 'MAD Lions KOI', 'paiN Gaming', 'Movistar R7']
# create a dictionary with team names as keys and leagues as values
team_leagues = {}
team_splits = {}

# add keys to the dictionary with values of a empty list
for team in important_teams:
    team_leagues[team] = find_leagues_given_team(multi_league_df, team)
    # print(f"{team} has participated in the following leagues: {team_leagues[team]}")
    team_splits[team] = find_splits_given_team(multi_league_df, team)
    # print(f"{team} has participated in the following splits: {team_splits[team]}")

# for every team and each split they have been in, create a dataframe, export to csv and store in /data/team_data
for team in important_teams:
    for split in team_splits[team]:
        if pd.isna(split):
            continue # skip if split is NaN

        # create a dataframe for a single team per split per playoffs from the multi-league dataframe
        non_playoff_df, playoff_df = create_single_split_team_df(multi_league_df, team, split)
        
        # export to csv for non-playoff games
        if not non_playoff_df.empty:
            non_playoff_filename = f"{team}_{split}.csv"
            non_playoff_df.to_csv(f"data/team_data/{non_playoff_filename}", index=False)

        # export to csv for playoff games
        if not playoff_df.empty:
            playoff_filename = f"{team}_{split}_Playoffs.csv"
            playoff_df.to_csv(f"data/team_data/{playoff_filename}", index=False)

def custom_role_sort_key(item):
    priority_list = ['top', 'jng', 'mid', 'bot', 'sup']
    pos = item.split('-')[1]
    # print("Item:", item, " - Position:", pos, " - Index:", priority_list.index(pos) if pos in priority_list else len(priority_list))
    return priority_list.index(pos) if pos in priority_list else len(priority_list)

# create an team_info.txt file in data/team_data with the teamname and players on the team
with open('info/playins_teams.txt', 'w') as f:
    for team in important_teams:

        # find unique players and positions for a team
        player_and_positions = find_unique_players_and_positions_given_team(multi_league_df, team)

        # list comprehension to remove team positions and NaN values
        unique_players_and_positions = [single_player_pos for single_player_pos in player_and_positions if single_player_pos.split('-')[1] != "team" and not pd.isna(single_player_pos.split('-')[0])]

        # reorganize the list of unique players and positions such that single_player_pos.split('-')[1] values are sorted with all the "top" players first, then "jng", "mid", "bot", and "sup"
        sorted_unique_players_and_positions = sorted(unique_players_and_positions, key=custom_role_sort_key)

        # write to file
        f.write(f"[{team}]\n")
        f.write(f"Leagues: {team_leagues[team]}\n")
        f.write(f"Splits: {team_splits[team]}\n")
        for player_pos in sorted_unique_players_and_positions:
            # hard coded in due to specific players being in different roles at Worlds
            if player_pos in ['Fireblade-top', 'Kratos-top', 'Tomrio-jng', 'SofM-sup', 'Kairi-sup', 'Blazes-mid', 'Pyshiro-bot', 'Neo-bot', 'Meech-bot', 'Keine-top', 'Summit-jng', 'Daiky-jng', 'Lava-mid', 'Ceo-mid', 'Lyonz-bot', 'Oddie-sup']:
                continue
            f.write(f"\n{player_pos}")
        f.write(f"\n\n\n")

# for every csv in /data/team_data folder, find total number of unique gameids per csv and print
output = []
for filename in os.listdir('data/team_data'): # relative path
    if filename.endswith('.csv'):
        df = pd.read_csv(f'data/team_data/{filename}')
        unique_gameids = df['gameid'].nunique() # find unique gameids

        # find unique gameids for when game is '1'
        unique_series = df[df['game'] == 1]['gameid'].nunique()

        # split filename into 3 parts
        # team, split, playoffs
        filename_parts = filename.split('_')
        if len(filename_parts) == 3: # if playoffs is in the filename
            team = filename_parts[0]
            split = filename_parts[1]
            playoffs = filename_parts[2].split('.')[0]
            output_msg = f"[{team}] [{split} {playoffs}] {unique_gameids} unique gameids ({unique_series} series)"
            output.append(output_msg)
            # print(f"[{team}] [{split} {playoffs}] {unique_gameids} unique gameids")
        elif len(filename_parts) == 2: # if playoffs is not in the filename
            team = filename_parts[0]
            split = filename_parts[1].split('.')[0]
            output_msg = f"[{team}] [{split}] {unique_gameids} unique gameids ({unique_series} series)"
            output.append(output_msg)
            # print(f"[{team}] [{split}] {unique_gameids} unique gameids")

# sort the output list alphabetically
output.sort()

# store output list in a txt file called /info/playins_history.txt
with open('info/playins_history.txt', 'w') as f:
    for item in output:
        f.write(f"{item}\n")
    f.write("\n")
        
        

