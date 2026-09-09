def create_character(client, headers, payload, **overrides):
    return client.post("/characters", headers=headers, json={**payload, **overrides})


def test_create_character(client, auth_headers, character_payload):
    response = create_character(client, auth_headers, character_payload)

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Arwen"
    assert data["race_id"] == character_payload["race_id"]
    assert data["class_id"] == character_payload["class_id"]
    assert data["background_id"] == character_payload["background_id"]
    assert data["level"] == 5
    assert data["strength"] == 10
    assert data["charisma"] == 15


def test_create_character_with_unknown_race(client, auth_headers, character_payload):
    response = create_character(client, auth_headers, character_payload, race_id=999)

    assert response.status_code == 404
    assert response.json()["detail"] == "Race not found"


def test_create_character_with_unknown_class(client, auth_headers, character_payload):
    response = create_character(client, auth_headers, character_payload, class_id=999)

    assert response.status_code == 404
    assert response.json()["detail"] == "Character class not found"


def test_create_character_with_unknown_background(
    client,
    auth_headers,
    character_payload,
):
    response = create_character(
        client,
        auth_headers,
        character_payload,
        background_id=999,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Background not found"


def test_get_characters(client, auth_headers, character_payload):
    assert create_character(client, auth_headers, character_payload).status_code == 201

    response = client.get("/characters", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Arwen"
    assert data[0]["race_id"] == character_payload["race_id"]
    assert data[0]["level"] == 5


def test_get_character(client, auth_headers, character_payload):
    create_response = create_character(client, auth_headers, character_payload)

    assert create_response.status_code == 201

    character_id = create_response.json()["id"]

    response = client.get(f"/characters/{character_id}", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == character_id
    assert data["name"] == "Arwen"
    assert data["level"] == 5


def test_get_character_not_found(client, auth_headers):
    response = client.get("/characters/999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Character not found"


def test_user_cannot_get_another_users_character(
    client,
    auth_headers,
    character_payload,
):
    create_response = create_character(client, auth_headers, character_payload)

    assert create_response.status_code == 201

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
        headers={"Authorization": f"Bearer {second_token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Character not found"


def test_update_character(client, auth_headers, character_payload):
    create_response = create_character(client, auth_headers, character_payload)

    character_id = create_response.json()["id"]

    response = client.patch(
        f"/characters/{character_id}",
        headers=auth_headers,
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


def test_update_character_reference_fields(
    client,
    auth_headers,
    character_payload,
    test_races,
    test_classes,
    test_backgrounds,
):
    create_response = create_character(client, auth_headers, character_payload)

    character_id = create_response.json()["id"]

    response = client.patch(
        f"/characters/{character_id}",
        headers=auth_headers,
        json={
            "race_id": test_races[1].id,
            "class_id": test_classes[1].id,
            "background_id": test_backgrounds[1].id,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["race_id"] == test_races[1].id
    assert data["class_id"] == test_classes[1].id
    assert data["background_id"] == test_backgrounds[1].id


def test_update_character_with_no_fields(client, auth_headers, character_payload):
    create_response = create_character(client, auth_headers, character_payload)

    character_id = create_response.json()["id"]

    response = client.patch(
        f"/characters/{character_id}",
        headers=auth_headers,
        json={},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "No fields to update"


def test_update_character_with_invalid_race(client, auth_headers, character_payload):
    create_response = create_character(client, auth_headers, character_payload)

    assert create_response.status_code == 201

    character_id = create_response.json()["id"]

    response = client.patch(
        f"/characters/{character_id}",
        headers=auth_headers,
        json={"race_id": 999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Race not found"


def test_update_character_with_invalid_class(client, auth_headers, character_payload):
    create_response = create_character(client, auth_headers, character_payload)

    character_id = create_response.json()["id"]

    response = client.patch(
        f"/characters/{character_id}",
        headers=auth_headers,
        json={"class_id": 999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Class not found"


def test_update_character_with_invalid_background(
    client,
    auth_headers,
    character_payload,
):
    create_response = create_character(client, auth_headers, character_payload)

    character_id = create_response.json()["id"]

    response = client.patch(
        f"/characters/{character_id}",
        headers=auth_headers,
        json={"background_id": 999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Background not found"


def test_user_cannot_update_another_users_character(
    client,
    auth_headers,
    character_payload,
):
    character_id = create_character(
        client,
        auth_headers,
        character_payload,
    ).json()["id"]

    client.post(
        "/users/registration",
        json={
            "email": "another@example.com",
            "nickname": "anotheruser",
            "password": "password123",
        },
    )

    token = client.post(
        "/users/login",
        data={"username": "another@example.com", "password": "password123"},
    ).json()["access_token"]

    response = client.patch(
        f"/characters/{character_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Stolen"},
    )

    assert response.status_code == 404


def test_delete_character(client, auth_headers, character_payload):
    create_response = create_character(client, auth_headers, character_payload)

    assert create_response.status_code == 201

    character_id = create_response.json()["id"]

    response = client.delete(f"/characters/{character_id}", headers=auth_headers)

    assert response.status_code == 204

    get_response = client.get(f"/characters/{character_id}", headers=auth_headers)

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Character not found"


def test_user_cannot_delete_another_users_character(
    client,
    auth_headers,
    character_payload,
):
    character_id = create_character(
        client,
        auth_headers,
        character_payload,
    ).json()["id"]

    client.post(
        "/users/registration",
        json={
            "email": "another@example.com",
            "nickname": "anotheruser",
            "password": "password123",
        },
    )

    token = client.post(
        "/users/login",
        data={"username": "another@example.com", "password": "password123"},
    ).json()["access_token"]

    response = client.delete(
        f"/characters/{character_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_create_character_validation(client, auth_headers, character_payload):
    response = create_character(client, auth_headers, character_payload, level=21)

    assert response.status_code == 422


def test_create_character_with_ability_score_below_min(
    client,
    auth_headers,
    character_payload,
):
    response = create_character(client, auth_headers, character_payload, strength=0)

    assert response.status_code == 422


def test_create_character_with_ability_score_above_max(
    client,
    auth_headers,
    character_payload,
):
    response = create_character(client, auth_headers, character_payload, strength=31)

    assert response.status_code == 422


def test_update_character_validation(client, auth_headers, character_payload):
    create_response = create_character(client, auth_headers, character_payload)

    assert create_response.status_code == 201

    character_id = create_response.json()["id"]

    response = client.patch(
        f"/characters/{character_id}",
        headers=auth_headers,
        json={"level": 21},
    )

    assert response.status_code == 422


def test_character_response_expands_reference_data(
    client,
    auth_headers,
    character_payload,
    test_races,
    test_classes,
    test_backgrounds,
):
    """The client should not need three extra fetches to render a character."""
    data = create_character(client, auth_headers, character_payload).json()

    assert data["race"]["id"] == test_races[0].id
    assert data["race"]["name"] == "Human"
    assert data["race"]["speed"] == 30

    assert data["character_class"]["id"] == test_classes[0].id
    assert data["character_class"]["name"] == "Wizard"

    assert data["background"]["id"] == test_backgrounds[0].id
    assert data["background"]["name"] == "Sage"

    # The raw ids stay, so an edit form can round-trip them.
    assert data["race_id"] == test_races[0].id
    assert data["class_id"] == test_classes[0].id
    assert data["background_id"] == test_backgrounds[0].id


def test_character_list_expands_reference_data(client, auth_headers, character_payload):
    create_character(client, auth_headers, character_payload)

    listed = client.get("/characters", headers=auth_headers).json()

    assert listed[0]["race"]["name"] == "Human"
    assert listed[0]["character_class"]["name"] == "Wizard"
    assert listed[0]["background"]["name"] == "Sage"


def test_updating_a_reference_id_updates_the_expanded_object(
    client,
    auth_headers,
    character_payload,
    test_races,
):
    character_id = create_character(client, auth_headers, character_payload).json()[
        "id"
    ]

    response = client.patch(
        f"/characters/{character_id}",
        headers=auth_headers,
        json={"race_id": test_races[1].id},
    )

    assert response.status_code == 200
    assert response.json()["race"]["name"] == "Elf"
