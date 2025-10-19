import requests
import geocoder
import datetime as dt
import streamlit as st
import altair as alt
import shelve
import pandas as pd
from datetime import datetime
import streamlit_option_menu as om
import time
import requests
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
def format_number(number):
    if number == None:
        return None
    return "{:,}".format(number)
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------\
# Crop Class used under Crop.py / tab2


class class_crop:  # Class for crops called by Crops.py file to save new crops to db
    def __init__(self, type=None, date=None,production_year=None, estimated=None, yield_amount=None,profit=None, production_cost=None, export_cost=None):
        self.production_year = production_year
        self.type = type
        self.yield_amount = yield_amount
        self.export_cost = export_cost
        self.date = date
        self.production_cost = production_cost
        if estimated != None:
            self.estimated = estimated
            self.user = "[User]"
        else:
            self.estimated = estimated_date(date, crop_dict[type])
            self.user  = "[Auto]"
        if export_cost != None and production_cost != None:
            self.profit = cal_profit(export_cost=export_cost, production_cost=production_cost)
        else:
            self.profit = profit
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
class class_livestock:
    def __init__(self, type, date, amount, production_year,export_date=None, import_cost=None, export_cost=None,production_cost=None, profit=None):
        self.production_year = production_year
        self.type = type
        self.date = date
        self.export_date = export_date
        self.amount = amount
        self.import_cost = import_cost
        self.export_cost = export_cost
        self.production_cost = production_cost
        if import_cost != None and export_cost != None:
            self.profit = cal_profit(import_cost=import_cost, export_cost=export_cost, production_cost=production_cost)
        else:
            self.profit = profit
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
class class_inventory:
    def __init__(self, id, label, quantity, date):
        self.id = id
        self.label = label
        self.quantity = quantity
        self.date = date

# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------

inventory_dict={
    "Shovel",
    "Fertilizer",
    "Tractors",
    "Seed",
    "Pesticides",
    "Hoes",
    "Watering Cans",
    "Plough",
    "Sprayers",
    "Wheelbarrows",
}
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
livestock_dict = {
    "Goat": 1,
    "Sheep": 1,
    "Cattle": 1,
    "Cow": 1,
    "Chicken": 1,
    "Pig": 1,
    "Beehive": 1,
    "Fish": 1,
}
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
crop_dict = {  # Some pre-defined crops used to show the obtions and contains their average harvest peroid in days
    "Teff": 75,
    "Maize": 90,
    "Inset": 730,
    "Wheat": 91,
    "Sorghum": 110,
    "Corn": 80,
    "Barley": 130,
    "Rice": 150,
}
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------

