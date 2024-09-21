from dotenv import load_dotenv
import pandas as pd
import csv
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

def find_leagues_given_team(multi_league_df, team_name):
    """
    Identify leagues in which a team has participated
    """
    df = multi_league_df[multi_league_df['teamname'] == team_name]
    leagues = df['league'].unique()
    return leagues

def create_single_league_df(multi_league_df, league_name):
    """
    Create a dataframe for a single league from the multi-league dataframe
    """
    df = multi_league_df[multi_league_df['league'] == league_name]
    return df

def export_df_to_csv(df, filename):
    """
    Export a dataframe to a csv file
    """
    df.to_csv(filename) #, index=False) # index=False to avoid writing row numbers
    