import streamlit as st
import datetime as dt


def estimated_date(current_date, add_days):

    def is_leap_year(year):
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    days_in_month = {
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
    while add_days > 0:
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

    return dt.date(year, month, day)


# date = st.date_input("Input date")
# add = st.number_input("Number of days expected", min_value=0)

# st.write(date)
# est = estimated_date(date, add)
# st.write(est)
