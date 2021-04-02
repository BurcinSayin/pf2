from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import re

featHolder = {}
featHolder['name'] = 'Pathfinder 2.0 feat list'
featHolder['date'] = datetime.date.today().strftime("%B %d, %Y")


def getTraits(detailsObject, detail):
    traitHolder = []
    traits = detail.find_all("span", {'class': 'trait'})
    for traitElement in traits:
        if traitElement.next:
            traitHolder.append(traitElement.next.text)

    if len(traitHolder) > 0:
        detailsObject['traits'] = traitHolder

def parseDetailsTitle(detailsObject, detail):
    titleInfo = detail.find("h1", {'class': 'title'})
    action = titleInfo.find("img", alt=re.compile("^((?!PFS).)*$"))
    pfsStatus = titleInfo.find("img", alt=re.compile("PFS"))

    if pfsStatus is not None:
        detailsObject['pfsLegal'] = True
    if action is not None:
        detailsObject['actions'] = action['alt']


def get_details(link):
    res = requests.get(link)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html5lib')
    feat = soup.find_all("div", {'class': 'main'})
    detail = soup.find("span", {'id': 'ctl00_MainContent_DetailedOutput'})
    # print(detail.contents)
    children = detail.contents
    reachedBreak = False
    detailHolder = []
    details = {}

    getTraits(details, detail)
    parseDetailsTitle(details, detail)

    for child in children:
        stringContents = str(child)
        if stringContents.startswith("<"):
            if stringContents == "<hr/>":
                reachedBreak = True
            if reachedBreak:
                if child.name == "a":
                    detailHolder.append(child.text)
                if child.name == "ul":
                    # print(child.text)
                    children3 = child.contents
                    for child3 in children3:
                        stringContents3 = str(child3)
                        if stringContents3.startswith("<"):
                            if child3.name == "li":
                                # print(child3.text)
                                detailHolder.append(child3.text)
        else:
            if reachedBreak:
                detailHolder.append(stringContents)
        # print(child)
        # print('<!!!!!!!!!!!!!!!!!!!!!!!!!>')
        string = " "
        details['text'] = string.join(detailHolder)
    return details


def get_feats(link):
    feats = []
    res = requests.get(link)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html5lib')
    table = soup.find(
        lambda tag: tag.name == 'table' and tag.has_attr('id') and tag['id'] == "ctl00_MainContent_TableElement")
    rows = table.findAll(lambda tag: tag.name == 'tr')
    string = " "
    t = 0
    for row in rows:
        t += 1
        # print(row)
        # print("-----------------------------------")
        feat = {}
        entries = row.find_all(lambda tag: tag.name == 'td')
        if entries is not None:
            if len(entries) > 0:
                addFeat = 1;
                name = entries[0].find("u").text
                link = entries[0].find("u").contents[0]["href"]
                # for entry in entries:
                #   print(entry)
                #  print("row---------------")
                level = entries[1].text
                traits = entries[2].text
                prereq = entries[3].text
                source = entries[4].text

                feat['name'] = name
                feat['level'] = int(level)
                feat['traits'] = traits.split(",")
                feat['link'] = "https://2e.aonprd.com/" + link
                feat['prerequisites'] = prereq.replace(u'\u2014', '')
                feat['benefits'] = source
                try:
                    details = get_details(feat['link'])
                    for key in details.keys():
                        if key != 'text':
                            feat[key] = details[key]
                except:
                    addFeat = 0;
                    print("Error while getting details : " + feat['link'])

                if addFeat > 0:
                    feats.append(feat)
        # if t > 5:
        # break
    return feats


def get_class_feats():
    holder = {}
    listOfPages = codecs.open("feats.csv", encoding='utf-8')
    for line in listOfPages:
        featMD = line.split(",")
        print("Getting feats for :", featMD[0], "This url:", featMD[2].strip('\n'))
        # if featMD[0] == "Ranger Feats":
        holder[featMD[1].strip()] = get_feats(featMD[2].strip('\n'))

    return holder


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


