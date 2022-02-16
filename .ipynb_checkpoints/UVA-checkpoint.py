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

st.set_page_config(page_title="Scouting Report: UVA", layout="wide")

player = st.sidebar.selectbox('Player', options=['Nate Savino'])
st.header(player)
st.caption("LHP / Jr / 6'3\" / 210lbs")

st.subheader("Basic Statisics")
basic_stats = pd.DataFrame({'G':[16,4],
                      'GS':[10,3],
                      'IP':[50.4, 10.2],
                      'Pitches':[814, 187],
                      'FIP':[0,0],
                      'wOBA':[0, 0],
                      'OPS':[0.736, 0.568],
                      'OBP':[0.335, 0.306],
                      'SLG':[0.401, 0.262],
                      'ERA':[3.79, 3.38],
                      'WHIP':[0, 0],
                      'SO':[34, 10],
                      'BB':[16, 5]},
                          index=[2021, 2020])
st.dataframe(basic_stats)

st.subheader("Arsenal")
"""
pitch mix (donut)
pitch mix by year (line)
videos of each pitch
video overlays (arm angle tells?)
putaway %
"""
### PITCH MIX BY YEAR ###








### PITCH TREE ###
with st.expander("Plinko"):
    ### LEVEL 1 ####
    labels = ['Fastball','Slider','Changeup','Curveball','Unknown']
    values_2020 = [126, 46, 8, 4, 3]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values_2020, hole=.5)])
    fig.update_layout(showlegend=False, annotations=[dict(text='0-0', x=0.5, y=0.5, font_size=20, showarrow=False)])
    st.plotly_chart(fig, use_container_width=True)


    ### LEVEL 2 ####
    zero_one, one_zero = st.columns(2)
    labels = ['Fastball','Slider','Changeup','Curveball','Unknown']
    values_2020 = [126, 46, 8, 4, 3]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values_2020, hole=.5)])
    fig.update_layout(showlegend=False, annotations=[dict(text='0-1', x=0.5, y=0.5, font_size=20, showarrow=False)])
    zero_one.plotly_chart(fig, use_container_width=True)

    labels = ['Fastball','Slider','Changeup','Curveball','Unknown']
    values_2021 = [16, 46, 8, 4, 3]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values_2021, hole=.5)])
    fig.update_layout(showlegend=False, annotations=[dict(text='1-0', x=0.5, y=0.5, font_size=20, showarrow=False)])
    one_zero.plotly_chart(fig, use_container_width=True)

    ### LEVEL 3 ####
    zero_two, one_one, two_zero = st.columns(3)
    labels = ['Fastball','Slider','Changeup','Curveball','Unknown']
    values_2020 = [126, 46, 8, 4, 3]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values_2020, hole=.5)])
    fig.update_layout(showlegend=False, annotations=[dict(text='0-2', x=0.5, y=0.5, font_size=20, showarrow=False)])
    zero_two.plotly_chart(fig, use_container_width=True)

    labels = ['Fastball','Slider','Changeup','Curveball','Unknown']
    values_2021 = [16, 46, 8, 4, 3]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values_2021, hole=.5)])
    fig.update_layout(showlegend=False, annotations=[dict(text='1-1', x=0.5, y=0.5, font_size=20, showarrow=False)])
    one_one.plotly_chart(fig, use_container_width=True)

    labels = ['Fastball','Slider','Changeup','Curveball','Unknown']
    values_2021 = [16, 46, 8, 4, 3]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values_2021, hole=.5)])
    fig.update_layout(showlegend=False, annotations=[dict(text='2-0', x=0.5, y=0.5, font_size=20, showarrow=False)])
    two_zero.plotly_chart(fig, use_container_width=True)

    ### LEVEL 4 ####
    zero_two, one_one, two_zero = st.columns(3)
    labels = ['Fastball','Slider','Changeup','Curveball','Unknown']
    values_2020 = [126, 46, 8, 4, 3]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values_2020, hole=.5)])
    fig.update_layout(showlegend=False, annotations=[dict(text='1-2', x=0.5, y=0.5, font_size=20, showarrow=False)])
    zero_two.plotly_chart(fig, use_container_width=True)

    labels = ['Fastball','Slider','Changeup','Curveball','Unknown']
    values_2021 = [16, 46, 8, 4, 3]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values_2021, hole=.5)])
    fig.update_layout(showlegend=False, annotations=[dict(text='2-1', x=0.5, y=0.5, font_size=20, showarrow=False)])
    one_one.plotly_chart(fig, use_container_width=True)

    labels = ['Fastball','Slider','Changeup','Curveball','Unknown']
    values_2021 = [16, 46, 8, 4, 3]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values_2021, hole=.5)])
    fig.update_layout(showlegend=False, annotations=[dict(text='3-0', x=0.5, y=0.5, font_size=20, showarrow=False)])
    two_zero.plotly_chart(fig, use_container_width=True)

    ### LEVEL 5 ####
    zero_two, one_one = st.columns(2)
    labels = ['Fastball','Slider','Changeup','Curveball','Unknown']
    values_2020 = [126, 46, 8, 4, 3]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values_2020, hole=.5)])
    fig.update_layout(showlegend=False, annotations=[dict(text='2-2', x=0.5, y=0.5, font_size=20, showarrow=False)])
    zero_two.plotly_chart(fig, use_container_width=True)

    labels = ['Fastball','Slider','Changeup','Curveball','Unknown']
    values_2021 = [16, 46, 8, 4, 3]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values_2021, hole=.5)])
    fig.update_layout(showlegend=False, annotations=[dict(text='3-1', x=0.5, y=0.5, font_size=20, showarrow=False)])
    one_one.plotly_chart(fig, use_container_width=True)

    ### LEVEL 6 ####
    labels = ['Fastball','Slider','Changeup','Curveball','Unknown']
    values_2020 = [126, 46, 8, 4, 3]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values_2020, hole=.5)])
    fig.update_layout(showlegend=False, annotations=[dict(text='3-2', x=0.5, y=0.5, font_size=20, showarrow=False)])
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Plate Discipline")
discipline = pd.DataFrame({'F-Strike%':[0, 0],
                      'Zone%':[0, 0],
                      'SwStr%':[0, 0],
                      'Contact%':[0, 0],
                      'O-Contact%':[0, 0],
                      'Z-Contact%':[0, 0],
                      'Swing%':[0, 0],
                      'Z-Swing%':[0, 0],
                      'O-Swing%':[0, 0],
                      'GB%':[0, 0],
                      'FB%':[0, 0]},
                         index=[2021, 2020])
