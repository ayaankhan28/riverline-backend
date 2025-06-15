from app.models.base import Base, engine
from app.models.call import Call, CallHistory

def init_database():
    """Initialize the database by creating all tables."""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {str(e)}")
        raise e 