import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise SystemExit("Defina MONGO_URI no arquivo .env (veja .env.exemplo).")

cliente = MongoClient(MONGO_URI)
banco = cliente["patinhas_carinho"]
