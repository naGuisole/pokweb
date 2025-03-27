# backend/main.py
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from contextlib import asynccontextmanager

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .config import settings
from .routes import auth, users, tournaments, blog, configurations, leagues, websockets
import logging
from .services.timer_service import start_timer_service, stop_timer_service


# Au début du fichier, après les imports
validation_logger = logging.getLogger("validation")
validation_logger.setLevel(logging.DEBUG)


# Context manager pour le startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: démarrer le service de timer
    await start_timer_service()

    yield

    # Shutdown: arrêter le service de timer
    await stop_timer_service()

# Création de l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="pokweb : application de gestion de tournois de poker. Notamment pour le célèbre JAPT",
    version="0.1.0",
    lifespan=lifespan
)


# Pour debugging :
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    validation_logger.error("Request Validation Error occurred")
    errors = []
    print("\n=== REQUEST VALIDATION ERROR ===")
    for error in exc.errors():
        err_info = {
            "loc": " -> ".join(str(x) for x in error["loc"]),
            "msg": error["msg"],
            "type": error["type"]
        }
        errors.append(err_info)
        print(f"Location: {err_info['loc']}")
        print(f"Message: {err_info['msg']}")
        print(f"Type: {err_info['type']}")
        print("---")

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Erreur de validation",
            "errors": errors
        }
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request, exc: ValidationError):
    validation_logger.error("Validation Error occurred")
    errors = []
    print("\n=== PYDANTIC VALIDATION ERROR ===")
    for error in exc.errors():
        err_info = {
            "loc": " -> ".join(str(x) for x in error["loc"]),
            "msg": error["msg"],
            "type": error["type"]
        }
        errors.append(err_info)
        print(f"Location: {err_info['loc']}")
        print(f"Message: {err_info['msg']}")
        print(f"Type: {err_info['type']}")
        print("---")

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Erreur de validation Pydantic",
            "errors": errors
        }
    )

@app.middleware("http")
async def debug_validation_errors(request, call_next):
    try:
        response = await call_next(request)
        return response
    except ValidationError as e:
        print("Pydantic Validation Error:")
        for error in e.errors():
            print(f"Field: {' -> '.join(str(x) for x in error['loc'])}")
            print(f"Error: {error['msg']}")
            print(f"Type: {error['type']}")
            print("---")
        raise

# Configuration basique du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Pour afficher dans la console
        logging.FileHandler('debug.log')  # Pour sauvegarder dans un fichier
    ]
)

# Configuration CORS pour autoriser les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL du frontend Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads/profile_images", StaticFiles(directory="uploads/profile_images"), name="profile_images")
app.mount("/uploads/sounds", StaticFiles(directory="uploads/sounds"), name="sounds")




# Pour debugging des requetes recues
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"Incoming request: {request.method} {request.url.path}")
    print(f"Request headers: {request.headers}")

    # # Pour les requêtes avec body (PUT, POST)
    # if request.method in ["PUT", "POST"]:
    #     body = await request.body()
    #     print(f"Body: {body.decode()}")
    #
    #     # Il faut reconstruire le body pour la requête suivante
    #     async def get_body():
    #         return body
    #
    #     request._body = body
    #     request.body = get_body

    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response

# Inclusion des différentes routes
app.include_router(auth.router, prefix="/auth", tags=["Authentification"])
app.include_router(users.router, prefix="/users", tags=["Utilisateurs"])
app.include_router(tournaments.router, prefix="/tournaments", tags=["Tournois"])
app.include_router(blog.router, prefix="/blog", tags=["Blog"])
app.include_router(configurations.router, prefix="/configurations", tags=["Configurations"])
app.include_router(leagues.router, prefix="/leagues", tags=["Ligues"])

# Inclusion des routes WebSocket après les autres routes
app.include_router(websockets.router, prefix="/ws", tags=["WebSockets"])

print("Available routes:")
for route in app.routes:
    if hasattr(route, "methods"):  # Routes API traditionnelles
        print(f"{route.methods} {route.path}")
    else:  # Points de montage (Mount objects)
        print(f"STATIC FILES {route.path}")

# Fonction pour gérer les erreurs WebSocket
@app.exception_handler(websockets.WebSocketDisconnect)
async def websocket_disconnect_handler(request, exc):
    # Les déconnexions WebSocket sont normales, nous les loggons simplement
    logging.info(f"WebSocket client disconnected with code: {exc.code}")
    return None


@app.get("/")



async def root():
    """
    Point d'entrée de l'API.
    Fournit des informations de base sur l'application.
    """
    return {
        "app_name": settings.APP_NAME,
        "status": "running",
        "version": "0.1.0"
    }
