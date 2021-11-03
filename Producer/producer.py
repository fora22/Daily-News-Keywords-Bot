from pymongo import MongoClient
from datetime import datetime
import pymongo
import logging

pw = open("/home/jinyes/Daily-News-Keywords-Bot/pw.txt", 'r').read()
client = MongoClient(host="jinyes-server",
                     port=27017,
                     username="jinyes",
                     password=pw)
db = client.news


def to_bson(data):
    raw = data.split(",")
    doc = {
        "date": raw[0],
        "portal": raw[1],
        "subject": raw[2].strip(),
        "specific_subject": raw[3].strip(),
        "title": raw[4].strip(),
        "url": raw[5].strip(),
    }

    return doc


def main():
    today = datetime.now().strftime("%Y%m%d")
    collection = db[str(today)]
    collection.create_index([("url", pymongo.ASCENDING)], name='url', unique=True)
    portal_list = ["NAVER", "DAUM"]

    for portal in portal_list:
        with open("/home/jinyes/Daily-News-Keywords-Bot/Data/{}{}.txt".format(portal, today), 'r') as records:
            for record in records:
                try:
                    doc = to_bson(record)
                    collection.insert_one(doc)
                except Exception as error:
                    logging.getLogger("[{}] - {}".format(datetime.now(), error))
                    with open("/home/jinyes/Daily-News-Keywords-Bot/Data/fail/{}{}.txt".format(portal, today), 'a') as fail:
                        fail.write(record+'\n')


if __name__ == "__main__":
    logging.getLogger("[{}] - Start producer")
    main()
    logging.getLogger("[{}] - Success produce")
