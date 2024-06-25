from sqlalchemy import Column,Date,DateTime,ForeignKey,Integer,String,Enum
from datetime import datetime
from sqlalchemy.orm import relationship
from ..database import Base
from .enums import Gender
from ..post.models import post_likes

class User(Base):
    __tablename__ = "users"

    #basic details

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    name = Column(String)
    hashed_password = Column(String,nullable=False)
    created_dt = Column(DateTime,default=datetime.utcnow())

    #profile details
    dob = Column(Date)
    gender = Column(Enum(Gender))
    profile_pic = Column(String) #link to our profile picture
    bio = Column(String)
    location = Column(String)

    #posts
    posts = relationship("Post.models.Post",back_populates="auther")

    #liked posts
    liked_posts = relationship("Post.models.Post",secondary="post_likes",back_populates="liked_by_users")