from league_stats import create_multi_league_df, create_single_league_df, export_df_to_csv

# Create a multi-league dataframe
multi_league_df = create_multi_league_df()

# Create a single league dataframe for each league 
# and export to a csv file in the data/league_data folder
leagues = multi_league_df['league'].unique()
for league in leagues:
    league_df = create_single_league_df(multi_league_df, league)
    export_df_to_csv(league_df, f'data/league_data/{league}_league.csv')

