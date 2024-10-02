from league_stats import create_multi_league_df, create_single_league_df, export_df_to_csv, create_single_split_team_df
from team_stats import find_leagues_given_team, find_splits_given_team, find_unique_players_and_positions_given_team
import pandas as pd
import numpy as np
import json
import os
import shutil
import sys

# LIST of unique league names
UNIQ_LEAGUE_NAMES = [] 

# LIST of directory paths to clean
DIRECTORY_PATHS = ['data/01_league_data/', 'data/02_league_team_split_playoffs_data/', 'data/03_data_trimmed_02_league_team_split_playoffs_data/', 'data/04_swiss_team_data_cleaned/', 'data/05_swiss_team_score_calcs/', 'data/06_swiss_team_scores_combined/']
NECESSARY_HEADERS = ['gameid', 'league', 'split', 'playoffs', 'game', 'series_num', 'participantid', 'position', 'playername', 'teamname', 'champion', 'gamelength', 'result', 'kills', 'assists', 'deaths', 'firstblood', 'dragons', 'heralds', 'barons', 'towers', 'total cs']
PLAYINS_EXCLUDE_PLAYERS = ['Fireblade-top', 'Kratos-top', 'Tomrio-jng', 'SofM-sup', 'Kairi-sup', 'Blazes-mid', 'Pyshiro-bot', 'Neo-bot', 'Meech-bot', 'Keine-top', 'Summit-jng', 'Daiky-jng', 'Lava-mid', 'Ceo-mid', 'Lyonz-bot', 'Oddie-sup']
SWISS_EXCLUDE_PLAYERS = ['Zdz-top', 'Youdang-jng', 'Xiaohao-jng', 'XBear-sup', 'Mark-sup', 'Xun-jng', 'Guwon-jng', 'Kellin-sup', 'Jensen-mid', 'Blazes-mid', 'Neo-bot', 'Pyshiro-bot']

# DICTIONARY of (keys) league (values) [ dictionary of (keys) team names (values) list of splits ]
UNIQ_LEAGUE_TEAM_SPLITS = {} 

# LIST of play_ins_teams
PLAY_INS_TEAMS = ['PSG Talon', 'Fukuoka SoftBank HAWKS gaming', 'Vikings Esports', 'GAM Esports', '100 Thieves', 'MAD Lions KOI', 'paiN Gaming', 'Movistar R7']

# LIST of swiss_teams / leagues
MAIN_LEAGUES = ['LCS', 'LEC', 'LCK', 'LPL', 'PCS', 'VCS', 'CBLOL', 'LLA']
SWISS_LEAGUES = ['LCS', 'LEC', 'LCK', 'LPL', 'WLDs', 'EWC', 'MSI']
SWISS_TEAMS = ['Bilibili Gaming', 'Weibo Gaming', 'LNG Esports', 'Top Esports',  # LPL
               'T1', 'Dplus KIA', 'Gen.G', 'Hanwha Life Esports',               # LCK
               'FlyQuest', 'Fnatic', 'Team Liquid', 'G2 Esports',               # LCS / LEC
               'MAD Lions KOI', 'paiN Gaming', 'PSG Talon', 'GAM Esports']      # WLDs (Play-Ins)
SWISS_TEAM_ID = ['WBG', 'LNG', 'TES', 'BLG', 
                 'T1', 'DK', 'GEN', 'HLE', 
                 'FLY', 'FNC', 'TL', 'G2', 
                 'MAD', 'PNG', 'PSG', 'GAM']
SWISS_TEAM_LEAGUES = {} # dictionary with (keys) team names (values) list of leagues

# INFO Data Structurs
INFO_TEAMS = {}
for team in SWISS_TEAMS:
    INFO_TEAMS[team] = [[],[],[]] # stores Leagues[], Splits[], Player-Pos[]

# Clean Directories Function
# Purpose: Deletes all CSV files from specified directories
def clean_directories(directory_paths):
    for directory in directory_paths:
        for filename in os.listdir(directory):
            
            # file path to delete
            file_path = os.path.join(directory, filename)
            
            # delete the file if it is a csv file
            if filename.endswith('.csv'):
                os.remove(file_path)

            # delete the directory if it is a folder
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

# Check & Create Directory (if not exist)
# Check and create directory if it doesn't exist
def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

# Custom Role Sorting Funciton
# Purpose: Sorts the roles in the order of 'top', 'jng', 'mid', 'bot', 'sup'
def custom_role_sort_key(item):
    priority_list = ['top', 'jng', 'mid', 'bot', 'sup']
    pos = item.split('-')[1]
    # print("Item:", item, " - Position:", pos, " - Index:", priority_list.index(pos) if pos in priority_list else len(priority_list))
    return priority_list.index(pos) if pos in priority_list else len(priority_list)

# Purpose: Convert an alphabetical string to a numerical value
def alpha_to_num(s):
    result = 0
    for char in s:
        result = result * 26 + (ord(char) - ord('A') + 1)
    return result

