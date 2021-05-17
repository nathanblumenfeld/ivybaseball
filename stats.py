"""
Stats module for IvyBaseball

# Nathan Blume
# May 11th 2021
"""


from datetime import datetime
from PIL import Image
import ipynb.fs.full.scraper as sc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")


def get_rd_data(team_name, start, end):
    """
        Returns: Dataframe with run_difference, opponent, and cumulative_rd for every game of given team
        in given seasons. 
        
        Parameter team_name: team to return games for
        Precondtion: team_name is a string
        Parameter start: start year, inclusive
        Precondition: start is a int 
        Parameter end: end year, inclusive
        Preconditon: end is an int
        """
    games = sc.get_games(team_name, start=start, end=end)
    games["date"] = pd.to_datetime(games["date"])
    games = games.sort_values(by="date")
    games = games.reset_index(drop="True")
    games = sc.add_run_difference_column(team_name, games)
    games = games.drop(
        columns=["team_1", "team_1_score", "team_2", "team_2_score", "field"])
    games["date"] = games["date"].dt.strftime('%Y-%m-%d')
    return games
# Pythagenpat intra-conference win %'s by team for the Ivy League


def generate_ivy_pythags(start, end):
    """
    Returns: Dataframe of actual and expected winning percentages of Ivy League for a given set of seasons. 
    Parameter start: start year, inclusive
    Precondition: start is an int YYYY
    Parameter end: end year, inclusive
    Precondtion: end is an int YYYY
    """
    assert type(start) == int, "start must be an int"
    assert type(end) == int, "end must be an int"
    ivy_pythagenpat = {"team_name": [], "pythagenpat_pct": [],
                       "actual_pct": [], "deviation": []}
    for i in ["Brown", "Columbia", "Cornell", "Dartmouth", "Harvard", "Pennsylvania", "Princeton", "Yale"]:
        games = sc.get_intra_ivy(i, start, end)
        pythagenpat_pct = sc.pythag_win_percentage_from_df(i, games)
        actual_pct = sc.actual_win_percentage_from_df(i, games)
        deviation = abs(round(pythagenpat_pct - actual_pct, 2))
        ivy_pythagenpat["team_name"].append(i)
        ivy_pythagenpat["pythagenpat_pct"].append(round(pythagenpat_pct, 2))
        ivy_pythagenpat["actual_pct"].append(round(actual_pct, 2))
        ivy_pythagenpat["deviation"].append(deviation)
        results = pd.DataFrame(ivy_pythagenpat)
    return results


def get_woba(player_id, year):
    """
    Returns: The Weighted On-Base Average  for a given player in a given season
    
    wOBA = (wBB×uBB + wHBP×HBP + w1B×1B + w2B×2B + w3B×3B +
    wHR×HR) / (AB + BB – IBB + SF + HBP)
    PA = AB + BB - IBB + SF + HBP 
    
    Parameter player_id: The ID of player to return for
    Precondition: player_id is 
    Parameter year: The season to return for 
    Precondition: year is an INT 
    """
    season_batting = pd.read_csv("data/cornellbatting"+str(year)+".csv")
    player_batting = season_batting[season_batting.player_id == player_id]
    player_batting = player_batting.fillna(0)
    linear_weights = pd.read_csv("data/ncaa_d1_woba_linear_weights.csv")
    season_weights = linear_weights[linear_weights.Season == year]
    wbb = season_weights["wBB"].values[0]
    whbp = season_weights["wHBP"].values[0]
    w1b = season_weights["w1B"].values[0]
    w2b = season_weights["w2B"].values[0]
    w3b = season_weights["w3B"].values[0]
    whr = season_weights["wHR"].values[0]
    walks = player_batting["BB"].values[0]
    hits_by_pitch = player_batting["HBP"].values[0]
    doubles = player_batting["2B"].values[0]
    triples = player_batting["3B"].values[0]
    home_runs = player_batting["HR"].values[0]
    hits = player_batting["H"].values[0]
    singles = hits-(doubles+triples+home_runs)
    at_bats = player_batting["AB"].values[0]
    sac_flies = player_batting["SF"].values[0]
    sac_bunts = player_batting["SH"].values[0]
    plate_appearances = at_bats+walks+sac_flies+sac_bunts+hits_by_pitch
    woba = (wbb*walks+whbp*hits_by_pitch+w1b*singles+w2b *
            doubles+w3b*triples+whr*home_runs)/plate_appearances
    return woba


