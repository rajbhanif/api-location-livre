from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.db.session import Base

class Pret(Base):
    __tablename__ = "prets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    date_pret = Column(Date, nullable=False)
    date_retour = Column(Date, nullable=True)
    renouvellements = Column(Integer, nullable=False, default=0)

    user = relationship("User")
    book = relationship("Book")
