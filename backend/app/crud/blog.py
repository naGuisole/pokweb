# backend/app/crud/blog.py
from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.blog import BlogPost, BlogPostImage
from ..schemas.blog import BlogPostCreate, BlogPostImageCreate

def create_blog_post(
    db: Session, 
    post_data: BlogPostCreate, 
    author_id: int
) -> BlogPost:
    """
    Crée un nouvel article de blog
    
    Args:
        db (Session): Session de base de données
        post_data (BlogPostCreate): Données de l'article
        author_id (int): ID de l'auteur
    
    Returns:
        BlogPost: Article de blog créé
    """
    db_post = BlogPost(
        title=post_data.title,
        content=post_data.content,
        author_id=author_id
    )
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # Ajouter les images si présentes
    if post_data.images:
        for img_path in post_data.images:
            create_blog_post_image(
                db, 
                BlogPostImageCreate(
                    blog_post_id=db_post.id, 
                    image_path=img_path
                )
            )
    
    return db_post

def get_blog_post_by_id(
    db: Session, 
    post_id: int
) -> Optional[BlogPost]:
    """
    Récupère un article de blog par son ID
    
    Args:
        db (Session): Session de base de données
        post_id (int): ID de l'article
    
    Returns:
        Optional[BlogPost]: Article de blog trouvé ou None
    """
    return db.query(BlogPost).filter(BlogPost.id == post_id).first()

def list_blog_posts(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[BlogPost]:
    """
    Liste les articles de blog
    
    Args:
        db (Session): Session de base de données
        skip (int): Nombre d'articles à ignorer
        limit (int): Nombre max d'articles à retourner
    
    Returns:
        List[BlogPost]: Liste des articles de blog
    """
    return db.query(BlogPost).order_by(BlogPost.created_at.desc()).offset(skip).limit(limit).all()

def create_blog_post_image(
    db: Session, 
    image_data: BlogPostImageCreate
) -> BlogPostImage:
    """
    Ajoute une image à un article de blog
    
    Args:
        db (Session): Session de base de données
        image_data (BlogPostImageCreate): Données de l'image
    
    Returns:
        BlogPostImage: Image créée
    """
    # Vérification de l'existence de l'article de blog
    blog_post = get_blog_post_by_id(db, image_data.blog_post_id)
    if not blog_post:
        raise ValueError("Article de blog non trouvé")
    
    db_image = BlogPostImage(
        blog_post_id=image_data.blog_post_id,
        image_path=image_data.image_path,
        description=image_data.description
    )
    
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return db_image

def get_blog_post_images(
    db: Session, 
    blog_post_id: int
) -> List[BlogPostImage]:
    """
    Récupère les images d'un article de blog
    
    Args:
        db (Session): Session de base de données
        blog_post_id (int): ID de l'article de blog
    
    Returns:
        List[BlogPostImage]: Liste des images de l'article
    """
    return db.query(BlogPostImage).filter(
        BlogPostImage.blog_post_id == blog_post_id
    ).all()
