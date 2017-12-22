import pymongo
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

db[MONGO_MAJOR_TABLE].remove()
