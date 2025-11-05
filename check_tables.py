from app.models.database import engine
from app.models.models import Base

def check_tables():
    """Check if tables exist"""
    inspector = engine.dialect.inspector(engine)
    table_names = inspector.get_table_names()
    print("Existing tables:", table_names)
    
    if 'users' in table_names:
        print("✅ Users table exists!")
    else:
        print("❌ Users table does not exist!")
        
    if 'otps' in table_names:
        print("✅ OTPs table exists!")
    else:
        print("❌ OTPs table does not exist!")

if __name__ == "__main__":
    check_tables()