##################################################################################################################
# clean_directories(DIRECTORY_PATHS) 
# sys.exit()
##################################################################################################################

##############################################
### [0] Create Multi-League Data DataFrame ###
##############################################
multi_league_df = create_multi_league_df()

# add a split value of "LPL_WLDs" to every game before 2024-09-03
# add a split value of "LCK_WLDs" to every game before 2024-09-14
# add a split value of "Playins" to every game after 2024-09-14
multi_league_df.loc[(multi_league_df['league'] == "WLDs") & (multi_league_df['date'] < "2024-09-20"), 'split'] = "WLDs"
# multi_league_df.loc[(multi_league_df['league'] == "WLDs") & (multi_league_df['date'] < "2024-09-03"), 'split'] = "LPL_WLDs"
multi_league_df.loc[(multi_league_df['league'] == "WLDs") & (multi_league_df['date'] >= "2024-09-20"), 'split'] = "Playins"

# delete all leagues of 'DCup' from the multi_league_df
multi_league_df = multi_league_df[multi_league_df['league'] != 'DCup']

# add a split value of "EWC" to every row with a league of "EWC"
multi_league_df.loc[multi_league_df['league'] == "EWC", 'split'] = "EWC"

# add a split value of "MSI" to every row with a league of "MSI"
multi_league_df.loc[multi_league_df['league'] == "MSI", 'split'] = "MSI"

# # print df.head() for each league for teamname='PSG Talon'
# team = 'PSG Talon'
# for league in find_leagues_given_team(multi_league_df, team):
#     print(f"\n{league} - PSG Talon")
#     print(multi_league_df[(multi_league_df['league'] == league) & (multi_league_df['teamname'] == 'PSG Talon')].head())

# sys.exit()

# give me a list of teams that competed in 'EWC'
ewc_teams = multi_league_df[multi_league_df['league'] == 'EWC']['teamname'].unique()
# print("\n")
# print(ewc_teams)
# print("EWC Teams:", len(ewc_teams))

print("\n")
# for every team in 'EWC', identify all leagues they competed in
for team in ewc_teams:
    temp_leagues = find_leagues_given_team(multi_league_df, team)
    # print(f"[EWC] Leagues for {team}:", temp_leagues)

    # find the league in temp_leagues that is also in MAIN_LEAGUES
    main_league = None
    for league in temp_leagues:
        if league in MAIN_LEAGUES:
            main_league = league
            # print(f"Main League for {team}:", main_league)

    # for this team, replace all 'EWC' leagues with the main_league
    multi_league_df.loc[(multi_league_df['league'] == 'EWC') & (multi_league_df['teamname'] == team), 'league'] = main_league

    temp_leagues = find_leagues_given_team(multi_league_df, team)
    # print(f"[EWC] Leagues for {team}:", temp_leagues)

# print("\n")
# give me a list of teams that competed in 'MSI'
msi_teams = multi_league_df[multi_league_df['league'] == 'MSI']['teamname'].unique()
# print(msi_teams)
# print("MSI Teams:", len(msi_teams))

# print("\n")
for team in msi_teams:
    temp_leagues = find_leagues_given_team(multi_league_df, team)
    # print(f"[MSI] Leagues for {team}:", temp_leagues)

    # find the league in temp_leagues that is also in MAIN_LEAGUES
    main_league = None
    for league in temp_leagues:
        if league in MAIN_LEAGUES:
            main_league = league
            # print(f"Main League for {team}:", main_league)

    # for this team, replace all 'MSI' leagues with the main_league
    multi_league_df.loc[(multi_league_df['league'] == 'MSI') & (multi_league_df['teamname'] == team), 'league'] = main_league
    
    temp_leagues = find_leagues_given_team(multi_league_df, team)
    # print(f"[MSI] Leagues for {team}:", temp_leagues)

# give me a list of teams that competed in 'WLDs'
# print("\n")
wlds_teams = multi_league_df[multi_league_df['league'] == 'WLDs']['teamname'].unique()
# print(wlds_teams)
# print("WLDs Teams:", len(wlds_teams))

# print("\n")
for team in wlds_teams:
    temp_leagues = find_leagues_given_team(multi_league_df, team)
    # print(f"[WLDs] Leagues for {team}:", temp_leagues)
    # find the league in temp_leagues that is also in MAIN_LEAGUES
    main_league = None
    for league in temp_leagues:
        if league in MAIN_LEAGUES:
            main_league = league
            # print(f"Main League for {team}:", main_league)

    # for this team, replace all 'EWC' leagues with the main_league
    multi_league_df.loc[(multi_league_df['league'] == 'WLDs') & (multi_league_df['teamname'] == team), 'league'] = main_league
    
    temp_leagues = find_leagues_given_team(multi_league_df, team)
    # print(f"[WLDs] Leagues for {team}:", temp_leagues)

