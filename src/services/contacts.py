from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from src.entity.models import Contact
from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactCreate


class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    #  Search contacts
    async def search_contacts(self, query: str):
        return await self.repository.search_contacts(query)

    #  Create a new contact
    async def create_contact(self, contact_data: ContactCreate):
        new_contact = Contact(**contact_data.model_dump())
        return await self.repository.create(new_contact)

    #  Retrieve all contacts
    async def get_contacts(self):
        return await self.repository.get_all()

    #  Retrieve a single contact by ID
    async def get_contact(self, contact_id: int):
        return await self.repository.get_by_id(contact_id)

    #  Update an existing contact
    async def update_contact(self, contact_id: int, updated_data: ContactCreate):
        return await self.repository.update(contact_id, updated_data)

    #  Delete a contact
    async def delete_contact(self, contact_id: int):
        return await self.repository.delete(contact_id)

    #  Retrieve contacts with upcoming birthdays
    async def get_upcoming_birthdays(self):
        return await self.repository.get_upcoming_birthdays()
