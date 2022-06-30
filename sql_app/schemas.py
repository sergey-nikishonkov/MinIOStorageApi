from datetime import datetime
from pydantic import BaseModel


class ImageBase(BaseModel):
    title: str
    date_register: datetime


class ImageCreate(ImageBase):
    pass


class Image(ImageBase):
    code: int

    class Config:
        orm_mode = True
