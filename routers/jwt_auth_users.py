from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Algorithm the defines the access token signature
ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1
# Seed used to further secure the token through a signature.
# If the signature is invalid, the token could have been modified. Hence, it is discarded. 
SECRET = "d172ca90107b2cca89ee7e75dad3bdb74d9d56511b3b30be2238c903b03ae2fe"

router = APIRouter(tags=["JWT"])

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

# Algorithm implemented to encrypt passwords into a hash.
# Install passlib[bcrypt] required.
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
Dependency that looks for an user performing a decryption
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
It depends on the decrypted user. Also, it validates whether is active or not.
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

    # Check if the encryted password in the bd matches the one in the request body
    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="La contraseña no es correcta")

    """
    An access token requires a limited time of use. Once reached that time, 
    it is necessary to request another one.
    """
    access_token = {
        "sub": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)
        }
    
    # Return the encrypted access token
    return {
        "access_token": jwt.encode(access_token, key=SECRET, algorithm=ALGORITHM),
        "token_type": "bearer"}

@router.get("/users/jwt/me")
async def me(user: User= Depends(current_user)):
    return user

"""
To sum up:
1. Import classes: jwt, CryptContext.
2. define the algorithm with which we will encrypt the token, the token's 
   expiration time, and the seed with which we will sign the token.
3. Define the ´login´ function, where we will verify the user and the 
   encrypted password and it will return the encrypted token.
4. Define the ´me´ function.
"""