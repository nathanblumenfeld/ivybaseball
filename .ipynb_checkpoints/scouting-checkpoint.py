import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid
from cornellbaseball import ncaa_scrape
from cornellbaseball import boydsworld_scraper as bd
from cornellbaseball import batting_metrics
from cornellbaseball import win_pct
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import time


@st.cache
def load_bd_data(team, start, end):
    """
    """
    res = pd.DataFrame()
    for season in range(start, end+1):
        data = bd.get_games(team, season, end = None)
        data.loc[:, "season"] = data.date.dt.year
        data.loc[:, "cum_rs"] = data.runs_scored.cumsum()
        data.loc[:, "cum_ra"] = data.runs_allowed.cumsum()
        data.loc[:, "cum_rd"] = data.run_difference.cumsum()
        data.loc[:, "game_number"] = data.index
        res = pd.concat([res, data], ignore_index=True)
    return res.sort_values(by='game_number')

st.set_page_config(page_title="Scouting Reports", layout="centered")

@st.cache 
def load_team_names():
    """
    Returns: pandas Series of accepted team names for boydsworld
    """
    df = pd.read_csv('data/boydsworld/team_names.csv')
    return df.team_name

def create_sparklines(team, start, end):
    """
    """   
    data = load_bd_data(team, start, end) 
    fig = px.line(data, x="game_number", y="cum_rd", color='season', line_group='season')
    fig.update_layout( 
        title = f"""Cumulative Run Differential by Season</sup><br><sup>{str(start)} to {str(end)}</sup>""",
        title_font_size = 20,
        title_xanchor = "center",
        title_yanchor = "top",
        title_x =  0.5,
        yaxis_title="Cumulative Run Differential",
        xaxis_title="Games Played",
        margin=dict(l=40, r=20, t=60, b=20)
    )
    fig.update_yaxes(ticklabelposition="inside top")
    fig.update_layout(showlegend=False)
    return fig, data
    
team_names = load_team_names()
team = st.selectbox('Team', options=team_names)
start, end = st.select_slider('Seasons', options = range(1992, 2022), value = (2015, 2021))

try:
    fig, data = create_sparklines(team, start, end)
    games = data[['opponent', 'run_difference', 'runs_scored', 'runs_allowed', 'date', 'field']].sort_values(by='date', ascending=False)
    st.plotly_chart(fig)
    actual, expected = st.columns(2)
    actual.metric(label="Actual Winning %", value=str(win_pct.calculate_actual_win_pct(games = games)))
    expected.metric(label="PythagenPat Expected Winning %: ", value=str(win_pct.calculate_pythagenpat_win_pct(games = games)))
    st.dataframe(games.style.bar(align = 'mid', subset=['run_difference', 'runs_scored', 'runs_allowed'], color=['#C05353', '#67A280']))

except:
    st.error('An error occured, please try another date range') 

st.info('data from boydsworld.com')