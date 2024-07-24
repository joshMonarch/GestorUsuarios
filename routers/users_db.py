from fastapi import APIRouter, HTTPException, status
from db.models.user import User
from db.schemas.user import user_schema, users_schema
from db.client import db_client
# Clase que representa el objeto `_id`
from bson import ObjectId

router = APIRouter(prefix='/userdb',
                   tags=["userdb"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}})

@router.get('/', response_model=list[User])
async def get_users():
    return users_schema(db_client.local.users.find())

# Path
@router.get('/{id}')
async def get_user(id: str):
    return search_user("_id", ObjectId(id))

# Query
@router.get('/')
async def get_user(id: str):
    return search_user("_id", ObjectId(id))

@router.post("/", response_model=User, status_code=201)
async def create_user(user: User):

    if isinstance(search_user("email", user.email), User):
        raise HTTPException(status_code=404,detail="User does not exist")

    
    user_dict = dict(user)
    del user_dict["id"]

    # Insert value and return the id
    id = db_client.local.users.insert_one(user_dict).inserted_id
    # Check the insertion returning the record by id.
    new_user = user_schema(db_client.local.users.find_one({"_id":id}))

    return User(**new_user)
    
@router.put('/')
async def update_user(user: User):

    user_dict = dict(user)
    del user_dict["id"]

    try:
        # Update a complete object, if found.
        db_client.local.users.find_one_and_replace(
            {"_id": ObjectId(user.id)},
            user_dict)
    except: 
        return {"error": "Update fail"}
    
    return search_user("_id", ObjectId(user.id))
        

@router.delete('/{id}')
async def delete_user(id: str):

    found = db_client.local.users.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        return {"error": "User not found"}
    return "Eliminado"
        
    

def search_user(field: str, key: str):
    try:
        user = user_schema(db_client.local.users.find_one({field: key}))
        return User(**user)
    except:
        return {"error": "User not found"}
    
    