######################################################
### [1] Export CSVs for League-Specific DataFrames ###
######################################################

# identify unique league names
leagues = multi_league_df['league'].unique()
UNIQ_LEAGUE_NAMES = leagues # store in global variable

# identify unique team names by region 
for league in UNIQ_LEAGUE_NAMES:
    unique_teams = multi_league_df[multi_league_df['league'] == league]['teamname'].unique()
    # create a dictionary with teamnames as keys and splits as values
    UNIQ_LEAGUE_TEAM_SPLITS[league] = {}
    for team in unique_teams:
        splits = multi_league_df[(multi_league_df['league'] == league) & (multi_league_df['teamname'] == team)]['split'].unique()
        UNIQ_LEAGUE_TEAM_SPLITS[league][team] = splits

# iterate through leagues
for league in SWISS_LEAGUES:
    league_df = create_single_league_df(multi_league_df, league)
    export_df_to_csv(league_df, f'data/01_league_data/{league}_league.csv')

###############################################################
### [2] Export CSVs for {League}{Team}{Split}{Playoffs} DFs ###
###############################################################

# find leagues each SWISS_TEAM has been in
for team in SWISS_TEAMS:
    SWISS_TEAM_LEAGUES[team] = find_leagues_given_team(multi_league_df, team)

for team in SWISS_TEAM_LEAGUES: # iterate through all SWISS_TEAMS

    for league in SWISS_TEAM_LEAGUES[team]: # iterate through all leagues for each SWISS_TEAM
        
        # skip if league is not in SWISS_LEAGUES
        if league not in SWISS_LEAGUES:
            continue
        
        # initialize series_num to "~" 
        series_num = "~"

        for split in UNIQ_LEAGUE_TEAM_SPLITS[league][team]: # iterate through all splits for each SWISS_TEAM in each league
            
            print(f"Exporting {team} in {league} {split}...")

            # sanity check for NaN values (except WLDs)
            if pd.isna(split):
                continue

            # create a dataframe for a single team per league per split per playoffs from the multi-league dataframe
            non_playoff_df, playoff_df = create_single_split_team_df(multi_league_df, team, split, league)

            # export to csv for non-playoff games
            if not non_playoff_df.empty:
                
                # logic to determine series_num for each game - find unique gameids
                unique_gameids = non_playoff_df['gameid'].unique() 

                 # add series_num to the dataframe before "game_num" header
                non_playoff_df.insert(4, 'series_num', series_num)
                
                # iterate through all unique gameids
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

                # determine team_id by index 
                team_id = SWISS_TEAM_ID[SWISS_TEAMS.index(team)]
                non_playoff_filename = f"{league}_{team_id}_{split}.csv"
                non_playoff_df.to_csv(f"data/02_league_team_split_playoffs_data/{non_playoff_filename}", index=False)

            # export to csv for playoff games
            if not playoff_df.empty:
                # logic to determine series_num for each game - find unique gameids
                unique_gameids = playoff_df['gameid'].unique() 

                # add series_num to the dataframe before "game_num" header
                playoff_df.insert(4, 'series_num', series_num) 

                # iterate through all unique gameids
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

                team_id = SWISS_TEAM_ID[SWISS_TEAMS.index(team)]
                playoff_filename = f"{league}_{team_id}_{split}_Playoffs.csv"
                playoff_df.to_csv(f"data/02_league_team_split_playoffs_data/{playoff_filename}", index=False)


#########################################
### [3] Data Trimmed CSVs for Fantasy ###
#########################################

# go through every csv in /data/02_league_team_split_playoffs_data folder and create a new csv file in /data/03_data_trimmed_02_league_team_split_playoffs_data folder
for filename in os.listdir('data/02_league_team_split_playoffs_data'): # relative path

    # if the file is a csv file
    if filename.endswith('.csv'):
        # keep only the columns that are needed for fantasy
        df = pd.read_csv(f'data/02_league_team_split_playoffs_data/{filename}')
        df = df[NECESSARY_HEADERS]

        # extract team name from filename
        team_id = filename.split('_')[1]

        # create directory for each SWISS_TEAM
        folder_path = f'data/03_data_trimmed_02_league_team_split_playoffs_data/{team_id}'
        ensure_directory_exists(folder_path) # create directory if it doesn't exist
        df.to_csv(f'{folder_path}/{filename}', index=False)

##################################
### [I1] SWISS TEAMS + PLAYERS ### 
##################################

# create an team_info.txt file in data/team_data with the teamname and players on the team
with open('info/swiss_teams.txt', 'w') as f:
    for team in SWISS_TEAMS:

        # find unique players and positions for a team
        player_and_positions = find_unique_players_and_positions_given_team(multi_league_df, team)

        # list comprehension to remove team positions and NaN values
        unique_players_and_positions = [single_player_pos for single_player_pos in player_and_positions if single_player_pos.split('-')[1] != "team" and not pd.isna(single_player_pos.split('-')[0])]

        # reorganize the list of unique players and positions such that single_player_pos.split('-')[1] values are sorted with all the "top" players first, then "jng", "mid", "bot", and "sup"
        sorted_unique_players_and_positions = sorted(unique_players_and_positions, key=custom_role_sort_key)

        # write to file
        f.write(f"[{team}]\n")
        INFO_TEAMS[team][0] = SWISS_TEAM_LEAGUES[team]
        f.write(f"Leagues: {SWISS_TEAM_LEAGUES[team]}\n")
        
        team_splits = []
        for league in SWISS_TEAM_LEAGUES[team]:
            for split in UNIQ_LEAGUE_TEAM_SPLITS[league][team]:
                team_splits.append(split)

        INFO_TEAMS[team][1] = team_splits
        f.write(f"Splits: {team_splits}\n")
        for player_pos in sorted_unique_players_and_positions:
            # hard coded in due to specific players being in different roles at Worlds
            if player_pos in SWISS_EXCLUDE_PLAYERS:
                continue
            INFO_TEAMS[team][2].append(player_pos)
            f.write(f"\n{player_pos}")
        f.write(f"\n\n\n")


###########################################
### [I2] SWISS TEAMS GAME / SERIES INFO ### 
###########################################
# for every csv in /data/team_data folder, find total number of unique gameids per csv and print
output = []
for filename in os.listdir('data/02_league_team_split_playoffs_data'): # relative path
    if filename.endswith('.csv'):
        df = pd.read_csv(f'data/02_league_team_split_playoffs_data/{filename}')
        
        # store all unique gameids in a list
        unique_gameids = df['gameid'].unique() 

        # find number of unique gameids
        num_unique_gameids = df['gameid'].nunique()

        # find unique gameids for when game is '1'
        num_unique_series = df[df['game'] == 1]['gameid'].nunique()

        # split filename by "_" ... [league, team, split, playoffs]
        filename_parts = filename.split('_')
       
        if len(filename_parts) == 4: # if playoffs is in the filename
            league = filename_parts[0]
            team = filename_parts[1]
            split = filename_parts[2]
            playoffs = filename_parts[3].split('.')[0]
            output_msg = f"[{league}] [{team}] [{split} {playoffs}] {num_unique_gameids} unique gameids ({num_unique_series} series)"
            output.append(output_msg)
        elif len(filename_parts) == 3: # if playoffs is not in the filename
            league = filename_parts[0]
            team = filename_parts[1]
            split = filename_parts[2].split('.')[0]
            output_msg = f"[{league}] [{team}] [{split}] {num_unique_gameids} unique gameids ({num_unique_series} series)"
            output.append(output_msg)

# sort the output list alphabetically
output.sort()

# store output list in a txt file called /info/playins_history.txt
with open('info/swiss_history.txt', 'w') as f:
    for item in output:
        f.write(f"{item}\n")
    f.write("\n")

################################################ 
### [4] Clean Swiss Team Data into Game Rows ###
################################################

for directory in os.listdir('data/03_data_trimmed_02_league_team_split_playoffs_data'): # relative path
    if os.path.isdir(f'data/03_data_trimmed_02_league_team_split_playoffs_data/{directory}'):
        for filename in os.listdir(f'data/03_data_trimmed_02_league_team_split_playoffs_data/{directory}'):
            if filename.endswith('.csv'):

                # create new csv file in /data/04_swiss_team_data_cleaned/{directory}/{filename}
                # create directory for each SWISS_TEAM
                folder_path = f'data/04_swiss_team_data_cleaned/{directory}'
                ensure_directory_exists(folder_path) # create directory if it doesn't exist
                # df.to_csv(f'{folder_path}/{filename}', index=False)
                with open(f'data/04_swiss_team_data_cleaned/{directory}/{filename}', 'w') as f:
                    # write the header
                    f.write("gameid,league,split,playoffs,series_num,game_num,ego_team,opp_team,gamelength,top_player,top_champion,top_primary_kills,top_primary_deaths,top_primary_assists,top_primary_total_cs,jgl_player,jgl_champion,jgl_primary_kills,jgl_primary_deaths,jgl_primary_assists,jgl_primary_total_cs,mid_player,mid_champion,mid_primary_kills,mid_primary_deaths,mid_primary_assists,mid_primary_total_cs,bot_player,bot_champion,bot_primary_kills,bot_primary_deaths,bot_primary_assists,bot_primary_total_cs,sup_player,sup_champion,sup_primary_kills,sup_primary_deaths,sup_primary_assists,sup_primary_total_cs,constant_turrets,constant_dragons,constant_heralds,constant_barons,constant_win,constant_win_under_30,constant_first_blood\n")

                    df = pd.read_csv(f'data/03_data_trimmed_02_league_team_split_playoffs_data/{directory}/{filename}')
                    team_id = filename.split('_')[1]
                    team_name = SWISS_TEAMS[SWISS_TEAM_ID.index(team_id)] # find the team name from the team_id

                    total_games = df['gameid'].nunique()

                    # find unique gameids 
                    unique_gameids = df['gameid'].unique()

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

