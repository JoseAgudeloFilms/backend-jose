from fastapi import FastAPI, Form, Depends
from pydantic import EmailStr
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import re
from DB import get_db,Base, engine  
from passlib.context import CryptContext


# Clase de la base de datos
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def validar_contraseña(password: str) -> bool:
    if (len(password) < 8 or
        not re.search(r'[A-Z]', password) or 
        not re.search(r'[a-z]', password) or 
        not re.search(r'[0-9]', password) or 
        not re.search(r'[!@#$%^&*(),.?":{}|<>]', password)):
        return False
    return True


@app.get("/")
def read_root():
    return {"message": "Hola desde FastAPI, prueba exitosa mamón"}

@app.post("/register")
def register(
    email: EmailStr = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    if not validar_contraseña(password):
        return {"error": "!Ojo! La contraseña no cumple con los requisitos de seguridad."}

   
    user_existente = db.query(User).filter(User.email == email).first()
    if user_existente:
        return {"error": "El usuario ya existe Culero"}

    # aqui esta el hash
    hashed_password = pwd_context.hash(password)
    nuevo_usuario = User(email=email, password=hashed_password)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {"message": f"Usuario {email} registrado con éxito mi perro"}

