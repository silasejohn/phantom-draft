from league_stats import create_multi_league_df, create_single_league_df, export_df_to_csv, create_single_split_team_df
from team_stats import find_leagues_given_team, find_splits_given_team, find_unique_players_and_positions_given_team
import pandas as pd
import json
import os
import sys

# Create a multi-league dataframe
multi_league_df = create_multi_league_df()

# Create a single league dataframe for each league 
# and export to a csv file in the data/league_data folder
leagues = multi_league_df['league'].unique()
for league in leagues:
    league_df = create_single_league_df(multi_league_df, league)
    export_df_to_csv(league_df, f'data/01_league_data/{league}_league.csv')

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
    series_num = "~" # initialize series_num to "~"
    for split in team_splits[team]:
        if pd.isna(split):
            continue # skip if split is NaN

        # create a dataframe for a single team per split per playoffs from the multi-league dataframe
        non_playoff_df, playoff_df = create_single_split_team_df(multi_league_df, team, split)
        
        # export to csv for non-playoff games
        if not non_playoff_df.empty: 
            
            unique_gameids = non_playoff_df['gameid'].unique() # find unique gameids
            non_playoff_df.insert(4, 'series_num', series_num) # add series_num to the dataframe before "game_num" header
            
            for gameid in unique_gameids:
                game_df = non_playoff_df[non_playoff_df['gameid'] == gameid] # all rows with the same gameid

                # if game is "1", increment series_num by 1 Letter 
                # if series_num is "Z", increment series_num to "A"
                if game_df['game'].values[0] == 1:
                    if series_num == "~":
                        series_num = "A"
                    elif series_num == "Z":
                        series_num = "AA"
                    else:
                        # get the last char of the series_num (even if there are multiple chars) and increment by one char
                        series_num = series_num[:-1] + chr(ord(series_num[-1]) + 1)
                
                # for all rows with the same gameid, update the series_num
                non_playoff_df.loc[non_playoff_df['gameid'] == gameid, 'series_num'] = series_num

            non_playoff_filename = f"{team}_{split}.csv"
            non_playoff_df.to_csv(f"data/02_team_data/{non_playoff_filename}", index=False)

        # export to csv for playoff games
        if not playoff_df.empty:

            unique_gameids = playoff_df['gameid'].unique() # find unique gameids
            playoff_df.insert(4, 'series_num', series_num) # add series_num to the dataframe before "game_num" header

            for gameid in unique_gameids:
                game_df = playoff_df[playoff_df['gameid'] == gameid] # all rows with the same gameid

                # if game is "1", increment series_num by 1 Letter 
                # if series_num is "Z", increment series_num to "A"
                if game_df['game'].values[0] == 1:
                    if series_num == "~":
                        series_num = "A"
                    elif series_num == "Z":
                        series_num = "AA"
                    else:
                        # get the last char of the series_num (even if there are multiple chars) and increment by one char
                        series_num = series_num[:-1] + chr(ord(series_num[-1]) + 1)
                        
                # for all rows with the same gameid, update the series_num
                playoff_df.loc[playoff_df['gameid'] == gameid, 'series_num'] = series_num

            playoff_filename = f"{team}_{split}_Playoffs.csv"
            playoff_df.to_csv(f"data/02_team_data/{playoff_filename}", index=False)

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
for filename in os.listdir('data/02_team_data'): # relative path
    if filename.endswith('.csv'):
        df = pd.read_csv(f'data/02_team_data/{filename}')
        unique_gameids = df['gameid'].nunique() # find unique gameids

        # store all unique gameids in a list
        unique_gameids = df['gameid'].unique()

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
for filename in os.listdir('data/02_team_data'): # relative path
    if filename.endswith('.csv'):

        # create new csv file in /data/playins_team_data/{filename}
        new_filename = filename.split('.')[0] + ".csv"
        with open(f'data/03_playins_team_data/{new_filename}', 'w') as f:
            # write the header
            f.write("gameid,league,split,playoffs,series_num,game_num,ego_team,opp_team,gamelength,top_player,top_champion,top_primary_kills,top_primary_deaths,top_primary_assists,top_primary_total_cs,jgl_player,jgl_champion,jgl_primary_kills,jgl_primary_deaths,jgl_primary_assists,jgl_primary_total_cs,mid_player,mid_champion,mid_primary_kills,mid_primary_deaths,mid_primary_assists,mid_primary_total_cs,bot_player,bot_champion,bot_primary_kills,bot_primary_deaths,bot_primary_assists,bot_primary_total_cs,sup_player,sup_champion,sup_primary_kills,sup_primary_deaths,sup_primary_assists,sup_primary_total_cs,constant_turrets,constant_dragons,constant_heralds,constant_barons,constant_win,constant_win_under_30,constant_first_blood\n")

            df = pd.read_csv(f'data/02_team_data/{filename}')
            team_name = filename.split('_')[0]

            total_games = df['gameid'].nunique()

            # find unique gameids 
            unique_gameids = df['gameid'].unique()

            # series_num = "Z" # initialize series_num to "Z"

            # extract match info
            for gameid in unique_gameids:
                # gameid, league, split, playoffs, series_num, game, ego_team, opp_team, gamelength,
                # top_player, top_champion, top_primary_kills, top_primary_deaths, top_primary_assists, top_primary_total_cs,
                # jgl_player, jgl_champion, jgl_primary_kills, jgl_primary_deaths, jgl_primary_assists, jgl_primary_total_cs, 
                # mid_player, mid_champion, mid_primary_kills, mid_primary_deaths, mid_primary_assists, mid_primary_total_cs, 
                # bot_player, bot_champion, bot_primary_kills, bot_primary_deaths, bot_primary_assists, bot_primary_total_cs, 
                # sup_player, sup_champion, sup_primary_kills, sup_primary_deaths, sup_primary_assists, sup_primary_total_cs, 
                # contant_towers, constant_dragons, constant_heralds, constant_barons, constant_result, constant_win_under_30, constant_firstblood
                relevant_match_info = {} 

                # gameid, league, split, playoffs, series_num, game, ego_team, opp_team, gamelength,
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
                # if game_df['game'].values[0] == 1:
                #     if series_num == "Z":
                #         series_num = "A"
                #     else:
                #         series_num = chr(ord(series_num) + 1)
                
                relevant_match_info["gameid"] = gameid
                relevant_match_info["league"] = game_df['league'].values[0]
                relevant_match_info["split"] = game_df['split'].values[0]
                relevant_match_info["playoffs"] = game_df['playoffs'].values[0]
                relevant_match_info["series_num"] = game_df['series_num'].values[0]
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
                f.write(f"{relevant_match_info['gameid']},{relevant_match_info['league']},{relevant_match_info['split']},{relevant_match_info['playoffs']},{relevant_match_info['series_num']},{relevant_match_info['game_num']},{relevant_match_info['ego_team']},{relevant_match_info['opp_team']},{relevant_match_info['game_length']},{relevant_match_info['top_player']},{relevant_match_info['top_champion']},{relevant_match_info['top_primary_kills']},{relevant_match_info['top_primary_deaths']},{relevant_match_info['top_primary_assists']},{relevant_match_info['top_primary_total_cs']},{relevant_match_info['jgl_player']},{relevant_match_info['jgl_champion']},{relevant_match_info['jgl_primary_kills']},{relevant_match_info['jgl_primary_deaths']},{relevant_match_info['jgl_primary_assists']},{relevant_match_info['jgl_primary_total_cs']},{relevant_match_info['mid_player']},{relevant_match_info['mid_champion']},{relevant_match_info['mid_primary_kills']},{relevant_match_info['mid_primary_deaths']},{relevant_match_info['mid_primary_assists']},{relevant_match_info['mid_primary_total_cs']},{relevant_match_info['bot_player']},{relevant_match_info['bot_champion']},{relevant_match_info['bot_primary_kills']},{relevant_match_info['bot_primary_deaths']},{relevant_match_info['bot_primary_assists']},{relevant_match_info['bot_primary_total_cs']},{relevant_match_info['sup_player']},{relevant_match_info['sup_champion']},{relevant_match_info['sup_primary_kills']},{relevant_match_info['sup_primary_deaths']},{relevant_match_info['sup_primary_assists']},{relevant_match_info['sup_primary_total_cs']},{relevant_match_info['constant_turrets']},{relevant_match_info['constant_dragons']},{relevant_match_info['constant_heralds']},{relevant_match_info['constant_barons']},{relevant_match_info['constant_win']},{relevant_match_info['constant_win_under_30']},{relevant_match_info['constant_first_blood']}\n")

