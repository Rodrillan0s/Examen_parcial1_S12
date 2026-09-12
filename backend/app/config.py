from dotenv import load_dotenv
import os

# Cargar .env buscando tanto en backend/ como en backend/app/
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, '.env'), override=True)
load_dotenv(os.path.join(os.path.dirname(base_dir), '.env'), override=True)
load_dotenv(override=True)

class Config:
    
    #CREDENCIALES PARA LA DB
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME") 
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    SCHEMA='comercio'
    
    
    #CREDENCIALES CONFIGURACION APP
    SECRET_KEY = os.getenv("SECRET_KEY")
    TOKEN_KEY = os.getenv("TOKEN_KEY")
    DEBUG = os.getenv("DEBUG", True)

    # CLOUDINARY MEDIA
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "dljz1f6ns")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "638117962672329")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "cA7cmDDU-CDW8DkFaZ-Ym0P30KY")
    CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")