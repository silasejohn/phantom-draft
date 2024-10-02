from dotenv import load_dotenv
import pandas as pd
import os

def create_multi_league_df():
    """
    Create a dataframe from the data file
    """
    load_dotenv() # Load environment variables from .env file
    data_file_path = os.getenv("MULTI_LEAGUE_DATA")
    df = pd.read_csv(data_file_path)
    return df

def unique_leagues(multi_league_df):
    """
    Identify unique leagues in the multi-league dataframe
    """
    leagues = multi_league_df['league'].unique()
    return leagues

def unique_splits(multi_league_df, league_name):
    """
    Identify unique splits in a single league from the multi-league dataframe
    """
    df = multi_league_df[multi_league_df['league'] == league_name]
    splits = df['split'].unique()
    return splits

def total_games(multi_league_df, league_name):
    """
    Identify total number of games in a single league from the multi-league dataframe
    """
    df = multi_league_df[multi_league_df['league'] == league_name]
    return len(df)

def unique_teams(multi_league_df, league_name):
    """
    Identify unique teams in a single league from the multi-league dataframe
    """
    # what are all the unique values in column team_name, prevent duplicates
    df = multi_league_df[multi_league_df['league'] == league_name]
    teams = df['teamname'].unique()
    return teams

def create_single_league_df(multi_league_df, league_name):
    """
    Create a dataframe for a single league from the multi-league dataframe
    """
    df = multi_league_df[multi_league_df['league'] == league_name]
    return df

def create_single_team_df(multi_league_df, team_name):
    """
    Create a dataframe for a single team from the multi-league dataframe
    """
    df = multi_league_df[multi_league_df['teamname'] == team_name]
    return df

def create_single_split_team_df(multi_league_df, team_name, split_name, league_name):
    """
    Create a dataframe for a single team per split per playoffs from the multi-league dataframe
    """

    # find all unique gameid values for a team in a split and add to a list
    df = multi_league_df[(multi_league_df['teamname'] == team_name) & (multi_league_df['split'] == split_name) & (multi_league_df['league'] == league_name)]

    # find all unique gameid values in df
    gameids = df['gameid'].unique()

    # for all gameids in the list, find all rows in the multi_league_df that have that gameid and create new df
    split_df = pd.DataFrame()
    for gameid in gameids:
        game_df = multi_league_df[multi_league_df['gameid'] == gameid]
        split_df = pd.concat([split_df, game_df])
    
    # if row in split_df is not a playoff game, add to new df
    non_playoff_split_df = split_df[split_df['playoffs'] == 0]

    # if row in split_df is a playoff game, add to new df
    playoff_split_df = split_df[split_df['playoffs'] == 1]

    return non_playoff_split_df, playoff_split_df
    
def export_df_to_csv(df, filename):
    """
    Export a dataframe to a csv file
    """
    df.to_csv(filename) #, index=False) # index=False to avoid writing row numbers
    