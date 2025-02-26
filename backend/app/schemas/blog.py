# backend/app/schemas/blog.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class BlogPostBase(BaseModel):
    """
    Modèle de base pour un article de blog
    """
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10)

class BlogPostCreate(BlogPostBase):
    """
    Modèle pour la création d'un article de blog
    """
    images: Optional[List[str]] = None

class BlogPostResponse(BlogPostBase):
    """
    Modèle de réponse pour un article de blog
    """
    id: int
    author_id: int
    created_at: datetime
    images: Optional[List[str]] = None

    class Config:
        from_attributes = True

class BlogPostImageBase(BaseModel):
    """
    Modèle de base pour une image de blog
    """
    blog_post_id: int
    image_path: str
    description: Optional[str] = None

class BlogPostImageCreate(BlogPostImageBase):
    """
    Modèle pour la création d'une image de blog
    """
    pass

class BlogPostImageResponse(BlogPostImageBase):
    """
    Modèle de réponse pour une image de blog
    """
    id: int

    class Config:
        from_attributes = True
