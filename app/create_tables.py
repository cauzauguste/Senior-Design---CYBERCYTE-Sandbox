# create_tables.py
from app.database import Base, engine
from app.models import Event

Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
