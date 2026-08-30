from models.user import User


def test_registration(client, db):
    response = client.post(
        "/users/registration",
        json={
            "email": "newuser@example.com",
            "nickname": "newuser",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "newuser@example.com"
    assert data["nickname"] == "newuser"
    assert data["role"] == "user"
    assert "password" not in data
    assert "password_hash" not in data

    user = db.query(User).filter(User.email == "newuser@example.com").first()

    assert user is not None

    db.delete(user)
    db.commit()


def test_registration_duplicate_email(client, test_user):
    response = client.post(
        "/users/registration",
        json={
            "email": test_user.email,
            "nickname": "another_user",
            "password": "password123",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"


def test_registration_duplicate_nickname(client, test_user):
    response = client.post(
        "/users/registration",
        json={
            "email": "another@example.com",
            "nickname": test_user.nickname,
            "password": "password123",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "User with this nickname already exists"


def test_login(client, test_user):
    response = client.post(
        "/users/login",
        data={
            "username": test_user.email,
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_login_wrong_password(client, test_user):
    response = client.post(
        "/users/login",
        data={
            "username": test_user.email,
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_admin_can_get_users(client, test_admin, test_user):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_admin.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_admin_can_get_user(client, test_admin, test_user):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_admin.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        f"/admin/users/{test_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == test_user.id
    assert data["email"] == "test@example.com"
    assert data["nickname"] == "testuser"


def test_admin_get_user_not_found(client, test_admin):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_admin.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/admin/users/999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_admin_can_update_user(client, test_admin, test_user):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_admin.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.patch(
        f"/admin/users/{test_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nickname": "updateduser",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == test_user.id
    assert data["nickname"] == "updateduser"
    assert data["email"] == "test@example.com"


def test_admin_cannot_update_user_with_existing_nickname(
    client,
    test_admin,
    test_user,
):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_admin.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.patch(
        f"/admin/users/{test_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nickname": "admin",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == ("User with this nickname already exists")


def test_admin_cannot_update_user_with_existing_email(
    client,
    test_admin,
    test_user,
):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_admin.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.patch(
        f"/admin/users/{test_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "admin@example.com",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == ("User with this email already exists")


def test_admin_can_delete_user(client, test_admin, test_user, db):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_admin.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.delete(
        f"/admin/users/{test_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204

    deleted_user = db.query(User).filter(User.id == test_user.id).first()

    assert deleted_user is None


def test_admin_delete_user_not_found(client, test_admin):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_admin.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.delete(
        "/admin/users/999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
