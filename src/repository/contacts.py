from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from src.entity.models import Contact
from src.schemas.contacts import ContactCreate
from src.schemas.users import UserResponse


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    # Create a new contact
    async def create(self, contact: Contact):
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    # Retrieve all contacts for the user
    async def get_all(self, user: UserResponse):
        result = await self.db.execute(
            select(Contact).where(Contact.user_id == user.id)
        )
        return result.scalars().all()

    # Retrieve a single contact by ID for the user
    async def get_by_id(self, contact_id: int, user: UserResponse):
        result = await self.db.execute(
            select(Contact).where(Contact.id == contact_id, Contact.user_id == user.id)
        )
        return result.scalar_one_or_none()

    # Update a contact for the user
    async def update(
        self, contact_id: int, updated_data: ContactCreate, user: UserResponse
    ):
        contact = await self.get_by_id(contact_id, user)
        if not contact:
            return None

        for key, value in updated_data.dict().items():
            setattr(contact, key, value)

        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    # Delete a contact for the user
    async def delete(self, contact_id: int, user: UserResponse):
        contact = await self.get_by_id(contact_id, user)
        if not contact:
            return None

        await self.db.delete(contact)
        await self.db.commit()
        return contact

    # Search contacts by name or email for the user
    async def search_contacts(self, query: str, user: UserResponse):
        stmt = select(Contact).where(
            Contact.user_id == user.id,
            or_(
                Contact.first_name.ilike(f"%{query}%"),
                Contact.last_name.ilike(f"%{query}%"),
                Contact.email.ilike(f"%{query}%"),
            ),
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # Get upcoming birthdays for the user
    async def get_upcoming_birthdays(self, user: UserResponse):
        today = datetime.today().date()
        next_week = today + timedelta(days=7)

        stmt = select(Contact).where(
            Contact.user_id == user.id,
            and_(Contact.birth_date >= today, Contact.birth_date <= next_week),
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
