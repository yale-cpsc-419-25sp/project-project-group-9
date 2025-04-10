from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Literal
from uuid import uuid4

app = FastAPI(title="Bazinga Community Board")

# User roles
UserRole = Literal["mentor", "mentee"]

# In-memory store
posts_db = []

# Post model
class Post(BaseModel):
    id: str
    author_name: str
    role: UserRole
    title: str
    content: str

class PostCreate(BaseModel):
    author_name: str
    role: UserRole
    title: str
    content: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Community Board! Visit /posts to see all discussions."}

@app.post("/posts", response_model=Post)
def create_post(post: PostCreate):
    new_post = Post(id=str(uuid4()), **post.dict())
    posts_db.append(new_post)
    return new_post

@app.get("/posts", response_model=List[Post])
def get_all_posts(role: UserRole = None):
    if role:
        return [post for post in posts_db if post.role == role]
    return posts_db

@app.get("/posts/{post_id}", response_model=Post)
def get_post(post_id: str):
    for post in posts_db:
        if post.id == post_id:
            return post
    raise HTTPException(status_code=404, detail="Post not found")

@app.delete("/posts/{post_id}")
def delete_post(post_id: str):
    global posts_db
    posts_db = [post for post in posts_db if post.id != post_id]
    return {"message": f"Post {post_id} deleted"}
