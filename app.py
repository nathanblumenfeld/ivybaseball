"""
A basic web application created as a front-end for cornellbaseball module

created by Nathan Blumenfeld for Cornell Baseball

"""
import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid
from cornellbaseball import ncaa_scrape
from cornellbaseball import batting_metrics
import plotly.express as px

@st.cache
def load_data():
    df = pd.read_pickle('data/ncaa/players_clean.df')
    df = df.astype({'stats_player_seq':'string'})
    return df

def load_player_lu_table():
    lu = pd.read_pickle('data/ncaa/players_lookup.df').reset_index()
    lu = lu.astype({'stats_player_seq':'string'})
    res = lu.to_dict('records')
    return res 


#### PLAYER STATS ######
records = load_player_lu_table()

# user input: select player
choice = st.selectbox('Select a player', options=records, format_func=lambda record: f'''{record['name'][0]}, {record['position']}, {record['school']}, {record['year']}''')

player_stats_container = st.container()
# regular stats
players = load_data()
player = players.loc[players['stats_player_seq'] == choice['stats_player_seq']]
player_row = player.iloc[0]

# load data from NCAA 
basic_stats = ncaa_scrape.get_career_stats(stats_player_seq = player_row['stats_player_seq'], team_id = player_row['school_id'], season_id = player_row['season_id'])

# transform NCAA data 
basic_stats['season_id'] = player_row['season_id']
basic_stats['school_id'] = player_row['school_id']
basic_stats['stats_player_seq'] = player_row['stats_player_seq']
basic_stats['name'] = player_row['name']
basic_stats.stats_player_seq.astype('string')
                                                            
 # join on player-seasons table                                    
df = pd.merge(basic_stats, players, left_on=['stats_player_seq', 'season_id'], right_on=['stats_player_seq', 'season_id'], copy=True)
df.drop(columns=['name_y', 'school_id_y', 'school_id_x', 'season_y', 'batting_id', 'pitching_id', 'conference_id', 'season_id', 'year', 'stats_player_seq', 'team_id'], inplace=True)
# TODO create details table to merge onto
df.rename(columns={'name_x':'name', 'season_x':'season'}, inplace=True)
                                                            
# add advanced stats 
advanced_stats = batting_metrics.add_columns(df).loc[:, ['season', 'wOBA', 'wRAA', 'wRC']]

# write basic stats 
player_stats_container.subheader('Season Totals')
player_stats_container.write(df)
# write advanced  stats 
player_stats_container.subheader('Advanced Metrics')
player_stats_container.write(advanced_stats)
                                                           
               
##### VISUALIZATIONS #####
# fig = px.scatter(advanced_stats, x="season", y="wOBA")
# player_stats_container.plotly_chart(fig, use_container_width=True)

# fig = px.scatter(advanced_stats, x="season", y="wRAA")
# player_stats_container.plotly_chart(fig, use_container_width=True)

# fig = px.scatter(advanced_stats, x="season", y="wRC")
# player_stats_container.plotly_chart(fig, use_container_width=True)


##### FOOTER #####
st.caption("Created by Nathan Blumenfeld")

