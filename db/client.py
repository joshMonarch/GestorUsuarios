from pymongo import MongoClient

# Local database
#db_client = MongoClient().local

# Remote database
db_client = MongoClient(
    "mongodb+srv://test:test@cluster0.juoqt5i.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
).test