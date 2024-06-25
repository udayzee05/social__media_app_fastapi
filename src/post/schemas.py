from pydantic import BaseModel
from typing import Optional
from datetime import date,datetime



class Hastag(BaseModel):
    id:int
    name:str

class PostCreate(BaseModel):
    content:Optional[str] = None
    image:str
    location:Optional[str] = None


class Post(PostCreate):
    id:int
    auther_id:int
    liked_count:int
    created_dt:datetime

    class Config:
        orm_mode = True