from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection URL
DATABASE_URL = "postgresql://postgres:pass@localhost:5432/cybercyte_db"
"

# Create engine
engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()

# Test Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)


# Create tables
Base.metadata.create_all(bind=engine)


# Insert test data
def test_insert():
    db = SessionLocal()
    try:
        test_user = User(name="Zion", email="zion@example.com")
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ Inserted: {test_user.id}, {test_user.name}, {test_user.email}")
    except Exception as e:
        db.rollback()
        print("❌ Error inserting:", e)
    finally:
        db.close()


# Query test data
def test_query():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if users:
            print("📌 Users in DB:")
            for user in users:
                print(user.id, user.name, user.email)
        else:
            print("⚠️ No users found in DB.")
    except Exception as e:
        print("❌ Error querying:", e)
    finally:
        db.close()


if __name__ == "__main__":
    test_insert()
    test_query()
