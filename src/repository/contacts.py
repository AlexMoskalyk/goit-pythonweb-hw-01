from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from src.entity.models import Contact
from src.schemas.contacts import ContactCreate
from src.schemas.users import UserResponse


class ContactRepository:
    """Repository for contact data operations.

    Provides methods for CRUD operations on contacts,
    as well as search and filtering functionality.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the repository with a database session.

        Args:
            session (AsyncSession): SQLAlchemy async session.
        """
        self.db = session

    async def create(self, contact: Contact):
        """Create a new contact.

        Args:
            contact (Contact): Contact model to create.

        Returns:
            Contact: Created contact with ID and timestamps.
        """
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def get_all(self, user: UserResponse):
        """Retrieve all contacts for a user.

        Args:
            user (UserResponse): User to get contacts for.

        Returns:
            list[Contact]: List of all contacts belonging to the user.
        """
        result = await self.db.execute(
            select(Contact).where(Contact.user_id == user.id)
        )
        return result.scalars().all()

    async def get_by_id(self, contact_id: int, user: UserResponse):
        """Retrieve a single contact by ID for a specific user.

        Args:
            contact_id (int): ID of the contact to retrieve.
            user (UserResponse): User who owns the contact.

        Returns:
            Contact: The requested contact or None if not found.
        """
        result = await self.db.execute(
            select(Contact).where(Contact.id == contact_id, Contact.user_id == user.id)
        )
        return result.scalar_one_or_none()

    async def update(
        self, contact_id: int, updated_data: ContactCreate, user: UserResponse
    ):
        """Update a contact for a user.

        Args:
            contact_id (int): ID of the contact to update.
            updated_data (ContactCreate): New contact data.
            user (UserResponse): User who owns the contact.

        Returns:
            Contact: Updated contact or None if not found.
        """
        contact = await self.get_by_id(contact_id, user)
        if not contact:
            return None

        for key, value in updated_data.dict().items():
            setattr(contact, key, value)

        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def delete(self, contact_id: int, user: UserResponse):
        """Delete a contact for a user.

        Args:
            contact_id (int): ID of the contact to delete.
            user (UserResponse): User who owns the contact.

        Returns:
            Contact: Deleted contact or None if not found.
        """
        contact = await self.get_by_id(contact_id, user)
        if not contact:
            return None

        await self.db.delete(contact)
        await self.db.commit()
        return contact

    async def search_contacts(self, query: str, user: UserResponse):
        """Search contacts by name or email for a user.

        Args:
            query (str): Search string to match against first name, last name, or email.
            user (UserResponse): User who owns the contacts.

        Returns:
            list[Contact]: List of matching contacts.
        """
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

    async def get_upcoming_birthdays(self, user: UserResponse):
        """Get contacts with upcoming birthdays within the next week.

        Args:
            user (UserResponse): User who owns the contacts.

        Returns:
            list[Contact]: List of contacts with birthdays in the next 7 days.
        """
        today = datetime.today().date()
        next_week = today + timedelta(days=7)

        stmt = select(Contact).where(
            Contact.user_id == user.id,
            and_(Contact.birth_date >= today, Contact.birth_date <= next_week),
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
