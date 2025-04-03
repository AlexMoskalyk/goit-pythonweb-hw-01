from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.contacts import ContactCreate, ContactResponse
from src.schemas.users import UserResponse
from src.services.contacts import ContactService
from src.services.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Create a new contact.

    Creates a new contact entry in the database for the authenticated user.

    Args:
        contact (ContactCreate): Contact data to create.
        db (AsyncSession): Database session.
        current_user (UserResponse): Authenticated user.

    Returns:
        ContactResponse: Created contact object.
    """
    service = ContactService(db)
    return await service.create_contact(contact, current_user)


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve all contacts for the current user.

    Args:
        db (AsyncSession): Database session.
        current_user (UserResponse): Authenticated user.

    Returns:
        list[ContactResponse]: List of contacts belonging to the user.
    """
    service = ContactService(db)
    return await service.get_contacts(current_user)


@router.get("/search", response_model=list[ContactResponse])
async def search_contacts(
    query: str = Query(..., description="Search by name or email"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Search contacts by name or email.

    Args:
        query (str): Search string to match against name or email.
        db (AsyncSession): Database session.
        current_user (UserResponse): Authenticated user.

    Returns:
        list[ContactResponse]: List of matching contacts.
    """
    service = ContactService(db)
    return await service.search_contacts(query, current_user)


@router.get("/birthdays", response_model=list[ContactResponse])
async def get_upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve contacts with upcoming birthdays.

    Fetches contacts with birthdays in the next 7 days.

    Args:
        db (AsyncSession): Database session.
        current_user (UserResponse): Authenticated user.

    Returns:
        list[ContactResponse]: List of contacts with upcoming birthdays.
    """
    service = ContactService(db)
    return await service.get_upcoming_birthdays(current_user)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve a single contact by ID.

    Args:
        contact_id (int): ID of the contact to retrieve.
        db (AsyncSession): Database session.
        current_user (UserResponse): Authenticated user.

    Returns:
        ContactResponse: The requested contact.

    Raises:
        HTTPException: 404 if contact not found.
    """
    service = ContactService(db)
    contact = await service.get_contact(contact_id, current_user)

    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    updated_data: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Update an existing contact.

    Args:
        contact_id (int): ID of the contact to update.
        updated_data (ContactCreate): New contact data.
        db (AsyncSession): Database session.
        current_user (UserResponse): Authenticated user.

    Returns:
        ContactResponse: Updated contact.

    Raises:
        HTTPException: 404 if contact not found.
    """
    service = ContactService(db)
    contact = await service.update_contact(contact_id, updated_data, current_user)

    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Delete a contact.

    Args:
        contact_id (int): ID of the contact to delete.
        db (AsyncSession): Database session.
        current_user (UserResponse): Authenticated user.

    Returns:
        None: No content on success.

    Raises:
        HTTPException: 404 if contact not found.
    """
    service = ContactService(db)
    contact = await service.delete_contact(contact_id, current_user)

    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    return None
