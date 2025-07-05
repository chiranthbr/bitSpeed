from sqlalchemy.orm import Session
from models import Contact
from datetime import datetime
import database
from sqlalchemy.sql import text

def get_contacts_by_email_and_phone(db: Session, email: str = None, phone: str = None):
    queryResult = db.query(Contact).filter((Contact.email == email) | (Contact.phoneNumber == phone)).all()
    return queryResult


def create_contact(db: Session, email: str, phone: str, linked_id: int = None, precedence = "primary"):
    new_contact = Contact(
        email=email,
        phoneNumber=phone,
        linkedId=linked_id,
        linkPrecedence=precedence,
        createdAt=datetime.now(),
        updatedAt=datetime.now()
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

def update_contact(db: Session, id: int, linked_id: int, linkedPrecedence: str):
    data = db.query(Contact).filter(Contact.id == id).first()
    if data:
        data.linkedId = linked_id
        data.linkPrecedence = linkedPrecedence
        data.updatedAt = datetime.now()
    db.commit()
    db.refresh(data)

def truncate():
    with database.engine.connect() as connection:
        connection.execute(text(f"TRUNCATE TABLE Contact;").execution_options(autocommit = True))
        return "Truncated!"