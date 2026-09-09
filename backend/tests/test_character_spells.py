import pytest


@pytest.fixture
def character_id(client, auth_headers, character_payload):
    response = client.post("/characters", headers=auth_headers, json=character_payload)

    assert response.status_code == 201

    return response.json()["id"]


def test_character_starts_with_no_spells(client, auth_headers, character_id):
    response = client.get(f"/characters/{character_id}/spells", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_add_spell_to_character(client, auth_headers, character_id, test_spells):
    spell = test_spells[0]

    response = client.post(
        f"/characters/{character_id}/spells",
        headers=auth_headers,
        json={"spell_id": spell.id},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Magic Missile"

    listed = client.get(f"/characters/{character_id}/spells", headers=auth_headers)

    assert listed.status_code == 200
    assert [s["id"] for s in listed.json()] == [spell.id]


def test_add_same_spell_twice(client, auth_headers, character_id, test_spells):
    spell = test_spells[0]

    body = {"spell_id": spell.id}

    assert (
        client.post(
            f"/characters/{character_id}/spells",
            headers=auth_headers,
            json=body,
        ).status_code
        == 201
    )

    response = client.post(
        f"/characters/{character_id}/spells",
        headers=auth_headers,
        json=body,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Spell already added to character"


def test_add_unknown_spell(client, auth_headers, character_id):
    response = client.post(
        f"/characters/{character_id}/spells",
        headers=auth_headers,
        json={"spell_id": 999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Spell not found"


def test_add_spell_to_unknown_character(client, auth_headers, test_spells):
    response = client.post(
        "/characters/999/spells",
        headers=auth_headers,
        json={"spell_id": test_spells[0].id},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Character not found"


def test_remove_spell_from_character(client, auth_headers, character_id, test_spells):
    spell = test_spells[0]

    client.post(
        f"/characters/{character_id}/spells",
        headers=auth_headers,
        json={"spell_id": spell.id},
    )

    response = client.delete(
        f"/characters/{character_id}/spells/{spell.id}",
        headers=auth_headers,
    )

    assert response.status_code == 204
    assert response.content == b""

    listed = client.get(f"/characters/{character_id}/spells", headers=auth_headers)

    assert listed.json() == []


def test_remove_spell_the_character_does_not_know(
    client,
    auth_headers,
    character_id,
    test_spells,
):
    response = client.delete(
        f"/characters/{character_id}/spells/{test_spells[0].id}",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Spell not found for this character"


def test_remove_unknown_spell(client, auth_headers, character_id):
    response = client.delete(
        f"/characters/{character_id}/spells/999",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Spell not found"


def test_spell_endpoints_require_a_token(client, character_id, test_spells):
    spell_id = test_spells[0].id

    assert client.get(f"/characters/{character_id}/spells").status_code == 401
    assert (
        client.post(
            f"/characters/{character_id}/spells",
            json={"spell_id": spell_id},
        ).status_code
        == 401
    )
    assert (
        client.delete(f"/characters/{character_id}/spells/{spell_id}").status_code
        == 401
    )


def test_user_cannot_touch_another_users_character_spells(
    client,
    auth_headers,
    character_id,
    test_spells,
):
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

    headers = {"Authorization": f"Bearer {token}"}

    assert (
        client.get(
            f"/characters/{character_id}/spells",
            headers=headers,
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/characters/{character_id}/spells",
            headers=headers,
            json={"spell_id": test_spells[0].id},
        ).status_code
        == 404
    )


def test_deleting_a_character_with_spells(
    client,
    auth_headers,
    character_id,
    test_spells,
):
    """A character that knows spells must still be deletable (FK cleanup)."""
    client.post(
        f"/characters/{character_id}/spells",
        headers=auth_headers,
        json={"spell_id": test_spells[0].id},
    )

    response = client.delete(f"/characters/{character_id}", headers=auth_headers)

    assert response.status_code == 204