st.dataframe(discipline)


    
with st.expander("Pitch Type Splits"):
    pitch_discipline = pd.DataFrame({'F-Strike%':[0, 0],
                          'Zone%':[0, 0],
                          'SwStr%':[0, 0],
                          'Contact%':[0, 0],
                          'O-Contact%':[0, 0],
                          'Z-Contact%':[0, 0],
                          'Swing%':[0, 0],
                          'Z-Swing%':[0, 0],
                          'O-Swing%':[0, 0],
                          'GB%':[0, 0],
                          'FB%':[0, 0]},
                             index=[2021, 2020])
    
    st.dataframe(pitch_discipline)

with st.expander("L/R Splits"):
    lr_discipline = pd.DataFrame({'F-Strike%':[0, 0],
                          'Zone%':[0, 0],
                          'SwStr%':[0, 0],
                          'Contact%':[0, 0],
                          'O-Contact%':[0, 0],
                          'Z-Contact%':[0, 0],
                          'Swing%':[0, 0],
                          'Z-Swing%':[0, 0],
                          'O-Swing%':[0, 0],
                          'GB%':[0, 0],
                          'FB%':[0, 0]},
                             index=[2021, 2020])
    st.dataframe(lr_discipline)    
    
with st.expander("See definitions"):
    st.text("Contact%: # of pitches on which contact was made / # swings")
    st.text("Swing%:  # swings / # pitches")
    st.text("GB%: # groundballs / # balls-in-play")
    st.text("FB%: # flyballs / # balls-in-play")
    st.text("SwStr%: # swings and misses / # pitches")
    st.text("O-: out-of-zone")
    st.text("Z-: in-zone")
    
st.subheader("Notes")
st.info("""
- Relies on slider against LHH (SL 19% → 30%, CHG 11% → 4%)

- Likes to lead off with SL vs. LHH (19% → 33%), FB vs. RHH 

- Struggles to command the slider, will leave some hanging when trying to put away hitters. 

- Vulnerable on CHG (RHH OPS .917). Almost always sets up low and away. Look to hit.""")
