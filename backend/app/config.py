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

    # PAYPAL SANDBOX CREDENTIALS (W27)
    PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "AZyqoWVhYMoxoHxti1XDWkSWJYCtlBOVkSi4hUhnlLZIi2j4sEow1v_yvmJ2zWOtewEzDLud7oKw-BQr")
    PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "EE35351cT6FGNRdpElcWzhQiy48F0by88ORIoDxRtAGX43RlF0u0DEKT3WFnfT8x4o3bcogR9VQPp9D1")
    PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")
    PAYPAL_BASE_URL = os.getenv("PAYPAL_BASE_URL", "https://api-m.sandbox.paypal.com")