###################################################
### [05] Swiss Team Point Calculation / Storage ### 
###################################################

# Load the multi-nested JSON object
with open('info/static_vals.json') as json_file:
    fantasy_static_vals = json.load(json_file)

match_pts_info = {}

# calculate points / make new spreadsheet per team in play-ins for their score
for directory in os.listdir('data/04_swiss_team_data_cleaned'): # relative path
    if os.path.isdir(f'data/04_swiss_team_data_cleaned/{directory}'):
        for filename in os.listdir(f'data/04_swiss_team_data_cleaned/{directory}'):
            if filename.endswith('.csv'):

                # create new csv file in /data/05_swiss_team_score_calcs/{directory}/{filename}
                new_filename = filename.split('.')[0] + "_pts.csv"
                

                # create new csv file in /data/05_swiss_team_score_calcs/{directory}/{filename}
                folder_path = f'data/05_swiss_team_score_calcs/{directory}'
                ensure_directory_exists(folder_path) # create directory if it doesn't exist
                with open(f'data/05_swiss_team_score_calcs/{directory}/{new_filename}', 'w') as f:
                    # write the header
                    f.write("gameid,league,split,playoffs,series_num,game_num,ego_team,opp_team,gamelength,top_player,top_champion,top_primary_kills,top_primary_kill_pts,top_primary_deaths,top_primary_death_pts,top_primary_assists,top_primary_assists_pts,top_primary_total_cs,top_primary_total_cs_pts,jgl_player,jgl_champion,jgl_primary_kills,jgl_primary_kills_pts,jgl_primary_deaths,jgl_primary_deaths_pts,jgl_primary_assists,jgl_primary_assists_pts,jgl_primary_total_cs,jgl_primary_total_cs_pts,mid_player,mid_champion,mid_primary_kills,mid_primary_kills_pts,mid_primary_deaths,mid_primary_deaths_pts,mid_primary_assists,mid_primary_assists_pts,mid_primary_total_cs,mid_primary_total_cs_pts,bot_player,bot_champion,bot_primary_kills,bot_primary_kills_pts,bot_primary_deaths,bot_primary_deaths_pts,bot_primary_assists,bot_primary_assists_pts,bot_primary_total_cs,bot_primary_total_cs_pts,sup_player,sup_champion,sup_primary_kills,sup_primary_kills_pts,sup_primary_deaths,sup_primary_deaths_pts,sup_primary_assists,sup_primary_assists_pts,sup_primary_total_cs,sup_primary_total_cs_pts,constant_turrets,constant_turrets_pts,constant_dragons,constant_dragons_pts,constant_heralds,constant_heralds_pts,constant_barons,constant_barons_pts,constant_win,constant_win_pts,constant_win_under_30,constant_first_blood,constant_first_blood_pts,top_kda_pts,jgl_kda_pts,mid_kda_pts,bot_kda_pts,sup_kda_pts,tdfbh_pts,top_total_pts,jgl_total_pts,mid_total_pts,bot_total_pts,sup_total_pts\n")

                    df = pd.read_csv(f'data/04_swiss_team_data_cleaned/{directory}/{filename}') # read the csv file

                    # extract match info in each gameid in the dataframe
                    # for each row in the dataframe

                    for index, row in df.iterrows():
                        gameid = row['gameid'] 
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

                        # if any value is NaN, set to 0
                        if pd.isna(constant_heralds):
                            constant_heralds = 0

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

                        f.write(f"{gameid},{league},{split},{playoffs},{series_num},{game_num},{ego_team},{opp_team},{gamelength},{top_player},{top_champion},{top_primary_kills},{top_primary_kill_pts},{top_primary_deaths},{top_primary_death_pts},{top_primary_assists},{top_primary_assists_pts},{top_primary_total_cs},{top_primary_total_cs_pts},{jgl_player},{jgl_champion},{jgl_primary_kills},{jgl_primary_kills_pts},{jgl_primary_deaths},{jgl_primary_death_pts},{jgl_primary_assists},{jgl_primary_assists_pts},{jgl_primary_total_cs},{jgl_primary_total_cs_pts},{mid_player},{mid_champion},{mid_primary_kills},{mid_primary_kills_pts},{mid_primary_deaths},{mid_primary_death_pts},{mid_primary_assists},{mid_primary_assists_pts},{mid_primary_total_cs},{mid_primary_total_cs_pts},{bot_player},{bot_champion},{bot_primary_kills},{bot_primary_kills_pts},{bot_primary_deaths},{bot_primary_death_pts},{bot_primary_assists},{bot_primary_assists_pts},{bot_primary_total_cs},{bot_primary_total_cs_pts},{sup_player},{sup_champion},{sup_primary_kills},{sup_primary_kills_pts},{sup_primary_deaths},{sup_primary_death_pts},{sup_primary_assists},{sup_primary_assists_pts},{sup_primary_total_cs},{sup_primary_total_cs_pts},{constant_turrets},{constant_turrets_pts},{constant_dragons},{constant_dragons_pts},{constant_heralds},{constant_heralds_pts},{constant_barons},{constant_barons_pts},{constant_win},{constant_win_pts},{constant_win_under_30},{constant_first_blood},{constant_first_blood_pts},{top_kda_pts},{jgl_kda_pts},{mid_kda_pts},{bot_kda_pts},{sup_kda_pts},{constant_tdfbh_pts},{top_total_pts},{jgl_total_pts},{mid_total_pts},{bot_total_pts},{sup_total_pts}\n")
                
                # import new_filename csv into df 
                df = pd.read_csv(f'data/05_swiss_team_score_calcs/{directory}/{new_filename}')
                
                # create new directory in /data/05_swiss_team_score_calcs/{directory}/{simplified}
                simplified_folder_path = f'data/05_swiss_team_score_calcs/{directory}/simplified'
                ensure_directory_exists(simplified_folder_path) # create directory if it doesn't exist
                new_filename_simplified = filename.split('.')[0] + "_pts_simplified.csv"

                necessary_headers = ['split', 'playoffs', 'series_num', 'game_num', 'ego_team', 'opp_team', 'constant_win', 'top_player', 'jgl_player', 'mid_player', 'bot_player', 'sup_player', 'top_total_pts', 'jgl_total_pts', 'mid_total_pts', 'bot_total_pts', 'sup_total_pts']
                df_simplified = df[necessary_headers]
                df_simplified.to_csv(f'data/05_swiss_team_score_calcs/{directory}/simplified/{new_filename_simplified}', index=False)

