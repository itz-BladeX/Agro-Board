import requests
import altair as alt
import pandas as pd
import streamlit as st
from datetime import datetime
import time
def get_client_count(kebele):
    client_count = requests.get(f"http://127.0.0.1:8000/client_count/{kebele}")
    client_count = client_count.json()
    return client_count["client_count"]
def get_common_crop(kebele):
    common_data = requests.get(f"http://127.0.0.1:8000/client/common_crop/{kebele}")
    common_crop = common_data.json()
    return common_crop["common_crop"]
def get_common_livestock(kebele):
    common_data = requests.get(f"http://127.0.0.1:8000/client/common_livestock/{kebele}")
    common_livestock = common_data.json()
    return common_livestock["common_livestock"]
def get_total_land_area(kebele):
    land_area = requests.get(f"http://127.0.0.1:8000/client/total_land_area/{kebele}")
    total_land_area = land_area.json()
    return "{:,}".format(total_land_area["total_land_area"])

def get_crop_ranking(kebele):
    ranking = requests.get(f"http://127.0.0.1:8000/client/crop_yield_ranking/{kebele}")
    ranking_by_year = ranking.json()
    return ranking_by_year['ranking']
def get_livestock_ranking(kebele):
    ranking = requests.get(f"http://127.0.0.1:8000/client/livestock_amount_ranking/{kebele}")
    ranking_by_year = ranking.json()
    return ranking_by_year["ranking"]
def sort_years(year_list):
    def sort_key(year_str):
        year_str = str(year_str)
        parts = year_str.split('/')
        first = int(parts[0])
        second = int(parts[1]) if len(parts) > 1 else first
        return (first, second)
    return sorted(year_list, key=sort_key, reverse=True)
def rank(data):
    return sorted(data.items(), key=lambda key: key[1], reverse=True)

def get_user_data(kebele):
    data = requests.get(f"http://127.0.0.1:8000/client/user_data/{kebele}").json()
    return data['users']

def formated(number):
    return "{:,}".format(number)

def alter_graph(data_year, data, height): #
    try:
        crop_yield = [data[data_year][data_type]["Yield"] for data_type in data[data_year]]
        metric = [name for name in data[data_year]]
    
        df = pd.DataFrame({
            "Metric" : metric,
            "Value" : crop_yield,
            "colors" :["#53f10f"] * len(crop_yield)
        })
    except Exception: 
        livestock_amount = [data[data_year][data_type]["Amount"] for data_type in data[data_year]]
        metric = [name for name in data[data_year]]
        df = pd.DataFrame({
            "Metric" : metric,
            "Value" : livestock_amount,
            "colors" :["#0fadf1"] * len(livestock_amount)
        })
    chart = alt.Chart(df).mark_bar().encode(

        x=alt.X("Metric:N", axis=alt.Axis(title=None, labels=True, ticks=False, grid=True)),
        y=alt.Y("Value:Q", axis=alt.Axis(title=None, labels=True, ticks=False, grid=True)),
        color = alt.Color("colors:N", scale=None)
    ).properties(
        width=800,
        height=height,
    )
    return chart



        # return None

@st.dialog("User Data", width="large")
def show_data(sn,data):
    heights = [200,240,200,240]
    col1, col2, col3, col4 = st.columns(4)
    for serial_number in data:
        if serial_number != sn: continue
    
    with col1: 
        st.button("Serial Number", key=f"sn{sn}", width='stretch')
        st.info(sn)
    with col2: 
        st.button("Full Name", key=f"user_Name{sn}", width='stretch')
        st.info(data['name'])
    with col3: 
        st.button("Land Area", key=f"user_land_area{sn}", width='stretch')
        st.info(f"{formated(data["land_area"])} Ha")
    with col4: 
        st.button("Last Updated", width='stretch')
        st.info(f"{data["last_updated"]}")

    

    with st.expander("Crop Data"):
        years = [data_years for data_years in data['crops']]
        sorted_years = sort_years(list(set(years)))
        yr = st.multiselect("Filter By Year", options=sorted_years, default=sorted_years)
        col1, col2, col3, col4 = st.columns(4)
        cols = [col1, col2, col3, col4]
        i = 0
        
        
        for data_year in yr:
            if data['sn'] != sn: continue
     
            with cols[i]:
                with st.container(border=True):
                    
                    st.metric(label=f"Production Year", value=f"{data_year}")
                        # st.metric(label=f"Growth", value=f"{percent_complete(data['crops'][data_year][data_type])}")
                    st.altair_chart(alter_graph(data_year=data_year, data=data['crops'],height=heights[i]), use_container_width=True)
                i += 1
                if i >= 4:
                    i = 0
                    heights = heights[::-1]
    with st.expander("Livestock Data"):
        years = [data_years for data_years in data['livestock']]
        sorted_years = sort_years(list(set(years)))
        yr = st.multiselect("Filter By Year ", options=sorted_years, default=sorted_years)
        col1, col2, col3, col4 = st.columns(4)
        cols = [col1, col2, col3, col4]
        i = 0
        for data_year in yr:
            if data['sn'] != sn: continue
     
            with cols[i]:
                with st.container(border=True):
                    
                    st.metric(label=f"Production Year", value=f"{data_year}")
                        # st.metric(label=f"Growth", value=f"{percent_complete(data['crops'][data_year][data_type])}")
                    st.altair_chart(alter_graph(data_year=data_year, data=data['livestock'],height=heights[i]), use_container_width=True)
                i += 1
                if i >= 4:
                    i = 0
                    heights = heights[::-1]

@st.dialog("More Crop Ranking", width="large")
def crop_ranking(sorted_years, crop_ranking_data):
    col1, col2 = st.columns(2)
    columns = [col1, col2]
    i = 0
    for yr in sorted_years:
        with columns[i]:
            with st.expander(f"{yr} Ranking"):
                st.button(f"{yr}", width='stretch')
                ranked = rank(crop_ranking_data[yr])
                c1, c2, c3 = st.columns([1,3,3])
                with c1:
                    st.button("No.", key=f"No {yr}",width='stretch')
                with c2:
                    st.button("Crop Type",key= f"type{yr}", width='stretch')
                with c3:
                    st.button("Yield", key=f"yield{yr}",width='stretch')
                number = 1
                
                for crop in ranked:
                    with c1:
                        st.button(f"{number}", key=f"{number}-{crop[0]}-{yr}",width='stretch')
                    with c2:
                        st.success(f"{crop[0]}")
                    with c3: 
                        st.success(f"{formated(crop[1])} KG")
                    number += 1
        i += 1
        if i >= 2:
            i = 0

@st.dialog("More Livestock Ranking", width="large")
def livestock_ranking(sorted_years, livestock_ranking_data):
    col1, col2 = st.columns(2)
    columns = [col1, col2]
    i = 0
    for yr in sorted_years:
        with columns[i]:
            with st.expander(f"{yr} Ranking"):
                st.button(f"{yr}", width='stretch')
                ranked = rank(livestock_ranking_data[yr])
                c1, c2, c3 = st.columns([1,3,3])
                with c1:
                    st.button("No.", key=f"No {yr}",width='stretch')
                with c2:
                    st.button("LiveStock Type",key= f"type{yr}", width='stretch')
                with c3:
                    st.button("Amount", key=f"yield{yr}",width='stretch')
                number = 1
                
                for livestock in ranked:
                    with c1:
                        st.button(f"{number}",key=f"{number}-{livestock[0]}-{yr}",width="stretch")
                    with c2:
                        st.info(f"{livestock[0]}")
                    with c3: 
                        st.info(f"{formated(livestock[1])} KG")
                    number += 1
        i += 1
        if i >= 2:
            i = 0

