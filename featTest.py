from bs4 import BeautifulSoup, NavigableString
import requests
import re
import json
import datetime
import codecs

from featsBase import get_details
from featsBase import getTraits
from featsBase import parseDetailsTitle

def getTraits(tag):
    return tag.has_attr('class') and tag.name == "span" and tag

def get_multi(link):
    items = []
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    main = soup2.find("span", {'id': 'ctl00_MainContent_DetailedOutput'})
    traits = main.find_all("span", {"class": lambda L: L and L.startswith('trai')})
    traitHolder = []
    children = main.contents
    item = {}
    item['link'] = link
    tagType = ""
    itemDetailHolder = []
    string = " "
    h1count = 0
    reachedFeats = False
    for child in children:

        stringContents = str(child)
        if stringContents.startswith("<"):
            # print(stringContents)
            if child.name == "img" and reachedFeats:
                item['actions'] = child['alt']

            if child.name == "u" and reachedFeats:
                # print("In underline")
                if tagType != "":
                    if tagType in item:
                        item[tagType] += " " + child.text.strip()
                    else:
                        item[tagType] = child.text.strip()
                else:
                    itemDetailHolder.append(child.text)

            if child.name == "h1":
                h1count += 1
                if h1count > 1:
                    reachedFeats = True
                if h1count > 2:
                    item['text'] = string.join(itemDetailHolder)
                    itemDetailHolder = []
                    item['traits'] = traitHolder
                    items.append(item)
                    item = {}
                    traitHolder = []
                    tagType = ""
                if h1count > 1:
                    item['link'] = link
                    name = child.text
                    start = name.find("Feat")
                    item['name'] = name[0:start].strip()
                    item['level'] = int(name[start + 5:].strip().replace("+", ""))

            if child.name == "span" and reachedFeats:
                if child['class'][0] == "trait":
                    traitHolder.append(child.text)

            if child.name == "hr" and reachedFeats:
                tagType = ""

            if child.name == "b" and reachedFeats:
                if (child.text != "Source"):
                    tagType = child.text.replace(" ", "").lower().strip()
            if child.name == "i" and reachedFeats:

                if tagType != "":
                    if tagType in item:
                        item[tagType] += " " + child.text.strip()
                    else:
                        item[tagType] = child.text.strip()
                else:
                    itemDetailHolder.append(child.text)

            if child.name == "a" and reachedFeats:
                try:
                    if child['class'][0] == "external-link":
                        item['source'] = child.text
                except:
                    if tagType != "":
                        if tagType in item:
                            item[tagType] += " " + child.text.strip()
                        else:
                            item[tagType] = child.text.strip()
                    else:
                        itemDetailHolder.append(child.text.strip())
                        tagType = ""
        else:
            if reachedFeats:
                if tagType == "level":

                    item['level'] = int(stringContents.replace(";", "").strip())
                elif tagType != "":
                    if tagType in item:
                        item[tagType] += stringContents.strip()
                    else:
                        item[tagType] = stringContents.strip()

                else:
                    if not stringContents.isspace():
                        itemDetailHolder.append(stringContents.strip())
                    # print(stringContents)

    item['traits'] = traitHolder
    item['text'] = string.join(itemDetailHolder)
    items.append(item)

    return items

def get_dedication_feats(link):
    items = []
    archetypeRequest = requests.get(link)
    archetypeRequest.raise_for_status()
    soup2 = BeautifulSoup(archetypeRequest.text, 'html5lib')
    main = soup2.find("span", {'id': 'ctl00_MainContent_DetailedOutput'})

    featList = []
    featLinks = main.find_all("a", href=re.compile("^Feats\.aspx\?ID=\d+$"))

    for featLink in featLinks:
        featTitle = featLink.find_parents("h2", {'class': 'title'})
        if len(featTitle) > 0:
            featList.append(featTitle)



    print(featList)



def get_archtype_feats():
    holder = {}
    listOfLinks = []
    # listOfLinks.append({'name': 'Alchemist', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=1'})
    # listOfLinks.append({'name': 'Barbarian', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=2'})
    # listOfLinks.append({'name': 'Bard', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=3'})
    # listOfLinks.append({'name': 'Champion', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=4'})
    # listOfLinks.append({'name': 'Cleric', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=5'})
    # listOfLinks.append({'name': 'Druid', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=6'})
    # listOfLinks.append({'name': 'Fighter', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=7'})
    # listOfLinks.append({'name': 'Monk', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=8'})
    # listOfLinks.append({'name': 'Ranger', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=9'})
    # listOfLinks.append({'name': 'Rogue', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=10'})
    # listOfLinks.append({'name': 'Sorcerer', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=11'})
    # listOfLinks.append({'name': 'Wizard', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=12'})

    res2 = requests.get("https://2e.aonprd.com/Archetypes.aspx")
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'html5lib')
    main = soup2.find(
        lambda tag: tag.name == 'span' and tag.has_attr('id') and tag['id'] == "ctl00_MainContent_DetailedOutput")
    h2s = main.find_all("h2", {"class": "title"})

    t = 0
    for row in h2s:
        # print(row.text)
        # children = row.findChildren(recursive=False)
        titleLink = row.find(href=re.compile("aspx\?ID=\d+$"))
        # print(children[0]['href'])
        listOfLinks.append({'name': titleLink.text, 'link': "https://2e.aonprd.com/" + titleLink['href']})

    for linkItem in listOfLinks:
        t += 1
        print("Getting feats for :", linkItem['name'].rstrip())
        holder[linkItem['name']] = get_dedication_feats(linkItem['link'])
        # if t > 3:
        # break

    return holder


featHolder = {}
featHolder['archTypeFeats'] = get_archtype_feats()
print(featHolder)





