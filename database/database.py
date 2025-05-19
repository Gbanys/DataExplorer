from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine
import os

load_dotenv()

# SQLite connection string
postgres_url = f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:5432"

# Create engine with SQL statement logging enabled
engine = create_engine(postgres_url, echo=True)

# Function to create database tables from SQLModel classes
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
