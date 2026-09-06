import uvicorn
import os
from app import create_app

# Instanciamos la aplicación llamando a la fábrica
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )