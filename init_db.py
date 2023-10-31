from sqlalchemy.orm import sessionmaker

from database import engine, Base, Session
from models import User, Order


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Commit the transaction
session = SessionLocal()
session.commit()
