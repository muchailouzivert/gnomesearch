from sqlalchemy import Column, Integer, VARCHAR, TEXT, Date

from database import Base

class Films(Base):
    __tablename__ = "films"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(VARCHAR(228))
    director = Column(VARCHAR(228))
    startYear = Column(Date)
    category = Column(VARCHAR(228))
    runtimeMinutes  = Column(VARCHAR(228))
    rate = Column(Integer)
    description = Column(TEXT)
    image = Column(VARCHAR(45))
