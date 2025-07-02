from sqlalchemy.orm import Session
from models import Contact

def get_contacts_by_email_or_phone(db: Session, email: str = None, phone: str = None):
    query = db.query(Contact)
    if email and phone:
        return query.filter((Contact.email == email) | (Contact.phoneNumber == phone)).all()
    elif email:
        return query.filter(Contact.email == email).all()
    elif phone:
        return query.filter(Contact.phoneNumber == phone).all()
    else:
        return []

def create_contact(db: Session, email: str, phone: str, linked_id=None, precedence="primary"):
    new_contact = Contact(
        email=email,
        phoneNumber=phone,
        linkedId=linked_id,
        linkPrecedence=precedence
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact
