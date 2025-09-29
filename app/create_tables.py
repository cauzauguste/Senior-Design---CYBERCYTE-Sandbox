from .database import Base, engine
from .models import Event

Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