def get_wrc(player_id, year):
    """
    Returns: The Weighted Runs Created  for a given player in a given season
    
    wRC = [((wOBA - lgwOBA)/wOBAScale) + (lgR/PA)] * PA
    PA = AB + BB - IBB + SF + HBP 

    Parameter player_id: The ID of player to return for
    Precondition: player_id is 
    Parameter year: The season to return for 
    Precondition: year is an INT 
    """
    season_batting = pd.read_csv("data/cornellbatting"+str(year)+".csv")
    player_batting = season_batting[season_batting.player_id == player_id]
    player_batting = player_batting.fillna(0)
    linear_weights = pd.read_csv("data/ncaa_d1_woba_linear_weights.csv")
    season_weights = linear_weights[linear_weights.Season == year]
    league_woba = season_weights["wOBA"].values[0]
    woba_scale = season_weights["wOBAScale"].values[0]
    league_runs_per_pa = season_weights["R/PA"].values[0]
    player_woba = get_woba(player_id, year)
    at_bats = player_batting["AB"].values[0]
    walks = player_batting["BB"].values[0]
    sac_flies = player_batting["SF"].values[0]
    sac_bunts = player_batting["SH"].values[0]
    hits_by_pitch = player_batting["HBP"].values[0]
    plate_appearances = at_bats+walks+sac_flies+sac_bunts+hits_by_pitch
    wrc = ((((player_woba-league_woba)/woba_scale) +
            league_runs_per_pa))*plate_appearances
    return wrc
    """
    Returns: The Weighted Runs Above Average (wRAA) for a given player in a given season
    
    [(wOBA−leagueWOBA) / wOBAscale] ∗ PA
    PA = AB + BB - IBB + SF + HBP 

    Parameter player_id: The ID of player to return for
    Precondition: player_id is 
    Parameter year: The season to return wRC for 
    Precondition: year is an INT 
    """
    season_batting = pd.read_csv("data/cornellbatting"+str(year)+".csv")
    player_batting = season_batting[season_batting.player_id == player_id]
    player_batting = player_batting.fillna(0)
    linear_weights = pd.read_csv("data/ncaa_d1_woba_linear_weights.csv")
    season_weights = linear_weights[linear_weights.Season == year]
    league_woba = season_weights["wOBA"].values[0]
    woba_scale = season_weights["wOBAScale"].values[0]
    league_runs_per_pa = season_weights["R/PA"].values[0]
    player_woba = get_woba(player_id, year)
    at_bats = player_batting["AB"].values[0]
    walks = player_batting["BB"].values[0]
    sac_flies = player_batting["SF"].values[0]
    sac_bunts = player_batting["SH"].values[0]
    hits_by_pitch = player_batting["HBP"].values[0]
    plate_appearances = at_bats+walks+sac_flies+sac_bunts+hits_by_pitch
    wraa = ((((player_woba-league_woba)/woba_scale)))*(plate_appearances)
    return wraa


def get_cornell_woba(year):
    """
    Returns: The Weighted On-Base Average  for a given player in a given season
    
    wOBA = (wBB×uBB + wHBP×HBP + w1B×1B + w2B×2B + w3B×3B +
    wHR×HR) / (AB + BB – IBB + SF + HBP)
    PA = AB + BB - IBB + SF + HBP 

    Parameter year: The season to return for 
    Precondition: year is an INT 2012-2020
    """
    linear_weights = pd.read_csv("data/ncaa_d1_woba_linear_weights.csv")
    season_weights = linear_weights[linear_weights.Season == year]
    wbb = season_weights["wBB"].values[0]
    whbp = season_weights["wHBP"].values[0]
    w1b = season_weights["w1B"].values[0]
    w2b = season_weights["w2B"].values[0]
    w3b = season_weights["w3B"].values[0]
    whr = season_weights["wHR"].values[0]
    totals = pd.read_excel("data/cornell_totals_2012_to_2020.xlsx")
    season_totals = totals[totals.Season == year]
    walks = season_totals["BB"].values[0]
    hits_by_pitch = season_totals["HBP"].values[0]
    doubles = season_totals["2B"].values[0]
    triples = season_totals["3B"].values[0]
    home_runs = season_totals["HR"].values[0]
    hits = season_totals["H"].values[0]
    singles = hits-(doubles+triples+home_runs)
    at_bats = season_totals["AB"].values[0]
    sac_flies = season_totals["SF"].values[0]
    sac_bunts = season_totals["SH"].values[0]
    plate_appearances = at_bats+walks+sac_flies+sac_bunts+hits_by_pitch
    woba = (wbb*walks+whbp*hits_by_pitch+w1b*singles+w2b *
            doubles+w3b*triples+whr*home_runs)/plate_appearances
    return woba
