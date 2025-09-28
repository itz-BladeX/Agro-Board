import date as dt



class crop_class:
    def __init__(self, type, date, id,user_estimated = None):
        self.type = type
        self.date = date
        self.estimated = dt.estimated_date(date, crop_dict[type])
        self.user_estimated = user_estimated
        self.id = id
crop_dict = {
    "Teff": 75,
    "Maize": 90,
    "Inset":730,
    "Wheat": 91,
    "Sorghum": 110,
}