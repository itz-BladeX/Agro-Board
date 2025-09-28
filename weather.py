import requests
import geocoder
from datetime import datetime
import streamlit as st


@st.cache_data(ttl=600)
def get_weather(arg):
    try:
        g = geocoder.ip('me')
        city = g.city
        state = g.state
        country = g.country
        lat, lon = g.latlng
        # url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=precipitation"
        print("Your approximate location (latitude, longitude):", g.latlng)

        response = requests.get(url)
        data = response.json()
        weather = data["current_weather"]
        rainfall = sum(data["hourly"]["precipitation"][:12])

        if arg == "temp":
            return f"☀️ {weather["temperature"]} °C"
        elif arg == "wind":
            return f"💨 {weather["windspeed"]} km/h"
        elif arg == "rainfall":
            return f"🌧️ {rainfall} mm"
        elif arg == "station":
            return f"🏠 {city}"

        print("Open-Meteo Current Weather:")
        print(data["current_weather"])
        print(response)
        print(response)
        print(f"""
            City: {city}
            State: {state}
            Country: {country}
            Time: {weather['time']}
            Temp: {weather["temperature"]} °C
            Wind Speed: {weather["windspeed"]} km/h
            Rainfall: {rainfall} mm
        """)
        # lit.st.metric("Weather", weather["temperature"], -3)

    except Exception as e:
        print(
            "Error while Searching for weather, Try again when enternet is available !", e)
        return "—"