def get_ivy_woba(year):
        """
        Returns: Ivy League Weighted On-Base Average in a given season

        wOBA = (wBB×uBB + wHBP×HBP + w1B×1B + w2B×2B + w3B×3B +
        wHR×HR) / (AB + BB – IBB + SF + HBP)
        PA = AB + BB - IBB + SF + HBP 

        Parameter year: The season to return for 
        Precondition: year is an INT 2012-2020
        """  
        linear_weights = pd.read_csv("data/ncaa_d1_woba_linear_weights.csv")
        season_weights = linear_weights[linear_weights.Season==year]
        wbb = season_weights["wBB"].values[0]
        whbp = season_weights["wHBP"].values[0]
        w1b = season_weights["w1B"].values[0]
        w2b = season_weights["w2B"].values[0]
        w3b = season_weights["w3B"].values[0]
        whr = season_weights["wHR"].values[0]
        ivy_totals = pd.read_excel("data/ivy_league_totals_2012_to_2020.xlsx", sheet_name="batting")
        season_totals = ivy_totals[ivy_totals.Season==year]
        walks = season_totals["BB"].values[0]
        hits_by_pitch = season_totals["HBP"].values[0]
        doubles = season_totals["2B"].values[0]
        triples = season_totals["3B"].values[0]
        home_runs = season_totals["HR"].values[0]
        hits = season_totals["H"].values[0]
        singles =  hits-(doubles+triples+home_runs)
        at_bats = season_totals["AB"].values[0]
        sac_flies = season_totals["SF"].values[0]
        sac_bunts = season_totals["SH"].values[0]
        plate_appearances = at_bats+walks+sac_flies+sac_bunts+hits_by_pitch
        woba = (wbb*walks+whbp*hits_by_pitch+w1b*singles+w2b*doubles+w3b*triples+whr*home_runs)/plate_appearances
        return wobadef get_cornell_wrc_plus(player_id, year):
    """
    Returns: wRC+ for a given player in given season

    wRC is a normalized, adjusting for park factors and run-scoring environment
    (((wRAA per PA + league runs per PA) + (league runs per PA - ballpark factor x league runs per PA) /
    league wRC per plate appearance, not including pitchers)) x 100.
    
    Parameter: player_id
    Precondtion: player_id is..
    Parameter year: season to return for
    Precondtion: year is an int YYYY
    """
#     linear_weights = pd.read_csv("data/ncaa_d1_woba_linear_weights.csv")
#     season_weights = linear_weights[linear_weights.Season==year]
#     league_woba = season_weights["wOBA"].values[0]
#     woba_scale = season_weights["wOBAScale"].values[0]
#     league_runs_per_pa = season_weights["R/PA"].values[0]
#     wraa = get_wraa(player_id, year)
#     park_factor = park_factors[park_factors["ballpark"]=="Cornell"]["park_factor_runs"].values[0]
#     at_bats = player_batting["AB"].values[0]
#     walks = player_batting["BB"].values[0]
#     sac_flies = player_batting["SF"].values[0]
#     sac_bunts = player_batting["SH"].values[0]
#     hits_by_pitch = player_batting["HBP"].values[0]
#     plate_appearances = at_bats+walks+sac_flies+sac_bunts+hits_by_pitch
#     wraa_per_pa = wraa/plate_appearances
#     wrc_plus = (((wraa_per_pa+league_runs_per_pa)+(league_runs_per_pa-park_factor*league_runs_per_pa)/(#league_) 
#     return wrc_plus
    pass
    def get_cornell_batting_stats(start):
        """
        Returns: 
        """
        batting = pd.read_csv("data/battingsince"+str(start)+".csv")
        batting = batting.loc[batting['BA']>0, :]
        team_list = {"player_id":[], "name":[], "year":[], "AB":[], "woba":[], "wrc":[], "wraa":[], "class_year":[]}
        for i in range(len(batting)):
            player_id = batting.iloc[i, 0]
            player = batting.iloc[i,6]
            year = batting.iloc[i, 1]
            at_bats = batting.iloc[i,15]
            class_year = batting.iloc[i,7]
            woba = get_woba(player_id, year)
            wrc  = get_wrc(player_id, year)
            wraa  = get_wraa(player_id, year)
            team_list["player_id"].append(player_id)
            team_list["AB"].append(at_bats)
            team_list["class_year"].append(class_year)
            team_list["name"].append(player)
            team_list["year"].append(year)
            team_list["woba"].append(woba)
            team_list["wrc"].append(wrc)
            team_list["wraa"].append(wraa)
        res = pd.DataFrame(team_list)
        return res