#####################################
### [06] Swiss Team Data Combined ###
#####################################

# for each team in SWISS_TEAMS, find all the respective csv files in /data/05_swiss_team_score_calcs and store in a list
team_csv_files = {}
team_csv_files_simplified = {}

for team in SWISS_TEAMS:
    team_id = SWISS_TEAM_ID[SWISS_TEAMS.index(team)]

    if team_id == 'PNG' or team_id == 'GAM' or team_id == 'PSG': # skip these teams
        continue

    team_csv_files[team] = []
    team_csv_files_simplified[team] = []

    for filename in os.listdir(f'data/05_swiss_team_score_calcs/{team_id}'):
        if filename.endswith('.csv'):
            team_csv_files[team].append(filename)
    for filename in os.listdir(f'data/05_swiss_team_score_calcs/{team_id}/simplified'):
        if filename.endswith('.csv'):
            team_csv_files_simplified[team].append(filename)

# for each team in team_csv_files, get a df of each csv file and combine all the dfs into one df for a team
team_combined_df_files = {}
team_combined_df_files_simplified = {}

for team in SWISS_TEAMS:
    team_id = SWISS_TEAM_ID[SWISS_TEAMS.index(team)]
    if team_id == 'PNG' or team_id == 'GAM' or team_id == 'PSG': # skip these teams
        continue
    team_combined_df_files[team] = []
    team_combined_df_files_simplified[team] = []
    for csv_file in team_csv_files[team]:
        df = pd.read_csv(f'data/05_swiss_team_score_calcs/{team_id}/{csv_file}')
        team_combined_df_files[team].append(df)
    for csv_file in team_csv_files_simplified[team]:
        df = pd.read_csv(f'data/05_swiss_team_score_calcs/{team_id}/simplified/{csv_file}')
        team_combined_df_files_simplified[team].append(df)
    
    temp_df = pd.concat(team_combined_df_files[team]) # combine all the dfs into one df    
    team_combined_df_files[team] = temp_df.assign(
        series_num_numeric=temp_df['series_num'].apply(alpha_to_num),  # Convert series_num to a sortable numeric value
        game_num_numeric=temp_df['game_num'].astype(int)  # Convert game_num from string to int
    ).sort_values(by=['series_num_numeric', 'game_num_numeric'])  # Sort by the new numeric columns

    team_combined_df_files[team] = team_combined_df_files[team].drop(columns=['series_num_numeric', 'game_num_numeric']) # drop the numeric columns

    temp_df2 = pd.concat(team_combined_df_files_simplified[team]) # combine all the dfs into one df    
    team_combined_df_files_simplified[team] = temp_df2.assign(
        series_num_numeric=temp_df2['series_num'].apply(alpha_to_num),  # Convert series_num to a sortable numeric value
        game_num_numeric=temp_df2['game_num'].astype(int)  # Convert game_num from string to int
    ).sort_values(by=['series_num_numeric', 'game_num_numeric'])  # Sort by the new numeric columns

    team_combined_df_files_simplified[team] = team_combined_df_files_simplified[team].drop(columns=['series_num_numeric', 'game_num_numeric']) # drop the numeric columns

