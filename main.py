import streamlit as st
# import weather
import supplementary as sup
import shelve
import streamlit_option_menu as om
import time
from streamlit_javascript import st_javascript
st.set_page_config(page_title="AGRO-BOARD", layout="wide", )
st.logo("logo.png", size='large')


width = st_javascript("window.innerWidth", key="main_width")
sup.render_nav("main", width)
time.sleep(0.5)

st.markdown("""
<style>
    /* Target the default nav section in sidebar */
    [data-testid="stSidebar"] > div > div > div > section > div:first-child {
        display: none !important;
    }
    /* Alternative selector if above doesn't catch it (more broad) */
    /* section[data-testid="stSidebar"] nav { display: none !important; } */
</style>
""", unsafe_allow_html=True)


crop = "crop_database"
livestock = "livestock_database"
inventory = "inventory_database"

with st.container():  # Weather Section
    st.markdown("""   
    <style text-align: center>
    [data-testid="stMetricLabel"],
    [data-testid="stTitle"],
    [data-testid="stMetric"] {
        text-align: center !important;
        display: block !important;
    }
    </style>          
    <h2 style="color: white; text-align: center; font-family: Arial, sans-serif;"> Today's Weather Report </h2>
    """, unsafe_allow_html=True)  # CSS Styling for the st.metric and Title

    st.divider()
    matric_col1, matric_col2, matric_col3, matric_col4 = st.columns(4)
    st.set_page_config(page_title="AGRO-BOARD", layout="wide")
    with st.spinner("Fetching Weather Data..."):
        with matric_col1:
            st.metric(label="Temperature", value=sup.get_weather('temp'), border=True)
        with matric_col2:
            st.metric("Wind Speed", sup.get_weather('wind'), border=True)
        with matric_col3:
            st.metric("Precipitation", sup.get_weather('rainfall'), border=True)
        with matric_col4:
            st.metric("Weather Station", sup.get_weather('station'), border=True)

    st.divider()

with shelve.open("config") as db:
    try:
        SN = db["SN"]
        name = db["name"]
    except KeyError:
        sup.configuration()
# Widgets

st.markdown("""

<h2 style="color: white; text-align: center; font-family: Arial, sans-serif;"> Statistics and Data </h2>


""", unsafe_allow_html=True)
# Crop
with st.expander("See Crop Data"):
    st.markdown("""<h3 style="color: white; text-align: center; font-family: Arial, sans-serif;"> Crops </h3>""", unsafe_allow_html=True)
    heights = [220,260, 220, 260]
    with shelve.open(crop) as db:
        i = 0
        years = [key for key in db]
        year_list = sup.sort_years(list(set(years)))
        selected_year_list = st.multiselect("Filter By Year", options=year_list, default=year_list, key="multiselect_crop")
        selected_year_list = sup.sort_years(list(set(selected_year_list)))
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        cols = [col1, col2, col3, col4]
        for yr in selected_year_list:
            for select_year in db:
                if select_year == yr:
                    year_data = db[select_year]
                    for data_type in year_data:
                        data = year_data[data_type]
                        height = heights[i]
                        with cols[i]:
                            with st.container(border=True):
                                left, right = st.columns(2)
                                with left:
                                    st.metric(label=f"{yr}", value=f"{data_type}")
                                with right:
                                    st.metric(label=f"Growth", value=sup.percent_complete(db[yr][data_type]))
                                st.altair_chart(sup.alter_graph(data_year=yr,data_type=data_type, database=crop, height=height), use_container_width=True)
                        if i >= 3:
                            i = 0
                            heights = heights[::-1]
                        else:
                            i += 1
            
    # Livestock

with st.expander("See LiveStock Data"):
    st.markdown("""<h3 style=" color: white; text-align: center; font-family: Arial, sans-serif;"> LiveStocks </h3>""", unsafe_allow_html=True)
    heights = [220,260, 220, 260]
    with shelve.open(livestock) as db:
        
        i = 0
        years = [key for key in db]
        year_list = sup.sort_years(list(set(years)))
        selected_year_list = st.multiselect("Filter By Year", options=year_list, default=year_list, key="multiselect_livestock")
        selected_year_list = sup.sort_years(list(set(selected_year_list)))
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        cols = [col1, col2, col3, col4]
        for yr in selected_year_list:
            for select_year in db:
                if select_year == yr:
                    year_data = db[select_year]
                    for data_type in year_data:
                        data = year_data[data_type]
                        height = heights[i]
                        with cols[i]:
                            with st.container(border=True):
                                left, right = st.columns(2)
                                with left:
                                    st.metric(label=f"{yr}", value=f"{data_type}")
                                with right:
                                    st.metric(label="Amount", value=db[yr][data_type].amount)
                                st.altair_chart(sup.alter_graph(data_year=yr,data_type=data_type, database=livestock,height=height), use_container_width=True)
                        if i >= 3:
                            i = 0
                            heights = heights[::-1]
                        else:
                            i += 1
for x in range(3):
    st.write("")
col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.button(" ⬆️ Upload Data", on_click=sup.package_data, width="stretch")
with col2:
    with st.container(border=True):
        st.button("⚙️ Edit Personal / Config /  Data", on_click=sup.edit_config, width="stretch")