print("Done!")  

# Load the multi-nested JSON object
with open('info/static_vals.json') as json_file:
    fantasy_static_vals = json.load(json_file)

match_pts_info = {}

# calculate points / make new spreadsheet per team in play-ins for their score
for filename in os.listdir('data/03_playins_team_data'): # relative path
    if filename.endswith('.csv'):

        # create new csv file in /data/playins_team_data/{filename}
        new_filename = filename.split('.')[0] + "_pts.csv"

        with open(f'data/04_playins_team_score/{new_filename}', 'w') as f:
            # write the header
            f.write("gameid,league,split,playoffs,series_num,game_num,ego_team,opp_team,gamelength,top_player,top_champion,top_primary_kills,top_primary_kill_pts,top_primary_deaths,top_primary_death_pts,top_primary_assists,top_primary_assists_pts,top_primary_total_cs,top_primary_total_cs_pts,jgl_player,jgl_champion,jgl_primary_kills,jgl_primary_kills_pts,jgl_primary_deaths,jgl_primary_deaths_pts,jgl_primary_assists,jgl_primary_assists_pts,jgl_primary_total_cs,jgl_primary_total_cs_pts,mid_player,mid_champion,mid_primary_kills,mid_primary_kills_pts,mid_primary_deaths,mid_primary_deaths_pts,mid_primary_assists,mid_primary_assists_pts,mid_primary_total_cs,mid_primary_total_cs_pts,bot_player,bot_champion,bot_primary_kills,bot_primary_kills_pts,bot_primary_deaths,bot_primary_deaths_pts,bot_primary_assists,bot_primary_assists_pts,bot_primary_total_cs,bot_primary_total_cs_pts,sup_player,sup_champion,sup_primary_kills,sup_primary_kills_pts,sup_primary_deaths,sup_primary_deaths_pts,sup_primary_assists,sup_primary_assists_pts,sup_primary_total_cs,sup_primary_total_cs_pts,constant_turrets,constant_turrets_pts,constant_dragons,constant_dragons_pts,constant_heralds,constant_heralds_pts,constant_barons,constant_barons_pts,constant_win,constant_win_pts,constant_win_under_30,constant_win_under_30_pts,constant_first_blood,constant_first_blood_pts,top_kda_pts,jgl_kda_pts,mid_kda_pts,bot_kda_pts,sup_kda_pts,tdfbh_pts,top_total_pts,jgl_total_pts,mid_total_pts,bot_total_pts,sup_total_pts\n")

            df = pd.read_csv(f'data/03_playins_team_data/{filename}') # read the csv file

            # extract match info in each gameid in the dataframe
            # for each row in the dataframe

            for index, row in df.iterrows():
                gameid = row['gameid'] 
                league = row['league'] 
                league = row['league']
                split = row['split']
                playoffs = row['playoffs']
                series_num = row['series_num']
                game_num = row['game_num']
                ego_team = row['ego_team']
                opp_team = row['opp_team']
                gamelength = row['gamelength']
                top_player = row['top_player']
                top_champion = row['top_champion']
                top_primary_kills = row['top_primary_kills']
                top_primary_deaths = row['top_primary_deaths']
                top_primary_assists = row['top_primary_assists']
                top_primary_total_cs = row['top_primary_total_cs']
                jgl_player = row['jgl_player']
                jgl_champion = row['jgl_champion']
                jgl_primary_kills = row['jgl_primary_kills']
                jgl_primary_deaths = row['jgl_primary_deaths']
                jgl_primary_assists =  row['jgl_primary_assists']
                jgl_primary_total_cs = row['jgl_primary_total_cs']
                mid_player = row['mid_player']
                mid_champion = row['mid_champion']
                mid_primary_kills = row['mid_primary_kills']
                mid_primary_deaths = row['mid_primary_deaths']
                mid_primary_assists = row['mid_primary_assists']
                mid_primary_total_cs = row['mid_primary_total_cs']
                bot_player = row['bot_player']
                bot_champion = row['bot_champion']
                bot_primary_kills = row['bot_primary_kills']
                bot_primary_deaths = row['bot_primary_deaths']
                bot_primary_assists = row['bot_primary_assists']
                bot_primary_total_cs = row['bot_primary_total_cs']  
                sup_player = row['sup_player']
                sup_champion = row['sup_champion']
                sup_primary_kills = row['sup_primary_kills']
                sup_primary_deaths = row['sup_primary_deaths']
                sup_primary_assists = row['sup_primary_assists']
                sup_primary_total_cs = row['sup_primary_total_cs']
                constant_turrets = row['constant_turrets']
                constant_dragons = row['constant_dragons']
                constant_heralds = row['constant_heralds']
                constant_barons = row['constant_barons']
                constant_win = row['constant_win']
                constant_win_under_30 = row['constant_win_under_30']
                constant_first_blood = row['constant_first_blood']

                # calculate points for each player
                top_primary_kill_pts = round(float(top_primary_kills) * float(fantasy_static_vals['primary']['kills']['top']), 4)
                top_primary_death_pts = round(float(top_primary_deaths) * float(fantasy_static_vals['primary']['deaths']['top']), 4)
                top_primary_assists_pts = round(float(top_primary_assists) * float(fantasy_static_vals['primary']['assists']['top']), 4)
                top_kda_pts = round(top_primary_kill_pts + top_primary_death_pts + top_primary_assists_pts, 4)
                top_primary_total_cs_pts = round(float(top_primary_total_cs) * float(fantasy_static_vals['primary']['cs']['top']), 4)

                jgl_primary_kills_pts = round(float(jgl_primary_kills) * float(fantasy_static_vals['primary']['kills']['jgl']), 4)
                jgl_primary_death_pts = round(float(jgl_primary_deaths) * float(fantasy_static_vals['primary']['deaths']['jgl']), 4)
                jgl_primary_assists_pts = round(float(jgl_primary_assists) * float(fantasy_static_vals['primary']['assists']['jgl']), 4)
                jgl_kda_pts = round(jgl_primary_kills_pts + jgl_primary_death_pts + jgl_primary_assists_pts, 4)
                jgl_primary_total_cs_pts = round(float(jgl_primary_total_cs) * float(fantasy_static_vals['primary']['cs']['jgl']), 4)

                mid_primary_kills_pts = round(float(mid_primary_kills) * float(fantasy_static_vals['primary']['kills']['mid']), 4)
                mid_primary_death_pts = round(float(mid_primary_deaths) * float(fantasy_static_vals['primary']['deaths']['mid']), 4)
                mid_primary_assists_pts = round(float(mid_primary_assists) * float(fantasy_static_vals['primary']['assists']['mid']), 4)
                mid_kda_pts = round(mid_primary_kills_pts + mid_primary_death_pts + mid_primary_assists_pts, 4)
                mid_primary_total_cs_pts = round(float(mid_primary_total_cs) * float(fantasy_static_vals['primary']['cs']['mid']), 4)

                bot_primary_kills_pts = round(float(bot_primary_kills) * float(fantasy_static_vals['primary']['kills']['bot']), 4)
                bot_primary_death_pts = round(float(bot_primary_deaths) * float(fantasy_static_vals['primary']['deaths']['bot']), 4)
                bot_primary_assists_pts = round(float(bot_primary_assists) * float(fantasy_static_vals['primary']['assists']['bot']), 4)
                bot_kda_pts = round(bot_primary_kills_pts + bot_primary_death_pts + bot_primary_assists_pts, 4)
                bot_primary_total_cs_pts = round(float(bot_primary_total_cs) * float(fantasy_static_vals['primary']['cs']['bot']), 4)

                sup_primary_kills_pts = round(float(sup_primary_kills) * float(fantasy_static_vals['primary']['kills']['sup']), 4)
                sup_primary_death_pts = round(float(sup_primary_deaths) * float(fantasy_static_vals['primary']['deaths']['sup']), 4)
                sup_primary_assists_pts = round(float(sup_primary_assists) * float(fantasy_static_vals['primary']['assists']['sup']), 4)
                sup_kda_pts = round(sup_primary_kills_pts + sup_primary_death_pts + sup_primary_assists_pts, 4)
                sup_primary_total_cs_pts = round(float(sup_primary_total_cs) * float(fantasy_static_vals['primary']['cs']['sup']), 4)

                constant_turrets_pts = round(float(constant_turrets) * float(fantasy_static_vals['constant']['turret']), 4)
                constant_dragons_pts = round(float(constant_dragons) * float(fantasy_static_vals['constant']['dragon']), 4)
                constant_first_blood_pts = round(float(constant_first_blood) * float(fantasy_static_vals['constant']['first_blood']), 4)
                constant_barons_pts = round(float(constant_barons) * float(fantasy_static_vals['constant']['baron']), 4)
                constant_heralds_pts = round(float(constant_heralds) * float(fantasy_static_vals['constant']['herald']), 4)
                constant_tdfbh_pts = round(constant_turrets_pts + constant_dragons_pts + constant_heralds_pts + constant_barons_pts + constant_first_blood_pts, 4)

                constant_win_pts = round(float(constant_win) * float(fantasy_static_vals['constant']['win']), 4) # can be (0 or 1) * 2
                constant_win_under_30_pts = round(float(constant_win_under_30) * float(fantasy_static_vals['constant']['win_under_30']), 4) # can be (0 or 1) * 1

                top_total_pts = round(top_kda_pts + top_primary_total_cs_pts + constant_tdfbh_pts + constant_win_pts + constant_win_under_30_pts, 4)
                jgl_total_pts = round(jgl_kda_pts + jgl_primary_total_cs_pts + constant_tdfbh_pts + constant_win_pts + constant_win_under_30_pts, 4)
                mid_total_pts = round(mid_kda_pts + mid_primary_total_cs_pts + constant_tdfbh_pts + constant_win_pts + constant_win_under_30_pts, 4)
                bot_total_pts = round(bot_kda_pts + bot_primary_total_cs_pts + constant_tdfbh_pts + constant_win_pts + constant_win_under_30_pts, 4)
                sup_total_pts = round(sup_kda_pts + sup_primary_total_cs_pts + constant_tdfbh_pts + constant_win_pts + constant_win_under_30_pts, 4)

                f.write(f"{gameid},{league},{split},{playoffs},{series_num},{game_num},{ego_team},{opp_team},{gamelength},{top_player},{top_champion},{top_primary_kills},{top_primary_kill_pts},{top_primary_deaths},{top_primary_death_pts},{top_primary_assists},{top_primary_assists_pts},{top_primary_total_cs},{top_primary_total_cs_pts},{jgl_player},{jgl_champion},{jgl_primary_kills},{jgl_primary_kills_pts},{jgl_primary_deaths},{jgl_primary_death_pts},{jgl_primary_assists},{jgl_primary_assists_pts},{jgl_primary_total_cs},{jgl_primary_total_cs_pts},{mid_player},{mid_champion},{mid_primary_kills},{mid_primary_kills_pts},{mid_primary_deaths},{mid_primary_death_pts},{mid_primary_assists},{mid_primary_assists_pts},{mid_primary_total_cs},{mid_primary_total_cs_pts},{bot_player},{bot_champion},{bot_primary_kills},{bot_primary_kills_pts},{bot_primary_deaths},{bot_primary_death_pts},{bot_primary_assists},{bot_primary_assists_pts},{bot_primary_total_cs},{bot_primary_total_cs_pts},{sup_player},{sup_champion},{sup_primary_kills},{sup_primary_kills_pts},{sup_primary_deaths},{sup_primary_death_pts},{sup_primary_assists},{sup_primary_assists_pts},{sup_primary_total_cs},{sup_primary_total_cs_pts},{constant_turrets},{constant_turrets_pts},{constant_dragons},{constant_dragons_pts},{constant_heralds},{constant_heralds_pts},{constant_barons},{constant_barons_pts},{constant_win},{constant_win_pts},{constant_win_under_30},{constant_win_under_30_pts},{constant_first_blood},{constant_first_blood_pts},{top_kda_pts},{jgl_kda_pts},{mid_kda_pts},{bot_kda_pts},{sup_kda_pts},{constant_tdfbh_pts},{top_total_pts},{jgl_total_pts},{mid_total_pts},{bot_total_pts},{sup_total_pts}\n")
