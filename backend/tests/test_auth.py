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

    user = db.query(User).filter(
        User.email == "newuser@example.com"
    ).first()

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