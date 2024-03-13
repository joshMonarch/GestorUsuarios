from pymongo import MongoClient

# Base de datos local
#db_client = MongoClient().local

# Base de datos remota
db_client = MongoClient(
    "mongodb+srv://test:test@cluster0.juoqt5i.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
).test