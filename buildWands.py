from bs4 import BeautifulSoup
import requests
import json
import datetime
import codecs
import time

wandHolder = {}
wandHolder['name'] = 'Pathfinder 2.0 Wand list'
wandHolder['date'] = datetime.date.today().strftime("%B %d, %Y")

def get_multi(link):
    items = []
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    main = soup2.find("span", {'id':'ctl00_MainContent_DetailedOutput'})
    traits = main.find_all("span", {"class" : lambda L: L and L.startswith('trai')})
    traitHolder = []
    for trait in traits:
        traitHolder.append(trait.text)
    children = main.contents
    reachedBreak = False
    reachedItem = False
    detailHolder = []
    notFirstH2 = False
    inHeader = False
    parentDetails = {}
    parentDetails['traits'] = traitHolder
    item = {}
    item['link'] = link
    tagType = ""
    itemDetailHolder = []
    frequencyHolder = []
    craftHolder = []
    noSkipImg = True
    string = " "
    for child in children:
        
        stringContents = str(child)
        if stringContents.startswith("<"):
            #print(stringContents)
            if child.name == "img":
                if tagType != "":
                    if noSkipImg:
                        if tagType == "Frequency":
                            frequencyHolder.append(child['alt'])
                        if tagType == "Craft Requirements":
                            craftHolder.append(child['alt'])
                        noSkipImg = False
                    else:
                        noSkipImg = True

                        
                else:
                    parentDetails['actions'] = child['alt']
            if child.name == "hr":
                tagType = ""
                reachedBreak = True
                inHeader = False
            if child.name == "img":
                item['actions'] = child['alt']
            if child.name == "h1":
                inHeader = True
            
            if child.name == "h2":
                #print(child.text)
                className = ""
                try:
                    className = child['class'][0]
                except:
                    className = ""
                if className == "title":
                    if notFirstH2: 
                        
                        item['text'] = detailHolder + itemDetailHolder
                        item['frequency'] = string.join(frequencyHolder)
                        item['craftRequirements'] = string.join(craftHolder)
                        for key in parentDetails.keys():
                            item[key] = parentDetails[key]
                        items.append(item)
                        item = {}
                        item['link'] = link
                        itemDetailHolder = []
                    else:

                        notFirstH2 = True
                
                    reachedBreak = False
                    reachedItem = True
                    inHeader = False
                    name = child.text
                    start = child.text.find("Item")
                    item['name'] = child.text[0:start]
            if child.name == "b":
                if(child.text != "Source"):
                    tagType = child.text
                    
            if child.name == "a":

                try:
                    if child['class'][0] == "external-link" :
                        item['source'] = child.text
                except:
                    pass
                tagType = ""
        else:
            
            if reachedBreak:
                if(tagType != ""):
                    if not stringContents.isspace():
                        if tagType == "Frequency":
                            frequencyHolder.append(stringContents)
                        elif tagType == "Craft Requirements":
                            craftHolder.append(stringContents)
                        else:
                            parentDetails[tagType] = stringContents
                        #tagType = ""
                else: 
                    detailHolder.append(stringContents)
            if inHeader:
                if tagType != "":
                    #print(tagType)
                    if tagType == "Frequency":
                        frequencyHolder.append(stringContents)
                    elif tagType == "Craft Requirements":
                        craftHolder.append(stringContents)
                    else:
                        parentDetails[tagType] = stringContents
                    #tagType = ""
            if reachedItem:
                
                if tagType != "":
                    item[tagType] = stringContents
                    tagType = ""
                else:
                    if not stringContents.isspace():
                        itemDetailHolder.append(stringContents)
                    #print(stringContents)

    for key in parentDetails.keys():
        item[key] = parentDetails[key]
    item['frequency'] = string.join(frequencyHolder)
    item['craftRequirements'] = string.join(craftHolder)
    item['text'] = detailHolder + itemDetailHolder
    items.append(item)
    
    return items

def get_single(link):
    details = {}
    itemDetails = {}
    res2 = requests.get(link)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'lxml')
    detail = soup2.find(lambda tag: tag.name=='span' and tag.has_attr('id') and tag['id']=="ctl00_MainContent_DetailedOutput") 

    traits = detail.find_all("span", {"class" : lambda L: L and L.startswith('trai')})
    traitHolder = []
    for trait in traits:
        traitHolder.append(trait.text)
    details['traits'] = traitHolder
    children = detail.contents
    reachedBreak = False
    detailHolder = []
    tagType = ""
    for child in children:

        stringContents = str(child)
        if stringContents.startswith("<"):
            if child.name == "h1":
                name = child.text
                start = name.find("Item")
                details['name'] = name[0:start].strip()
            if child.name == "hr":
                tagType = ""
                reachedBreak = True
            
            if child.name == "a":
                try:
                    if child['class'][0] == "external-link" :
                        
                        details['source'] = child.text
                except:
                    pass
                tagType = ""
            if child.name == "b":

                if(child.text != "Source"):
                    tagType = child.text
            if child.name == "img":
                details['actions'] = child['alt']
            if child.name == "i":
                if(reachedBreak):
                    detailHolder.append(child.text) 
            #else:
                #if not stringContents.isspace() :
                    #detailHolder.append(child.text)        
        else:
            if reachedBreak:
                if tagType != "":
                    if not stringContents.isspace():
                            details[tagType] = stringContents
                else:
                    if not stringContents.isspace() :
                        detailHolder.append(stringContents)
            else:
                if tagType != "":
                    if not stringContents.isspace():
                        details[tagType] = stringContents
                

       #print(child)
        details['text'] = detailHolder
    return details



def get_from_csv(fileName):
    items = []
    listOfPages = codecs.open(fileName, encoding='utf-8')
    t = 0
    for line in listOfPages: 
        t += 1
        runeMD = line.split(",")
        print("Getting wand for :", runeMD[0],"This url:", runeMD[2].strip('\n'),"|is it multi:",runeMD[1])
        if runeMD[1] == "True":
            multiHolder = get_multi(runeMD[2].strip('\n'))
            for shield in multiHolder:
                shield['category'] = "wand"
                items.append(shield)
        else:
            items.append(get_single(runeMD[2].strip('\n')))
    return items



def get_all():
    wandHolder['specialMaterialWeapons'] = get_from_csv("wands.csv")

    
    return wandHolder

#print(get_all())
json_data = json.dumps(get_all())
#print(json_data)
filename = "wands-pf2.json"
f = open(filename, "w")
f.write(json_data)
f.close