# create a csv file for each team df in team_combined_df_files and store in /data/06_swiss_team_scores_combined
for team in SWISS_TEAMS:
    team_id = SWISS_TEAM_ID[SWISS_TEAMS.index(team)]
    if team_id == 'PNG' or team_id == 'GAM' or team_id == 'PSG': # skip these teams
        continue
    
    # full version
    team_combined_df_files[team].to_csv(f'data/06_swiss_team_scores_combined/{team_id}_combined.csv', index=False)
    
    # simplified version
    folder_path = f'data/06_swiss_team_scores_combined/simplified'
    ensure_directory_exists(folder_path) # create directory if it doesn't exist
    team_combined_df_files_simplified[team].to_csv(f'data/06_swiss_team_scores_combined/simplified/{team_id}_combined_simplified.csv', index=False)

##############################
### [I3] Swiss Score Stats ###
##############################

# Reference Data: data/06_swiss_team_scores_combined/simplified/{team}_combined_simplified.csv
# Reference Data Structure: INFO_TEAMS
with open('info/swiss_teams_score_summary.txt', 'w') as f:
    for team in SWISS_TEAMS:

        team_id = SWISS_TEAM_ID[SWISS_TEAMS.index(team)]
        if team_id == 'PNG' or team_id == 'GAM' or team_id == 'PSG': # skip these teams
            continue

        # write some basic info about the team
        f.write(f"[{team}]\n")
        f.write(f"Leagues: {INFO_TEAMS[team][0]}\n")
        f.write(f"Splits: {INFO_TEAMS[team][1]}\n")

        df = pd.read_csv(f'data/06_swiss_team_scores_combined/simplified/{team_id}_combined_simplified.csv')
        player_pos = INFO_TEAMS[team][2]
        for item in player_pos:
            # split item by '-'
            player, pos = item.split('-')

            # QOL change for jng -> jgl
            if pos == 'jng': 
                pos = 'jgl'
            
            # find the min, average, max points for player in pos in df (general)
            avg_pts = round(df[f'{pos}_total_pts'].mean(), 4)
            max_pts = round(df[f'{pos}_total_pts'].max(), 4)
            min_pts = round(df[f'{pos}_total_pts'].min(), 4)

            # find the min, average, max points for player in pos in df (during wins)
            avg_pts_wins = round(df[df['constant_win'] == 1][f'{pos}_total_pts'].mean(), 4)
            max_pts_wins = round(df[df['constant_win'] == 1][f'{pos}_total_pts'].max(), 4)
            min_pts_wins = round(df[df['constant_win'] == 1][f'{pos}_total_pts'].min(), 4)

            # find the min, average, max points for player in pos in df (during losses)
            avg_pts_losses = round(df[df['constant_win'] == 0][f'{pos}_total_pts'].mean(), 4)
            max_pts_losses = round(df[df['constant_win'] == 0][f'{pos}_total_pts'].max(), 4)
            min_pts_losses = round(df[df['constant_win'] == 0][f'{pos}_total_pts'].min(), 4)

            f.write(f"\n{player} ({pos})")
            f.write(f"\nGeneral: Min ({min_pts}) ... Avg ({avg_pts}) ... Max ({max_pts})")
            f.write(f"\nWins: Min ({min_pts_wins}) ... Avg ({avg_pts_wins}) ... Max ({max_pts_wins})")
            f.write(f"\nLosses: Min ({min_pts_losses}) ... Avg ({avg_pts_losses}) ... Max ({max_pts_losses})")
            f.write("\n")
        f.write(f"\n\n\n")

##############################################
### [I4] Swiss Score Stats - International ###
##############################################

