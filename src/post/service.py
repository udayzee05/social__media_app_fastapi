from sqlalchemy.orm import Session
from datetime import datetime
from .schemas import PostCreate,Post as PostSchema,Hastag as HastagSchema
from .models import Post,Hashtag,post_hashtags
from ..auth.service import existing_user
import re
from sqlalchemy import desc
from ..auth.models import User


#create post

async def create_post_svc(db:Session,post:PostCreate,user_id:int):
    # check user id exists
    db_user = existing_user(db,user_id)
    if not db_user:
        return None

    db_post = Post(
        content=post.content,
        image=post.image,
        location=post.location,
        auther_id=user_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


#create hastag from post

async def create_hastag_svc(db:Session,post:Post):
    regex = r"#(\w+)"
    matches = re.findall(regex, post.content)

    for match in matches:
        name = match[1:]
        hashtag = db.query(Hashtag).filter(Hashtag.name == name).first()

        if not hashtag:
            hashtag = Hashtag(name=name)
            db.add(hashtag)
            db.commit()
        post.hashtags.append(hashtag)

#get user post

async def get_user_post_svc(db:Session,user_id:int)->list[PostSchema]:
    posts = db.query(Post).filter(Post.auther_id == user_id).order_by(desc(Post.created_dt)).all()

    return posts



#get post from hashtag
async def get_hashtag_post_svc(db:Session,hashtag_name:str):

    hashtag = db.query(Hashtag).filter(Hashtag.name == hashtag_name).first()

    if not hashtag:
        return []

    return hashtag.posts


#get random post for feed return the latest post of all user

async def get_random_post_svc(db:Session,page:int=1,limit:int=10,hashtag:str=None):
    total_posts = db.query(Post).count()

    offset = (page - 1) * limit

    if offset >= total_posts:
        return []
    posts = db.query(Post,User.username).join(User).order_by(desc(Post.created_dt))

    if hashtag:
        posts = posts.join(post_hashtags).join(Hashtag).filter(Hashtag.name == hashtag)
         
    posts = posts.offset(offset).limit(limit).all()
    result = []
    for post,username in posts:
        post_dict = post.__dict__
        post_dict["username"] = username
        result.append(post_dict)

    return result
        
#get post by post id
async def get_post_by_id_svc(db:Session,post_id:int)->PostSchema:
    return db.query(Post).filter(Post.id == post_id).first()

#delete post
async def delete_post_svc(db:Session,post_id:int):
    db_post = await get_post_by_id_svc(db,post_id)

    if not db_post:
        return None

    db.delete(db_post)
    db.commit()



# like post