def get_fip(player_id, year):
    """
    Returns: Fielding Independent Pitching for a given player in a given season
    
    FIP = ((13*HR)+(3*(BB+HBP))-(2*K))/IP + constant
    FIP Constant = lgERA – (((13*lgHR)+(3*(lgBB+lgHBP))-(2*lgK))/lgIP)

    Parameter player_id: The ID of player to return for
    Precondition: player_id is 
    Parameter year: The season to return wRC for 
    Precondition: year is an INT 
    """
    season_pitching = pd.read_csv("data/cornellpitching"+str(year)+".csv")
    player_pitching =  season_pitching[season_pitching.player_id==player_id]
    player_pitching = player_pitching.fillna(0)
    strike_outs = player_pitching["SO"].values[0]
    hit_batters = player_pitching["HB"].values[0]
    walks_given = player_pitching["BB"].values[0]
    home_runs_allowed = player_pitching["HR-A"].values[0]
    strike_outs = player_pitching["IP"].values[0]
    linear_weights = pd.read_csv("data/ncaa_d1_woba_linear_weights.csv")
    season_weights = linear_weights[linear_weights.Season== year]
    fip_constant =season_weights["cFIP"].values[0]
    fip = (((13*home_runs_allowed)+(3*(walks_given+hit_batters))-(2*strike_outs))/strike_outs) + fip_constant
    return fip

  def get_cornell_fip(year):
    """
    Returns: Cornell total  Fielding Independent Pitching (FIP) for a given player in a given season
    
    FIP = ((13*HR)+(3*(BB+HBP))-(2*K))/IP + constant
    FIP Constant = lgERA – (((13*lgHR)+(3*(lgBB+lgHBP))-(2*lgK))/lgIP)

    Parameter player_id: The ID of player to return for
    Precondition: player_id is 
    Parameter year: The season to return wRC for 
    Precondition: year is an INT 
    """
    cu_pitching = pd.read_csv("data/cornellpitching"+str(year)+".csv")
    season_totals = cu_pitching[cu_pitching.Player=="Totals"]
    strike_outs = season_totals["SO"].values[0]
    hit_batters = season_totals["HB"].values[0]
    walks_given = season_totals["BB"].values[0]
    home_runs_allowed = season_totals["HR-A"].values[0]
    strike_outs = season_totals["IP"].values[0]
    linear_weights = pd.read_csv("data/ncaa_d1_woba_linear_weights.csv")
    season_weights = linear_weights[linear_weights.Season== year]
    fip_constant =season_weights["cFIP"].values[0]
    fip = (((13*home_runs_allowed)+(3*(walks_given+hit_batters))-(2*strike_outs))/strike_outs) + fip_constant
    return fip

get_cornell_fip(2015)
def get_ivy_fip(year):
    """
    Returns: Ivy League total Fielding Independent Pitching (FIP) for a given season
    
    FIP = ((13*HR)+(3*(BB+HBP))-(2*K))/IP + constant
    FIP Constant = lgERA – (((13*lgHR)+(3*(lgBB+lgHBP))-(2*lgK))/lgIP)

    Parameter year: The season to return fip for 
    Precondition: year is an INT 
    """
    ivy_pitching = pd.read_excel("data/ivy_league_totals_2012_to_2020.xlsx", sheet_name="pitching")
    season_totals = ivy_pitching[ivy_pitching.Season==year]
    walks = season_totals["BB"].values[0]   
    strike_outs = season_totals["SO"].values[0]
    hit_batters = season_totals["HB"].values[0]
    walks_given = season_totals["BB"].values[0]
    home_runs_allowed = season_totals["HR-A"].values[0]
    strike_outs = season_totals["IP"].values[0]
    linear_weights = pd.read_csv("data/ncaa_d1_woba_linear_weights.csv")
    season_weights = linear_weights[linear_weights.Season== year]
    fip_constant =season_weights["cFIP"].values[0]
    fip = (((13*home_runs_allowed)+(3*(walks_given+hit_batters))-(2*strike_outs))/strike_outs) + fip_constant
    return fip

