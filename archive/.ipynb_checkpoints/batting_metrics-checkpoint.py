import pandas as pd
import numpy as np
from cornellbaseball import ncaa_scrape

# GLOBAL VARIABLES
# filepath of Cornell individual season totals
STATS_FILEPATH = "data/cornell/cornell_batting_individual_season_totals_2015_to_2020.xlsx"
# filepath of D1 linear weights
LW_FILEPATH = "data/ncaa_d1_woba_linear_weights.csv"  # <-- Driveline BB's Linear Weights
# Alternate LW_FILEPATH: "data/ncaa_guts.csv" <-- Robert Fray's Linear Weights

# round to 
ROUND_TO = 3


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

# CALCULATE BATTING METRICS PER PLAYER PER SEASON 
def calculate_babip(player_id, season, stats_filepath=STATS_FILEPATH, lw_filepath=LW_FILEPATH, round_to=ROUND_TO):
    """
    Returns: BABIP (Batting Average on Balls in Play) for a given player in a given season
    """
    player_batting = get_season_totals(player_id, season, stats_filepath)
    walks = player_batting["BB"].values[0]
    hits_by_pitch = player_batting["HBP"].values[0]
    hits = player_batting["H"].values[0]
    home_runs = player_batting["HR"].values[0]
    at_bats = player_batting["AB"].values[0]
    strikeouts = player_batting["K"].values[0]
    sac_flies = player_batting["SF"].values[0]
    if (at_bats-strikeouts-home_runs-sac_flies) == 0: 
        res = 0
    else: 
        res = (hits*walks)/(at_bats-strikeouts-home_runs-sac_flies)
    return round(res, round_to)

def calculate_woba(player_id, season, stats_filepath=STATS_FILEPATH, lw_filepath=LW_FILEPATH, round_to=ROUND_TO):
    """
    Returns: The Weighted On-Base Average for a given player in a given season
    Data from NCAA

    wOBA = (wBB×uBB + wHBP×HBP + w1B×1B + w2B×2B + w3B×3B +
    wHR×HR) / (AB + BB – IBB + SF + HBP)
    PA = AB + BB - IBB + SF + HBP 

    Parameter player_id: The NCAA ID of player to return for
    Precondition: player_id is an int
    Parameter year: The season to return for 
    Precondition: year is an int, 2015 <= year <= 2020
    """
    player_batting = get_season_totals(player_id, season, stats_filepath)
    if len(player_batting) > 0: 
        # get linear weights for given season
        linear_weights = pd.read_csv(lw_filepath)
        season_weights = linear_weights[linear_weights.Season==season]
        wbb = season_weights["wBB"].values[0]
        whbp = season_weights["wHBP"].values[0]
        w1b = season_weights["w1B"].values[0]
        w2b = season_weights["w2B"].values[0]
        w3b = season_weights["w3B"].values[0]
        whr = season_weights["wHR"].values[0]
        # get player totals for given season
        walks = player_batting["BB"].values[0]
        hits_by_pitch = player_batting["HBP"].values[0]
        doubles = player_batting["2B"].values[0]
        triples = player_batting["3B"].values[0]
        home_runs = player_batting["HR"].values[0]
        hits =  player_batting["H"].values[0]
        singles = hits-(doubles+triples+home_runs)
        at_bats = player_batting["AB"].values[0]
        sac_flies = player_batting["SF"].values[0]
        sac_bunts = player_batting["SH"].values[0]
        # calculate woba
        plate_appearances = at_bats+walks+sac_flies+sac_bunts+hits_by_pitch
        if plate_appearances <= 0:
            res = 0 
        else: 
            res = (wbb*walks+whbp*hits_by_pitch+w1b*singles+w2b*doubles+w3b*triples+whr*home_runs)/plate_appearances
    else: 
        print(f"""No batting records found for player_id {player_id} within given range""")
        res = 0
    return round(res, round_to)

