# backend/app/models/blog.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class BlogPost(Base):
    """
    Modèle représentant un article de blog
    """
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    author_id = Column(Integer, ForeignKey('users.id'))
    author = relationship("User", back_populates="blog_posts")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class BlogPostImage(Base):
    """
    Images associées à un article de blog
    """
    __tablename__ = "blog_post_images"

    id = Column(Integer, primary_key=True, index=True)
    blog_post_id = Column(Integer, ForeignKey('blog_posts.id'))
    blog_post = relationship("BlogPost")
    
    image_path = Column(String(255), nullable=False)
    description = Column(String(200), nullable=True)