def get_archtype_feats():
    holder = {}
    listOfLinks = []
    listOfLinks.append({'name': 'Alchemist', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=1'})
    listOfLinks.append({'name': 'Barbarian', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=2'})
    listOfLinks.append({'name': 'Bard', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=3'})
    listOfLinks.append({'name': 'Champion', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=4'})
    listOfLinks.append({'name': 'Cleric', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=5'})
    listOfLinks.append({'name': 'Druid', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=6'})
    listOfLinks.append({'name': 'Fighter', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=7'})
    listOfLinks.append({'name': 'Monk', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=8'})
    listOfLinks.append({'name': 'Ranger', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=9'})
    listOfLinks.append({'name': 'Rogue', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=10'})
    listOfLinks.append({'name': 'Sorcerer', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=11'})
    listOfLinks.append({'name': 'Wizard', 'link': 'https://2e.aonprd.com/Archetypes.aspx?ID=12'})

    res2 = requests.get("https://2e.aonprd.com/Archetypes.aspx")
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    main = soup2.find(
        lambda tag: tag.name == 'span' and tag.has_attr('id') and tag['id'] == "ctl00_MainContent_DetailedOutput")
    h2s = main.find_all("h2", {"class": "title"})

    t = 0
    for row in h2s:
        # print(row.text)
        children = row.findChildren(recursive=False)
        # print(children[0]['href'])
        listOfLinks.append({'name': row.text, 'link': "https://2e.aonprd.com/" + children[0]['href']})

    for linkItem in listOfLinks:
        t += 1
        print("Getting feats for :", linkItem['name'].rstrip())
        holder[linkItem['name']] = get_multi(linkItem['link'])
        # if t > 3:
        # break

    return holder


def get_all():
    # tempHolder = get_class_feats()
    # for key in tempHolder.keys():
    featHolder['baseFeats'] = get_class_feats()

    # tempHolder = get_archtype_feats()
    # for key in tempHolder.keys():
    featHolder['archTypeFeats'] = get_archtype_feats()

    return featHolder





json_data = json.dumps(get_all(), indent=4)
# print(json_data)
filename = "feats-pf2-v2.json"
f = open(filename, "w")
f.write(json_data)
f.close

filename = "feats-pf2-v2.json"
f = open(filename, "w")
f.write(json_data)
f.close

def is_feat_not_in_list(linkText, listToCheck):

    for featToCheck in listToCheck:
        if(linkText == featToCheck['link']):
            return False
    return True

featHolder2 = {}
featHolder2['name'] = 'Pathfinder 2.0 Consolidated feat list'
featHolder2['date'] = datetime.date.today().strftime("%B %d, %Y")
scratchHolder = []
scratchHolder.extend(featHolder['baseFeats']['generalFeats'])
for feat in featHolder['baseFeats']['alchemistFeats']:
    if is_feat_not_in_list(feat['link'], scratchHolder):
        scratchHolder.append(feat)
for feat in featHolder['baseFeats']['barbarianFeats']:
    if is_feat_not_in_list(feat['link'], scratchHolder):
        scratchHolder.append(feat)
for feat in featHolder['baseFeats']['bardFeats']:
    if is_feat_not_in_list(feat['link'], scratchHolder):
        scratchHolder.append(feat)
for feat in featHolder['baseFeats']['championFeats']:
    if is_feat_not_in_list(feat['link'], scratchHolder):
        scratchHolder.append(feat)
for feat in featHolder['baseFeats']['clericFeats']:
    if is_feat_not_in_list(feat['link'], scratchHolder):
        scratchHolder.append(feat)
for feat in featHolder['baseFeats']['druidFeats']:
    if is_feat_not_in_list(feat['link'], scratchHolder):
        scratchHolder.append(feat)
for feat in featHolder['baseFeats']['fighterFeats']:
    if is_feat_not_in_list(feat['link'], scratchHolder):
        scratchHolder.append(feat)
for feat in featHolder['baseFeats']['monkFeats']:
    if is_feat_not_in_list(feat['link'], scratchHolder):
        scratchHolder.append(feat)
for feat in featHolder['baseFeats']['rangerFeats']:
    if is_feat_not_in_list(feat['link'], scratchHolder):
        scratchHolder.append(feat)
for feat in featHolder['baseFeats']['rogueFeats']:
    if is_feat_not_in_list(feat['link'], scratchHolder):
        scratchHolder.append(feat)
for feat in featHolder['baseFeats']['sorcererFeats']:
    if is_feat_not_in_list(feat['link'], scratchHolder):
        scratchHolder.append(feat)
for feat in featHolder['baseFeats']['wizardFeats']:
    if is_feat_not_in_list(feat['link'], scratchHolder):
        scratchHolder.append(feat)
for key3 in featHolder['archTypeFeats']:
    scratchHolder.extend(featHolder['archTypeFeats'][key3])
featHolder2['feats'] = scratchHolder
json_data2 = json.dumps(featHolder2, indent=4)

filename2 = "feats-pf2-consolidated.json"
f2 = open(filename2, "w")
f2.write(json_data2)
f2.close
