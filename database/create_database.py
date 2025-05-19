from database import create_db_and_tables
import models

def main():
    create_db_and_tables()
    print("Database tables created!")

if __name__ == "__main__":
    main()