# Get Weather -----------------------------------------------------------------------------------------------
@st.cache_data(ttl=5000)  # Store to catch
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
            return f"☀️ {round(weather["temperature"], 2)} °C"
        elif arg == "wind":
            return f"💨 {round(weather["windspeed"],2)} km/h"
        elif arg == "rainfall":
            return f"🌧️ {round(rainfall,2)} mm"
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
def cal_profit(export_cost, import_cost=None, production_cost=None):  #Profil Calculation
    if import_cost != None:
        return export_cost - (import_cost + production_cost)
    return export_cost - production_cost
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
def alter_graph(data_year, data_type, database, height): #
    with shelve.open(database) as db:
        # print(db[data_year][data_type].production_cost, db[data_year][data_type].export_cost, db[data_year][data_type].yield_amount, db[data_year][data_type].profit)
        try:
            df = pd.DataFrame({
                "Metric" : ["Prod","Export","Yield","Profit" ],
                "Value" : [db[data_year][data_type].production_cost, db[data_year][data_type].export_cost, db[data_year][data_type].yield_amount, db[data_year][data_type].profit],
                "colors" :["#e74c3c","#3498db","#f1c40f", "#2ecc71"]    
        })
        except:
            df = pd.DataFrame({
                "Metric" : ["import Cost", "Prod","Export","Profit" ],
                "Value" : [db[data_year][data_type].import_cost, db[data_year][data_type].production_cost, db[data_year][data_type].export_cost, db[data_year][data_type].profit],
                "colors" :["#e74c3c", "#e74c3c","#3498db", "#2ecc71"]    
        })
    chart = alt.Chart(df).mark_bar().encode(

        x=alt.X("Metric:N", axis=alt.Axis(title=None, labels=True, ticks=False, grid=True)),
        y=alt.Y("Value:Q", axis=alt.Axis(title=None, labels=True, ticks=False, grid=True)),
        color = alt.Color("colors:N", scale=None)
    ).properties(
        width=800,
        height=height,
    )
    return chart
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
def percent_complete(data):
 
    try:
        start_date = data.date
        try: end_date = data.estimated
        except: end_date = data.export_date
        finally:
            print(type(start_date), start_date, end_date, id)
            total_days = (end_date - start_date).days
            current_date = datetime.now().date()
            days_passed = (current_date - start_date).days

            print(total_days, days_passed, current_date, start_date)
            if total_days == 0:
                day = 100
            else:
                day = min((days_passed / total_days) *100,100)

            return f"{int(day)} %"
    except:
        return None
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
def render_nav(current_page, width):
    pages = {
    "main": "main.py",
    "Crop Data": "pages/Crop.py",
    "Livestock Data": "pages/LiveStock.py",
    "Inventory Data": "pages/Inventory.py",
    "About": "pages/About.py",
    }
    page_list = list(pages.keys())
    if width < 1000:
        with st.sidebar:
            selected = om.option_menu(
                menu_title=None,
                options=page_list ,
                icons=["house", "bar-chart", "bar-chart", "bar-chart"],
                default_index=page_list.index(current_page)
            )
    else:
         selected = om.option_menu(
                menu_title=None,
                options=page_list, 
                icons=["house", "bar-chart", "bar-chart", "bar-chart" ],
                default_index=page_list.index(current_page),
                orientation="horizontal",
                styles={"nav-link": {"text-align": "center", "margin": "0em", "--hover-color": "#676767"},
                
            }
         )
            
    if selected != current_page:
        st.switch_page(pages[selected])
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
@st.dialog("Add Data")
def add_data(database):
    if database == "crop_database":
        with st.form(key="crop info"):
            st.success("Mandatory Fields 📌")
            # id = str(st.text_input("ID: ", placeholder="3 digit ID recommended", help="Unique ID for each crop"))
            crop_type = st.selectbox(label="Type", options=[key for key in crop_dict],help="Type of crop")
            date = st.date_input("Planted Date: ", help="Date when the crop was planted")
            production_year = st.text_input("Production Year", help="Only Production year, partial years like 2020/2021 are Allowed", placeholder="Production Year")
            st.info("Non Mandatory Fields ℹ️")
            estimated = st.date_input(label="Expected Harvest: ",value=None,help="date of harvest. If left empty, it will be calculated automatically")
            yield_amount = st.number_input(label="Yield [kg]", value=None, min_value=0.0, help="Expected or Actual Yield amount in kg, if left empty, it will be set to None")
            production_cost = st.number_input(label="Production Cost", value=None, min_value=0.0, help="Cost of producing the crop, e.g. seed price,fertilizer, water, etc.")
            export_cost = st.number_input(label="Export Price", value=None, min_value=0.0, help="Expected selling price of the crop")
            submit = st.form_submit_button("Submit", type="primary", width='stretch')
            
            if submit:  # Check if ID is taken or not
                if all([crop_type, date, submit, production_year]) == False:  # check if every parameter is filled
                    st.warning("Please Fill every box")
                else:
                    with shelve.open(database) as db:
                       
                        crop_data = class_crop(
                            date=date, 
                            type = crop_type,
                            production_year=production_year,
                            estimated=estimated,
                            export_cost=export_cost, 
                            production_cost=production_cost,
                            yield_amount=yield_amount,
                            )
                        year_data = db.get(production_year, {})
                        if crop_type in year_data:
                            st.warning(f"Crop Type Exists for the production year {production_year}, Try Editing Instead")
                        else:
                            # year_data = db[production_year] if db[production_year] else db[production_year] = {}  # Get the dict for this year
                            year_data[crop_type] =  crop_data # Add or update crop type
                            db[production_year] = year_data   # Save back to shelve
                            st.success(f"Data Saved!", width="stretch")
                            time.sleep(1)
                            st.rerun()
    elif database == "livestock_database":
        with st.form(key="livestock info"):
            st.success("Mandatory Fields 📌")
            livestock_type = st.selectbox(label="Type", options=[key for key in livestock_dict], help="Type of livestock")
            date = st.date_input("Date: ",help="Date when the livestock was imported or bought")
            production_year = st.text_input("Production Year")
            amount = st.number_input(label="Amount", value=1, min_value=1, help="Number of livestock imported or bought")
            st.info("Non Mandatory Fields ℹ️")
            export_date = st.date_input(label="Export Date: ",value=None,help="estimated export date, if left empty, it will be filled automatically")
            import_cost = st.number_input(label="Import Price", value=None, min_value=0.0, help="Cost of importing or buying the livestock")
            export_cost = st.number_input(label="Export Price", value=None, min_value=0.0, help="Expected selling price of the crop")
            production_cost = st.number_input(label="Production Cost", value=None, min_value=0.0, help="Cost of producing the crop, e.g. fertilizer, water, etc.")
            submit = st.form_submit_button("Submit", type="primary", width='stretch')           
            if submit:  # Check if ID is taken or not
                if all([production_year, livestock_type, date, amount, submit]) == False:  # check if every parameter is filled
                    st.warning("Please Fill every box")
                else:
                    with shelve.open(database) as db:
                        livestock_data = class_livestock(
                            type=livestock_type,
                            date=date,
                            production_year=production_year,
                            amount=amount,
                            import_cost=import_cost,
                            export_cost=export_cost,
                            production_cost=production_cost,
                            export_date=export_date
                            )
                        year_data = db.get(production_year, {})
                        if livestock_type in year_data:
                            st.warning(f"Livestock Type Exists for the production year {production_year}, Try Editing Instead")
                        else:
                            year_data[livestock_type] =  livestock_data
                            db[production_year] = year_data
                            st.success(f"Saved Successfully! ", width="stretch")
                            time.sleep(1)
                            st.rerun()             
    elif database == "inventory_database":
        with st.form(key="inventory info"):
            st.success("Mandatory Fields 📌")
            id = str(st.text_input("ID: ", placeholder="3 digit ID recommended", help="Unique ID for each inventory item"))
            label = st.selectbox(label="Label", options=[key for key in inventory_dict], help="Type of inventory item")
            date = st.date_input("Date: ", help="Date when the inventory item was added")
            quantity = st.number_input(label="Quantity", value=1, min_value=1, help="Quantity of the inventory item")
            submit = st.form_submit_button("Submit", type="primary", width='stretch')           
            if submit:  # Check if ID is taken or not
                if all([id, label, date, quantity, submit]) == False:  # check if every parameter is filled
                    st.warning("Please Fill every box")
                else:
                    with shelve.open(database) as db:
                        if id not in db:
                            inventory = class_inventory(
                                id=id,
                                label=label,
                                date=date,
                                quantity=quantity
                                )
                            db[id] = inventory
                            st.success(f"Saved Successfully !", width="stretch")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("Inventory ID is Taken")
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
@st.dialog("Update / Edit Data")
def edit(database=None, edit_id=None, edit_year=None, edit_type=None):
    if database == "crop_database":
        with st.form(key="crop edit"):
                with shelve.open(database, writeback=True) as db:
                # Collect Crop Informatioln
                    # new_id = str(st.text_input("ID", placeholder="3 digit ID recommended", value=db[edit_id].id))
                    new_type = st.selectbox(label="Type", options=[key for key in crop_dict], index=[key for key in crop_dict].index(db[edit_year][edit_type].type))
                    new_date = st.date_input("Planted Date", value=db[edit_year][edit_type].date)
                    new_production_year = st.text_input("Production year", value=db[edit_year][edit_type].production_year, disabled=True)
                    new_estimated = st.date_input(label="Expected Harvest", value=db[edit_year][edit_type].estimated)
                    new_yield_price = st.number_input(label="Yield[kg]", value=db[edit_year][edit_type].yield_amount)
                    new_production_cost = st.number_input(label = "Production Cost [Birr]", value=db[edit_year][edit_type].production_cost)
                    new_exported_price = st.number_input(label="Exported Price [Birr]", value=db[edit_year][edit_type].export_cost)
                    
                    submit_edit = st.form_submit_button(width="stretch")
                    if submit_edit:
                        if not all([new_production_year, new_type, new_date, submit_edit]):  # check if every parameter is filled
                            st.warning("Please Fill every box")
                        if not (new_type in db[edit_year] and new_type != edit_type):
                            if new_type != edit_type :
                                del db[edit_year][edit_type]
                            new_crop = class_crop(production_year=new_production_year,type=new_type, date=new_date, yield_amount=new_yield_price, estimated=new_estimated, export_cost=new_exported_price, production_cost=new_production_cost)
                            db[edit_year][new_type] = new_crop
                            st.success(f"Changes Saved Successfully!", width="stretch")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("Crop Type Already Taken")


    elif database == "livestock_database":
        with st.form(key="Livestock edit"):
                with shelve.open(database, writeback=True) as db:
                # Collect Crop Informatioln
                    new_type = st.selectbox(label="Type", options=[key for key in livestock_dict], index=[key for key in livestock_dict].index(db[edit_year][edit_type].type))
                    new_date = st.date_input("Imported Date", value=db[edit_year][edit_type].date)
                    new_production_year = st.text_input("Production year", value=db[edit_year][edit_type].production_year, disabled=True)
                    new_amount = st.number_input("Amount Imported", min_value=1, value=db[edit_year][edit_type].amount)
                    new_export_date = st.date_input(label="Estimated", value=db[edit_year][edit_type].export_date)
                    new_import_price = st.number_input(label="Import Price [Birr]", value=db[edit_year][edit_type].import_cost)
                    new_exported_price = st.number_input(label="Exported Price [Birr]", value=db[edit_year][edit_type].export_cost)
                    new_production_cost = st.number_input(label = "Production Cost [Birr]", value=db[edit_year][edit_type].production_cost)
                    submit_edit = st.form_submit_button(width="stretch")
                    if submit_edit:
                        if not all([new_production_year, new_type, new_date, submit_edit]):  # check if every parameter is filled
                            st.warning("Please Fill every box")
                        if not (new_type in db[edit_year] and new_type != edit_type):
                            if new_type != edit_type :
                                del db[edit_year][edit_type]
                                new_livestock = class_livestock(
                                type=new_type,
                                date=new_date,
                                production_year=new_production_year,
                                amount=new_amount,
                                import_cost=new_import_price,
                                export_date=new_export_date,
                                export_cost=new_exported_price,
                                production_cost=new_production_cost)
                            db[edit_year][new_type] = new_livestock
                            st.success(f"Changes Saved Successfully", width="stretch")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("ID Already Taken")
    elif database == "inventory_database":
        with st.form(key="Inventory edit"):
                with shelve.open(database) as db:
                # Collect Crop Informatioln
                    new_id = str(st.text_input("ID", placeholder="3 digit ID recommended", value=db[edit_id].id))
                    new_label = st.selectbox(label="Label", options=[key for key in inventory_dict], index=[key for key in inventory_dict].index(db[edit_id].label))
                    new_date = st.date_input("Date", value=db[edit_id].date)
                    new_quantity = st.number_input("Quantity", min_value=1, value=db[edit_id].quantity)
                    submit_edit = st.form_submit_button(width="stretch")
                    if submit_edit:
                        if not all([new_id, new_label, new_date, new_quantity, submit_edit]):  # check if every parameter is filled
                            st.warning("Please Fill every box")
                        if not (new_id in db and new_id!= edit_id):
                            if new_id != edit_id:
                                del db[edit_id]
                            new_inventory = class_inventory(
                                id=new_id,
                                label=new_label,
                                date=new_date,
                                quantity=new_quantity)
                            db[new_id] = new_inventory
                            st.success(f"Changes Saved Successfully!", width="stretch")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("ID Already Taken")
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
@st.dialog("Delete Data Permenantly🚨")
def delete(database, del_year, del_type=None):
    with shelve.open(database, writeback=True) as db:
        if database == "inventory_database":
            st.write(f"Are you sure you want to delete data {del_year} of label {db[del_year].label} ? ?")
        else: st.write(f"Are you sure you want to delete data  of type {del_type} ?")
        st.error("This action is irreversible! ⚠️", width="stretch")
        confirm = st.button("Confirm Delete", type="primary", width="stretch", icon=":material/delete:", help="This action is irreversible")
        if confirm:
            if database == "inventory_database": del db[del_year]
            else:
                del db[del_year][del_type]
                if not db[del_year]:
                    del db[del_year]
            st.success("Deleted Successfully", width="stretch")
            time.sleep(1)
            st.rerun()
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
@st.dialog("Welcome to Agro-Board")
def configuration(arg = None):
    with st.container(border=True):
        st.info("Fill out the following to set up your app")
        name = st.text_input("Name", placeholder="Enter your full name", help="This is used to personalize the app")
        kebele = st.selectbox("Qabale",options=["01", "02"], placeholder="Your current Qabale")
        land_area = st.number_input("Argicultural Land Area [Ha]", min_value=0, step=1, help="Your Average Agricultural Land Area in Hectars", value=0)
        if st.button("Get Serial Number /REGISTER/", help="Your special SN that identifies you to higher authorities", width="stretch"):
            if all([name, kebele]):
                SN = requests.get(f"http://127.0.0.1:8000/client/register/{name}")
                if SN:
                    sn = SN.json()
                    st.success(f"Successfully Registered: SN: {sn["SN"]}")
                    with shelve.open("config") as db:
                        db["SN"] = sn["SN"]
                    
                    with shelve.open("config", writeback=True) as db:
                        db["name"] = name
                        db["kebele"] = kebele
                        db["land_area"] = int(land_area)
                    st.success("Saved Successfully", width="stretch")
                    time.sleep(1)
                    st.rerun()
            else:
                st.info("Please Fill Every Parameter")

    return None
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
def get_config(arg):
    with shelve.open("config") as config:
        return config[arg]
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
@st.dialog("Upload Data")
def package_data():
    with st.form("Upload Data"):
        st.info("Data to Upload", width="stretch")
        crop_confirm = st.checkbox("Crop Data", value=True)
        livestock_confirm = st.checkbox("LiveStock Data", value=True)
        submit = st.form_submit_button("Send To Server",width="stretch")
    if submit:
        crop_data = {}
        livestock_data = {}
        
        if crop_confirm:
            with shelve.open("crop_database") as db:
                crop_type_dict = {}
                years = [year for year in db]
                ordered_year_list = sort_years(list(set(years)))
                for yr in ordered_year_list:
                    for production_year in db:
                        if production_year != yr:
                            continue
                        year_dict = {}
                        year_dict[yr] = {}
                        for crop_type in db[yr]:
                            crop = db[yr][crop_type]
                            crop_type_dict = {crop_type:{
                                "Planted Date" : crop.date.isoformat() if hasattr(crop.date, "isoformat") else str(crop.date),
                                "Harvested Date": crop.estimated.isoformat() if hasattr(crop.estimated, "isoformat") else str(crop.estimated),
                                "Yield" : crop.yield_amount,
                                "Export Cost": crop.export_cost,
                                "Production Cost": crop.production_cost,
                                "Profit": crop.profit
                                }
                            }
                            year_dict[yr].update(crop_type_dict)
                        crop_data.update(year_dict)
        if livestock_confirm:
            livestock_data = {}
            with shelve.open("livestock_database") as db:
                livestock_type_dict = {}
                years = [year for year in db]
                ordered_year_list = sort_years(list(set(years)))
                for yr in ordered_year_list:
                    for production_year in db:
                        if production_year != yr:
                            continue
                        year_dict = {}
                        year_dict[yr] = {}
                        for livestock_type in db[yr]:
                            livestock = db[yr][livestock_type]
                            livestock_type_dict = {livestock_type:{
                                "Imported Date": livestock.date.isoformat() if hasattr(livestock.date, "isoformat") else str(livestock.date),
                                "Export Date": livestock.date.isoformat() if hasattr(livestock.export_date, "isoformat") else str(livestock.export_date),
                                "Amount": livestock.amount,
                                "Import Cost": livestock.import_cost,
                                "Export Cost": livestock.export_cost,
                                "Production Cost": livestock.production_cost,
                                "Profit": livestock.profit
                                }
                            }
                            year_dict[yr].update(livestock_type_dict)
                        livestock_data.update(year_dict)
            
        # print(crop_data)
        payload = {
        "SN" : get_config("SN"),
        "name": get_config("name"),
        "land_area" : 0 if get_config("land_area") == None else get_config("land_area"),
        "kebele": get_config("kebele"),
        "crop_data": crop_data,
        "livestock_data":livestock_data
        
        }
        post = requests.post("http://127.0.0.1:8000/client/upload", json=payload)
        if post:
            post = post.json()
            st.success(f"{post['msg']}")
        else:
            st.error("Something Unexpected Happened! ")
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
def sort_years(year_list):
    def sort_key(year_str):
        year_str = str(year_str)
        parts = year_str.split('/')
        first = int(parts[0])
        second = int(parts[1]) if len(parts) > 1 else first
        # For single years, second == first, so they come before ranges
        return (first, second)
    return sorted(year_list, key=sort_key, reverse=True)
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
@st.dialog("Edit Configuration")
def edit_config():
    with shelve.open("config", writeback=True) as db:
        with st.form("edit Config"):
            st.text_input("Serail Number",placeholder=f"{db["SN"]}",disabled=True)
            st.selectbox("Qabale",options=["01", "02"], placeholder="Your current Qabale", disabled=True)
            new_name = st.text_input("Name", placeholder="Enter your full name", help="This is used to personalize the app", value=db["name"])            
            new_land_area = st.number_input("Argicultural Land Area [Ha]", min_value=0, step=1, help="Your Average Agricultural Land Area in Hectars", value= 0 if db["land_area"] == None else 0)
            submit = st.form_submit_button("Save Changes")
            if submit:
                db["name"] = new_name
                db["land_area"] = new_land_area
                st.success("Changes Successfully Saved !")
                time.sleep(1)
                st.rerun()
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------
@st.cache_data(ttl=600)
def get_client_count(kebele):
    client_count = requests(f"http://127.0.0.1:8000/client_count/{kebele}")
    return client_count
# ---------------------------------------------------------------------------------------------------
# ==================================================================================================
# ---------------------------------------------------------------------------------------------------


