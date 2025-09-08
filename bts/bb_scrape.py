#import modules
from json import dump, load
import requests
from bs4 import BeautifulSoup
import re as re

def dump_to(dic:dict, f:str)->None:
    with open(f"bts/json/{f}", "w") as file:
        dump(dic, file)
        
def anchor_w_view(tag)->bool:
    return tag.name == "a" and "View" in tag.text

def h4_and_title(tag)->bool:
    return tag.name == "h4" and tag.attrs == {"class":["title"]}

def not_br(tag)->bool:
    return tag.name != "br" and tag.name != "hr"

def is_heading(tag)->bool:
    return tag.name == "h2" or tag.name == "h3"

def robot_links()->dict:
    # list comprehension of urls for seasons of interest
    urls = [f"https://battlebots.com/{year}-season-robots/" for year in [2021, 2020, 2019, 2018]]
    [urls.append(f"https://battlebots.com/season-{x}-robots/") for x in range(1,3)]
    dict_links = {}
    # loop through season"s url
    for url in urls:
        r = requests.get(url, verify=False)
        soup = BeautifulSoup(r.text.encode("utf-8"), features="html.parser")
        robo_soup = soup.find(id="main-content").find_all([h4_and_title, anchor_w_view])
    # create key,val pairs based on tag type
        for temp in robo_soup:
            if temp.name == "h4":
                robot = temp.get_text().strip()
                dict_links[robot] = ""
            else:
                dict_links[robot] = temp.get("href")
    # add missing date to Lucky 2018 key, url pair
    dict_links["Lucky (2018)"] = dict_links.pop("Lucky", "N/A")
    return dict_links

def get_info(dic:dict)->dict:
    lst_robots = []
    for i, v in dic.items():
        dict_robot = {}
        dict_info = {}
        if v != "#":
            dict_info["url"] = v
            r = requests.get(v, verify=False)
            # get robot info
            soup = BeautifulSoup(r.text.encode("utf-8"), features="html.parser")
            for temp in soup.find_all("strong"):          
                key = temp.get_text().strip(":") 
                if temp.parent.name == "p":
                    nxt = temp.parent.find_next_siblings(not_br)                                   
                else:
                    nxt = temp.find_next_siblings(not_br)
                if len(nxt) > 1:
                    val = [x.get_text() for x in nxt]
                elif len(nxt) > 0:
                    val = nxt[0].get_text()
                # capture interesting fact text
                else:
                    div = temp.find_parent("div")
                    if div.contents[-1] in ["\n", "<br/>", "<hr>"]:
                        val = div.contents[-2].string
                        if val == temp:
                            val = "N/A"
                    else:
                        if div.contents[-1] == temp:
                            val = "N/A"
                        else:
                            val = div.contents[-1].string
                if val != None and type(val) == list:
                    if any(":" in x for x in val):
                        temp2 = min([val.index(x) for x in val if ":" in x])
                        val2 = [x for x in val if val.index(x) < temp2]
                        if len(val2) == 1:
                            val2 = val2[0]
                        val = val2
                dict_info[key] = val
                # get photo url
                #dict_info["img_url"] = ??
            dict_robot[i] = dict_info
            lst_robots.append(dict_robot)
    return lst_robots    

def get_stats(dic:dict)->dict:
    # create stat 
    lst_stats = []
    dict_bots = {}
    for i, v in dic.items():
        bot = i.split("(")[0].strip().lower()
    # highlight specific bots with name changes (same team) thru the seasons
        if "sow" in bot or "son of whyachi" in bot:
            bot = "son of whyachi (sow)"
        if "complete control" in bot:
            bot = "complete control (mk v)"
        if bot.startswith("lock-"):
            bot = "lock jaw"
        yr = i.split("(")[1].split(")")[0]
        if bot in dict_bots.keys():
            pass
        else:
            dict_bots[bot] = {}
            if v != "#":
                r = requests.get(v, verify=False,)
                soup = BeautifulSoup(r.text.encode("utf-8"), features="html.parser")
                # find Stat history then next element that is table
                tbl = soup.find("table")
                # avoid match history for those missing stat history 
                if tbl != None and "match history" not in [x.lower().strip() for x in tbl.find_previous(is_heading).stripped_strings]: 
                    head_txt = [x for x in tbl.find("thead").stripped_strings]
                    for k in head_txt[1:]:
                        dict_bots[bot][k] = {}
                    
                    for n in range(1, len(head_txt)):
                        key_yr = head_txt[n]
                        dict_stat = {}
                        for tr in tbl.find("tbody").find_all("tr"):
                            if "\n" in tr.contents:
                                row = [x for x in tr.contents if x != "\n"]
                            else:
                                row = tr.contents
                            
                            key_stat = row[0].get_text()
                            stat = row[n].get_text()
                            dict_stat[key_stat] = stat
                        dict_bots[bot][key_yr] = dict_stat
    lst_stats.append(dict_bots)
    return lst_stats

def main():
    # last run 09/07/2025
    # run web requests to get robot links
    dump_to(robot_links(), "bb-links.json")
    # read from newly created json file
    with open("bts/json/bb-links.json", "r") as f:
        dict_links = load(f)
    # create json file for battlebots data
    dump_to(get_info(dict_links), "bb-base.json")
    dump_to(get_stats(dict_links), "bb-stats.json")

