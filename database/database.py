from setting.setting import *
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de la conexión a la base de datos
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Declaración de la clase de modelo de datos
Base = declarative_base()

# Creación de una sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
