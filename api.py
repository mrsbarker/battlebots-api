import os
from flask_sqlalchemy import SQLAlchemy
from dbmodels import Robot, Season, Team, Stat
from flask import Flask, jsonify, render_template, request
from random import choice


db = SQLAlchemy()
app = Flask(__name__)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI")

# initialize the app with the extension
db.init_app(app)

@app.route("/")
def home():
    return render_template("index.html")

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
    return jsonify(Battlebot = bot_json)

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
                        "url": getattr(bot, "url", "https://battlebots.com/"),
                        "url_img": team.img_url}
            seasons.append(bot_json)
        bot_dict = {"robot": query,
                    "seasons": seasons}
        return jsonify(Battlebot = bot_dict), 200
    else:
        res = {"Not found": "Sorry this robot was not found please check your spelling and/or capitalization."}
        return jsonify(error = res), 404

if __name__ == "__main__":
    app.run(debug=False)
