"""Function to scrape Europeana
    1) Read Europeana
    2) Check if Wikidataobject exist
    3) Write to file
    4) Use OpenRefine/Quickstatement for uploading to Wikidata
"""
import json
import csv

import requests
import time
urlbase = 'http://data.europeana.eu/agent/base/'
import sys
print (sys.getdefaultencoding())


def check(Qnumber):
    checkURL = "https://www.wikidata.org/wiki/Special:EntityData/" + Qnumber + ".json"
    responseQikidata = requests.get(checkURL)
    if responseQikidata.status_code == 404:
        return False
    return True

# 30489 -  42557
# 42557 - 55541
# 55541 - 70410
# 70410 - 81234 Europeana agent 11 78200 - 81234
# 81234 - 91000 Europeana agent 12 81235 - 91000
# 91000 - 105700 Europeana agent 13 93609 - 105700
# 105701 - 118368 Europeana agent 20
# 118368 - 124745 Europeana agent 21
# 124746 - 137954 Europeana agent 13 124746 - 137954
# 137954 - 138977 Europeana agent 15 137954 - 138977
# 138979 - 152164 Europeana agent 14
# 152165 - 153830 Europeana agent 16
# 153830 - 155402 Europeana agent 17
# 155402 -  165086 Europeana agent 18
# 165087 - 200000 no objects ?!?!?
with open('Europeana21.csv', mode='w') as europeana_file:
    europeana_writer = csv.writer(europeana_file, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for line in  range(118369,124745):
        url = urlbase + str(line)
        response = requests.get(url)
        if response.status_code == 404:
            print(url,"\t 404")
            continue;
        data = json.loads(response.content)
        #print(data)
        if  'sameAs' in data.keys():
            if 'prefLabel' in data.keys():
                if 'en' in (data['prefLabel']):
                    labelen = data['prefLabel']['en']
            for sameAs in data['sameAs' ]:
                if "http://www.wikidata.org/entity/" in sameAs:
                    Qnumber = sameAs.replace("http://www.wikidata.org/entity/","")
                    if check(Qnumber):
                        print(line , "|",sameAs.replace("http://www.wikidata.org/entity/",""),"|",url,"|",labelen)
                        europeana_writer.writerow([line ,sameAs.replace("http://www.wikidata.org/entity/",""),url,labelen])

        else:
            print("No Wikidata", url)



