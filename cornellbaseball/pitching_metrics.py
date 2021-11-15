import pandas as pd
import numpy as np

# GLOBAL VARIABLES
# filepath of Cornell individual season totals
STATS_FILEPATH = "data/cornell/cornell_pitching_individual_season_totals_2015_to_2020.xlsx"
# filepath of D1 linear weights
LW_FILEPATH = "data/ncaa_d1_woba_linear_weights.csv"
# default number of places to round to 
ROUND_TO = 3

def get_fip(player_id, season, stats_filepath=STATS_FILEPATH, lw_filepath=LW_FILEPATH, round_to=ROUND_TO):
    """
    Returns: Fielding Independent Pitching for a given player in a given season
    
    FIP = ((13 * HR)+(3 * (BB + HBP))-(2 * K))/IP + constant
    FIP Constant = lgERA – (((13 * lgHR) + (3 * (lgBB+lgHBP))-(2 * lgK))/ lgIP)

    Parameter player_id: The ID of player to return for
    Precondition: player_id is an int
    Parameter year: The season to return wRC for 
    Precondition: year is an int
    """
    player_pitching = (pd.read_excel(stats_filepath)
                      .query(f"""player_id=={player_id}""")
                      .query(f"""season=={season}""")
                      .fillna(0)
                     )
    strike_outs = player_pitching["SO"].values[0]
    hit_batters = player_pitching["HB"].values[0]
    walks_given = player_pitching["BB"].values[0]
    home_runs_allowed = player_pitching["HR-A"].values[0]
    strike_outs = player_pitching["IP"].values[0]
    
    season_weights = (pd.read_csv(lw_filepath)
                      .query(f"""season=={season}""")
                     )
    fip_constant = season_weights["cFIP"].values[0]
    if strike_outs <= 0: 
        print(f"""warning: player {player_id} has no recorded strikeouts in {season}, cannot calculate FIP""")
        res = 0
    res = (((13*home_runs_allowed)+(3*(walks_given+hit_batters))-(2*strike_outs))/strike_outs)+fip_constant
    return round(res, round_to)

def get_era(player_id, season, stats_filepath=STATS_FILEPATH, lw_filepath=LW_FILEPATH, round_to=ROUND_TO): 
    """
    Returns: ERA for a given player in a given season 
    
    Parameter player_id: The ID of player to return for
    Precondition: player_id is 
    Parameter year: The season to return wRC for 
    Precondition: year is an INT 
    """
    player_pitching = (pd.read_excel(stats_filepath)
                      .query(f"""player_id=={player_id}""")
                      .query(f"""season=={season}""")
                      .fillna(0)
                     )
    res = player_pitching["ERA"].values[0]
    return round(res, round_to)
                      
def get_runs_per_ip(player_id, season, stats_filepath=STATS_FILEPATH, lw_filepath=LW_FILEPATH, round_to=ROUND_TO): 
    """
    Returns: runs per innings pitched
    
    runs allowed / innings pitched

    """
    player_pitching = (pd.read_excel(stats_filepath)
                      .query(f"""player_id=={player_id}""")
                      .query(f"""season=={season}""")
                      .fillna(0)
                     )
    runs_allowed = player_pitching["R"].values[0]
    innings_pitched = player_pitching["IP"].values[0]
    if innings_pitched <= 0: 
        res = 0 
    else: 
        res = runs_allowed/innings_pitched
    return round(res, round_to)