print("Done!")

# for each team in important_teams, find all the respective csv files in /data/playins_team_score and store in a list
team_csv_files = {}
for team in important_teams:
    team_csv_files[team] = []
    for filename in os.listdir('data/04_playins_team_score'):
        if filename.startswith(f"{team}_"):
            team_csv_files[team].append(filename)

def alpha_to_num(s):
    result = 0
    for char in s:
        result = result * 26 + (ord(char) - ord('A') + 1)
    return result

# for each team in team_csv_files, get a df of each csv file and combine all the dfs into one df for a team
team_combined_df_files = {}
for team in important_teams:
    team_combined_df_files[team] = []
    for csv_file in team_csv_files[team]:
        df = pd.read_csv(f'data/04_playins_team_score/{csv_file}')
        team_combined_df_files[team].append(df)
    
    temp_df = pd.concat(team_combined_df_files[team]) # combine all the dfs into one df    
    team_combined_df_files[team] = temp_df.assign(
        series_num_numeric=temp_df['series_num'].apply(alpha_to_num),  # Convert series_num to a sortable numeric value
        game_num_numeric=temp_df['game_num'].astype(int)  # Convert game_num from string to int
    ).sort_values(by=['series_num_numeric', 'game_num_numeric'])  # Sort by the new numeric columns

    team_combined_df_files[team] = team_combined_df_files[team].drop(columns=['series_num_numeric', 'game_num_numeric']) # drop the numeric columns

