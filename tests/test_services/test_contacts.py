import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from src.services.contacts import ContactService
from src.schemas.contacts import ContactCreate
from src.schemas.users import UserResponse


@pytest.mark.asyncio
async def test_create_contact(override_get_db):
    # Create a mock repository
    mock_repo = AsyncMock()
    mock_repo.create.return_value = MagicMock(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        birth_date=datetime.now(),
        additional_info="Test contact",
        user_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Create a mock user
    user = UserResponse(
        id=1, email="test@example.com", created_at=datetime.now(), avatar_url=None
    )

    # Create the service with the mock repo
    with patch("src.repository.contacts.ContactRepository", return_value=mock_repo):
        service = ContactService(override_get_db)

        # Create contact data
        contact_data = ContactCreate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890",
            birth_date=datetime.now(),
            additional_info="Test contact",
        )

        # Create the contact
        result = await service.create_contact(contact_data, user)

    # Assertions
    assert result is not None
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.email == "john.doe@example.com"
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_contacts(override_get_db):
    # Create mock contacts
    mock_contacts = [
        MagicMock(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890",
            birth_date=datetime.now(),
            additional_info="Test contact",
            user_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        MagicMock(
            id=2,
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone_number="0987654321",
            birth_date=datetime.now(),
            additional_info="Another test contact",
            user_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]

    # Create a mock repository
    mock_repo = AsyncMock()
    mock_repo.get_all.return_value = mock_contacts

    # Create a mock user
    user = UserResponse(
        id=1, email="test@example.com", created_at=datetime.now(), avatar_url=None
    )

    # Create the service with the mock repo
    with patch("src.repository.contacts.ContactRepository", return_value=mock_repo):
        service = ContactService(override_get_db)

        # Get all contacts
        result = await service.get_contacts(user)

    # Assertions
    assert result is not None
    assert len(result) == 2
    assert result[0].first_name == "John"
    assert result[1].first_name == "Jane"
    mock_repo.get_all.assert_called_once_with(user)


@pytest.mark.asyncio
async def test_get_contact(override_get_db):
    # Create a mock contact
    mock_contact = MagicMock(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        birth_date=datetime.now(),
        additional_info="Test contact",
        user_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Create a mock repository
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = mock_contact

    # Create a mock user
    user = UserResponse(
        id=1, email="test@example.com", created_at=datetime.now(), avatar_url=None
    )

    # Create the service with the mock repo
    with patch("src.repository.contacts.ContactRepository", return_value=mock_repo):
        service = ContactService(override_get_db)

        # Get the contact
        result = await service.get_contact(1, user)

    # Assertions
    assert result is not None
    assert result.id == 1
    assert result.first_name == "John"
    assert result.email == "john.doe@example.com"
    mock_repo.get_by_id.assert_called_once_with(1, user)


@pytest.mark.asyncio
async def test_update_contact(override_get_db):
    # Create a mock updated contact
    mock_updated_contact = MagicMock(
        id=1,
        first_name="John-Updated",
        last_name="Doe-Updated",
        email="john.updated@example.com",
        phone_number="1234567890",
        birth_date=datetime.now(),
        additional_info="Updated test contact",
        user_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Create a mock repository
    mock_repo = AsyncMock()
    mock_repo.update.return_value = mock_updated_contact

    # Create a mock user
    user = UserResponse(
        id=1, email="test@example.com", created_at=datetime.now(), avatar_url=None
    )

    # Create the service with the mock repo
    with patch("src.repository.contacts.ContactRepository", return_value=mock_repo):
        service = ContactService(override_get_db)

        # Update data
        updated_data = ContactCreate(
            first_name="John-Updated",
            last_name="Doe-Updated",
            email="john.updated@example.com",
            phone_number="1234567890",
            birth_date=datetime.now(),
            additional_info="Updated test contact",
        )

        # Update the contact
        result = await service.update_contact(1, updated_data, user)

    # Assertions
    assert result is not None
    assert result.first_name == "John-Updated"
    assert result.last_name == "Doe-Updated"
    assert result.email == "john.updated@example.com"
    mock_repo.update.assert_called_once_with(1, updated_data, user)


@pytest.mark.asyncio
async def test_delete_contact(override_get_db):
    # Create a mock contact to delete
    mock_deleted_contact = MagicMock(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        user_id=1,
    )

    # Create a mock repository
    mock_repo = AsyncMock()
    mock_repo.delete.return_value = mock_deleted_contact

    # Create a mock user
    user = UserResponse(
        id=1, email="test@example.com", created_at=datetime.now(), avatar_url=None
    )

    # Create the service with the mock repo
    with patch("src.repository.contacts.ContactRepository", return_value=mock_repo):
        service = ContactService(override_get_db)

        # Delete the contact
        result = await service.delete_contact(1, user)

    # Assertions
    assert result is not None
    assert result.id == 1
    assert result.first_name == "John"
    mock_repo.delete.assert_called_once_with(1, user)


@pytest.mark.asyncio
async def test_search_contacts(override_get_db):
    # Create mock search results
    mock_results = [
        MagicMock(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890",
            birth_date=datetime.now(),
            additional_info="Test contact",
            user_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
    ]

    # Create a mock repository
    mock_repo = AsyncMock()
    mock_repo.search_contacts.return_value = mock_results

    # Create a mock user
    user = UserResponse(
        id=1, email="test@example.com", created_at=datetime.now(), avatar_url=None
    )

    # Create the service with the mock repo
    with patch("src.repository.contacts.ContactRepository", return_value=mock_repo):
        service = ContactService(override_get_db)

        # Search for contacts
        result = await service.search_contacts("Doe", user)

    # Assertions
    assert result is not None
    assert len(result) == 1
    assert result[0].last_name == "Doe"
    mock_repo.search_contacts.assert_called_once_with("Doe", user)


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(override_get_db):
    # Create mock upcoming birthdays
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    mock_birthdays = [
        MagicMock(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890",
            birth_date=today,
            additional_info="Test contact",
            user_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        MagicMock(
            id=2,
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone_number="0987654321",
            birth_date=tomorrow,
            additional_info="Another test contact",
            user_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]

    # Create a mock repository
    mock_repo = AsyncMock()
    mock_repo.get_upcoming_birthdays.return_value = mock_birthdays

    # Create a mock user
    user = UserResponse(
        id=1, email="test@example.com", created_at=datetime.now(), avatar_url=None
    )

    # Create the service with the mock repo
    with patch("src.repository.contacts.ContactRepository", return_value=mock_repo):
        service = ContactService(override_get_db)

        # Get upcoming birthdays
        result = await service.get_upcoming_birthdays(user)

    # Assertions
    assert result is not None
    assert len(result) == 2
    assert result[0].first_name == "John"
    assert result[1].first_name == "Jane"
    mock_repo.get_upcoming_birthdays.assert_called_once_with(user)
