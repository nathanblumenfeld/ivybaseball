"""
Scraper module for IvyBaseball 

With this module, you can obtain college baseball data from number of sources with a few commands. 

# Nathan Blumenfeld
# May 11th 2021
"""
# third party imports
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import tempfile
import lxml.html as lh
from io import StringIO
import warnings
warnings.filterwarnings("ignore")

#local imports
from . import consts

class Games(): 
    """
    Holds a DataFrame of Games for a given team over a given interval of seasons. 
    """
    # ATTRIBUTES
    url = consts.GAMES_URL
    
    # METHODS    
    def __init__(self, team=consts.TEAM_NAME, start=consts.START_YEAR, end=consts.END_YEAR):
        """
        Initializer for Games class.
        Returns: a dataframe of all games played for a given team inclusive of given start & end year

        Parameter team_name: team whose games to select
        Precondition: team_name is a lowercase string
        Parameter start: the start year of games. To select only games from one year, leave
        Precondition: start is an int
        Parameter end: the end year of games
        Precondition: end is an int
        """
        assert type(team_name) == str, "team_name invalid, must be string"
        assert type(start) == int, "team_name invalid, must be int"
        assert type(end) == int, "team_name invalid, must be int"
        payload = {"team1": team_name, "firstyear": str(
            start), "team2": "all", "lastyear": str(end), "format": "Text", "submit": "Fetch"}
        s = requests.Session()
        r = requests.get(url, params=payload)
        response = r.text
        if (len(response) < 10):
                return pd.DataFrame
                print('No data found.')
        else:
            df = pd.read_fwf(StringIO(response), encoding='utf8', header=None)
            col_names = ["date", "team_1", "team_1_score",
                        "team_2", "team_2_score", "field"]
            try:
                df.shift(periods=1)
                df.columns = col_names
            except:
                df.columns = df.columns.astype("str")
                df.drop("2", inplace=True, axis=1)
                df.columns = col_names
            return df

    def wins(self):
        return Wins(self)
    
    def losses(self):
        return Losses(self)

    

    class Wins(Games): 
        """
        A subclass of Games 
        """
        def get_wins_from_df(team_name, games):
            """
            Returns a dataframe of victories of a given team from given get_games dataframe

            Parameter team_name: team to return victories of
            Preconditions: team_name is a string format ex. "Cornell," "Colgate"
            Parameter games: Games to filter
            Precondition: games is a DataFrame returned by getGames() function
            """
            assert type(team_name) == str, "team_name invalid, must be string"
            wins = games[(games["team_1"] == team_name) & (
                games["team_1_score"] > games["team_2_score"])]
            return wins

    class Losses(Games):
        """
        A subclass of Games 
            """
        def get_losses_from_df(team_name, games):
            """
            Returns a dataframe of losses of a given dataframe from get_games dataframe

            Parameter team_name: team to return losses of
            Preconditions: team_name is a string format ex. "Cornell," "Colgate"
            Parameter games: Games to filter
            Precondition: games is a DataFrame returned by getGames() function
            """
            assert type(team_name) == str, "team_name invalid, must be string"
            losses = games[(games["team_2"] == team_name) & (
                games["team_1_score"] > games["team_2_score"])]
            return losses


    class In_Conference(Games):
        """
        A Subclass of Games
        """ 

        def get_intra_ivy_from_df(team_name, games):
            """
            Returns: data frame of in-conference games of given team from get_games dataframe

            Creates a temporary column "intra_ivy" equal to 1 if against an Ivy-League opponent, 0 if not, and then
            selects the rows for which this intra_ivy is one.

            Plan to make this work for any team. Conference changes get tricky, will need helper to get conference team list for each season,
            check each game against per-season list.

            Parameter team_name: team whose games to select
            Precondition: team_name is a lowercase string
            Parameter games: Games to filter
            Precondition: games is a DataFrame returned by getGames() function
            """
            assert type(team_name) == str, "team_name invalid, must be string"
            conference = ["Brown", "Cornell", "Columbia", "Dartmouth",
                        "Harvard", "Pennsylvania", "Princeton", "Yale"]
            conference.remove(team_name)
            wins = get_wins_from_df(team_name, games)
            losses = get_losses_from_df(team_name, games)
            wins["intra_ivy"] = [1 if x in conference else 0 for x in wins["team_2"]]
            losses["intra_ivy"] = [
                1 if x in conference else 0 for x in losses["team_1"]]
            new_df = pd.concat([wins, losses])
            in_conference = new_df[new_df["intra_ivy"] == 1]
            return in_conference