# create a csv file for each team df in team_combined_df_files and store in /data/04_playins_team_score_combined
for team in important_teams:
    team_combined_df_files[team].to_csv(f'data/05_playins_team_score_combined/{team}_combined.csv', index=False)

### OVERALL STATS
# Position / Player who carries the MOST games
# ON WINS ... rank player / position who carries most + points
# ON LOSSES ... rank player / position who carries most + points

# for each team in csv files in 05_playins_team_score_combined, find the player who carries the most games (aka has the most points)
# you can find the player who carries the most games by looking in the top_total_pts, jgl_total_pts, mid_total_pts, bot_total_pts, sup_total_pts columns
player_point_combos = {}
player_carry_potential = {}

# start by every game for a team, store a list ranking tuple of playername and their respective points for that game
for team in important_teams:
    # store a list of tuples of playername and their respective points for that game
    player_point_combos[team] = []

    # assume range from 0 to 25
    # based on every player + their point value per game, calculate a standardized value from 0 to 10 based on their 0 to 25 point score range and keep a running total
    player_carry_potential[team] = {}

    df = pd.read_csv(f'data/05_playins_team_score_combined/{team}_combined.csv')

    for index, row in df.iterrows():
        top_player = row['top_player']
        top_total_pts = row['top_total_pts']
        jgl_player = row['jgl_player']
        jgl_total_pts = row['jgl_total_pts']
        mid_player = row['mid_player']
        mid_total_pts = row['mid_total_pts']
        bot_player = row['bot_player']
        bot_total_pts = row['bot_total_pts']
        sup_player = row['sup_player']
        sup_total_pts = row['sup_total_pts']

        # create a tuple of playername and their respective points for that game add all the tuples to a list 
        player_point_combos[team].append((top_player, top_total_pts, round((top_total_pts / 25) * 10, 2)))
        player_point_combos[team].append((jgl_player, jgl_total_pts, round((jgl_total_pts / 25) * 10, 2)))
        player_point_combos[team].append((mid_player, mid_total_pts, round((mid_total_pts / 25) * 10, 2)))
        player_point_combos[team].append((bot_player, bot_total_pts, round((bot_total_pts / 25) * 10, 2)))
        player_point_combos[team].append((sup_player, sup_total_pts, round((sup_total_pts / 25) * 10, 2)))

        # sort the list in decreasing total_pts order
        player_point_combos[team].sort(key=lambda x: x[1], reverse=True)

    # add the standardized value and # of games played to the player_carry_potential dictionary
    for player, points, standardized_points in player_point_combos[team]:
        if player not in player_carry_potential[team]:
            player_carry_potential[team][player] = {}
            player_carry_potential[team][player]['standardized_score'] = standardized_points
            player_carry_potential[team][player]['games_played'] = 1
        else:
            player_carry_potential[team][player]['standardized_score'] += standardized_points
            player_carry_potential[team][player]['games_played'] += 1

# print player_carry_potential 
player_standardized_carry_potential = {}
for team in important_teams:
    player_standardized_carry_potential[team] = []
    print(f"[{team}]")
    for player in player_carry_potential[team]:
        # print player standardized score / # of games played
        print(f"{player}: {(player_carry_potential[team][player]['standardized_score'] / player_carry_potential[team][player]['games_played'])}")
        player_standardized_carry_potential[team].append((player, (player_carry_potential[team][player]['standardized_score'] / player_carry_potential[team][player]['games_played'])))
    print()

# store the player who has highest standardized carry potential + associated # of games played in a txt file called /info/player_most_games.txt
with open('info/player_carry_potential.txt', 'w') as f:
    for team in important_teams:
        f.write(f"[{team}]\n")
        for player, standardized_score in player_standardized_carry_potential[team]:
            f.write(f"{player}: {standardized_score}\n") # write player and standardized score
            f.write(f"Games Played: {player_carry_potential[team][player]['games_played']}\n") # write number of games played for player 
        f.write("\n")

# lowest_points = player_most_games[team][-1][1] ... 0.51
# highest_points = player_most_games[team][0][1] ... 19.95 Kiaya



        



        



                            
                
                            
                            

                    

                    

                

                



       

        
     

        
        

