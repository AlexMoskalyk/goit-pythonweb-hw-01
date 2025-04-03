import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
from sqlalchemy import select

from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactCreate
from src.schemas.users import UserResponse
from src.entity.models import Contact, User


@pytest.mark.asyncio
async def test_create_contact(override_get_db):
    # Create a test user first
    user = User(
        email="test@example.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(user)
    await override_get_db.commit()
    await override_get_db.refresh(user)

    # Create a user response object
    user_response = UserResponse(
        id=user.id, email=user.email, created_at=user.created_at
    )

    # Create a contact
    contact = Contact(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        birth_date=datetime.now(),
        additional_info="Test contact",
        user_id=user.id,
    )

    # Use the repository
    repo = ContactRepository(override_get_db)
    result = await repo.create(contact)

    assert result is not None
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.email == "john.doe@example.com"
    assert result.user_id == user.id


@pytest.mark.asyncio
async def test_get_all_contacts(override_get_db):
    # Create a test user first
    user = User(
        email="test@example.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(user)
    await override_get_db.commit()
    await override_get_db.refresh(user)

    # Create a user response object
    user_response = UserResponse(
        id=user.id, email=user.email, created_at=user.created_at
    )

    # Create multiple contacts
    contacts = [
        Contact(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890",
            birth_date=datetime.now(),
            additional_info="Test contact 1",
            user_id=user.id,
        ),
        Contact(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone_number="0987654321",
            birth_date=datetime.now(),
            additional_info="Test contact 2",
            user_id=user.id,
        ),
    ]

    for contact in contacts:
        override_get_db.add(contact)

    await override_get_db.commit()

    # Use the repository
    repo = ContactRepository(override_get_db)
    results = await repo.get_all(user_response)

    assert results is not None
    assert len(results) == 2
    emails = [c.email for c in results]
    assert "john.doe@example.com" in emails
    assert "jane.smith@example.com" in emails


@pytest.mark.asyncio
async def test_get_by_id(override_get_db):
    # Create a test user first
    user = User(
        email="test@example.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(user)
    await override_get_db.commit()
    await override_get_db.refresh(user)

    # Create a user response object
    user_response = UserResponse(
        id=user.id, email=user.email, created_at=user.created_at
    )

    # Create a contact
    contact = Contact(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        birth_date=datetime.now(),
        additional_info="Test contact",
        user_id=user.id,
    )

    override_get_db.add(contact)
    await override_get_db.commit()
    await override_get_db.refresh(contact)

    # Use the repository to get by ID
    repo = ContactRepository(override_get_db)
    result = await repo.get_by_id(contact.id, user_response)

    assert result is not None
    assert result.id == contact.id
    assert result.first_name == "John"
    assert result.email == "john.doe@example.com"

    # Test get_by_id with non-existent ID
    non_existent = await repo.get_by_id(9999, user_response)
    assert non_existent is None

    # Test get_by_id with wrong user
    other_user = UserResponse(
        id=user.id + 1, email="other@example.com", created_at=datetime.now()
    )

    other_result = await repo.get_by_id(contact.id, other_user)
    assert other_result is None


@pytest.mark.asyncio
async def test_update_contact(override_get_db):
    # Create a test user first
    user = User(
        email="test@example.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(user)
    await override_get_db.commit()
    await override_get_db.refresh(user)

    # Create a user response object
    user_response = UserResponse(
        id=user.id, email=user.email, created_at=user.created_at
    )

    # Create a contact
    contact = Contact(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        birth_date=datetime.now(),
        additional_info="Test contact",
        user_id=user.id,
    )

    override_get_db.add(contact)
    await override_get_db.commit()
    await override_get_db.refresh(contact)

    # Update data
    updated_data = ContactCreate(
        first_name="John-Updated",
        last_name="Doe-Updated",
        email="updated@example.com",
        phone_number="5555555555",
        birth_date=datetime.now(),
        additional_info="Updated info",
    )

    # Use the repository to update
    repo = ContactRepository(override_get_db)
    result = await repo.update(contact.id, updated_data, user_response)

    assert result is not None
    assert result.first_name == "John-Updated"
    assert result.last_name == "Doe-Updated"
    assert result.email == "updated@example.com"
    assert result.phone_number == "5555555555"

    # Test update with non-existent ID
    non_existent = await repo.update(9999, updated_data, user_response)
    assert non_existent is None

    # Test update with wrong user
    other_user = UserResponse(
        id=user.id + 1, email="other@example.com", created_at=datetime.now()
    )

    other_result = await repo.update(contact.id, updated_data, other_user)
    assert other_result is None


@pytest.mark.asyncio
async def test_delete_contact(override_get_db):
    # Create a test user first
    user = User(
        email="test@example.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(user)
    await override_get_db.commit()
    await override_get_db.refresh(user)

    # Create a user response object
    user_response = UserResponse(
        id=user.id, email=user.email, created_at=user.created_at
    )

    # Create a contact
    contact = Contact(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        birth_date=datetime.now(),
        additional_info="Test contact",
        user_id=user.id,
    )

    override_get_db.add(contact)
    await override_get_db.commit()
    await override_get_db.refresh(contact)

    # Use the repository to delete
    repo = ContactRepository(override_get_db)
    result = await repo.delete(contact.id, user_response)

    assert result is not None
    assert result.id == contact.id
    assert result.first_name == "John"

    # Verify contact is deleted
    stmt = select(Contact).where(Contact.id == contact.id)
    query_result = await override_get_db.execute(stmt)
    deleted_contact = query_result.scalar_one_or_none()
    assert deleted_contact is None

    # Test delete with non-existent ID
    non_existent = await repo.delete(9999, user_response)
    assert non_existent is None

    # Test delete with wrong user
    # Create another contact first
    another_contact = Contact(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
        phone_number="0987654321",
        birth_date=datetime.now(),
        additional_info="Test contact 2",
        user_id=user.id,
    )

    override_get_db.add(another_contact)
    await override_get_db.commit()
    await override_get_db.refresh(another_contact)

    other_user = UserResponse(
        id=user.id + 1, email="other@example.com", created_at=datetime.now()
    )

    other_result = await repo.delete(another_contact.id, other_user)
    assert other_result is None


@pytest.mark.asyncio
async def test_search_contacts(override_get_db):
    # Create a test user first
    user = User(
        email="test@example.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(user)
    await override_get_db.commit()
    await override_get_db.refresh(user)

    # Create a user response object
    user_response = UserResponse(
        id=user.id, email=user.email, created_at=user.created_at
    )

    # Create multiple contacts with different names
    contacts = [
        Contact(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890",
            birth_date=datetime.now(),
            additional_info="Test contact 1",
            user_id=user.id,
        ),
        Contact(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone_number="0987654321",
            birth_date=datetime.now(),
            additional_info="Test contact 2",
            user_id=user.id,
        ),
        Contact(
            first_name="Alice",
            last_name="Johnson",
            email="alice.johnson@example.com",
            phone_number="1122334455",
            birth_date=datetime.now(),
            additional_info="Test contact 3",
            user_id=user.id,
        ),
    ]

    for contact in contacts:
        override_get_db.add(contact)

    await override_get_db.commit()

    # Use the repository to search
    repo = ContactRepository(override_get_db)

    # Search by first name
    results_first_name = await repo.search_contacts("John", user_response)
    assert len(results_first_name) == 1
    assert results_first_name[0].first_name == "John"

    # Search by last name
    results_last_name = await repo.search_contacts("Smith", user_response)
    assert len(results_last_name) == 1
    assert results_last_name[0].last_name == "Smith"

    # Search by email
    results_email = await repo.search_contacts("alice", user_response)
    assert len(results_email) == 1
    assert results_email[0].first_name == "Alice"

    # Search with no results
    no_results = await repo.search_contacts("XYZ", user_response)
    assert len(no_results) == 0

    # Create a contact for another user
    another_user = User(
        email="another@example.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(another_user)
    await override_get_db.commit()
    await override_get_db.refresh(another_user)

    another_contact = Contact(
        first_name="Bob",
        last_name="Williams",
        email="bob.williams@example.com",
        phone_number="9876543210",
        birth_date=datetime.now(),
        additional_info="Another user's contact",
        user_id=another_user.id,
    )

    override_get_db.add(another_contact)
    await override_get_db.commit()

    # Search should not return another user's contacts
    results_with_other_user = await repo.search_contacts("Bob", user_response)
    assert len(results_with_other_user) == 0


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(override_get_db):
    # Create a test user first
    user = User(
        email="test@example.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(user)
    await override_get_db.commit()
    await override_get_db.refresh(user)

    # Create a user response object
    user_response = UserResponse(
        id=user.id, email=user.email, created_at=user.created_at
    )

    # Get the current date
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    last_week = today - timedelta(days=7)

    # Create contacts with different birthdays
    contacts = [
        Contact(
            first_name="Today",
            last_name="Birthday",
            email="today@example.com",
            phone_number="1111111111",
            birth_date=today,
            additional_info="Birthday today",
            user_id=user.id,
        ),
        Contact(
            first_name="Tomorrow",
            last_name="Birthday",
            email="tomorrow@example.com",
            phone_number="2222222222",
            birth_date=tomorrow,
            additional_info="Birthday tomorrow",
            user_id=user.id,
        ),
        Contact(
            first_name="NextWeek",
            last_name="Birthday",
            email="nextweek@example.com",
            phone_number="3333333333",
            birth_date=next_week,
            additional_info="Birthday next week",
            user_id=user.id,
        ),
        Contact(
            first_name="LastWeek",
            last_name="Birthday",
            email="lastweek@example.com",
            phone_number="4444444444",
            birth_date=last_week,
            additional_info="Birthday last week",
            user_id=user.id,
        ),
    ]

    for contact in contacts:
        override_get_db.add(contact)

    await override_get_db.commit()

    # Use the repository to get upcoming birthdays
    repo = ContactRepository(override_get_db)
    results = await repo.get_upcoming_birthdays(user_response)

    # Should include today, tomorrow, and next week birthdays
    assert len(results) >= 2  # At least today and tomorrow

    # Create a contact for another user with birthday today
    another_user = User(
        email="another@example.com", hashed_password="hashed_password", is_verified=True
    )
    override_get_db.add(another_user)
    await override_get_db.commit()
    await override_get_db.refresh(another_user)

    another_contact = Contact(
        first_name="Another",
        last_name="Birthday",
        email="another@example.com",
        phone_number="5555555555",
        birth_date=today,
        additional_info="Another user's birthday",
        user_id=another_user.id,
    )

    override_get_db.add(another_contact)
    await override_get_db.commit()

    # Results should not include another user's contact
    another_user_response = UserResponse(
        id=another_user.id, email=another_user.email, created_at=another_user.created_at
    )

    results_for_first_user = await repo.get_upcoming_birthdays(user_response)
    results_for_another_user = await repo.get_upcoming_birthdays(another_user_response)

    assert len(results_for_another_user) == 1
    assert results_for_another_user[0].first_name == "Another"

    # First user's results should not include "Another"
    assert all(contact.first_name != "Another" for contact in results_for_first_user)
