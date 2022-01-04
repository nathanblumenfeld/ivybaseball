import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid
from cornellbaseball import ncaa_scrape
from cornellbaseball import batting_metrics

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

def format_names(original):
    try: 
        split = original.split(',')
        split.reverse()
        res = ' '.join(split).strip().title()
    except:
        res = np.nan
    return res

records = load_player_lu_table()
choice = st.selectbox('Select Player', options=records, format_func=lambda record: f'''{record['name'][0]}, {record['position']}, {record['school']}''')

# regular stats
players = load_data()
player = players.loc[players['stats_player_seq'] == choice['stats_player_seq']]
row = player.iloc[0]
basic_stats = ncaa_scrape.get_career_stats(stats_player_seq = row['stats_player_seq'], team_id = row['school_id'], season_id = row['season_id'])
res = basic_stats.drop(columns=['Team', 'TB', 'Picked', 'CS', 'SB'])
st.write('Season Totals')
st.write(res)

basic_stats['season_id'] = row['season_id']
basic_stats['school_id'] = row['school_id']
basic_stats['stats_player_seq'] = row['stats_player_seq']
basic_stats['name'] = row['name']
basic_stats.stats_player_seq = basic_stats.stats_player_seq.astype('string')
df = pd.merge(basic_stats, players, how='left', left_on=['stats_player_seq', 'season_id'], right_on=['stats_player_seq', 'season_id'], copy=True)
df.drop(columns=['name_y', 'school_id_y'], inplace=True)
advanced_stats = batting_metrics.add_columns(df).loc[:, ['Year', 'wOBA', 'wRAA', 'wRC']]
st.write('Advanced Metrics')
st.write(advanced_stats)


st.write("Created by Nathan Blumenfeld")

