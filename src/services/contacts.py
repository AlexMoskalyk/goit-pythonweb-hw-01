from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Contact
from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactCreate
from src.schemas.users import UserResponse


class ContactService:
    """Service for contact management operations.

    Handles business logic for contact operations, sitting between
    the route handlers and repository.
    """

    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session.

        Args:
            db (AsyncSession): SQLAlchemy async session.
        """
        self.repository = ContactRepository(db)

    async def search_contacts(self, query: str, user: UserResponse):
        """Search for contacts by name or email.

        Args:
            query (str): Search string.
            user (UserResponse): Current user.

        Returns:
            list[Contact]: Matching contacts.
        """
        return await self.repository.search_contacts(query, user)

    async def create_contact(self, contact_data: ContactCreate, user: UserResponse):
        """Create a new contact for a user.

        Args:
            contact_data (ContactCreate): Contact data.
            user (UserResponse): Current user.

        Returns:
            Contact: Created contact.
        """
        new_contact = Contact(**contact_data.model_dump(), user_id=user.id)
        return await self.repository.create(new_contact)

    async def get_contacts(self, user: UserResponse):
        """Get all contacts for a user.

        Args:
            user (UserResponse): Current user.

        Returns:
            list[Contact]: All user's contacts.
        """
        return await self.repository.get_all(user)

    async def get_contact(self, contact_id: int, user: UserResponse):
        """Get a single contact by ID.

        Args:
            contact_id (int): Contact ID.
            user (UserResponse): Current user.

        Returns:
            Contact: Requested contact or None if not found.
        """
        return await self.repository.get_by_id(contact_id, user)

    async def update_contact(
        self, contact_id: int, updated_data: ContactCreate, user: UserResponse
    ):
        """Update a contact.

        Args:
            contact_id (int): Contact ID to update.
            updated_data (ContactCreate): New contact data.
            user (UserResponse): Current user.

        Returns:
            Contact: Updated contact or None if not found.
        """
        return await self.repository.update(contact_id, updated_data, user)

    async def delete_contact(self, contact_id: int, user: UserResponse):
        """Delete a contact.

        Args:
            contact_id (int): Contact ID to delete.
            user (UserResponse): Current user.

        Returns:
            Contact: Deleted contact or None if not found.
        """
        return await self.repository.delete(contact_id, user)

    async def get_upcoming_birthdays(self, user: UserResponse):
        """Get contacts with upcoming birthdays.

        Args:
            user (UserResponse): Current user.

        Returns:
            list[Contact]: Contacts with birthdays in the next 7 days.
        """
        return await self.repository.get_upcoming_birthdays(user)
