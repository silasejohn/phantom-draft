import pandas as pd

def find_leagues_given_team(multi_league_df, team_name):
    """
    Identify leagues in which a team has participated
    """
    df = multi_league_df[multi_league_df['teamname'] == team_name]
    leagues = df['league'].unique()
    return leagues

def find_splits_given_team(multi_league_df, team_name):
    """
    Identify splits in which a team has participated
    """
    df = multi_league_df[multi_league_df['teamname'] == team_name]
    splits = df['split'].unique()
    return splits

def find_unique_players_and_positions_given_team(multi_league_df, team_name):
    """
    Identify unique players in a team
    """
    df = multi_league_df[multi_league_df['teamname'] == team_name]
    non_unique_players = df['playername']
    non_unique_positions = df['position']
    # create new string of format {playername}-{position}
    players = [f"{player}-{position}" for player, position in zip(non_unique_players, non_unique_positions)]
    # find unique values in the list
    players = list(set(players))
    return players
