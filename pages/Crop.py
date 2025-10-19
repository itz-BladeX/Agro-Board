import streamlit as st
import shelve
import pandas as pd
import supplementary as sup
import time
from streamlit_javascript import st_javascript

st.set_page_config(layout="wide")
st.logo("logo.png", size='large')
database = "crop_database"


width = st_javascript("window.innerWidth", key="crop_width")
with st.spinner("Loading..."):
    sup.render_nav("Crop Data", width)

time.sleep(0.5)




width = st_javascript("window.innerWidth")

# tab1, tab2, tab3 = st.tabs(["View", "Add", "Update"])

if "ad" not in st.session_state:
    st.session_state.ad = False

# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------

st.markdown("""<style> button { height: 56px !important; padding-bottom:5px !important; } </style>""", unsafe_allow_html=True)



if "big" not in st.session_state:
    st.session_state.big = False
# Toggle for custom made table of built in st.framework()
bcol1, bcol2 = st.columns(2)


if st.button("Change Table", width="stretch", icon=":material/fullscreen:"):
    st.session_state.big = not st.session_state.big


        
    
if st.session_state.big:
    info1, info2 = st.columns([1.2,1])
    with info1:
        st.button("Progress", width="stretch")
    with info2:
        st.button("Economics [Birr]" ,width='stretch')
    

    
    with shelve.open(database) as db:
        col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([3,3,3,3,3,2.5,2.5,1,1])
        with col1: st.button("Type", width="stretch")
        with col2: st.button("Planted Date", width="stretch")
        with col3: st.button("Harvest Date", width="stretch")
        with col4: st.button("Yield [kg]", width="stretch")
        with col5: st.button("Export Cost", width="stretch")
        with col6: st.button("Prod. Cost", width="stretch")
        with col7: st.button("Profit", width="stretch")
        with col8: st.button("",  icon=":material/add:", on_click=sup.add_data, args=(database,), width="stretch")
        with col9: st.button("", icon=":material/autorenew:", on_click=st.rerun,width="stretch")
        years = [key for key in db]
        year_list = sup.sort_years(list(set(years)))
        for yr in year_list:
            st.button(f"{yr}", width="stretch")
            for select_year in db:
                if select_year == yr:
                    year_data = db[select_year]
                    for crop_type in year_data:
                        crop = year_data[crop_type]
                                                    
                        col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([3,3,3,3,3,2.5,2.5,1,1])  # Loop over the db keys and display results
                        
                        with col1: st.success(crop.type)
                        with col2: st.success(crop.date)
                        with col3: st.success(str(crop.estimated) + " " + crop.user)
                        with col4: st.success(sup.format_number(crop.yield_amount))
                        with col5: st.success(sup.format_number(crop.production_cost))
                        with col6: st.success(sup.format_number(crop.export_cost))
                        with col7: st.success(sup.format_number(crop.profit))
                        with col8: st.button(icon=":material/edit:", label="", key=f"edit{yr}{crop_type}", on_click=sup.edit, args=(database, None, yr, crop_type), type="secondary", width='stretch')
                        with col9: st.button(icon=":material/delete:",label="", key=f"del{yr}{crop_type}", on_click=sup.delete, args=(database, yr, crop_type), type="primary", width="stretch")
                
                        


else:  # DataFrame for small table id toggle not toggled
    with shelve.open(database) as db:
        # data_years = [years for years in db]
        data = {}
        for year, crops_dict in db.items():
            for crop_type, crop_data in crops_dict.items():
                data[year, crop_type] = vars(crop_data)
        # st.write("Loaded keys:", list(db.keys()))
        data = pd.DataFrame.from_dict(data, orient="index")
        if "production_year" in data.columns and "type" in data.columns:
            data = data.drop(columns=["production_year", "type"])
        try:data.index.names = ["Production year", "Type"]
        except:data.index.name = "Production year"  
        data = data.rename(columns={
            "type": "Crop Type",
            "date": "Planted Date",
            "estimated": "Harvest Estimation",
            "yield_amount": "Yield [kg]",
            "export_cost": "Export Cost",
            "production_cost" : "Prod. Cost",
            "profit" : "Profit"
        })
        st.dataframe(data, width="stretch")


    





# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
