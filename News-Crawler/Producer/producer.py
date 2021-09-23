from pymongo import MongoClient
from datetime import datetime
from password import pw

client = MongoClient(host="jinyes-server",
                     port=27017,
                     username="jinyes",
                     password=pw)
db = client.news


def to_bson(data):
    raw = data.split(",")
    doc = {
        "date": raw[0],
        "subject": raw[1].strip(),
        "specific_subject": raw[2].strip(),
        "title": raw[3].strip(),
        "url": raw[4].strip(),
    }

    return doc


def main():
    dataset = []
    today = datetime.now().strftime("%Y%m%d")
    with open("/Users/jinyes/git/Daily-News-Keywords-Bot/Data/{}.txt".format(today), 'r') as records:
        for record in records:
            doc = to_bson(record)
            dataset.append(doc)

    db.news_test.insert_many(dataset)


if __name__ == "__main__":
    main()
