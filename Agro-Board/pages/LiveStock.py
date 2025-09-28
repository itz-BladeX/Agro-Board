import streamlit as st
import shelve
import pandas as pd
import supplementary as sup

database = "livestock_database"

st.set_page_config(layout="wide")

tab1, tab2 = st.tabs(["Livestock", "Add New"])

# if "ad" not in st.session_state:
#     st.session_state.ad = False

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
                st.info("Imported Date!")
            with col4:
                st.info("Amount Imported")
            with col5:
                st.info("Duration Set Upto")
            st.divider()

            for key in db:  # Loop over the db keys and display results
                livestock = db[key]
                with st.container():
                    with col1:
                        st.success(livestock.id)
                    with col2:
                        st.success(livestock.type)
                    with col3:
                        st.success(livestock.date)
                    with col4:
                        st.success(livestock.amount)
                    with col5:
                        st.success(livestock.duration)

    else:  # DataFrame for small table id toggle not toggled
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with shelve.open(database) as db:
                data = {key: vars(livestock) for key, livestock in db.items()}
                # st.write("Loaded keys:", list(db.keys()))
                data = pd.DataFrame.from_dict(data, orient="index")
                if "id" in data.columns:
                    data = data.drop(columns=["id"])
                data.index.name = "ID"
                data = data.rename(columns={
                    "id": "Livestock ID",
                    "type": "Livestock Type",
                    "date": "Imported Date",
                    "amount": "Livestock Amount",
                    "duration": "Duration"
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
            id = str(st.text_input("LiveStock-ID"))
            search = st.button("Search", width="stretch", icon=":material/search:")
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
                    st.info("Imported Date")
                    st.success(db[id].date)
                with col4:
                    st.info("Imported Amount")
                    st.success(db[id].amount)
                with col5:
                    st.info("Duration")
                    st.success(livestock.duration)
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------

if "advanced" not in st.session_state:
    st.session_state.advanced = False
def toggle():   # Advanced Obtion Toggle
    st.session_state.advanced = not st.session_state.advanced
with tab2:
    left, middle, right = st.columns([1, 2, 1])
    with middle:
        with st.container():
            st.title("Add Livestock")
            st.toggle("Advanced", on_change=toggle, value=st.session_state.advanced)
            with st.form(key="livestock info"):
                # Collect livestock Informatioln
                id = str(st.text_input("ID: ", placeholder="3 digit ID recommended"))
                type = st.selectbox(label="Type", options=[key for key in sup.livestock_dict])
                date = st.date_input("Imported Date: ")
                amount = st.number_input("Amount imported: ", min_value=1)
                if st.session_state.advanced:
                    duration  = st.date_input(label="Duration: ")
                submit = st.form_submit_button(width="stretch")
                if not all([id, type, date, submit]):  # check if every parameter is filled
                    st.warning("Please Fill every box")
                if submit:  # Check if ID is taken or not
                    with shelve.open(database) as db:
                        if id not in db:
                            try:
                                livestock  = sup.livestock(type, id,date,amount, duration)
                            except:
                                livestock  = sup.livestock(type, id,date,amount, duration)
                            st.success(f"Saved Successfully {livestock.id}: {livestock.type}", width="stretch")
                            db[id] = livestock

                        else:
                            st.warning("Livestock ID is Taken")
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------