def test_get_me(client, auth_headers, test_user):
    response = client.get("/users/me", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == test_user.id
    assert data["email"] == "test@example.com"
    assert data["nickname"] == "testuser"
    assert data["role"] == "user"
    assert "password_hash" not in data


def test_get_me_without_token(client):
    assert client.get("/users/me").status_code == 401


def test_get_me_with_invalid_token(client):
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_get_me_with_non_numeric_subject(client, test_user):
    from security import create_access_token

    token = create_access_token({"sub": "not-an-int"})

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_get_me_with_token_for_deleted_user(client, db, test_user):
    from security import create_access_token

    token = create_access_token({"sub": str(test_user.id + 12345)})

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User not found"


def test_edit_me(client, auth_headers):
    response = client.patch(
        "/users/me",
        headers=auth_headers,
        json={"nickname": "renamed"},
    )

    assert response.status_code == 200
    assert response.json()["nickname"] == "renamed"

    assert client.get("/users/me", headers=auth_headers).json()["nickname"] == "renamed"


def test_edit_me_with_no_fields(client, auth_headers):
    response = client.patch("/users/me", headers=auth_headers, json={})

    assert response.status_code == 400
    assert response.json()["detail"] == "No fields to update"


def test_edit_me_with_taken_email(client, auth_headers, test_admin):
    response = client.patch(
        "/users/me",
        headers=auth_headers,
        json={"email": test_admin.email},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"


def test_edit_me_with_taken_nickname(client, auth_headers, test_admin):
    response = client.patch(
        "/users/me",
        headers=auth_headers,
        json={"nickname": test_admin.nickname},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "User with this nickname already exists"


def test_edit_me_keeping_own_email_is_not_a_conflict(client, auth_headers, test_user):
    response = client.patch(
        "/users/me",
        headers=auth_headers,
        json={"email": test_user.email},
    )

    assert response.status_code == 200


def test_user_cannot_promote_self_to_admin(client, auth_headers):
    """Regression: PATCH /users/me must not accept a role change."""
    response = client.patch(
        "/users/me",
        headers=auth_headers,
        json={"role": "admin"},
    )

    # `role` is not part of the self-update schema, so it is ignored and the
    # request has no updatable fields left.
    assert response.status_code == 400

    assert client.get("/users/me", headers=auth_headers).json()["role"] == "user"
    assert client.get("/admin/users", headers=auth_headers).status_code == 403


def test_user_cannot_smuggle_role_alongside_a_valid_field(client, auth_headers):
    response = client.patch(
        "/users/me",
        headers=auth_headers,
        json={"nickname": "sneaky", "role": "admin"},
    )

    assert response.status_code == 200
    assert response.json()["nickname"] == "sneaky"
    assert response.json()["role"] == "user"

    assert client.get("/admin/users", headers=auth_headers).status_code == 403


def test_change_own_password(client, auth_headers, test_user):
    response = client.patch(
        "/users/me",
        headers=auth_headers,
        json={"password": "brand-new-password", "current_password": "password123"},
    )

    assert response.status_code == 200
    assert "password" not in response.json()
    assert "password_hash" not in response.json()

    # The old password stops working and the new one starts working.
    assert (
        client.post(
            "/users/login",
            data={"username": test_user.email, "password": "password123"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/users/login",
            data={"username": test_user.email, "password": "brand-new-password"},
        ).status_code
        == 200
    )


def test_change_password_with_wrong_current_password(client, auth_headers, test_user):
    response = client.patch(
        "/users/me",
        headers=auth_headers,
        json={"password": "brand-new-password", "current_password": "not-it"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Current password is incorrect"

    assert (
        client.post(
            "/users/login",
            data={"username": test_user.email, "password": "password123"},
        ).status_code
        == 200
    )


def test_change_password_without_current_password(client, auth_headers):
    response = client.patch(
        "/users/me",
        headers=auth_headers,
        json={"password": "brand-new-password"},
    )

    assert response.status_code == 422


def test_change_password_below_minimum_length(client, auth_headers):
    response = client.patch(
        "/users/me",
        headers=auth_headers,
        json={"password": "short", "current_password": "password123"},
    )

    assert response.status_code == 422


def test_change_password_alongside_another_field(client, auth_headers, test_user):
    response = client.patch(
        "/users/me",
        headers=auth_headers,
        json={
            "nickname": "renamed",
            "password": "brand-new-password",
            "current_password": "password123",
        },
    )

    assert response.status_code == 200
    assert response.json()["nickname"] == "renamed"

    assert (
        client.post(
            "/users/login",
            data={"username": test_user.email, "password": "brand-new-password"},
        ).status_code
        == 200
    )