# Reference Data: data/06_swiss_team_scores_combined/simplified/{team}_combined_simplified.csv
# Reference Data Structure: INFO_TEAMS
with open('info/swiss_teams_score_summary_intl.txt', 'w') as f:
    for team in SWISS_TEAMS:

        team_id = SWISS_TEAM_ID[SWISS_TEAMS.index(team)]
        if team_id == 'PNG' or team_id == 'GAM' or team_id == 'PSG': # skip these teams
            continue

        # write some basic info about the team
        f.write(f"[{team}]\n")
        f.write(f"Leagues: {INFO_TEAMS[team][0]}\n")
        f.write(f"Splits: {INFO_TEAMS[team][1]}\n")

        df = pd.read_csv(f'data/06_swiss_team_scores_combined/simplified/{team_id}_combined_simplified.csv')
        # use subset of df where split is "EWC" or "MSI"
        df = df[(df['split'] == 'EWC') | (df['split'] == 'MSI')]
        if df.empty:
            f.write(f"No international games found for {team}\n")
            f.write(f"\n\n\n")
            continue
        player_pos = INFO_TEAMS[team][2]
        for item in player_pos:
            # split item by '-'
            player, pos = item.split('-')

            # QOL change for jng -> jgl
            if pos == 'jng': 
                pos = 'jgl'
            
            # find the min, average, max points for player in pos in df (general)
            avg_pts = round(df[f'{pos}_total_pts'].mean(), 4)
            max_pts = round(df[f'{pos}_total_pts'].max(), 4)
            min_pts = round(df[f'{pos}_total_pts'].min(), 4)

            # find the min, average, max points for player in pos in df (during wins)
            avg_pts_wins = round(df[df['constant_win'] == 1][f'{pos}_total_pts'].mean(), 4)
            max_pts_wins = round(df[df['constant_win'] == 1][f'{pos}_total_pts'].max(), 4)
            min_pts_wins = round(df[df['constant_win'] == 1][f'{pos}_total_pts'].min(), 4)

            # find the min, average, max points for player in pos in df (during losses)
            avg_pts_losses = round(df[df['constant_win'] == 0][f'{pos}_total_pts'].mean(), 4)
            max_pts_losses = round(df[df['constant_win'] == 0][f'{pos}_total_pts'].max(), 4)
            min_pts_losses = round(df[df['constant_win'] == 0][f'{pos}_total_pts'].min(), 4)

            f.write(f"\n{player} ({pos})")
            f.write(f"\nGeneral: Min ({min_pts}) ... Avg ({avg_pts}) ... Max ({max_pts})")
            f.write(f"\nWins: Min ({min_pts_wins}) ... Avg ({avg_pts_wins}) ... Max ({max_pts_wins})")
            f.write(f"\nLosses: Min ({min_pts_losses}) ... Avg ({avg_pts_losses}) ... Max ({max_pts_losses})")
            f.write("\n")
        f.write(f"\n\n\n")

sys.exit()

### OVERALL STATS
# Position / Player who carries the MOST games
# ON WINS ... rank player / position who carries most + points
# ON LOSSES ... rank player / position who carries most + points

# for each team in csv files in 05_playins_team_score_combined, find the player who carries the most games (aka has the most points)
# you can find the player who carries the most games by looking in the top_total_pts, jgl_total_pts, mid_total_pts, bot_total_pts, sup_total_pts columns
player_point_combos = {}
player_carry_potential = {}

# start by every game for a team, store a list ranking tuple of playername and their respective points for that game
for team in PLAY_INS_TEAMS:
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
for team in PLAY_INS_TEAMS:
    player_standardized_carry_potential[team] = []
    print(f"[{team}]")
    for player in player_carry_potential[team]:
        # print player standardized score / # of games played
        standardized_metric = round(player_carry_potential[team][player]['standardized_score'] / player_carry_potential[team][player]['games_played'], 4)
        print(f"{player}: {standardized_metric}")
        player_standardized_carry_potential[team].append((player, standardized_metric))

    # sort the list in decreasing standardized score order
    player_standardized_carry_potential[team].sort(key=lambda x: x[1], reverse=True)

    print()

# store the player who has highest standardized carry potential + associated # of games played in a txt file called /info/player_most_games.txt
with open('info/player_carry_potential.txt', 'w') as f:
    for team in PLAY_INS_TEAMS:
        f.write(f"[{team}]\n")
        for player, standardized_score in player_standardized_carry_potential[team]:
            f.write(f"{player}: {standardized_score} ... Games ({round(player_carry_potential[team][player]['games_played'], 4)})\n") # write number of games played for player 
        f.write("\n")

# lowest_points = player_most_games[team][-1][1] ... 0.51
# highest_points = player_most_games[team][0][1] ... 19.95 Kiaya



        
# ###################################
# ### [4] Player-Specific Data??? ###
# ###################################
# for directory in os.listdir('data/03_data_trimmed_02_league_team_split_playoffs_data'): # relative path
#     if os.path.isdir(f'data/03_data_trimmed_02_league_team_split_playoffs_data/{directory}'):
#         for filename in os.listdir(f'data/03_data_trimmed_02_league_team_split_playoffs_data/{directory}'):
#             if filename.endswith('.csv'):
#                 df = pd.read_csv(f'data/03_data_trimmed_02_league_team_split_playoffs_data/{directory}/{filename}')
#                 unique_players = df['playername'].unique()
#             for player in unique_players:
#                 # player df is where 'playername' == player and 'teamname' == directory
#                 # directory is the team_id and we need teammane
#                 teamname = SWISS_TEAMS[SWISS_TEAM_ID.index(directory)]
#                 player_df = df[(df['playername'] == player) & (df['teamname'] == teamname)]
#                 if player_df.empty:
#                     continue
#                 player_filename = f"{player}_{filename}"
#                 # create directory for player if it doesn't exist
#                 ensure_directory_exists(f'data/03_data_trimmed_02_league_team_split_playoffs_data/{directory}/{player}')
#                 player_df.to_csv(f'data/03_data_trimmed_02_league_team_split_playoffs_data/{directory}/{player}/{player_filename}', index=False)
# sys.exit()
