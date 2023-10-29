from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql://postgres:ytrewq2332@localhost:5433/delivery_db"

engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base()
Session = sessionmaker(engine)




