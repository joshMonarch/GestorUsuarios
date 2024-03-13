from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
"""
OAuth2PasswordBearer:      Clase que gestionará la autentificación (usuario y contraseña).
OAuth2PasswordRequestForm: Clase que define la forma en la que se envían nuestros 
                           criterios de autentificación al backend.
"""
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(tags=["OAuth2"])

"""
Criterio de autentificación.
Recibe como parámetro la URL donde el cliente debe 
enviar las credencales para obterner el token de acceso 
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
Función que retorna el usuario de la Base de datos
que coincide que el nombre de usuario introducido
"""
def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])
    
def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])

"""
Función que se encarga de obtener el token de autentificación obtenido
de la Url de `tokenUrl` de la clase OAuth2PasswordBearer
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
Función POST que se encargará de enviar las credenciales.
Depends(): Intenta encontrar una manera de aportar la
           dependencia requerida (OAuth2PasswordRequestForm).
           Se encarga de extraer este objeto del request body,
           lugar donde se encuentran las credenciales.
"""
@router.post("/login/oauth2")
async def login(form: OAuth2PasswordRequestForm= Depends()):
    user_db = users_db.get(form.username)

    # Comprobamos que el usuario se encuentra en la BD.
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            details='El usuario no es correcto')
    
    user = search_user_db(form.username)
    # Comprobamos que la contraseña e corresponda con la guardada en la BD.
    if not form.password == user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="La contraseña no es correcta")
    
    # El token debería estar encriptado, que solo conozca el backend.
    return {"access_token": user.username, "token_type": "bearer"}

"""
Función que me revela cuál es mi usuario
Depends(current_user): Esta fucnión depende de que el usuario
                       esté autentificado.
"""
@router.get("/users/oauth2/me")
async def me(user: User= Depends(current_user)):
    return user

"""
En terminos generales:
1. Importamos las clases esenciales (passwordBearer y passwordRequestForm)
2. Definimos una función de login que estará pendiente de recibir las 
   credenciales del request body y validarlas.
3. Definimos una función que nos devuelva el usuario logeado que, a su vez,
   depende de otra función (current_user) que valide el token creado a
   partir de las credenciales obtenidas. 
"""