from dotenv import load_dotenv

import os
load_dotenv()

class Config:
    
    #CREDENCIALES PARA LA DB
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME") 
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    SCHEMA='taller'
    
    
    #CREDENCIALES CONFIGURACION APP
    SECRET_KEY = os.getenv("SECRET_KEY")
    TOKEN_KEY = os.getenv("TOKEN_KEY")
    DEBUG = os.getenv("DEBUG", True)