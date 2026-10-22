
from fastapi import FastAPI
from dotenv import load_dotenv

from app.movements.routes import router as movements_router
from app.auth.routes import router as auth_router
from app.categories.routes import router as categories_router

# Carga las variables de entorno del proyecto.
load_dotenv()

# Crea la aplicación principal de FINGO.
app = FastAPI(title="FINGO API")

# Registra las rutas de movimientos financieros.
app.include_router(movements_router)

# Registra las rutas de autenticación.
app.include_router(auth_router)

# Registra las rutas de categorías.
app.include_router(categories_router)


@app.get("/")
def root():
    """Comprueba que la API esté funcionando."""
    return {"message": "FINGO API funcionando"}
