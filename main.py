from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import extract
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from conf.database import engine, async_session, get_db
from conf.models import Base, Contact
from shemas import ContactBase, ContactCreate, Contact


app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


@app.post("/contacts/", response_model=Contact)
async def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact

@app.get("/contacts/", response_model=List[Contact])
async def read_contacts(search: Optional[str] = None, db: Session = Depends(get_db)):
    if search:
        stmt = select(Contact).where(
            Contact.first_name.ilike(f"%{search}%") |
            Contact.last_name.ilike(f"%{search}%") |
            Contact.email.ilike(f"%{search}%")
        )
    else:
        stmt = select(Contact)
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    return contacts

@app.get("/contacts/{contact_id}", response_model=Contact)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    db_contact = result.scalar_one_or_none()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.put("/contacts/{contact_id}", response_model=Contact)
async def update_contact(contact_id: int, contact: ContactCreate, db: Session = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    db_contact = result.scalar_one_or_none()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    for key, value in contact.dict().items():
        setattr(db_contact, key, value)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact

@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    db_contact = result.scalar_one_or_none()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    await db.delete(db_contact)
    await db.commit()
    return {"ok": True}

@app.get("/contacts/birthdays/", response_model=List[Contact])
async def get_upcoming_birthdays(db: Session = Depends(get_db)):
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    stmt = select(Contact).where(
        (extract('month', Contact.birthday) == today.month & extract('day', Contact.birthday) >= today.day) |
        (extract('month', Contact.birthday) == next_week.month & extract('day', Contact.birthday) < today.day)
    )
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    return contacts

