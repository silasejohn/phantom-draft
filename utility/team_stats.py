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