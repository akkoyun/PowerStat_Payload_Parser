from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .Config import APP_Settings

# Define Database Connection
SQLALCHEMY_DATABASE_URL = f'postgresql://{APP_Settings.POSTOFFICE_DB_USERNAME}:{APP_Settings.POSTOFFICE_DB_PASSWORD}@{APP_Settings.POSTOFFICE_DB_HOSTNAME}:{APP_Settings.POSTOFFICE_DB_PORT}/{APP_Settings.POSTOFFICE_DB_NAME}'

# Create Database Engine
DB_Engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=20, max_overflow=0)

# Create Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=DB_Engine)

# Defibe Base Class
Base = declarative_base()

# Create DataBase
def Create_Database():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()