get_ivy_fip(2017)
def get_era(player_id, year): 
    """
    Returns: ERA for a given player in a given season 
    
    Parameter player_id: The ID of player to return for
    Precondition: player_id is 
    Parameter year: The season to return wRC for 
    Precondition: year is an INT 
    """
    season_pitching = pd.read_csv("data/cornellpitching"+str(year)+".csv")
    player_pitching =  season_pitching[season_pitching.player_id==player_id]
    player_pitching = player_pitching.fillna(0)
    era = player_pitching["ERA"].values[0]
    return era

get_era(1546998, 2017)def get_runs_per_ip(player_id, year):
    """
    Returns: runs per innings pitched
    
    runs allowed / innings pitched
    
    """
    season_pitching = pd.read_csv("data/cornellpitching"+str(year)+".csv")
    player_pitching =  season_pitching[season_pitching.player_id==player_id]
    player_pitching = player_pitching.fillna(0)
    runs_allowed = player_pitching["R"].values[0]
    innings_pitched = player_pitching["IP"].values[0]
    res = runs_allowed/innings_pitched
    return res

get_runs_per_ip(1546998, 2017)
def get_cornell_pitching_stats(start):
    """
    Returns: Dataframe of advanced pitching statistics
    """
    pitching = pd.read_csv("data/pitchingsince"+str(start)+".csv")
    pitching = pitching.loc[pitching['App']>0, :]
    team_list = {"player_id":[], "name":[], "year":[], "innings_pitched":[], "runs":[], "era":[], "fip":[], "runs_per_ip":[],"class_year":[]}
    for i in range(len(pitching)):
        player_id = pitching.iloc[i, 0]
        player = pitching.iloc[i,6]
        year = pitching.iloc[i, 1]
        class_year = pitching.iloc[i,7]
        innings_pitched = pitching.iloc[i, 13]
        runs_allowed = pitching.iloc[i, 15]
        era = get_era(player_id, year)
        fip = get_fip(player_id, year)
        runs_per_ip = get_runs_per_ip(player_id, year)
        team_list["player_id"].append(player_id)
        team_list["innings_pitched"].append(innings_pitched)
        team_list["runs"].append(runs_allowed)
        team_list["class_year"].append(class_year)
        team_list["name"].append(player)
        team_list["year"].append(year)
        team_list["era"].append(era)
        team_list["fip"].append(fip)
        team_list["runs_per_ip"].append(runs_per_ip)
    res = pd.DataFrame(team_list)
    return res

team_name = "Cornell"
games = sc.get_intra_ivy(team_name, 2010, 2020)
games["date"] =  pd.to_datetime(games["date"])
games = games.sort_values(by="date")
games = games.reset_index(drop="True")
games = sc.add_run_difference_column(team_name, games)
cu_df = pd.DataFrame({"date":games.date, team_name:games.cumulative_rd}, index=games.index)

team_name = "Brown"
games = sc.get_intra_ivy(team_name, 2010, 2020)
games["date"] =  pd.to_datetime(games["date"])
games['month'] = pd.DatetimeIndex(games['date']).month
games = games.sort_values(by="date")
games = games.reset_index(drop="True")
games = sc.add_run_difference_column(team_name, games)
br_df = pd.DataFrame({"date" : games.date, team_name: games.cumulative_rd}, index=games.index)

df = pd.merge(cu_df, br_df,how="outer",on="date")
df = df.sort_values(by="date")
df = df.reset_index(drop="True")
df = df.fillna(method="pad")
df.set_index("date")
df = pd.melt(df, id_vars=["date"], value_vars=["Cornell", "Brown"])
df = df.sort_values(by="date")
df = df.rename(columns={"variable": "team_name", "value": "cum_rd"})
format_str = "%Y-%m-%d"
df["date"] = df["date"].dt.strftime('%Y-%m-%d')
df 
