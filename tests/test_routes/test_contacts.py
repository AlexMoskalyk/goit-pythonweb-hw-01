import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_create_contact(async_client, test_contact, mock_jwt):
    # Set auth header with mock token
    headers = {"Authorization": f"Bearer {mock_jwt}"}

    # Mock get_current_user to return a user
    with patch(
        "src.services.auth.get_current_user", new_callable=AsyncMock
    ) as mock_user:
        from src.entity.models import User

        mock_user.return_value = User(
            id=1,
            email="test@example.com",
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        response = await async_client.post(
            "/contacts/", json=test_contact, headers=headers
        )

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == test_contact["first_name"]
    assert data["last_name"] == test_contact["last_name"]
    assert data["email"] == test_contact["email"]
    assert data["user_id"] == 1


@pytest.mark.asyncio
async def test_get_contacts(async_client, test_contact, mock_jwt):
    # First create a contact
    headers = {"Authorization": f"Bearer {mock_jwt}"}

    # Mock get_current_user
    with patch(
        "src.services.auth.get_current_user", new_callable=AsyncMock
    ) as mock_user:
        from src.entity.models import User

        mock_user.return_value = User(
            id=1,
            email="test@example.com",
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        # Create a contact
        await async_client.post("/contacts/", json=test_contact, headers=headers)

        # Get all contacts
        response = await async_client.get("/contacts/", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["email"] == test_contact["email"]


@pytest.mark.asyncio
async def test_get_contact(async_client, test_contact, mock_jwt):
    # First create a contact
    headers = {"Authorization": f"Bearer {mock_jwt}"}

    # Mock get_current_user
    with patch(
        "src.services.auth.get_current_user", new_callable=AsyncMock
    ) as mock_user:
        from src.entity.models import User

        mock_user.return_value = User(
            id=1,
            email="test@example.com",
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        # Create a contact
        create_response = await async_client.post(
            "/contacts/", json=test_contact, headers=headers
        )
        contact_id = create_response.json()["id"]

        # Get the contact
        response = await async_client.get(f"/contacts/{contact_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == contact_id
    assert data["email"] == test_contact["email"]


@pytest.mark.asyncio
async def test_update_contact(async_client, test_contact, mock_jwt):
    # First create a contact
    headers = {"Authorization": f"Bearer {mock_jwt}"}

    # Mock get_current_user
    with patch(
        "src.services.auth.get_current_user", new_callable=AsyncMock
    ) as mock_user:
        from src.entity.models import User

        mock_user.return_value = User(
            id=1,
            email="test@example.com",
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        # Create a contact
        create_response = await async_client.post(
            "/contacts/", json=test_contact, headers=headers
        )
        contact_id = create_response.json()["id"]

        # Update the contact
        updated_data = test_contact.copy()
        updated_data["first_name"] = "Updated"
        response = await async_client.put(
            f"/contacts/{contact_id}", json=updated_data, headers=headers
        )

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_contact(async_client, test_contact, mock_jwt):
    # First create a contact
    headers = {"Authorization": f"Bearer {mock_jwt}"}

    # Mock get_current_user
    with patch(
        "src.services.auth.get_current_user", new_callable=AsyncMock
    ) as mock_user:
        from src.entity.models import User

        mock_user.return_value = User(
            id=1,
            email="test@example.com",
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        # Create a contact
        create_response = await async_client.post(
            "/contacts/", json=test_contact, headers=headers
        )
        contact_id = create_response.json()["id"]

        # Delete the contact
        response = await async_client.delete(f"/contacts/{contact_id}", headers=headers)

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_search_contacts(async_client, test_contact, mock_jwt):
    # First create a contact
    headers = {"Authorization": f"Bearer {mock_jwt}"}

    # Mock get_current_user
    with patch(
        "src.services.auth.get_current_user", new_callable=AsyncMock
    ) as mock_user:
        from src.entity.models import User

        mock_user.return_value = User(
            id=1,
            email="test@example.com",
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        # Create a contact
        await async_client.post("/contacts/", json=test_contact, headers=headers)

        # Search for contacts
        response = await async_client.get("/contacts/search?query=Doe", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["last_name"] == "Doe"


@pytest.mark.asyncio
async def test_upcoming_birthdays(async_client, test_contact, mock_jwt):
    # First create a contact with today's birthday
    headers = {"Authorization": f"Bearer {mock_jwt}"}

    # Mock get_current_user
    with patch(
        "src.services.auth.get_current_user", new_callable=AsyncMock
    ) as mock_user:
        from src.entity.models import User

        mock_user.return_value = User(
            id=1,
            email="test@example.com",
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        # Create a contact with birthday today
        today_contact = test_contact.copy()
        today_contact["birth_date"] = datetime.now().isoformat()
        await async_client.post("/contacts/", json=today_contact, headers=headers)

        # Get upcoming birthdays
        response = await async_client.get("/contacts/birthdays", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
