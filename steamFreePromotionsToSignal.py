#!/usr/bin/python3
import requests
import json
import sys

from bs4 import BeautifulSoup
from pathlib import Path

localStorageFile = "./freePromotions.json"
steamShopUrl = "https://store.steampowered.com/search/?maxprice=free&supportedlang=english&specials=1&ndl=1"
debug = False

if "-debug" in sys.argv:
    debug = True


try:
    promotions = json.loads(Path(localStorageFile).read_text())
except FileNotFoundError:
    if debug:
        print("No local storage found.")
        print("Creating a new one.")
    Path(localStorageFile).write_text('{"Promotions":[]}')
    promotions = json.loads(Path(localStorageFile).read_text())

response = requests.get(steamShopUrl)

if response.status_code == 200:
    if debug:
        print("Connection ok.")

    livePromotions = []

    html = BeautifulSoup(response.content, features="lxml")
    games = html.find_all('a', {"data-ds-itemkey": True})
    for a in games:
        if debug:
            print("Found:", a["data-ds-itemkey"], "(" + a.find('span', {"class":"title"}).getText() + ")")
        livePromotions.append(a["data-ds-itemkey"])
        if a["data-ds-itemkey"] not in promotions["Promotions"]:
            # SEND SIGNAL MESSAGE
            if debug:
                print(" + New Promotion")
            promotions["Promotions"].append(a["data-ds-itemkey"])

    for promotion in promotions["Promotions"]:
        if promotion not in livePromotions:
            if debug:
                print(promotion, "expired")
            promotions["Promotions"].remove(promotion)
    Path(localStorageFile).write_text(json.dumps(promotions))
    if debug:
        print("Safed changes.")
    
else:
    if debug:
        print("Connection failed.\n")
