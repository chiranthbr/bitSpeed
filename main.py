from fastapi import FastAPI, Depends
from sqlalchemy import delete
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Contact, IdentifyRequest, ContactResponse, TestInsert
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

def update_results(i, resEmail = None, resPhone: list[str] = None, resSecondaryIds: list[int] = None, selectedIds: list[int] = None):
    if resEmail is not None:
        resEmail.append(i.email)
        resEmail[:] = list(set(resEmail))

    if resPhone is not None:
        resPhone.append(i.phoneNumber)
        resPhone[:] = list(set(resPhone))

    if resSecondaryIds is not None:
        resSecondaryIds.append(i.id)
        resSecondaryIds[:] = list(set(resSecondaryIds))

    if selectedIds is not None:
        selectedIds.append(i.id)
        selectedIds[:] = list(set(selectedIds))

def update_rest_secondary(db: Session, email: str, phone: str, primId: int, resEmail: list[str], resPhone: list[str], resSecondaryIds: list[int], selectedIds: list[int]):
    children = crud.get_contacts_by_email_and_phone(db, email, phone)
    children = [i for i in children if i.id not in selectedIds and i.id is not primId]

    if not children:
        return
    
    for i in children:
        i.linkPrecedence = "secondary"
        i.linkedId = primId
        update_results(i, resEmail, resPhone, resSecondaryIds, selectedIds)
        update_rest_secondary(db, i.email, i.phoneNumber, primId, resEmail, resPhone, resSecondaryIds, selectedIds)

    # for i in phones:
    #     if i.linkPrecedence != "Secondary" or i.linkedId != primId:
    #         i.linkPrecedence = "Secondary"
    #         i.linkedId = primId
    #         update_rest_secondary(db, i.email, i.phoneNumber, primId, resEmail, resPhone, resSecondaryIds)
    

def update_first_secondary(db: Session, email: str, phone: str, resEmail: list[str], resPhone: list[str], resSecondaryIds: list[int], selectedIds: list[int]):
    identifiedRows = crud.get_contacts_by_email_and_phone(db, email, phone)
    emails = [i.email for i in identifiedRows]
    phones = [i.phoneNumber for i in identifiedRows]

    if len(identifiedRows) == 0:
        entered = crud.create_contact(db, email, phone)
        update_results(entered, resEmail=resEmail, resPhone=resPhone)
        return entered
    else:
        primary_row: Contact = identifiedRows[0]

    if email not in emails or phone not in phones:
        entered = crud.create_contact(db, email, phone, primary_row.id, "secondary")

        update_results(entered, resEmail= resEmail, resPhone=resPhone, resSecondaryIds=resSecondaryIds)
        update_results(primary_row, resEmail=resEmail, resPhone=resPhone)

        return entered
    
    update_results(primary_row, resEmail=resEmail, resPhone=resPhone)

    # if len(emails) == 0 or len(phones) == 0:
    #     entered = crud.create_contact(db, email, phone, primary_row.id, "Secondary")
    #     return []

    for i in identifiedRows:
        if i.id != primary_row.id:

            crud.update_contact(db, i.id, primary_row.id, "secondary")

            update_results(i, resEmail, resPhone, resSecondaryIds, selectedIds)


            update_rest_secondary(db, i.email, i.phoneNumber, primary_row.id, resEmail, resPhone, resSecondaryIds, selectedIds)
    return primary_row

@app.get('/')
def root():
    return {'message': 'all are working!'}

@app.post("/identify", response_model=ContactResponse)
def insert_test(data: IdentifyRequest, db: Session = Depends(get_db)):
    resEmail = []
    resPhone = []
    resSecondaryIds = []

    selectedIds = []

    if data.email == "" and data.phoneNumber == "":
        print("No data is given!!")
        return {
            "contact": {
                "primaryContactId": 0,
                "emails": resEmail,
                "phoneNumbers": resPhone,
                "secondaryContactIds": resSecondaryIds
            }
        }
    
    email = data.email
    phone = data.phoneNumber

    primary_row = update_first_secondary(db, email, phone, resEmail, resPhone, resSecondaryIds, selectedIds)

    return {
        "contact": {
            "primaryContactId": primary_row.id,
            "emails": resEmail,
            "phoneNumbers": resPhone,
            "secondaryContactIds": resSecondaryIds
        }
    }

@app.post("/testInsert")
def test_insert(data: Dict[str, TestInsert], db: Session = Depends(get_db)):
    for i in data.values():
        a = crud.create_contact(db, i.email, i.phoneNumber)

@app.post("/truncateTable")
def test_truncate():
    crud.truncate()