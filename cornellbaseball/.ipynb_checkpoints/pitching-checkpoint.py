import pandas as pd
import numpy as np

# filepath of D1 linear weights
LW_FILEPATH = "data/ncaa_d1_woba_linear_weights.csv"
# default number of places to round to 
ROUND_TO = 3
# FIP Weights
FIP_HR_WEIGHT = 13
FIP_BB_WEIGHT = 3
FIP_K_WEIGHT = 2 

def calculate_fip(player_row):
    """
    """
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

    pass

def calculate_era(player_row):
    """
    """
    pass


def calculate_whip(player_row):
    """
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
    pass


def calculate_rip(player_row):
    """
    """
    pass

