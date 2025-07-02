from fastapi import FastAPI, Depends
from sqlalchemy import delete
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Contact
import crud

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/')
def root():
    return {'message': 'all are working!'}

@app.get("/identify")
def insert_test(db: Session = Depends(get_db)):
    # new_contact = Contact(
    #     phoneNumber="1234567890",
    #     email="test@example.com",
    #     linkPrecedence="primary"
    # )
    # db.add(new_contact)
    # db.commit()
    # db.refresh(new_contact)
    # return {"message": "Added!!"}

    cont = db.query(Contact).filter(Contact.id == 2).first()

    db.delete(cont)
    db.commit()

    return {"Message": "Deleted!!"}