from sqlalchemy import Column, Integer, Float, String
from database import Base

class UserProfile(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    age = Column(Integer)
    salary = Column(Float)
    investments = Column(Float)
    loans = Column(Float)
    goals = Column(String)
