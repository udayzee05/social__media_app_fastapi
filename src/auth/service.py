from fastapi import Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import jwt,JWTError
from datetime import datetime, timedelta
from .models import User
from .schemas import UserCreate,UserUpdate

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #hasing password
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="v1/auth/token")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256" # for encoding of jwt
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 30 minutes


# check for existing user
async def existing_user(db:Session,username:str,email:str):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        return db_user
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        return db_user
    return None

#create access token
async def create_access_token(username:str,id:int):
    encode = {"sub":username,"id":id}
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encode.update({"exp":expire})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

#get current user from token
async def get_current_user(db:Session,token:str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str = payload.get("sub")
        expires:datetime = payload.get("exp")
        if  datetime.fromtimestamp(expires) < datetime.now():
            return None
        if username is None:
            return None
        id:int = payload.get("id")
        if id is None:
            return None
        user = db.query(User).filter(User.id == id).first()
        return user
    except JWTError:
        return None
    

#get user from ID

async def get_user_from_user_id(db:Session,user_id:int):
    return db.query(User).filter(User.id == user_id).first()


async def create_user(db:Session,user:UserCreate):
    db_user = User(username=user.username.lower().strip(),
                   email=user.email.lower().strip(),
                   hashed_password=bcrypt_context.hash(user.password),
                   dob=user.dob or None,
                   gender=user.gender or None,
                   bio=user.bio or None,
                   location=user.location or None,
                   profile_pic=user.profile_pic or None,
                   name=user.name)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
    


# authentication
async def authenticate_user(db:Session,username:str,password:str):
    db_user = await existing_user(db,username=username,email=None)
    if not db_user:
        return False
    if not bcrypt_context.verify(password,db_user.hashed_password):
        return None
    return db_user


# update user

async def update_user(db:Session,db_user:User,user_update:UserUpdate):
    db_user.bio = user_update.bio or db_user.bio
    db_user.dob = user_update.dob or db_user.dob
    db_user.gender = user_update.gender or db_user.gender
    db_user.location = user_update.location or db_user.location
    db_user.profile_pic = user_update.profile_pic or db_user.profile_pic
    db_user.name = user_update.name or db_user.name
    db.commit()
    # db.refresh(db_user)
    # return db_user