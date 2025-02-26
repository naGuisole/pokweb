# backend/app/routes/blog.py
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
from pathlib import Path
from datetime import datetime

from ..database import get_db
from ..crud import blog as blog_crud
from ..schemas.blog import BlogPostCreate, BlogPostResponse
from .auth import get_current_user
from ..models.models import User

router = APIRouter()

UPLOAD_DIR = Path("uploads/blog")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/", response_model=BlogPostResponse)
async def create_blog_post(
    title: str,
    content: str,
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crée un nouvel article de blog"""
    image_paths = []
    
    # Sauvegarde des images
    for image in images:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = UPLOAD_DIR / f"{current_user.id}_{timestamp}_{image.filename}"
        with image_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_paths.append(str(image_path))
    
    post_data = BlogPostCreate(
        title=title,
        content=content,
        images=image_paths
    )
    
    try:
        return blog_crud.create_blog_post(db, post_data, current_user.id)
    except ValueError as e:
        # En cas d'erreur, supprimer les images uploadées
        for path in image_paths:
            Path(path).unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[BlogPostResponse])
async def list_blog_posts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Liste les articles de blog"""
    return blog_crud.list_blog_posts(db, skip=skip, limit=limit)

@router.get("/{post_id}", response_model=BlogPostResponse)
async def get_blog_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Récupère un article de blog spécifique"""
    post = blog_crud.get_blog_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article non trouvé"
        )
    return post

@router.delete("/{post_id}")
async def delete_blog_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprime un article de blog"""
    post = blog_crud.get_blog_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article non trouvé"
        )
        
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez supprimer que vos propres articles"
        )
    
    # Supprimer les images associées
    for image in blog_crud.get_blog_post_images(db, post_id):
        Path(image.image_path).unlink(missing_ok=True)
    
    blog_crud.delete_blog_post(db, post_id)
    return {"status": "success", "message": "Article supprimé"}

@router.post("/{post_id}/images")
async def add_images_to_post(
    post_id: int,
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ajoute des images à un article existant"""
    post = blog_crud.get_blog_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article non trouvé"
        )
        
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que vos propres articles"
        )
    
    image_paths = []
    for image in images:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = UPLOAD_DIR / f"{current_user.id}_{timestamp}_{image.filename}"
        with image_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_paths.append(str(image_path))
        
        blog_crud.add_image_to_post(db, post_id, str(image_path))
    
    return {"status": "success", "message": "Images ajoutées", "paths": image_paths}
