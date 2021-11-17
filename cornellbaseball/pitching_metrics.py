import pandas as pd
import numpy as np

# GLOBAL VARIABLES
# filepath of Cornell individual season totals
STATS_FILEPATH = "data/cornell/cornell_pitching_individual_season_totals_2015_to_2020.xlsx"

# filepath of D1 linear weights
LW_FILEPATH = "data/ncaa_d1_woba_linear_weights.csv"
# default number of places to round to 
ROUND_TO = 3
# FIP Weights
FIP_HR_WEIGHT = 13
FIP_BB_WEIGHT = 3
FIP_K_WEIGHT = 2 

def get_season_totals(player_id, season, stats_filepath=STATS_FILEPATH):
    """
    A helper function to filter and prepare data for downstream calcuations
    Returns: pandas.DataFrame object

    """
    res = (pd.read_excel(stats_filepath)
                      .query(f"""player_id=={player_id}""")
                      .query(f"""season=={season}""")
                      .fillna(0)
                     )
    return res

def get_fip(player_id, season, stats_filepath=STATS_FILEPATH, lw_filepath=LW_FILEPATH, round_to=ROUND_TO, hr_weight=FIP_HR_WEIGHT, bb_weight=FIP_BB_WEIGHT, k_weight=FIP_K_WEIGHT):
    """
    Returns: Fielding Independent Pitching for a given player in a given season
    
    FIP = ((13 * HR)+(3 * (BB + HBP))-(2 * K))/IP + constant
    FIP Constant = lgERA – (((13 * lgHR) + (3 * (lgBB+lgHBP))-(2 * lgK))/ lgIP)

    Parameter player_id: The ID of player to return for
    Precondition: player_id is an int
    Parameter year: The season to return wRC for 
    Precondition: year is an int
    """
    data = get_season_totals(player_id, season, stats_filepath)
    strike_outs = data["SO"].values[0]
    hit_batters = data["HB"].values[0]
    walks_given = data["BB"].values[0]
    home_runs_allowed = data["HR-A"].values[0]
    strike_outs = data["IP"].values[0]
    season_weights = (pd.read_csv(lw_filepath)
                      .query(f"""Season=={season}""")
                     )
    fip_constant = season_weights["cFIP"].values[0]
    if strike_outs <= 0: 
        print(f"""warning: player {player_id} has no recorded strikeouts in {season}, cannot calculate FIP""")
        res = 0
    res = (((hr_weight*home_runs_allowed)+(bb_weight*(walks_given+hit_batters))-(k_weight*strike_outs))/strike_outs)+fip_constant
    return round(res, round_to)

def get_era(player_id, season, stats_filepath=STATS_FILEPATH, lw_filepath=LW_FILEPATH, round_to=ROUND_TO): 
    """
    Returns: ERA for a given player in a given season 
    
    Parameter player_id: The ID of player to return for
    Precondition: player_id is 
    Parameter year: The season to return wRC for 
    Precondition: year is an INT 
    """
    data = get_season_totals(player_id, season, stats_filepath)
    res = data["ERA"].values[0]
    return round(res, round_to)
                      
def get_runs_per_ip(player_id, season, stats_filepath=STATS_FILEPATH, lw_filepath=LW_FILEPATH, round_to=ROUND_TO): 
    """
    Returns: runs per innings pitched
    
    runs allowed / innings pitched
    """
    data = get_season_totals(player_id, season, stats_filepath)
    runs_allowed = data["R"].values[0]
    innings_pitched = data["IP"].values[0]
    if innings_pitched <= 0: 
        res = 0 
    else: 
        res = runs_allowed/innings_pitched
    return round(res, round_to)

def get_whip(player_id, season, stats_filepath=STATS_FILEPATH, lw_filepath=LW_FILEPATH, round_to=ROUND_TO): 
    """
    Returns: WHIP: walks and hits per innings pitched
    WHIP = (BB+H)/IP
    runs allowed / innings pitched
    """
    data = get_season_totals(player_id, season, stats_filepath)
    walks = data["BB"].values[0]
    hits = data["H"].values[0]
    raw_ip = data["IP"].values[0]
    ip = round(raw_ip,0)+((raw_ip-raw_ip)*3.3)
    # properly scale IP by multiplying number after decimal point by .33
    if ip <= 0: 
        res = 0 
        print(f"""no records found for {player_id} in {season}""")
    else:
        # WHIP = (BB+H)/IP
        res = round((walks+hits)/ip, round_to)
    return res

# CALCULATE BATTING METRICS PER PLAYER PER SEASON 
def get_cornell_pitching_stats(stats_filepath=STATS_FILEPATH, lw_filepath=LW_FILEPATH, round_to=ROUND_TO, hr_weight=FIP_HR_WEIGHT, bb_weight=FIP_BB_WEIGHT, k_weight=FIP_K_WEIGHT):
    """
    Returns: DataFrame()
    """
    data = (pd.read_excel(stats_filepath)
                   .fillna(0)
           )
    # properly scale IP by multiplying number after decimal point by .33
    data["IP"] = round(data["IP"],0)+((data["IP"]-round(data["IP"],0))*3.3)
    linear_weights = (pd.read_csv(lw_filepath)
                                      .rename(columns={"Season":"season"})
                                      .loc[:,["cFIP", "season"]]
                     )
    df = pd.merge(data, linear_weights, on="season",how="left")
    #  cFIP = lgERA – (((13 * lgHR) + (3 * (lgBB+lgHBP))-(2 * lgK))/ lgIP)
    #  FIP = ((13 * HR)+(3 * (BB + HBP))-(2 * K))/IP + cFIP
    df["FIP"] = round(((((hr_weight*df["HR-A"])+(bb_weight*(df["BB"]+df["HB"]))-(k_weight*df["SO"]))/df["IP"]).replace(np.inf, 0)+df["cFIP"]),round_to)
    df["WHIP"] = round(((df["BB"]+df["H"])/df["IP"]),round_to) 
    return df.sort_values(by="FIP", ascending=True)