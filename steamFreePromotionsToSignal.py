#!/usr/bin/python3
import requests
import json
import sys
import subprocess

from bs4 import BeautifulSoup
from pathlib import Path

try:
    settings = json.loads(Path("./config.json").read_text())
except FileNotFoundError:
    exit("Configuration file is missing.")

# File to store promotions local
localStorageFile = settings["localStorageFile"]
# Steam shop url, able to edit filter
steamShopUrl = settings["steamShopUrl"]
# Path to signal-cli binary
signalCliPath = settings["signalCliPath"]
# Account used to send the signal messages
signalAccount = settings["signalAccount"]
# Target number or group
signalTarget = settings["signalTarget"]
# Target number for debug output
signalDebugTarget = settings["signalDebugTarget"]
# Set to true to enable debug output
debug = False

newPromotionsFound = False

def sendSignalMessage(signalCliPath, account, message, target):
    if target[1:].isnumeric():
        result = subprocess.run([signalCliPath, "-a", account, "send", "-m", message, target])
    else:
        result = subprocess.run([signalCliPath, "-a", account, "send", "-m", message, "-g", target])



if "-debug" in sys.argv:
    debug = True
    sendSignalMessage(signalCliPath, signalAccount, "Debug run", signalDebugTarget)

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
            print("Found:", a["data-ds-itemkey"], "(" + a.find('span', {"class":"title"}).getText(), end=", ")
            print(a["href"].split('?')[0] + ")", end=", ")
        livePromotions.append(a["data-ds-itemkey"])
        if a["data-ds-itemkey"] not in promotions["Promotions"]:
            newPromotionsFound = True
            message = "This game is currently free to keep:\n"
            message += a.find('span', {"class":"title"}).getText() + '\n'
            message += a["href"].split('?')[0]
            if debug:
                print(message)
                print("new")
            sendSignalMessage(signalCliPath, signalAccount, message, signalTarget)
            promotions["Promotions"].append(a["data-ds-itemkey"])
        else:
            if debug:
                print("known")

    for promotion in promotions["Promotions"]:
        if promotion not in livePromotions:
            if debug:
                print(promotion, "expired")
            promotions["Promotions"].remove(promotion)
    if not newPromotionsFound:
        if debug:
            sendSignalMessage(signalCliPath, signalAccount, "No new promotions found.", signalDebugTarget)
        sendSignalMessage
    Path(localStorageFile).write_text(json.dumps(promotions))
    if debug:
        print("Safed changes.")
    
else:
    if debug:
        print("Connection failed.\n")
