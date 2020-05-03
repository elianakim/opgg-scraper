import requests
import re
import sys
import os
from bs4 import BeautifulSoup
import json
import random
import time
from datetime import datetime

def randomSleep():
    dice = random.randint(1, 6)
    if dice <= 4:
        time.sleep(random.uniform(1, 5))
    else:
        time.sleep(random.uniform(5, 10))

def randomShorterSleep():
    time.sleep(random.uniform(1, 3))

def create_url(userName):
    splited = userName.split(" ")
    if len(splited) > 1:
        new_Name = ""
        for i, word in enumerate(splited):
            new_Name += word
            if i < len(splited) - 1:
                new_Name += "+"
        return new_Name
    else:
        return userName

def get_records(summonerId, ranks_dict):
    season_converter = {"S1":1, "S2":2, "S3": 3, "S4": 4, "S5": 5, "S6": 6, "S7": 7, "S8": 11, "S9": 13}
    champions = []
    additionalIndexes = ['gold', 'cs', 'maxKills', 'maxDeaths', 'avgDamageDealt', 'avgDamageTaken', 'doubleKill', 'tripleKill', 'quadraKill', 'pentaKill']

    for s in list(ranks_dict.keys()):
        season = season_converter[s]
        records_url = "https://www.op.gg/summoner/champions/ajax/champions.rank/summonerId={id}&season={s}".format(
            id=summonerId, s=season)
        print(records_url)
        page = requests.get(records_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        # no record
        if len(soup.prettify()) < 1000:
            continue
        start = soup.find('tr', class_ = "Row TopRanker")
        recording = False
        record = {}
        additionalData = []
        next_elements = 'something'
        try:
            pls = start.next_elements
        except AttributeError:
            return champions
        else:
            next_elements = pls
        for e in next_elements:
            if e.name == 'td' and e['class'][0] == 'Rank' and recording == False:
                record = {"season": season, "rank": e.string}
                additionalData = []
                recording = True
                continue
            if e.name == 'td' and e['class'][0] == 'Rank' and recording == True:
                for i, index in enumerate(additionalIndexes):
                    record[index] = additionalData[i]
                champions.append(record)
                record = {"season": season, "rank": e.string}
                additionalData = []
                continue
            if e.name == 'td' and recording == True:
                className = e['class'][0]
                if className == 'ChampionName':
                    record['name'] = e['data-value']
                elif className == 'RatioGraph':
                    record['winRatio'] = e['data-value']
                    for c in e.findAll('div'):
                        if c['class'][0] == 'Text':
                            if c['class'][1] == 'Left':
                                record["win"] = c.string
                            elif c['class'][1] == 'Right':
                                record['lose'] = c.string
                elif className == 'KDA':
                    record['avgKDA'] = e['data-value']
                    kda = ""
                    for c in e.findAll('span'):
                        if c['class'][0] == 'Kill':
                            kda += c.string
                            kda += "/"
                        elif c['class'][0] == 'Death':
                            kda += c.string
                            kda += "/"
                        elif c['class'][0] == 'Assist':
                            kda += c.string
                    record['KDA'] = kda
                elif className == 'Value':
                    additionalData.append(e.string.strip())
        randomShorterSleep()
    return champions

def check_if_done(proceedings):
    for k in list(proceedings.keys()):
        b = proceedings[k]
        if b[1] == False:
            return False
    return True

def nighty_night():
    now = datetime.today()
    h = now.hour
    if h >= 21:
        future = datetime(now.year, now.month, now.day + 1, 4, 0)
        print("nighty night")
        time.sleep((future - now).seconds)
        return
    elif h < 4:
        future = datetime(now.year, now.month, now.day, 4, 0)
        print("nighty night")
        time.sleep((future - now).seconds)
        return
    else:
        return

# global variables declaration
tiers_list = ['Iron', 'Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Master', 'Grandmaster', 'Challenger']
seasons_list = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10']

# import file
fileNames = ["PLATINUM_II.txt",\
             "PLATINUM_I.txt", "DIAMOND_IV.txt", "DIAMOND_III.txt", "DIAMOND_II.txt", "DIAMOND_I.txt",\
             "BRONZE_IV.txt", "BRONZE_III.txt", "BRONZE_II.txt", "BRONZE_I.txt", "SILVER_IV.txt",\
             "SILVER_III.txt", "SILVER_II.txt", "SILVER_I.txt", "GOLD_IV.txt", "GOLD_III.txt",\
             "GOLD_II.txt", "GOLD_I.txt", "PLATINUM_IV.txt", "PLATINUM_III.txt"]
# fileNames = ["test2.txt", "test4.txt", "test9.txt"]
proceedings = {}
for i, f in enumerate(fileNames):
    if i <= 5:
        proceedings[f] = (6500, False)
    else:
        proceedings[f] = (7000, False)
#print(proceedings)
# check file lengths
file_lists = {}
for n in fileNames:
    f = open(n, 'rt', encoding = 'utf-8')
    ret = []
    for l in f:
        ret.append(l)
    file_lists[n] = ret

chunk_size = 500

while True:
    if check_if_done(proceedings):
        break
    for file in fileNames:
        # make for-loop!
        if proceedings[file][1] == True:
            continue
        usersList = file_lists[file]
        index = proceedings[file][0]
        indexEnd = index + chunk_size
        if indexEnd >= len(usersList):
            indexEnd = len(usersList)
            proceedings[file] = (indexEnd, True)
        else:
            proceedings[file] = (index+chunk_size, False)
        returnData = []
        print(file)
        print(index)
        for userName in usersList[index:indexEnd]:
            nighty_night()
            print(userName)
            userEntry = {}
            userEntry['userName'] = userName[:-1]
            # userName = "hide on bush"
            userName_for_url = create_url(userName)
            URL = 'https://www.op.gg/summoner/userName={name}'.format(name = userName_for_url)

            print(URL)
            ###################################
            error_status = False
            emergency = False
            soup = 'something'

            while True:
                try:
                    page = requests.get(URL)
                    page.raise_for_status()
                except requests.exceptions.Timeout:
                # Maybe set up for a retry, or continue in a retry loop
                    print("timeout error, sleep 10 minutes")
                    time.sleep(600)
                    if error_status == True:
                        print("same error again, try a different one")
                        break
                except requests.exceptions.TooManyRedirects:
                # Tell the user their URL was bad and try a different one
                    error_status = True
                    print("Too Many Redirections, try a different one")
                    break
                except requests.exceptions.ConnectionError:
                    # hing
                    print("Connection Error, sleep 10 minutes")
                    time.sleep(600)
                    if error_status == True:
                        print("same error again, try a different one")
                        break
                except requests.exceptions.HTTPError:
                    print("HTTP Error, try a different one")
                    error_status = True
                    break
                except requests.exceptions.RequestException:
                    # catastrophic error. bail.
                    print("Request Exception error")
                    time.sleep(600)
                    if error_status == True:
                        print("same error again, try a different one")
                        break
                else:
                    soup = BeautifulSoup(page.content, 'html.parser')
                    break
            if emergency == True:
                break
            if error_status == True:
                continue

            # soup = BeautifulSoup(page.content, 'html.parser')
            if len(soup.prettify()) < 100000:
                continue
            # get past rank
            past_ranks = 'something'
            try:
                p = soup.find('div', class_='PastRank').contents[1]
            except (AttributeError, TypeError):
                print("unranked")
                continue
            else:
                past_ranks = p
            ranks_dict = {}
            tier = ""
            season = ""
            for e in past_ranks.contents:
                e = str(e)
                if len(e) > 1:
                    for item in re.split('<b>|</b> |title="|">\n|\n', e):
                        if item in seasons_list:
                            season = item
                        if item[-2:] == 'LP' or item in tiers_list:
                            tier = item
                    ranks_dict[season] = tier
            print(ranks_dict)

            # get rid of players who are not active or new
            if len(list(ranks_dict.keys())) < 2:
                continue

            # obtain summonerId
            url_with_id = 'something'
            try:
                u = soup.find('div', class_='tabItem overview-stats--soloranked')['data-tab-data-url']
            except (AttributeError, TypeError):
                print("there is no record")
                continue
            else:
                url_with_id = u
            summonerId = re.split('summonerId=|&season', url_with_id)[1]
            userEntry['userId'] = summonerId

            tiersData = []
            for season in list(ranks_dict.keys()):
                tier = {}
                # print(season)
                # print(ranks_dict[season])
                tier['season'] = int(season[-1])
                tierSplited = ranks_dict[season].split(" ")
                if season == 'S1' or season == 'S2':
                    continue
                elif season == 'S3' or season == 'S4':
                    tier['tier'] = ranks_dict[season]
                    tier['division'] = 'None'
                elif tierSplited[0] == 'Master' or tierSplited[0] == 'Grandmaster' or tierSplited[0] == 'Challenger':
                    tier['tier'] = tierSplited[0]
                    tier['division'] = 'None'
                else:
                    tier['tier'] = tierSplited[0]
                    try:
                        tier['division'] = int(tierSplited[1])
                    except IndexError:
                        tier['division'] = 'None'
                    else:
                        tier['division'] = int(tierSplited[1])
                tiersData.append(tier)
            champions = get_records(summonerId, ranks_dict)

            userEntry['previousTiers'] = tiersData
            userEntry['Champions'] = champions

            returnData.append(userEntry)
            randomSleep()

        # save json file
        div = int(index / chunk_size)
        name = file[:-4] + "_" + str(div) + '.json'
        save_path = 'jan17success/'
        if not os.path.isdir(save_path):
            os.makedirs(save_path)

        fileName = os.path.join(save_path, name)

        with open(fileName, 'w') as f:
            json.dump(returnData, f)

        f.close()
