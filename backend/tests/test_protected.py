def test_get_characters_without_token(client):
    response = client.get("/characters")

    assert response.status_code == 401


def test_get_characters_with_token(client, test_user):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_user.email,
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/characters",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == []
