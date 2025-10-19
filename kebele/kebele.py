
import streamlit as st
import add_on as sp

st.logo("logo.png", size='large')



kebele = "02"

st.set_page_config(layout="wide")
st.markdown("""<style> button { height: 56px !important; padding-bottom:5px !important; } </style>""", unsafe_allow_html=True)
st.markdown("""   
    <style text-align: center>
    [data-testid="stMetricLabel"],
    [data-testid="stTitle"],
    [data-testid="stMetric"] {
        text-align: center !important;
        display: block !important;
    }
    </style> <h2 style="color: white; text-align: center; font-family: Arial, sans-serif;"> Kebele DashBoard </h2>""", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)


# st.markdown("""<style> button { height: 56px !important; padding-bottom:5px !important; } </style>""", unsafe_allow_html=True)

with col1: st.metric("Total Users Registered", value=sp.get_client_count(kebele), border=True)
with col2: st.metric("Total Land Area", value=f"{sp.get_total_land_area(kebele)} Ha", border=True)
with col3: st.metric("Most Common Crop Type", value=f"{sp.get_common_crop(kebele)}",border=True)
with col4: st.metric("Most Common Livestock Type", value=f"{sp.get_common_livestock(kebele)}", border=True)
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.markdown("""</style> <h3 style="color: white; text-align: center; font-family: Arial, sans-serif;"> Crop Ranking By Yield </h3>""", unsafe_allow_html=True)
    crop_ranking_data = sp.get_crop_ranking(kebele)
    years = [year for year in crop_ranking_data]
    sorted_years = sp.sort_years(list(set(years)))
    
    
    for yr in sorted_years[:1]:
        st.button(f"{yr}", width='stretch')
        ranked = sp.rank(crop_ranking_data[yr])
        c1, c2, c3 = st.columns([1,3,3])
        with c1:
            st.button("No.", width='stretch')
        with c2:
            st.button("Crop Type", width='stretch')
        with c3:
            st.button("Yield", width='stretch')
        rank = 1
        for crop in ranked:
            with c1:
                st.button(f"{rank}", key=f"crop-ranking{rank}", width="stretch")
            with c2:
                st.success(f"{crop[0]}")
            with c3: 
                st.success(f"{sp.formated(crop[1])} KG")
            rank += 1
            if rank > 3:
                break
        
        for x in range(4-rank):
            with c1:
                st.button(f"{rank}", key=f"crop{rank}", width="stretch")
            with c2:
                st.success("None")
            with c3: 
                st.success("None")
            
    st.button("See More",key=f"See more Crop ranking", on_click=sp.crop_ranking, args=(sorted_years,crop_ranking_data),width="stretch")
  
with col2:
    st.markdown("""</style> <h3 style="color: white; text-align: center; font-family: Arial, sans-serif;"> LiveStock Ranking By Amount </h3>""", unsafe_allow_html=True)
    livestock_ranking_data = sp.get_livestock_ranking(kebele)
    years = [year for year in livestock_ranking_data]
    sorted_years = sp.sort_years(list(set(years)))
    for yr in sorted_years[:1]:
        st.button(f"{yr}", width='stretch', key={yr})
        ranked = sp.rank(livestock_ranking_data[yr])
        col1, col2, col3 = st.columns([1,3,3])
        with col1:
            st.button("No.", width='stretch', key='random')
        with col2:
            st.button("Livestock Type", width='stretch', key="{yr}")
        with col3:
            st.button("Amount", width='stretch', key="{yr}1")
        rank = 1
        for livestock in ranked:
            with col1:
                st.button(f"{rank}", width='stretch', key=f"livestock-ranking{rank}")
            with col2:
                st.info(f"{livestock[0]}")
            with col3: 
                st.info(f"{sp.formated(livestock[1])}")
            rank += 1
            if rank > 3:
                break
    for x in range(4-rank):
        with col1:
            st.button(f"{rank}",width='stretch', key=f"livestock{rank}")
        with col2:
            st.info("None")
        with col3: 
            st.info("None")
    st.button("See More",key=f"See more livestock ranking",on_click=sp.livestock_ranking, args=(sorted_years,livestock_ranking_data), width="stretch")
        
st.divider()

st.markdown("""</style> <h3 style="color: white; text-align: center; font-family: Arial, sans-serif;"> User Data </h3>""", unsafe_allow_html=True)

col1, col2, col3, col4,  col6, col7 = st.columns([0.7,2,2,2,2,0.5])
number = 1
with col1: st.button("No.", key=f"user_number", width='stretch')
with col2: st.button("Serial Number", key=f"user_SN", width='stretch')
with col3: st.button("Full Name", key=f"user_Name", width='stretch')
with col4: st.button("Land Area", key=f"user_land_area", width='stretch')
with col6: st.button("Last Updated", width='stretch')
with col7: st.button("", icon=":material/autorenew:", width='stretch')

for sn, data in sp.get_user_data(kebele).items():
    with col1: st.button(f"{number}", width="stretch")
    with col2: st.info(sn)
    with col3: st.info(data['name'])
    with col4: st.info(f"{sp.formated(data["land_area"])} Ha")
    with col6: st.info(f"{data["last_updated"]}")
    with col7: st.button("☰", key=sn, use_container_width=True, on_click=sp.show_data, args=(sn,data))
    number += 1

st.button(" ", width="stretch")


    

