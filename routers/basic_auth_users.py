from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
"""
OAuth2PasswordBearer: Class that handles authentication 
                      (username and password).
OAuth2PasswordRequestForm: Class that defines how our 
                           authentication credentials 
                           are sent to the backend.
"""
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(tags=["OAuth2"])

"""
Authentication criterion.
It receives the URL where the client must send the 
credentials as a parameter to obtain the access token.
"""
oauth2 = OAuth2PasswordBearer(tokenUrl="/login/oauth2")

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
        "password": "123456"
    },
    "jose": {
        "username": "jose",
        "full_name": "Jose Rey",
        "email": "joserey@email.com",
        "disabled": True,
        "password": "678903"
    }
}

"""
Funtion which returns the user from the db as long as it 
matches the provided username.
"""
def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])
    
def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])

"""
Function responsible for obtaining the authentication token
from the tokenUrl of the OAuth2PasswordBearer class.
"""
async def current_user(token: str = Depends(oauth2)):
    user = search_user_db(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciales de autentificación inválidas",
            headers={"WWW-Authenticate": "Bearer"})
    
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Usuario inactivo")
    
    return user

"""
POST function responsible for sending the credentials.
Depends(): Attempts to find a way to provide the required
           dependency (OAuth2PasswordRequestForm). It extracts 
           this object from the request body, where the 
           credentials are located.
"""
@router.post("/login/oauth2")
async def login(form: OAuth2PasswordRequestForm= Depends()):
    user_db = users_db.get(form.username)

    # Check if the user is in the db
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            details='El usuario no es correcto')
    
    user = search_user_db(form.username)
    # Check if the password matches the one saved in the db
    if not form.password == user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="La contraseña no es correcta")
    
    # The token should be encrypted, only known by the backend
    return {"access_token": user.username, "token_type": "bearer"}

"""
Fucntion that shows which is my user.
Depends(current_user): It depends on the user being authenticated.
"""
@router.get("/users/oauth2/me")
async def me(user: User= Depends(current_user)):
    return user

"""
To sum up:
1. Import esenssial clases (passwordBearer y passwordRequestForm).
2. Define a login function pending to receive the credentials from the 
   request body and validate them.
3. Define a function responisble for returning the logged user which, 
   at the same time, depends on another function (current_user) that 
   validates the token provided by the obteined credentials.
"""