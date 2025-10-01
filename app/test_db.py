# app/test_db.py

from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL connection URL
DATABASE_URL = "postgresql://postgres:pass@localhost:5432/cybercyte_db"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)  # echo=True prints SQL statements

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Base class for models
Base = declarative_base()

# Define a test table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

# Create tables in the database
Base.metadata.create_all(bind=engine)
# Insert a test user
test_user = User(name="Alice", email="alice@example.com")
db.add(test_user)   # Make sure the parentheses are closed
db.commit()
db.refresh(test_user)
print(f"Inserted user: {test_user.id}, {test_user.name}, {test_user.email}")
