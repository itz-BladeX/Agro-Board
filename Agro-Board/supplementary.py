import requests
import geocoder
import datetime as dt
import streamlit as st
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------\
# Crop Class used under Crop.py / tab2


class crop:  # Class for crops called by Crops.py file to save new crops to db
    def __init__(self, type, date, id, user_estimated=None):
        self.type = type
        self.date = date
        self.estimated = estimated_date(date, crop_dict[type])
        self.user_estimated = user_estimated
        self.id = id
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------


class livestock:
    def __init__(self, id, type, date, amount, duration=None):
        self.id = id
        self.type = type
        self.date = date
        self.amount = amount
        self.duration = duration


livestock_dict = {
    "Goat": 1,
    "Sheep": 1,
    "Cattle": 1,
    "Cow": 1
}
crop_dict = {  # Some pre-defined crops used to show the obtions and contains their average harvest peroid in days
    "Teff": 75,
    "Maize": 90,
    "Inset": 730,
    "Wheat": 91,
    "Sorghum": 110,
}
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
# Get Weather -----------------------------------------------------------------------------------------------


@st.cache_data(ttl=600)  # Store to catch
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
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
# Caculate Estimated Harvest Day, Called by class Crop


def estimated_date(current_date, add_days):

    def is_leap_year(year):  # Check for leap year, if found make feb 28 days else feb is 29 days
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    days_in_month = {  # Days for each month
        1: 31,
        2: 28,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31
    }

    day = current_date.day
    month = current_date.month
    year = current_date.year
    while add_days > 0:  # Calculate the day, month and year
        if month == 2 and is_leap_year(year):
            days_in_month[month] += 1
        if day < days_in_month[month]:
            day += 1
        else:
            day = 1
            month += 1
            if month > 12:
                month = 1
                year += 1
        add_days -= 1
    # return the estimated date as datetime object
    return dt.date(year, month, day)
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
