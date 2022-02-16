"""
A module to calculate additional baseball statistics based on results produced with ncaa_scrape module

created by Nathan Blumenfeld for Cornell Baseball
"""
import pandas as pd
import numpy as np
from cornellbaseball import ncaa_scrape


# filepath of D1 linear weights
LW_FILEPATH = 'data/guts/ncaa_d1_woba_linear_weights.csv' # <-- Robert Fray's Linear Weights

# number of decimal places to round floats to 
ROUND_TO = 3

def calculate_pa(player_row):
    """
    Returns (int): the number of plate appearances by a given player based on the following formula: 
    
    PA = AB + BB + SF + SH + HBP - IBB
    """    
    PA = player_row['AB'] + player_row['BB'] + player_row['SF'] + player_row['SH'] + player_row['HBP'] - player_row['IBB']
    return PA

def calculate_singles(player_row):
    """
    Returns (int): the number of singles by a given player based on the following formula: 

    1B = H - 2B - 3B - HR
    """
    singles = player_row['H'] - player_row['2B'] - player_row['3B'] - player_row['HR']
    return singles

def calculate_woba(player_row, weights_df, round_to = ROUND_TO):
    """
    Returns (float): the weighted on base average of a given player based on the following formula: 

    wOBA = (wBB×uBB + wHBP×HBP + w1B×1B + w2B×2B + w3B×3B +
    wHR×HR) / PA
    """
    # get linear weights for given season
    weights_row = weights_df.loc[weights_df.Season == player_row['season']]
    # to avoid div by zero
    if not player_row['PA'] == 0:
        woba = ((weights_row['wBB'] * player_row['BB']
                + weights_row['wHBP'] * player_row['HBP']
                + weights_row['w1B'] * player_row['1B']
                + weights_row['w2B'] * player_row['2B']
                + weights_row['w3B'] * player_row['3B']
                + weights_row['wHR'] * player_row['HR']) / player_row['PA'])
        try:
            woba = woba.iloc[0]
        except:
            print(player_row['stats_player_seq'])
    else: 
        woba = 0.00
    return round(woba, round_to)

def calculate_wraa(player_row, weights_df, round_to = ROUND_TO):
    """
    Returns (float): the weighted runs created above average of a given player based on the following formula: 

    wRAA = [(wOBA − leagueWOBA) / wOBAscale] ∗ PA
    """
    # get linear weights for given season
    weights_row = weights_df.loc[weights_df.Season == player_row['season']]
    if not player_row['PA'] == 0:
        wraa = (((player_row['wOBA'] - weights_row['wOBA']) / weights_row['wOBAScale']) * player_row['PA'])
        try:
            wraa = wraa.iloc[0]
        except: 
            print(player_row['stats_player_seq'])
            wraa = 0.00
    else:
        wraa = 0.00
    return round(wraa, round_to)

def calculate_wrc(player_row, weights_df, round_to = ROUND_TO):
    """
    Returns (float): the weighted runs created of a given player based on the following formula: 

    wRC = [((wOBA - lgwOBA) / wOBAScale) + (lgR / PA))] * PA
    """
    weights_row = weights_df.loc[weights_df.Season == player_row['season']]
    if not player_row['PA'] == 0:
        wrc = (((player_row['wOBA'] - weights_row['wOBA']) / weights_row['wOBAScale']) + weights_row['R/PA']) * player_row['PA']
        try:
            wrc = wrc.iloc[0]
        except:
            print(player_row['stats_player_seq'])
            wrc = 0.00
    else: 
        wrc = 0.00
    return round(wrc, round_to)

def add_columns(df, lw_filepath = LW_FILEPATH):
    """
    Adds the following columns to a given DataFrame:
    
    PA 
    1B 
    wOBA
    wRAA
    wRC
    """
    lw = pd.read_csv(lw_filepath)
    df.loc[:, 'PA'] = df.apply(lambda x: calculate_pa(x), axis = 1)
    df.loc[:, '1B'] = df.apply(lambda x: calculate_singles(x), axis = 1)
    df.loc[:, 'wOBA'] = df.apply(lambda x: calculate_woba(x, weights_df = lw), axis = 1)
    df.loc[:, 'wRAA'] = df.apply(lambda x: calculate_wraa(x, weights_df = lw), axis = 1)
    df.loc[:, 'wRC'] = df.apply(lambda x: calculate_wrc(x, weights_df = lw), axis = 1)
    return df