def calculate_wraa(player_id, season, stats_filepath=STATS_FILEPATH, lw_filepath=LW_FILEPATH, round_to=ROUND_TO):
    """
    Returns: The Weighted Runs Above Average (wRAA) for a given player in a given season
    Data from NCAA

    [(wOBA−leagueWOBA) / wOBAscale] ∗ PA
    PA = AB + BB - IBB + SF + HBP 

    Parameter player_id: The NCAA ID of player to return for
    Precondtion: player_id is an int
    Parameter year: The season to return wRC for 
    Precondition: year is an int
    """
    player_batting = get_season_totals(player_id, season, stats_filepath)
    if len(player_batting) > 0: 
        at_bats = player_batting["AB"].values[0]
        walks = player_batting["BB"].values[0]
        sac_flies = player_batting["SF"].values[0]
        sac_bunts = player_batting["SH"].values[0]
        hits_by_pitch = player_batting["HBP"].values[0]

        linear_weights = pd.read_csv(lw_filepath)
        season_weights = linear_weights[linear_weights.Season == season]
        league_woba = season_weights["wOBA"].values[0]
        woba_scale = season_weights["wOBAScale"].values[0]
        league_runs_per_pa = season_weights["R/PA"].values[0]

        player_woba = calculate_woba(player_id, season)
        plate_appearances = at_bats+walks+sac_flies+sac_bunts+hits_by_pitch

        if plate_appearances < 0: 
            res = 0
        else: 
            res = ((((player_woba-league_woba)/woba_scale)))*(plate_appearances)
    else: 
        print(f"""No batting records found for player_id {player_id} within given range""")
        res = 0 
    return round(res, round_to)

def calculate_wrc(player_id, season, stats_filepath=STATS_FILEPATH, lw_filepath=LW_FILEPATH, round_to=ROUND_TO):
    """
    Returns: The Weighted Runs Created for a given player in a given season
    Data from NCAA

    wRC = [((wOBA - lgwOBA) / wOBAScale) + (lgR / PA))] * PA
    PA = AB + BB - IBB + SF + HBP 
    
    wRC = (((wOBA-League wOBA)/wOBA Scale)+(League R/PA))*PA

    Parameter player_id: The ID of player to return for
    Precondition: player_id is an int
    Parameter year: The season to return for 
    Precondition: year is an int 
    """
    player_batting = get_season_totals(player_id, season, stats_filepath)
    if len(player_batting) > 0: 
        at_bats = player_batting["AB"].values[0]
        walks = player_batting["BB"].values[0]
        sac_flies = player_batting["SF"].values[0]
        sac_bunts = player_batting["SH"].values[0]
        hits_by_pitch = player_batting["HBP"].values[0]

        plate_appearances = at_bats+walks+sac_flies+sac_bunts+hits_by_pitch
        if plate_appearances <= 0:
            res = 0 
        else:     
            linear_weights = pd.read_csv(lw_filepath)
            season_weights = linear_weights[linear_weights.Season == season]
            league_woba = season_weights["wOBA"].values[0]
            woba_scale = season_weights["wOBAScale"].values[0]
            league_runs_per_pa = season_weights["R/PA"].values[0]

            player_woba = calculate_woba(player_id, season)   
            res = ((((player_woba-league_woba)/woba_scale)+league_runs_per_pa))*plate_appearances
    else:
        print(f"""No batting records found for player_id {player_id} within given range""")
        res = 0
    return round(res, ROUND_TO)

