import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from file_handler import uploader, deleter, getter
from sql_app import crud, schemas, models
from sql_app.database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)
app = FastAPI()


def get_db():
    """Database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/frames/', status_code=201)
def save_image(
        images: list[UploadFile] = File(..., media_type='image/jpeg'),
        db: Session = Depends(get_db)):
    """
    This function puts images into MinIo and creates record in the database.

    Response - list of created elements.
    """
    # Add image to Minio
    if len(images) > 15:
        detail = f'Count of images must be no more then 15. Got {len(images)}.'
        raise HTTPException(422, detail=detail)

    for file in images:

        if file.content_type != 'image/jpeg':
            raise HTTPException(422, detail='Invalid file format')

        file.filename = f'{uuid.uuid1()}.jpg'

    # Do record in database
    if uploader(images):
        response = []
        for file in images:
            img = schemas.ImageCreate
            img.title = file.filename
            img.date_register = datetime.now()
            res = crud.create_image(db=db, image=img)
            response.append(jsonable_encoder(res))

        return response


@app.get('/frames/', status_code=200)
def get_images(request_code: list[int] = Query(..., title='', ge=1), db: Session = Depends(get_db)):
    """Return list of images matched request_dode"""
    if not request_code:
        raise HTTPException(400, "Empty request code")
    request_code = list(set(request_code))
    images_list = crud.get_images(db=db, request_code=request_code)

    if not images_list:
        raise HTTPException(404, detail='Images not found')

    return getter(images_list)


@app.delete('/frames/', status_code=200)
def delete_images(
        request_code: list[int] = Query(..., title='', ge=1),
        db: Session = Depends(get_db)):
    """
    Delete files from MinIo and related records in database
    """
    request_code = list(set(request_code))
    to_delete = crud.get_images(db=db, request_code=request_code)

    if not to_delete:
        raise HTTPException(422, detail='Images don`t exist')

    if deleter(to_delete):
        crud.delete_images(db=db, request_code=request_code)

    return {'Were deleted': f'{", ".join(img.title for img in to_delete)}'}
