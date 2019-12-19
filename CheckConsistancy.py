"""Function to check consistancy Europeana agent/base -> Wikidata
    1) Read Wikidata
    2) Check if Europeana agent/base 1 - RANGEEuropeana
    2-1) Record exist
    2-2) do we have a same as Wikidata
    2-3) does the Wikidata object exist
    2-4) is this object referenced in Wikidata
    3) Log missing to file

TODO:   Check WD -> Europeana
        Add some statistics
See also Constraints report in Wikidata
        https://www.wikidata.org/wiki/Wikidata:Database_reports/Constraint_violations/P7704
"""
import json
import csv
import datetime
import requests
import logging

from SPARQLWrapper import SPARQLWrapper,JSON

__version__ = "1.0.0"

RANGEEuropeana = 170000
# - 170 000

class wd_dict(dict):

    # __init__ function
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value

logger = logging.getLogger(__name__)
urlbase = 'http://data.europeana.eu/'
urlagent = 'agent/base/'
wd_dictionary = wd_dict()

def check_WD_not_deleted(Qnumber):
    checkURL = "https://www.wikidata.org/wiki/Special:EntityData/" + Qnumber + ".json"
    responseQikidata = requests.get(checkURL)
    if responseQikidata.status_code == 404:
        print(Qnumber, " deleted in WD")
        logger.warning("Deleted in WD:  %s",Qnumber)
        return False
    logger.info("WD object ok: %s ", Qnumber)
    return True

def get_sparql_results(endpoint_url, query):
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def checkWDValue(Qnumber,EuropeanaEntityID):
    if check_WD_not_deleted(Qnumber):
        try:
            if wd_dictionary[Qnumber] == EuropeanaEntityID:
                logger.info("WD: %s Europeana: %s", Qnumber, EuropeanaEntityID)
                return True

        except:
            logger.exception("WD missing: %s Europeana: %s", Qnumber, EuropeanaEntityID)
    return

def set_WD_Europeana():
    endpoint_url = "https://query.wikidata.org/sparql"
    query = 'SELECT (REPLACE(STR(?item),".*Q","Q") AS ?Q) ?EuropeanaEntityID WHERE { ?item wdt:P7704  ?EuropeanaEntityID }'
    print(query)
    try:
        WDresults = get_sparql_results(endpoint_url, query)
        for WDrec in WDresults["results"]["bindings"]:
            wd_dictionary.add(WDrec['Q']['value'], WDrec['EuropeanaEntityID']['value'])
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        logging.exception("SPARQL error")
    return

def main():
    # Create logger
    today = str(datetime.date.today())
    LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s"
    logging.basicConfig(filename="log/EuropeanaWikidata" + today + ".log",
                        level=logging.INFO,
                        format=LOG_FORMAT)
    # Add terminal logging
    logging.getLogger().addHandler(logging.StreamHandler())
    logger.info("Version %s", __version__)
    logger.info("Start Europeana / WD")

    set_WD_Europeana()
    logger.info("WD records with EuropeanaEntity %s ",wd_dictionary.__len__())

    with open('EuropeanaCheckAll.csv', mode='w') as europeana_file:
        europeana_writer = csv.writer(europeana_file, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for line in  range(1,RANGEEuropeana):
            EuropeanaEntitryID = urlagent + str(line)
            urlEuropeana = urlbase + EuropeanaEntitryID
            response = requests.get(urlEuropeana)
            if response.status_code == 404:
                print(urlEuropeana,"\t 404")
                logger.info("Europena missing %s ", urlEuropeana)
                continue;
            data = json.loads(response.content)

            if  'sameAs' in data.keys():
                if 'prefLabel' in data.keys():
                    if 'en' in (data['prefLabel']):
                        labelen = data['prefLabel']['en']
                for sameAs in data['sameAs' ]:
                    if "http://www.wikidata.org/entity/" in sameAs:
                        QnumberEuropeana = sameAs.replace("http://www.wikidata.org/entity/","")
                        logger.info("Europeana %s %s %s ", QnumberEuropeana, EuropeanaEntitryID,labelen)
                        if not checkWDValue(QnumberEuropeana,EuropeanaEntitryID):
                             europeana_writer.writerow([line ,QnumberEuropeana,urlEuropeana,labelen])
            else:
                print("No Wikidata", urlEuropeana)
            #'http://www.wikidata.org/entity/

if __name__ == "__main__":
    main()
