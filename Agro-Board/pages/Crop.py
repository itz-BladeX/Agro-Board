import streamlit as st
import shelve
import pandas as pd
import supplementary as sup

database = "crop_database"

st.set_page_config(layout="wide")

tab1, tab2 = st.tabs(["Crops", "Add New "])

if "ad" not in st.session_state:
    st.session_state.ad = False


def toggle():   # Advanced Obtion Toggle
    st.session_state.ad = not st.session_state.ad
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------


with tab1:
    # Toggle for custom made table of built in st.framework()
    s = st.toggle("Big Screen")
    if s:
        col1, col2, col3, col4, col5 = st.columns(5)

        with shelve.open(database) as db:
            with col1:
                st.info("ID")
            with col2:
                st.info("Type")
            with col3:
                st.info("Planted Date!")
            with col4:
                st.info("Harvest Estimation [Auto]")
            with col5:
                st.info("Harvest Estimation [User]")
            st.divider()

            for key in db:  # Loop over the db keys and display results
                crop = db[key]
                with st.container():
                    with col1:
                        st.success(crop.id)
                    with col2:
                        st.success(crop.type)
                    with col3:
                        st.success(crop.date)
                    with col4:
                        st.success(crop.estimated)
                    with col5:
                        st.success(crop.user_estimated)

    else:  # DataFrame for small table id toggle not toggled
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with shelve.open(database) as db:
                data = {key: vars(crop) for key, crop in db.items()}
                # st.write("Loaded keys:", list(db.keys()))
                data = pd.DataFrame.from_dict(data, orient="index")
                if "id" in data.columns:
                    data = data.drop(columns=["id"])
                data.index.name = "ID"
                data = data.rename(columns={
                    "id": "Crop ID",
                    "type": "Crop Type",
                    "date": "Planted Date",
                    "estimated": "Harvest Estimation [Auto]",
                    "user_estimated": "Harvest Estimation [User]"
                })
                st.dataframe(data)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:  # Clear DataBase

        if "confirm" not in st.session_state:
            st.session_state.confirm = False

        if st.button("Clear", width="stretch", icon=":material/warning:"):
            st.session_state.confirm = True

        if st.session_state.confirm:

            st.error("WARNING", width="stretch", icon=":material/warning:")
            st.error("YOU ARE ABOUT TO CLEAR ALL YOUR DATABASE!!!",
                     width="stretch", icon=":material/warning:")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("DELETE", type="primary", use_container_width=True):

                    with shelve.open(database) as db:
                        db.clear()
                    st.success("Database cleared ✅")
                    st.session_state.confirm = False
                    st.rerun()

            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.confirm = False
                    st.rerun()

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:  # Search Bar

        with st.container(border=True):
            id = str(st.text_input("Crop-ID"))
            search = st.button("Search", width="stretch",
                               icon=":material/search:")
    if search:  # Search Alg
        col1, col2, col3, col4, col5 = st.columns(5)
        with shelve.open(database) as db:
            if id not in db:
                st.warning("ID not found")
            else:
                with col1:
                    st.info("ID")
                    st.success(db[id].id)
                with col2:
                    st.info("Type")
                    st.success(db[id].type)
                with col3:
                    st.info("Planted Date")
                    st.success(db[id].date)
                with col4:
                    st.info("Harvest Estimation [Auto]")
                    st.success(db[id].estimated)
                with col5:
                    st.info("Harvest Estimation [User]")
                    st.success(db[id].user_estimated)
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
with tab2:
    left, middle, right = st.columns([1, 2, 1])
    with middle:
        with st.container():
            st.title("Add Crop")
            st.toggle("Advanced", on_change=toggle, value=st.session_state.ad)
            with st.form(key="crop info"):
                # Collect Crop Informatioln
                id = str(st.text_input(
                    "ID: ", placeholder="3 digit ID recommended"))
                type = st.selectbox(label="Type", options=[
                                    key for key in sup.crop_dict], )
                date = st.date_input("Planted Date")
                if st.session_state.ad:
                    user_estimated = st.date_input(label="Expected Harvest: ")

                submit = st.form_submit_button(width="stretch")

                if not all([id, type, date, submit]):  # check if every parameter is filled
                    st.warning("Please Fill every box")
                if submit:  # Check if ID is taken or not
                    with shelve.open(database) as db:
                        if id not in db:
                            try:
                                crop = sup.crop(
                                    type, date, id, user_estimated)
                            except:
                                crop = sup.crop(
                                    type, date, id, user_estimated=None)
                            db[id] = crop
                            st.success(
                                f"Saved Successfully {crop.id}: {crop.type}", width="stretch")
                        else:
                            st.warning("Crop ID is Taken")
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
