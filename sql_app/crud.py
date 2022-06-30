"""This module provides tools witch allow to get, create and delete new records from database"""
from sqlalchemy.orm import Session
from .models import Image as ImageModel
from .schemas import ImageCreate


def create_image(db: Session, image: ImageCreate):
    """Add records to database"""
    db_image = ImageModel(
        title=image.title,
        date_register=image.date_register
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def get_images(db: Session, request_code: list[int]) -> list:
    """Get records from database"""
    images = list(db.query(ImageModel).filter(ImageModel.code.in_(request_code)).all())
    return images


def delete_images(db: Session, request_code: list[int]) -> None:
    """Delete records from database"""
    db.query(ImageModel).filter(ImageModel.code.in_(request_code)).delete()
    db.commit()
