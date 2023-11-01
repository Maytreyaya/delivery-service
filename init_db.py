from sqlalchemy.orm import sessionmaker

from database import engine, Base

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Commit the transaction
session = SessionLocal()
session.commit()
