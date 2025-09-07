import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from json import dump, loads
from bts.bb_scrape import main
from dbmodels import Base, Season, Robot, Team, Stat

# declare global variables
if os.listdir("bts/json") == []:
    main()

file = "bts/json/bb-stats.json"
with open(file, "r") as f:
    RAW_STATS = loads(f.read())

file = "bts/json/bb-base.json"
with open(file, "r") as f:
    RAW_INFO = loads(f.read())

SEASONS_YEARS = [
    (1, 2015),
    (2, 2016),
    (3, 2018),
    (4, 2019),
    (5, 2020),
    (6, 2021)]      

def clean_key(x):
    if x.startswith("son of whyachi"):
        key_robo = "son of whyachi (sow)"
    elif x.startswith("complete control"):
        key_robo = "complete control (mk v)"
    elif x.startswith("lock-"):
        key_robo = "lock jaw"
    elif x.startswith("slammow"):
        key_robo = "slammo!"
    else:
        key_robo = [y for y in RAW_STATS[0].keys() if x.split("(")[0].strip() in y.replace("()", "")][0]
    return key_robo
    
# functions to populate tables
def populate_season(session:Session)->None:
    for tpl in SEASONS_YEARS:
            temp = Season(season=tpl[0], year=tpl[1])
            session.add(temp)
            session.commit()

def populate_robotinfo(session:Session)->None:        
    for dic in RAW_INFO:
        for k,v in dic.items():
            key_robo = clean_key(k.lower())
            if type(v["Type"]) == list:
                temp_type = " | ".join(v["Type"])
            else:
                temp_type = v["Type"]
            if type(v["Robot"]) == list:
                temp_robo = k.split("(")[0].strip()
            else:
                temp_robo = v["Robot"]
            yr = k.split("(")[1].split(")")[0]
            yr_id = session.execute(select(Season).where(Season.year == yr)).scalar()
            new_bot = Robot(
                robot_key = key_robo,
                robot = temp_robo,
                year_id = yr_id.id,
                type = temp_type
            )
            session.add(new_bot)
            session.commit()

            new_team = Team(
                robot_id = new_bot.id,
                team = v["Team"][0],
                members = " | ".join(v["Team"][1:]),
                hometown = v["Hometown"]
            )
            session.add(new_team)
            session.commit()

def populate_stats(session:Session)->None:
    yr = Season
    for k,v in RAW_STATS[0].items():
        if v:
            for i in v.keys(): 
                if len(i) == 4:
                    yr = session.execute(select(Season).where(Season.year == int(i))).scalar()
                    if session.execute(select(Robot).where(Robot.robot_key == k, Robot.year_id == yr.id)).scalar():
                        robo_id = session.execute(select(Robot).where(Robot.robot_key == k, Robot.year_id == yr.id)).scalar().id
                        new_stat = Stat(
                            robot_id = robo_id,
                            matches = v[i]["Total matches"],
                            wins = v[i]["Total wins"],
                            losses = v[i]["Losses"],
                            knockouts = v[i]["Knockouts"],
                            avg_ko_time = v[i]["Average knockout time"],
                            knocked_out = v[i]["Knockouts against"],
                            judged_win = v[i]["Judges decision wins"]
                        )
                        session.add(new_stat)
                        session.commit()
                    
                elif "Season" in i:
                    yr = session.execute(select(Season).where(Season.season == int(i[-1]))).scalar()
                    temp = "Season " + str(yr.season)
                    if session.execute(select(Robot).where(Robot.robot_key == k, Robot.year_id == yr.id)).scalar():
                        robo_id = session.execute(select(Robot).where(Robot.robot_key == k, Robot.year_id == yr.id)).scalar().id
                    
                        new_stat = Stat(
                            robot_id = robo_id,
                            matches = v[temp]["Total matches"],
                            wins = v[temp]["Total wins"],
                            losses = v[temp]["Losses"],
                            knockouts = v[temp]["Knockouts"],
                            avg_ko_time = v[temp]["Average knockout time"],
                            knocked_out = v[temp]["Knockouts against"],
                            judged_win = v[temp]["Judges decision wins"]
                        )
                        session.add(new_stat)
                        session.commit()
                
# create database
def createDB()->None:
    engine = create_engine("sqlite:///instance/battlebots.db")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        populate_season(session)
        populate_robotinfo(session)
        populate_stats(session)       

if "instance/battlebots.db" not in os.listdir("bts/"):
    createDB()



   

