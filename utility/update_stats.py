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

        # store all unique gameids in a list
        unique_gameids = df['gameid'].unique()
        # print(unique_gameids)

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

# calculate points / make new spreadsheet per team in play-ins
for filename in os.listdir('data/team_data'): # relative path
    if filename.endswith('.csv'):

        # create new csv file in /data/playins_team_data/{filename}
        new_filename = filename.split('.')[0] + "_pts.csv"
        with open(f'data/playins_team_data/{new_filename}', 'w') as f:
            # write the header
            f.write("gameid, league, split, playoffs, series_num, game_num, ego_team, opp_team, gamelength, top_player, top_champion, top_primary_kills, top_primary_deaths, top_primary_assists, top_primary_total_cs, jgl_player, jgl_champion, jgl_primary_kills, jgl_primary_deaths, jgl_primary_assists, jgl_primary_total_cs, mid_player, mid_champion, mid_primary_kills, mid_primary_deaths, mid_primary_assists, mid_primary_total_cs, bot_player, bot_champion, bot_primary_kills, bot_primary_deaths, bot_primary_assists, bot_primary_total_cs, sup_player, sup_champion, sup_primary_kills, sup_primary_deaths, sup_primary_assists, sup_primary_total_cs, constant_turrets, constant_dragons, constant_heralds, constant_barons, constant_win, constant_win_under_30, constant_first_blood\n")

            df = pd.read_csv(f'data/team_data/{filename}')
            team_name = filename.split('_')[0]

            total_games = df['gameid'].nunique()

            # find unique gameids 
            unique_gameids = df['gameid'].unique()

            series_num = "Z" # initialize series_num to "Z"

            # extract match info
            for gameid in unique_gameids:
                # gameid, league, split, playoffs, series_num, game, ego_team, opp_team, gamelength,
                # top_player, top_champion, top_primary_kills, top_primary_deaths, top_primary_assists, top_primary_total_cs,
                # jgl_player, jgl_champion, jgl_primary_kills, jgl_primary_deaths, jgl_primary_assists, jgl_primary_total_cs, 
                # mid_player, mid_champion, mid_primary_kills, mid_primary_deaths, mid_primary_assists, mid_primary_total_cs, 
                # bot_player, bot_champion, bot_primary_kills, bot_primary_deaths, bot_primary_assists, bot_primary_total_cs, 
                # sup_player, sup_champion, sup_primary_kills, sup_primary_deaths, sup_primary_assists, sup_primary_total_cs, 
                # contant_towers, constant_dragons, constant_heralds, constant_barons, constant_result, constant_win_under_30, constant_firstblood
                # include opp player / champ / rank later
                relevant_match_info = {} 

                # game_id, league, split, playoffs, series_num, game_num, ego_team, opp_team
                # top_player, top_primary_kill_pts, top_primary_death_pts, top_primary_assist_pts, top_primary_cs_pts,
                # jgl_player, jgl_primary_kill_pts, jgl_primary_death_pts, jgl_primary_assist_pts, jgl_primary_cs_pts, 
                # mid_player, mid_primary_kill_pts, mid_primary_death_pts, mid_primary_assist_pts, mid_primary_cs_pts, 
                # bot_player, bot_primary_kill_pts, bot_primary_death_pts, bot_primary_assist_pts, bot_primary_cs_pts, 
                # sup_player, sup_primary_kill_pts, sup_primary_death_pts, sup_primary_assist_pts, sup_primary_cs_pts, 
                # contant_turrets, constant_dragons, constant_hearlds, constant_barons, constant_win, constant_win_under_30, constant_first_blood
                match_pts_info = {}

                game_df = df[df['gameid'] == gameid] # all rows with the same gameid

                # if game is "1", increment series_num by 1 Letter 
                # if series_num is "Z", increment series_num to "A"
                if game_df['game'].values[0] == 1:
                    if series_num == "Z":
                        series_num = "A"
                    else:
                        series_num = chr(ord(series_num) + 1)
                
                relevant_match_info["gameid"] = gameid
                relevant_match_info["league"] = game_df['league'].values[0]
                relevant_match_info["split"] = game_df['split'].values[0]
                relevant_match_info["playoffs"] = game_df['playoffs'].values[0]
                relevant_match_info["series_num"] = series_num
                relevant_match_info["game_num"] = game_df['game'].values[0]
                
                # pull the "teamname" from row with participantid of 100
                team1 = game_df[game_df['participantid'] == 100]['teamname'].values[0]
                team2 = game_df[game_df['participantid'] == 200]['teamname'].values[0]

                # if team1 is the team_name, ego_team is team1, opp_team is team2
                top_id, jng_id, mid_id, bot_id, sup_id, team_id = 0, 0, 0, 0, 0, 0
                if team1 == team_name:
                    relevant_match_info["ego_team"] = team1
                    relevant_match_info["opp_team"] = team2
                    top_id, jng_id, mid_id, bot_id, sup_id = 1, 2, 3, 4, 5
                    team_id = 100
                else:
                    relevant_match_info["ego_team"] = team2
                    relevant_match_info["opp_team"] = team1
                    top_id, jng_id, mid_id, bot_id, sup_id = 6, 7, 8, 9, 10
                    team_id = 200
                
                # find the player and champion for each role
                top_player = game_df[game_df['participantid'] == top_id]['playername'].values[0]
                jng_player = game_df[game_df['participantid'] == jng_id]['playername'].values[0]
                mid_player = game_df[game_df['participantid'] == mid_id]['playername'].values[0]
                bot_player = game_df[game_df['participantid'] == bot_id]['playername'].values[0]
                sup_player = game_df[game_df['participantid'] == sup_id]['playername'].values[0]

                top_champion = game_df[game_df['participantid'] == top_id]['champion'].values[0]
                jng_champion = game_df[game_df['participantid'] == jng_id]['champion'].values[0]
                mid_champion = game_df[game_df['participantid'] == mid_id]['champion'].values[0]
                bot_champion = game_df[game_df['participantid'] == bot_id]['champion'].values[0]
                sup_champion = game_df[game_df['participantid'] == sup_id]['champion'].values[0]

                # find the primary stats for each role
                top_kills = game_df[game_df['participantid'] == top_id]['kills'].values[0]
                # print(top_kills)
                top_deaths = game_df[game_df['participantid'] == top_id]['deaths'].values[0]
                # print(top_deaths)
                top_assists = game_df[game_df['participantid'] == top_id]['assists'].values[0]
                # print(top_assists)
                top_total_cs = game_df[game_df['participantid'] == top_id]['total cs'].values[0]
                

                jng_kills = game_df[game_df['participantid'] == jng_id]['kills'].values[0]
                jng_deaths = game_df[game_df['participantid'] == jng_id]['deaths'].values[0]
                jng_assists = game_df[game_df['participantid'] == jng_id]['assists'].values[0]
                jng_total_cs = game_df[game_df['participantid'] == jng_id]['total cs'].values[0]

                mid_kills = game_df[game_df['participantid'] == mid_id]['kills'].values[0]
                mid_deaths = game_df[game_df['participantid'] == mid_id]['deaths'].values[0]
                mid_assists = game_df[game_df['participantid'] == mid_id]['assists'].values[0]
                mid_total_cs = game_df[game_df['participantid'] == mid_id]['total cs'].values[0]

                bot_kills = game_df[game_df['participantid'] == bot_id]['kills'].values[0]
                bot_deaths = game_df[game_df['participantid'] == bot_id]['deaths'].values[0]
                bot_assists = game_df[game_df['participantid'] == bot_id]['assists'].values[0]
                bot_total_cs = game_df[game_df['participantid'] == bot_id]['total cs'].values[0]

                sup_kills = game_df[game_df['participantid'] == sup_id]['kills'].values[0]
                sup_deaths = game_df[game_df['participantid'] == sup_id]['deaths'].values[0]
                sup_assists = game_df[game_df['participantid'] == sup_id]['assists'].values[0]
                sup_total_cs = game_df[game_df['participantid'] == sup_id]['total cs'].values[0]

                # find the constant stats for the game for team
                constant_turrets = game_df[game_df['participantid'] == team_id]['towers'].values[0]
                constant_dragons = game_df[game_df['participantid'] == team_id]['dragons'].values[0]
                constant_heralds = game_df[game_df['participantid'] == team_id]['heralds'].values[0]
                constant_barons = game_df[game_df['participantid'] == team_id]['barons'].values[0]
                constant_win = game_df[game_df['participantid'] == team_id]['result'].values[0]
                game_length = game_df['gamelength'].values[0] 
                if game_length < 3000 and constant_win == 1:
                    constant_win_under_30 = 1
                else:
                    constant_win_under_30 = 0
                constant_first_blood = game_df[game_df['participantid'] == team_id]['firstblood'].values[0]
                
                # store all relevant match info
                relevant_match_info["game_length"] = game_length

                relevant_match_info["top_player"] = top_player
                relevant_match_info["jgl_player"] = jng_player
                relevant_match_info["mid_player"] = mid_player
                relevant_match_info["bot_player"] = bot_player
                relevant_match_info["sup_player"] = sup_player

                relevant_match_info["top_champion"] = top_champion
                relevant_match_info["jgl_champion"] = jng_champion
                relevant_match_info["mid_champion"] = mid_champion
                relevant_match_info["bot_champion"] = bot_champion
                relevant_match_info["sup_champion"] = sup_champion

                relevant_match_info["top_primary_kills"] = top_kills
                relevant_match_info["top_primary_deaths"] = top_deaths
                relevant_match_info["top_primary_assists"] = top_assists
                relevant_match_info["top_primary_total_cs"] = top_total_cs

                relevant_match_info["jgl_primary_kills"] = jng_kills
                relevant_match_info["jgl_primary_deaths"] = jng_deaths
                relevant_match_info["jgl_primary_assists"] = jng_assists
                relevant_match_info["jgl_primary_total_cs"] = jng_total_cs

                relevant_match_info["mid_primary_kills"] = mid_kills
                relevant_match_info["mid_primary_deaths"] = mid_deaths
                relevant_match_info["mid_primary_assists"] = mid_assists
                relevant_match_info["mid_primary_total_cs"] = mid_total_cs

                relevant_match_info["bot_primary_kills"] = bot_kills
                relevant_match_info["bot_primary_deaths"] = bot_deaths
                relevant_match_info["bot_primary_assists"] = bot_assists
                relevant_match_info["bot_primary_total_cs"] = bot_total_cs

                relevant_match_info["sup_primary_kills"] = sup_kills
                relevant_match_info["sup_primary_deaths"] = sup_deaths
                relevant_match_info["sup_primary_assists"] = sup_assists
                relevant_match_info["sup_primary_total_cs"] = sup_total_cs
                
                relevant_match_info["constant_turrets"] = constant_turrets
                relevant_match_info["constant_dragons"] = constant_dragons
                relevant_match_info["constant_heralds"] = constant_heralds
                relevant_match_info["constant_barons"] = constant_barons
                relevant_match_info["constant_win"] = constant_win
                relevant_match_info["constant_win_under_30"] = constant_win_under_30
                relevant_match_info["constant_first_blood"] = constant_first_blood

                # write relevant match info to csv
                f.write(f"{relevant_match_info['gameid']}, {relevant_match_info['league']}, {relevant_match_info['split']}, {relevant_match_info['playoffs']}, {relevant_match_info['series_num']}, {relevant_match_info['game_num']}, {relevant_match_info['ego_team']}, {relevant_match_info['opp_team']}, {relevant_match_info['game_length']}, {relevant_match_info['top_player']}, {relevant_match_info['top_champion']}, {relevant_match_info['top_primary_kills']}, {relevant_match_info['top_primary_deaths']}, {relevant_match_info['top_primary_assists']}, {relevant_match_info['top_primary_total_cs']}, {relevant_match_info['jgl_player']}, {relevant_match_info['jgl_champion']}, {relevant_match_info['jgl_primary_kills']}, {relevant_match_info['jgl_primary_deaths']}, {relevant_match_info['jgl_primary_assists']}, {relevant_match_info['jgl_primary_total_cs']}, {relevant_match_info['mid_player']}, {relevant_match_info['mid_champion']}, {relevant_match_info['mid_primary_kills']}, {relevant_match_info['mid_primary_deaths']}, {relevant_match_info['mid_primary_assists']}, {relevant_match_info['mid_primary_total_cs']}, {relevant_match_info['bot_player']}, {relevant_match_info['bot_champion']}, {relevant_match_info['bot_primary_kills']}, {relevant_match_info['bot_primary_deaths']}, {relevant_match_info['bot_primary_assists']}, {relevant_match_info['bot_primary_total_cs']}, {relevant_match_info['sup_player']}, {relevant_match_info['sup_champion']}, {relevant_match_info['sup_primary_kills']}, {relevant_match_info['sup_primary_deaths']}, {relevant_match_info['sup_primary_assists']}, {relevant_match_info['sup_primary_total_cs']}, {relevant_match_info['constant_turrets']}, {relevant_match_info['constant_dragons']}, {relevant_match_info['constant_heralds']}, {relevant_match_info['constant_barons']}, {relevant_match_info['constant_win']}, {relevant_match_info['constant_win_under_30']}, {relevant_match_info['constant_first_blood']}\n")

print("Done!")  
            


       

        
     

        
        

