#signup
#login to generate token
#get current user
#update user
#delete user


from fastapi import APIRouter, Depends,status,HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
from .schemas import UserCreate,UserUpdate, User as UserSchema
from ..database import get_db
from .service import (create_access_token,
                      existing_user,
                      create_user,
                      authenticate_user,
                      get_current_user
                      ,update_user )


router = APIRouter(
    prefix="/auth",
    tags=['auth']
)

@router.post('/signup',status_code=status.HTTP_201_CREATED)
async def register_user(user:UserCreate,db:Session = Depends(get_db)):
    # check existing user
    db_user = await existing_user(db,user.username,user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User with same email or username already exists")
    db_user = await create_user(db,user)
    access_token = await create_access_token(user.username,db_user.id)

    return {"access_token":access_token,
            "token_type":"bearer",
            "username":db_user.username}
 

#login to generate token

@router.post("/token",status_code=status.HTTP_201_CREATED)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),db:Session = Depends(get_db)):
    db_user = await authenticate_user(db,form_data.username,form_data.password)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect username or password")
    access_token = await create_access_token(db_user.username,db_user.id)

    return {"access_token":access_token,
            "token_type":"bearer",
            "username":db_user.username}



#get current user
@router.get("/profile",status_code=status.HTTP_200_OK,response_model=UserSchema)
async def current_user(token:str,db:Session = Depends(get_db)):
    db_user = await get_current_user(db,token)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")
    return db_user


#update user
@router.put("/{username}",status_code=status.HTTP_204_NO_CONTENT)
async def update_user_data(username:str,token:str,user_update:UserUpdate,db:Session = Depends(get_db)):
    db_user = await get_current_user(db,token)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")
    if db_user.username != username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid user request")
    
    await update_user(db,db_user,user_update)
  