def calculate_lw_metrics(player_id, season, stats_filepath=STATS_FILEPATH, lw_filepath=LW_FILEPATH, round_to=ROUND_TO):
    """
    returns: woba, wraa, wrc for given player
    """
    player_batting = get_season_totals(player_id, season, stats_filepath)
    if len(player_batting) < 0:
        print(f"""no records found for {player_id} in given range""")
        woba = 0 
        wraa = 0
        wrc = 0
    else: 
        walks = player_batting["BB"].values[0]
        hits_by_pitch = player_batting["HBP"].values[0]
        doubles = player_batting["2B"].values[0]
        triples = player_batting["3B"].values[0]
        home_runs = player_batting["HR"].values[0]
        hits =  player_batting["H"].values[0]
        singles = hits-(doubles+triples+home_runs)
        at_bats = player_batting["AB"].values[0]
        sac_flies = player_batting["SF"].values[0]
        sac_bunts = player_batting["SH"].values[0]
        plate_appearances = at_bats+walks+sac_flies+sac_bunts+hits_by_pitch
        if plate_appearances > 0:
            linear_weights = pd.read_csv(lw_filepath)
            season_weights = linear_weights[linear_weights.Season==season]
            wbb = season_weights["wBB"].values[0]
            whbp = season_weights["wHBP"].values[0]
            w1b = season_weights["w1B"].values[0]
            w2b = season_weights["w2B"].values[0]
            w3b = season_weights["w3B"].values[0]
            whr = season_weights["wHR"].values[0]
            league_woba = season_weights["wOBA"].values[0]
            woba_scale = season_weights["wOBAScale"].values[0]
            league_runs_per_pa = season_weights["R/PA"].values[0]
            # calculate metrics
            woba = (wbb*walks+whbp*hits_by_pitch+w1b*singles+w2b*doubles+w3b*triples+whr*home_runs)/plate_appearances
            wraa = ((((woba-league_woba)/woba_scale)))*(plate_appearances)
            wrc = ((((woba-league_woba)/woba_scale)+league_runs_per_pa))*plate_appearances
        else: 
            print(f"""No batting records found for player_id {player_id} within given range""")
            woba = 0 
            wraa = 0
            wrc = 0            
    return round(woba, round_to), round(wraa, round_to), round(wrc, round_to)

# CALCULATE BATTING METRICS PER PLAYER PER SEASON 
def get_cornell_batting_stats():
    """
    Returns: pandas.DataFrame Object
    """
# load data 
    data = (pd.read_excel("data/cornell/cornell_batting_individual_season_totals_2015_to_2020.xlsx")
                   .fillna(0)
           )
    # set per player per season via uuid of PLAYERID_SEASON _B(atting)
    data["uuid"] = data.player_id.astype(str)+"_"+data.season.astype(str)+"_b"
    data = data.set_index("uuid").reset_index()
    # PA = AB + BB + SF + SH + HBP 
    data["PA"] =  data["AB"]+data["BB"]+data["SF"]+data["SH"]+data["HBP"]
    data = data.fillna(0)
    #  singles = hits-(doubles+triples+home_runs)
    data["1B"] =  data["H"]-data["2B"]-data["3B"]-data["HR"]
    # BABIP = (H – HR)/(AB – K – HR + SF)
    data["BABIP"] = (data["H"]-data["HR"])/(data["AB"]-data["K"]-data["HR"]+data["SF"])
    # # load in linear weights
    lw_filepath =  "data/ncaa_d1_woba_linear_weights.csv"
    linear_weights = (pd.read_csv(lw_filepath)
                                      .rename(columns={"wOBA":"lgwOBA","Season":"season", "R/PA":"lgR/PA"})
                                      .loc[:,["season", "lgwOBA", "wOBAScale", "wBB", "wHBP", "w1B", "w2B", "w3B", "wHR", "lgR/PA", "RPG"]]
                             )
    df = pd.merge(data, linear_weights, left_on="season", right_on="season", how="left")
    # wOBA = (wBB×uBB + wHBP×HBP + w1B×1B + w2B×2B + w3B×3B + wHR×HR) / (AB + BB – IBB + SF + HBP)
    df["wOBA"] =  (((df["wBB"]*df["BB"])+(df["wHBP"]*df["HBP"])+(df["w1B"]*df["1B"])+(df["w2B"]*df["2B"])+(df["w3B"]+df["3B"])+(df["wHR"]*df["HR"])) / df["PA"]).replace(np.inf, 0)
    # wRAA = [(wOBA−leagueWOBA) / wOBAscale] ∗ PA
    df["wRAA"] = (((df["wOBA"]-df["lgwOBA"])/df["wOBAScale"])*df["PA"]).replace(np.inf, 0)
    # wRC = (((wOBA – lgwOBA) / wOBAScale) + (lgR/PA)) * PA
    df["wRC"] = ((((df["wOBA"]-df["lgwOBA"])/df["wOBAScale"])+df["lgR/PA"])*df["PA"]).replace(np.inf, 0)
    return df