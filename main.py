from fastapi import FastAPI, Depends
from sqlalchemy import delete
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Contact, IdentifyRequest, ContactResponse, TestInsert
from datetime import datetime
import crud
from typing import Dict

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def update_rest_secondary(db: Session, email: str, phone: str, primId: int, resEmail: list[str], resPhone: list[str], resSecondaryIds: list[int]):
    children = crud.get_contacts_by_email_and_phone(db, email, phone)

    if not children:
        return
    
    for i in children:
        i.linkPrecedence = "Secondary"
        i.linkedId = primId
        update_rest_secondary(db, i.email, i.phoneNumber, primId, resEmail, resPhone, resSecondaryIds)

    # for i in phones:
    #     if i.linkPrecedence != "Secondary" or i.linkedId != primId:
    #         i.linkPrecedence = "Secondary"
    #         i.linkedId = primId
    #         update_rest_secondary(db, i.email, i.phoneNumber, primId, resEmail, resPhone, resSecondaryIds)
    

def update_first_secondary(db: Session, email: str, phone: str, resEmail: list[str], resPhone: list[str], resSecondaryIds: list[int]):
    identifiedRows = crud.get_contacts_by_email_and_phone(db, email, phone)

    if len(identifiedRows) == 0:
        entered = crud.create_contact(db, email, phone)
        return [entered.id, entered.email, entered.phoneNumber, []]
    else:
        primary_row: Contact = identifiedRows[0]

    # if len(emails) == 0 or len(phones) == 0:
    #     entered = crud.create_contact(db, email, phone, primary_row.id, "Secondary")
    #     return []

    for i in identifiedRows:
        if i.id != primary_row.id:

            crud.update_contact(db, i.id, primary_row.id, "Secondary")

            # i.linkedId = primary_row.id
            # i.linkPrecedence = "Secondary"
            # i.updatedAt = datetime.now()
            list(set(resEmail.append(i.email)))
            list(set(resPhone.append(i.phoneNumber)))
            list(set(resSecondaryIds.append(i.id)))
            # resEmail.append(i.email)
            # resPhone.append(i.phoneNumber)
            # resSecondaryIds.append(i.id)
        update_rest_secondary(db, email, phone, primary_row.id, resEmail, resPhone, resSecondaryIds)
    return primary_row.id

@app.get('/')
def root():
    return {'message': 'all are working!'}

@app.post("/identify", response_class=ContactResponse)
def insert_test(data: IdentifyRequest, db: Session = Depends(get_db)):
    resEmail = []
    resPhone = []
    resSecondaryIds = []
    if data.email == "" and data.phoneNumber == "":
        return {"Data not found": "Email and phone number is missing!"}
    
    email = data.email
    phone = data.phoneNumber

    primId = update_first_secondary(db, email, phone, resEmail, resPhone, resSecondaryIds)

    return {
        "contact": {
            "primaryContatctId": primId,
            "emails": resEmail,
            "phoneNumbers": resPhone,
            "secondaryContactIds": resSecondaryIds
        }
    }

@app.post("/testInsert")
def test_insert(data: Dict[str, TestInsert], db: Session = Depends(get_db)):
    for i in data.values():
        a = crud.create_contact(db, i.email, i.phoneNumber)

@app.post("truncateTable")
def test_truncate():
    crud.truncate()