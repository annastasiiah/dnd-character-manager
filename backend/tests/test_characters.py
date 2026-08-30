def test_create_character(client, test_user, test_races):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_user.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    race = test_races[0]

    response = client.post(
        "/characters",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Arwen",
            "race_id": race.id,
            "level": 5,
            "strength": 10,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 16,
            "wisdom": 13,
            "charisma": 15,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Arwen"
    assert data["race_id"] == race.id
    assert data["level"] == 5
    assert data["strength"] == 10
    assert data["charisma"] == 15

def test_get_characters(client, test_user, test_races):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_user.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    race = test_races[0]

    create_response = client.post(
        "/characters",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Arwen",
            "race_id": race.id,
            "level": 5,
            "strength": 10,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 16,
            "wisdom": 13,
            "charisma": 15,
        },
    )

    assert create_response.status_code == 200

    response = client.get(
        "/characters",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Arwen"
    assert data[0]["race_id"] == race.id
    assert data[0]["level"] == 5

def test_get_character(client, test_user, test_races):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_user.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    race = test_races[0]

    create_response = client.post(
        "/characters",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Arwen",
            "race_id": race.id,
            "level": 5,
            "strength": 10,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 16,
            "wisdom": 13,
            "charisma": 15,
        },
    )

    assert create_response.status_code == 200

    character_id = create_response.json()["id"]

    response = client.get(
        f"/characters/{character_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == character_id
    assert data["name"] == "Arwen"
    assert data["race_id"] == race.id
    assert data["level"] == 5

def test_user_cannot_get_another_users_character(
    client,
    test_user,
    test_races,
):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_user.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    race = test_races[0]

    create_response = client.post(
        "/characters",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Arwen",
            "race_id": race.id,
            "level": 5,
            "strength": 10,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 16,
            "wisdom": 13,
            "charisma": 15,
        },
    )

    assert create_response.status_code == 200

    character_id = create_response.json()["id"]

    registration_response = client.post(
        "/users/registration",
        json={
            "email": "another@example.com",
            "nickname": "anotheruser",
            "password": "password123",
        },
    )

    assert registration_response.status_code == 201

    second_login_response = client.post(
        "/users/login",
        data={
            "username": "another@example.com",
            "password": "password123",
        },
    )

    assert second_login_response.status_code == 200

    second_token = second_login_response.json()["access_token"]

    response = client.get(
        f"/characters/{character_id}",
        headers={
            "Authorization": f"Bearer {second_token}"
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Character not found"

def test_update_character(client, test_user, test_races):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_user.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]
    race = test_races[0]

    create_response = client.post(
        "/characters",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Arwen",
            "race_id": race.id,
            "level": 5,
            "strength": 10,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 16,
            "wisdom": 13,
            "charisma": 15,
        },
    )

    character_id = create_response.json()["id"]

    response = client.patch(
        f"/characters/{character_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Arwen Evenstar",
            "level": 10,
            "strength": 12,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == character_id
    assert data["name"] == "Arwen Evenstar"
    assert data["level"] == 10
    assert data["strength"] == 12

    assert data["dexterity"] == 14
    assert data["charisma"] == 15

def test_update_character_with_invalid_race(
    client,
    test_user,
    test_races,
):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_user.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]
    race = test_races[0]

    create_response = client.post(
        "/characters",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Arwen",
            "race_id": race.id,
            "level": 5,
            "strength": 10,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 16,
            "wisdom": 13,
            "charisma": 15,
        },
    )

    assert create_response.status_code == 200

    character_id = create_response.json()["id"]

    response = client.patch(
        f"/characters/{character_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "race_id": 999,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Race not found"

def test_delete_character(client, test_user, test_races):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_user.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]
    race = test_races[0]

    create_response = client.post(
        "/characters",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Arwen",
            "race_id": race.id,
            "level": 5,
            "strength": 10,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 16,
            "wisdom": 13,
            "charisma": 15,
        },
    )

    assert create_response.status_code == 200

    character_id = create_response.json()["id"]

    response = client.delete(
        f"/characters/{character_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/characters/{character_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Character not found"