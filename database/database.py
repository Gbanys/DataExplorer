from sqlmodel import SQLModel, create_engine

# SQLite connection string
postgres_url = f"postgresql://postgres:drakonas@0.0.0.0:5432"

# Create engine with SQL statement logging enabled
engine = create_engine(postgres_url, echo=True)

# Function to create database tables from SQLModel classes
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
