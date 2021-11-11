"""
Scraper module for boydsworld.com historical game results 

# Nathan Blumenfeld
# November 11th 2021
"""
# Imports
import pandas as pd
import numpy as np
import requests
from io import StringIO
from datetime import date
import lxml 

# MAIN FUNCTION
def get_games(team_1, start, end=None, team_2=None):
    """
    Returns: a dataframe of all games played for a given team inclusive of given start & end year
    Data from boydsworld.com
    
    Parameter team_name: team whose games to select 
    Precondition: team_name is a lowercase string
    Parameter start: the start year of games. To select only games from one year, leave  
    Precondition: start is an int >= 1992
    Parameter end: the end year of games
    Precondition: end is an int <= 2020
    """
    df = (load_data(team_1, start, end, team_2)
#             .pipe(handle_errors())
            .pipe(enrich_data, team_1)
            .pipe(set_dtypes)
            .drop(columns=["team_1","team_1_score","team_2","team_2_score"])
            .sort_values(by="date",axis=0, ascending=True)
         )
    # boydsworld sometimes struggles with single year inquiries 
    return df

# HELPER FUNCTIONS
def load_data(team_1, start, end=None, team_2=None): 
    """
    rtype: DataFrame
    """
    if end is None: 
        end = start
    if team_2 is None: 
        team_2 = "all"
    payload = {"team1":team_1,"firstyear":str(start),"team2":team_2,"lastyear":str(end),"format":"HTML","submit":"Fetch"}
    url = "http://www.boydsworld.com/cgi/scores.pl?" 
    s = requests.Session()
    r = requests.get(url, params=payload)
    response = r.text 
    dfs = pd.read_html(StringIO(response), parse_dates=True)
    df = dfs[1].dropna(how="all", axis=1)
    col_names = ["date", "team_1", "team_1_score", "team_2", "team_2_score", "field"]
    df.columns = col_names
    df["date"] = df["date"].astype("datetime64[ns]")
    return df

def enrich_data(df, team_1, team_2=None):
    """
    rtype: DateFrame
    """
    wins = df[(df["team_1"] == team_1) & (df["team_1_score"] > df["team_2_score"])]
    losses = df[(df["team_2"] == team_1) & (df["team_1_score"] > df["team_2_score"])]
    wins["opponent"] = wins["team_2"]
    losses["opponent"] = losses["team_1"]
    wins["runs_scored"] = wins["team_1_score"]
    wins["runs_allowed"] = wins["team_2_score"]
    losses["runs_scored"] = losses["team_2_score"]
    losses["runs_allowed"] = losses["team_1_score"]       
    df = pd.concat([wins,losses])
    df["run_difference"] = df["runs_scored"] - df["runs_allowed"]
    return df 

def set_dtypes(df):
    """
    rtype: DateFrame
    """
    df["run_difference"] = df["run_difference"].astype(int)
    df["runs_allowed"] = df["runs_allowed"].astype(int)
    df["runs_scored"] = df["runs_scored"].astype(int)
    return df