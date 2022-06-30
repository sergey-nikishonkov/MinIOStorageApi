from sqlalchemy import Column, Integer, String, DateTime
from .database import Base


class Image(Base):
    __tablename__ = "inbox"

    code = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    date_register = Column(DateTime, nullable=False)

    def __repr__(self):
        return f'Image title: {self.title}'
