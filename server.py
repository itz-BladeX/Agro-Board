from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, String, JSON, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.ext.mutable import MutableDict
from pydantic import BaseModel
import random, string
from datetime import datetime
#-------------------Setup---------------
sql_base = declarative_base()
engine = create_engine("postgresql+psycopg2://postgres:bladex@localhost:5432/Test")
session_local = sessionmaker(bind=engine)
app = FastAPI()
def session():
    db = session_local()
    try: yield db
    finally: db.close()
def generate_SN(db:Session):

    char = string.ascii_uppercase + string.digits
    repeat = 0
    while repeat < 5:
        repeat += 1
        SN = "".join(random.choice(char) for _ in range(10)) 
        exists = db.query(Clients).filter(Clients.SN == SN).first()
        if not exists:
            break
        
    return f"#USER-{SN}"
# ------------Setup Functions ------------

# Class for Expected Package post
class Package(BaseModel):
    SN: str
    name: str
    land_area: int
    kebele: str
    crop_data: dict
    livestock_data: dict
    
# SetUp Client Database Table with the Following Columns and expected Storage Types
class Clients(sql_base):
    __tablename__= "Client_Table"
    SN = Column(String, primary_key=True)
    Name = Column(String, nullable=True)
    Land_Area = Column(Integer, nullable=True)
    Kebele = Column(String, nullable=True)
    Date = Column(String, nullable=True)
    Crop = Column(MutableDict.as_mutable(JSON), nullable=True)
    Livestock = Column(MutableDict.as_mutable(JSON), nullable=True)

sql_base.metadata.create_all(bind=engine)

@app.get("/client/register/{name}")
def register(name:str, db : Session = Depends(session)):
    sn = generate_SN(db)
    data = Clients(
        SN = sn,
        Name = name,
        Date = "None",
        Crop = {},
        Livestock = {}, 
    )
    db.add(data)
    db.commit()
    db.refresh(data)
    return {"SN": sn}
@app.post("/client/upload")
def upload_client_data(data : Package, db : Session = Depends(session)):
    user = db.query(Clients).filter(Clients.SN == data.SN).first()
    if not user:
        return {"Error!": "Cleint Couldnt be found, please Register First"}
    user.Name = data.name
    user.Land_Area = data.land_area
    user.Kebele = data.kebele 
    user.Date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user.Crop.update(data.crop_data) 
    user.Livestock.update(data.livestock_data)
    db.commit()
    db.refresh(user)
    return {"msg":"Successfully Uploaded"}
@app.get("/client_count/{kebele}")
def get_client_count(kebele:str, db: Session = Depends(session)):
    client_count = 0
    for x in db.query(Clients).filter(Clients.Kebele == kebele):
        client_count += 1
    return {"client_count": client_count}

@app.get("/client/common_crop/{kebele}")
def most_common_crop(kebele:str, db:Session = Depends(session)):
    crops = {}
    common_count =  0
    common = "-"
    for data in db.query(Clients).filter(Clients.Kebele == kebele):
        for production_year in data.Crop:
            for crop_type in data.Crop[production_year]:
                if crop_type not in crops: crops[crop_type] = 1 
                else: crops[crop_type] += 1
    for crop_type in crops:
        if crops[crop_type] > common_count:
            common_count = crops[crop_type]
            common = crop_type
    return {"common_crop":common}

@app.get("/client/common_livestock/{kebele}")
def most_common_livestock(kebele:str, db:Session = Depends(session)):
    livestocks = {}
    common_count =  0
    common = "-"
    for data in db.query(Clients).filter(Clients.Kebele == kebele):
        for production_year in data.Livestock:
            for livestock_type in data.Livestock[production_year]:
                if livestock_type not in livestocks: livestocks[livestock_type] = 1 
                else: livestocks[livestock_type] += 1
    for crop_type in livestocks:
        if livestocks[crop_type] > common_count:
            common_count = livestocks[crop_type]
            common = crop_type
    return {"common_livestock":common}

@app.get("/client/total_land_area/{kebele}")
def total_land_area(kebele: str, db: Session = Depends(session)):
    land_area = 0
    for data in db.query(Clients).filter(Clients.Kebele == kebele):
        land_area += data.Land_Area
    return {"total_land_area" : land_area}
@app.get("/client/crop_yield_ranking/{kebele}")
def get_crop_yield(kebele:str, db:Session = Depends(session)):
    yearly_crop_rank = {}
    for data in db.query(Clients).filter(Clients.Kebele == kebele):
        for production_year, crop_data in data.Crop.items():
            year_dict = yearly_crop_rank.setdefault(production_year, {})
            for crop_type, crop_type_data in crop_data.items():
                yield_val = crop_type_data.get("Yield", 0) or 0
                try:
                    yield_val = float(yield_val)
                except Exception:
                    yield_val = 0
                year_dict[crop_type] = year_dict.get(crop_type, 0) + yield_val
    return {"ranking": yearly_crop_rank}

@app.get("/client/livestock_amount_ranking/{kebele}")
def get_livestock_amount(kebele:str, db:Session = Depends(session)):
    yearly_livestock_rank = {}
    for data in db.query(Clients).filter(Clients.Kebele == kebele):
        for production_year, livestock_data in data.Livestock.items():
            year_dict = yearly_livestock_rank.setdefault(production_year, {})
            for livestock_type,livestock_type_data in livestock_data.items():
                yield_val = livestock_type_data.get("Amount", 0) or 0
                try:
                    yield_val = int(yield_val)
                except Exception:
                    yield_val = 0
                year_dict[livestock_type] = year_dict.get(livestock_type, 0) + yield_val
            
    return {"ranking" : yearly_livestock_rank}


@app.get("/client/user_data/{kebele}")
def get_user_data(kebele: str, db: Session = Depends(session)):
    user_data = {}
    crops = {}
    livestock = {}
    for data in db.query(Clients).filter(Clients.Kebele == kebele):
        user_data[data.SN] = {
            "sn" : data.SN,
            "name" : data.Name,
            "land_area" : data.Land_Area,
            "kebele" : data.Kebele,
            "crops" : data.Crop,
            "livestock": data.Livestock,
            "last_updated" : data.Date
        }
    return {"users": user_data}
        
    








    