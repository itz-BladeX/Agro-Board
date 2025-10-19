import streamlit as st
import shelve
import pandas as pd
import supplementary as sup
from streamlit_javascript import st_javascript
import time

database = "livestock_database"
st.set_page_config(layout="wide")
st.logo("logo.png", size='large')


Width = st_javascript("window.innerWidth", key="livestock_width")
sup.render_nav("Livestock Data", Width)
time.sleep(0.5)


if "adl" not in st.session_state:
    st.session_state.adl = False




st.markdown("""<style> button { height: 56px !important; padding-bottom:5px !important; } </style>""", unsafe_allow_html=True)


if "big" not in st.session_state:
    st.session_state.big = False
# Toggle for custom made table of built in st.framework()
bcol1, bcol2 = st.columns(2)


 


if st.button("Change Table", width="stretch", icon=":material/fullscreen:"):
    st.session_state.big = not st.session_state.big

if st.session_state.big:
    info1, info2 = st.columns([0.84,1])
    with info1:
        st.button("Progress", width="stretch")
    with info2:
        st.button("Economics [Birr]", width="stretch")

    with shelve.open(database) as db:
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([3,2,3,3,3,3,2.5,2.5,1,1])
        with col1: st.button("Type", width="stretch")
        with col2: st.button("Amount", width="stretch")
        with col3: st.button("Imported Date", width="stretch")
        with col4: st.button("Export Date", width="stretch")
        with col5: st.button("Import Cost", width="stretch")
        with col6: st.button("Export Cost", width="stretch")
        with col7: st.button("Prod. Cost", width="stretch")
        with col8: st.button ("Profit", width="stretch")
        with col9: st.button("", icon=":material/add:", on_click=sup.add_data, args=(database,))
        with col10: st.button("",icon=":material/autorenew:", on_click=st.rerun)
        years = [key for key in db]
        year_list = sup.sort_years(list(set(years)))
        for yr in year_list:

            st.button (yr, width="stretch")
            for selected_year in db:  # Loop over the db keys and display results
                if selected_year == yr:
                    year_data = db[selected_year]
                    for livestock_type in year_data:
                        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([3,2,3,3,3,3,2.5,2.5,1,1])
                        livestock = year_data[livestock_type]
                        with col1: st.info(livestock.type)
                        with col2: st.info(livestock.amount)
                        with col3: st.info(livestock.date)
                        with col4: st.info(livestock.export_date)
                        with col5: st.info(sup.format_number(livestock.import_cost))
                        with col6: st.info(sup.format_number(livestock.export_cost))
                        with col7: st.info(sup.format_number(livestock.production_cost))
                        with col8: st.info(sup.format_number(livestock.profit))
                        with col9: st.button(icon=":material/edit:", label="", key=f"edit{yr}{livestock_type}", on_click=sup.edit, args=(database,None, yr,livestock_type ), type="secondary", help="Edit Data")
                        with col10: st.button(icon=":material/delete:",label="", key=f"del{yr}{livestock_type}", on_click=sup.delete, args=(database,yr, livestock_type), type="primary", help="Delete Data Permanently")


else:  # DataFrame for small table id toggle not toggled
    with shelve.open(database) as db:
        data = {}
        for year, livestock_dict in db.items():
            for livestock_type, livestock_data in livestock_dict.items():
                data[year , livestock_type] = vars(livestock_data)
        data = pd.DataFrame.from_dict(data, orient="index")
        if "production_year" in data.columns and "type" in data.columns:
            data = data.drop(columns=["production_year", "type"])
        try:data.index.names = ["Production year", "Type"]
        except:data.index.name = "Production year"
        data = data.rename(columns={
            "date": "Imported Date",
            "export_date": "Export Date",
            "amount": "Amount",
            "import_cost": "Import Cost",
            "export_cost": "Export Cost",
            "production_cost" : "Prod.Cost",
            "profit" : "Profit"
        })
        st.dataframe(data, width="stretch")



