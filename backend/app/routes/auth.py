# backend/app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt

from ..database import get_db
from ..crud import user as user_crud
from ..models.models import League, LeagueAdmin
from ..schemas import schemas as user_schemas
from ..config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def create_access_token(data: dict):
    """Crée un token JWT d'accès"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    """Récupère l'utilisateur courant à partir du token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = user_crud.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception


    return user

# @router.post("/register", response_model=user_schemas.UserResponse)
# async def register(
#     user_data: user_schemas.UserCreate,
#     db: Session = Depends(get_db)
# ):
#     """Inscription d'un nouvel utilisateur sans image de profil"""
#     try:
#         user = user_crud.create_user(db, user_data)
#         return user
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )



@router.post("/register", response_model=user_schemas.UserResponse)
async def register(
        user_data: user_schemas.UserCreate,
        db: Session = Depends(get_db)
):
    # Vérifier si l'email existe déjà
    db_user = user_crud.get_user_by_email(db, user_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")

    # Démarrer une transaction
    try:
        # Si l'utilisateur fournit des données de ligue
        league_id = None
        if user_data.league:
            if user_data.league.get("isNew"):
                # Créer la ligue
                db_league = League(
                    name=user_data.league["name"],
                    description=user_data.league.get("description")
                )
                db.add(db_league)
                db.flush()
                league_id = db_league.id
            else:
                league_id = user_data.league.get("id")

        # Créer l'utilisateur
        db_user = user_crud.create_user(db, user_data)

        # Si une nouvelle ligue a été créée, créer l'association admin
        if league_id and user_data.league.get("isNew"):
            league_admin = LeagueAdmin(
                league_id=league_id,
                user_id=db_user.id
            )
            db.add(league_admin)

        db.commit()
        return db_user


    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint de connexion - génère un token JWT
    """
    user = user_crud.authenticate_user(
        db, 
        form_data.username, 
        form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token({"sub": user.username})
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }


