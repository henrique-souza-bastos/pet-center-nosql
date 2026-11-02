"""
Conexão com o MongoDB Atlas.

A connection string (endereço + usuário + senha do banco) fica no arquivo
.env, que NÃO é enviado para o GitHub. Veja o modelo em .env.exemplo.

Autores: Henrique Souza e Yuri Cainã
"""
import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()  # lê as variáveis do arquivo .env

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise SystemExit("Defina MONGO_URI no arquivo .env (veja .env.exemplo).")

cliente = MongoClient(MONGO_URI)
banco = cliente["patinhas_carinho"]  # o banco é criado no primeiro dado gravado
