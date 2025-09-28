import streamlit as st
# import weather
import supplementary as sup


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
    <h1 style="color: white; text-align: center; font-family: Arial, sans-serif;"> Today's Weather Report </h1>
    """, unsafe_allow_html=True)  # CSS Styling for the st.metric and Title

    st.divider()
    matric_col1, matric_col2, matric_col3, matric_col4 = st.columns(4)
    st.set_page_config(page_title="AGRO-BOARD", layout="wide")

    with matric_col1:
        st.metric(label="Temperature", value=sup.get_weather('temp'), border=True)
    with matric_col2:
        st.metric("Wind Speed", sup.get_weather('wind'), border=True)
    with matric_col3:
        st.metric("Precipitation", sup.get_weather('rainfall'), border=True)
    with matric_col4:
        st.metric("Weather Station", sup.get_weather('station'), border=True)

    st.divider()
