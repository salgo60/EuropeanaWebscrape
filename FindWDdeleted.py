"""Just writes to a log deleted WD objects referenced from Europeana
see https://gist.github.com/salgo60/12896b356e74b47446eaaeb9a31d1669
"""
import json

import requests
import time
urlbase = 'http://data.europeana.eu/agent/base/'
RANGEEuropeana = 170000

import sys
print (sys.getdefaultencoding())

def check(Qnumber,line):
    checkURL = "https://www.wikidata.org/wiki/Special:EntityData/" + Qnumber + ".json"
    responseQikidata = requests.get(checkURL)
    if responseQikidata.status_code == 404:
        print(line, "|", sameAs.replace("http://www.wikidata.org/entity/", ""), "|", url, "|")
        return False
    return True


for line in  range(1 ,RANGEEuropeana):
    url = urlbase + str(line)
    response = requests.get(url)
    if response.status_code == 404:
        continue;
    data = json.loads(response.content)
    if  'sameAs' in data.keys():
        for sameAs in data['sameAs' ]:
            if "http://www.wikidata.org/entity/" in sameAs:
                Qnumber = sameAs.replace("http://www.wikidata.org/entity/","")
                check(Qnumber,line):
    else:
        print("Same As", url)


