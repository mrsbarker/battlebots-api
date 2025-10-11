import os
from flask_sqlalchemy import SQLAlchemy
from bb_create_db import Robot, Season, Team, Stat, createDB
from flask import Flask, jsonify, request
from random import choice

if "instance" not in os.listdir("."):
    os.mkdir("instance")
    createDB(os.getenv("CREATE_DB_URL"))

elif "battlebots.db" not in os.listdir("instance/"):
    createDB(os.getenv("CREATE_DB_URL"))

db = SQLAlchemy()
app = Flask(__name__)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///battlebots.db"

# initialize the app with the extension
db.init_app(app)

@app.route("/")
def home():
    html_str = "<h1>Battlebots API</h1>" \
    "<p>See battlebots official <a href='battlebots.com'>website</a> for more details on the robots." \
    " And see the battlebots-api <a href='https://github.com/mrsbarker/battlebots-api'>github</a> for more information on the associated code.</p>"
    return html_str

@app.route("/random")
def get_random():
    temp = db.session.execute(db.select(Robot).order_by(Robot.robot,Robot.year_id)).scalars().all()
    bot = choice(temp)
    seasn = db.session.execute(db.select(Season).where(Season.id == bot.year_id)).scalar()
    seasn_str = f"Season {seasn.season} ({seasn.year})"
    team = db.session.execute(db.select(Team).where(Team.robot_id == bot.id)).scalar()
    stats = db.session.execute(db.select(Stat).where(Stat.robot_id == bot.id)).scalar()
    bot_json = {"robot": bot.robot,
                "season": seasn_str,
                "robot type": bot.type,
                "team": team.team,
                "team members": team.members,
                "season matches": getattr(stats, "matches", "N/A"),
                "season wins": getattr(stats, "wins", "N/A")}
    return jsonify(query = bot_json)

@app.route("/all-robots")
def get_all_bots():
    lst = []
    temp = db.session.execute(db.select(Robot).order_by(Robot.robot,Robot.year_id)).scalars().all()
    bots = {}
    for bot in temp:
        seasn = db.session.execute(db.select(Season).where(Season.id == bot.year_id)).scalar()
        seasn_str = f"Season {seasn.season} ({seasn.year})"
        team = db.session.execute(db.select(Team).where(Team.robot_id == bot.id)).scalar()
        stats = db.session.execute(db.select(Stat).where(Stat.robot_id == bot.id)).scalar()
        bot_json = {"season": seasn_str,
                    "robot type": bot.type,
                    "team": team.team,
                    "team members": team.members,
                    "season matches": getattr(stats, "matches", "N/A"),
                    "season wins": getattr(stats, "wins", "N/A")}
        if bot.robot not in bots.keys():
            bots[bot.robot] = {}
        bots[bot.robot][seasn.year] = bot_json 
    lst.append(bots)   
    return jsonify(Battlebots = lst)

@app.route("/search")
def find_bots():
    query = request.args.get("bot")
    temp = db.session.execute(db.select(Robot).where(Robot.robot == query)).scalars().all()
    if temp:
        test = {}
        seasons = []
        for bot in temp:
            seasn = db.session.execute(db.select(Season).where(Season.id == bot.year_id)).scalar()
            team = db.session.execute(db.select(Team).where(Team.robot_id == bot.id)).scalar()
            stats = db.session.execute(db.select(Stat).where(Stat.robot_id == bot.id)).scalar()
            bot_json = {"year": seasn.year,
                        "type": bot.type,
                        "team": team.team,
                        "team members": team.members,
                        "season": seasn.season,
                        "season matches": getattr(stats, "matches", "N/A"),
                        "season wins": getattr(stats, "wins", "N/A"),
                        "season losses": getattr(stats, "losses", "N/A"),
                        "season knockouts": getattr(stats, "knockouts", "N/A"),
                        "knockout time (avg.)": getattr(stats, "avg_ko_time", "N/A"),
                        "knocked out": getattr(stats, "knocked_out", "N/A"),
                        "judges decision wins": getattr(stats, "judged_win", "N/A"),
                        "url": getattr(bot, "url", "N/A"),
                        "url_img": getattr(team, "img_url", "N/A")}
            seasons.append(bot_json)
        season_dict = {"seasons": seasons}
        bot_dict = {query: season_dict}
        return jsonify(Battlebot = bot_dict), 200
    else:
        res = {"Not found": "Sorry this robot was not found please check your spelling and/or capitalization."}
        return jsonify(error = res), 404

if __name__ == "__main__":
    app.run(debug=False)
