from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Algoritmo que define la firma de los tokens de acceso
ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1
# Semilla que se utiliza para asegurar aún mas el token mediante una firma.
# Si la firma no es válida, el token podría haber sido modificado, por lo tanto se desecha.
SECRET = "d172ca90107b2cca89ee7e75dad3bdb74d9d56511b3b30be2238c903b03ae2fe"

router = APIRouter(tags=["JWT"])

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

# Algoritmo que utilizaremos para encriptar las contraseñas en un hash.
# Requiere instalar passlib[bcrypt]
crypt = CryptContext(schemes=["bcrypt"])

class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool

class UserDB(User):
    password: str

users_db = {
    "mouredev": {
        "username": "mouredev",
        "full_name": "Brais Moure",
        "email": "braismoure@mourede.com",
        "disabled": False,
        "password": "$2a$12$HpsV43cfDgs8.4gINOP98eoNxghfGw6QtO2hUorbjPOOGbkc0ohAK"
    },
    "jose": {
        "username": "jose",
        "full_name": "Jose Rey",
        "email": "joserey@email.com",
        "disabled": False,
        "password": "$2a$12$KNnZRZincB5jjWFFSPAO6.ZeQmE26cTeCUVk/lRW5zMlpyRusKMLu"
    }
}

def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])
    
"""
Dependencia para buscar el ususario realizando una desencriptación.
"""
async def auth_user(token: str = Depends(oauth2)):

    exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciales de autentificación inválidas",
            headers={"WWW-Authenticate": "Bearer"})

    try:

        username = jwt.decode(token, SECRET, algorithms=ALGORITHM).get("sub")

        if username is None:  raise exception
        
    except JWTError: raise exception

    return search_user_db(username)

"""
Depende del usuario desencriptado. Además, valida si está inactivo o no.
"""
async def current_user(user: str = Depends(auth_user)):

    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Usuario inactivo")

    return user

@router.post("/login/jwt")
async def login(form: OAuth2PasswordRequestForm= Depends()):
    user_db = users_db.get(form.username)

    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            details='El usuario no es correcto')
    
    user = search_user_db(form.username)

    # Verifica que la contraseña encriptada de la base de datos se corresponda con 
    # la contraseña del request body
    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="La contraseña no es correcta")

    """
    El concepto de access token requiere de un tiempo limite de uso de ese token. 
    Una vez alcanzado ese tiempo límite será necesario solicitar otro token. 
    """
    access_token = {
        "sub": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)
        }
    
    # Retornamos el ccess_token encriptado
    return {
        "access_token": jwt.encode(access_token, key=SECRET, algorithm=ALGORITHM),
        "token_type": "bearer"}

@router.get("/users/jwt/me")
async def me(user: User= Depends(current_user)):
    return user

"""
En términos generales:
1. Importamos las librerías: jwt, CryptContext.
2. Definimos el algorítmo con el que encriptaremos el token, el tiempo límite de 
   validez del mismo y la semilla con la que firmaremos el token.
3. Definimos la funcion ´login´, en donde verificaremos el usuario y la contraseña 
   encriptada y nos devolverá el token encriptado.
4. Definimos la función ´me´, 
"""