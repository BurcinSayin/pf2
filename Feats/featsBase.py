from bs4 import BeautifulSoup
import requests
import re


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

