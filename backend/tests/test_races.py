RACE_PAYLOAD = {
    "name": "Dwarf",
    "description": "Stout and hardy.",
    "speed": 25,
}


def test_get_races(client, test_races):
    response = client.get("/races")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Human"
    assert data[1]["name"] == "Elf"


def test_get_races_exposes_description_and_speed(client, test_races):
    """The race picker needs more than {id, name}."""
    human = client.get("/races").json()[0]

    assert human["description"] == "Test human"
    assert human["speed"] == 30


def test_get_race(client, test_races):
    elf = test_races[1]

    response = client.get(f"/races/{elf.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == elf.id
    assert data["name"] == "Elf"
    assert data["speed"] == 30
    assert data["description"] == "Test elf"


def test_get_race_not_found(client, test_races):
    response = client.get("/races/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Race not found"


def test_get_races_when_empty(client):
    response = client.get("/races")

    assert response.status_code == 200
    assert response.json() == []


def test_admin_can_create_race(client, admin_headers):
    response = client.post("/races", headers=admin_headers, json=RACE_PAYLOAD)

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Dwarf"
    assert data["description"] == "Stout and hardy."
    assert data["speed"] == 25

    assert "Dwarf" in [r["name"] for r in client.get("/races").json()]


def test_create_duplicate_race(client, admin_headers, test_races):
    response = client.post(
        "/races",
        headers=admin_headers,
        json={**RACE_PAYLOAD, "name": "Human"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Race already exists"


def test_create_race_requires_admin(client, auth_headers):
    response = client.post("/races", headers=auth_headers, json=RACE_PAYLOAD)

    assert response.status_code == 403


def test_create_race_requires_token(client):
    assert client.post("/races", json=RACE_PAYLOAD).status_code == 401


def test_create_race_validation(client, admin_headers):
    response = client.post(
        "/races",
        headers=admin_headers,
        json={**RACE_PAYLOAD, "speed": 0},
    )

    assert response.status_code == 422


def test_admin_can_edit_race(client, admin_headers, test_races):
    human = test_races[0]

    response = client.patch(
        f"/races/{human.id}",
        headers=admin_headers,
        json={"speed": 35},
    )

    assert response.status_code == 200
    assert response.json()["speed"] == 35
    assert response.json()["name"] == "Human"


def test_edit_race_with_taken_name(client, admin_headers, test_races):
    response = client.patch(
        f"/races/{test_races[0].id}",
        headers=admin_headers,
        json={"name": "Elf"},
    )

    assert response.status_code == 409


def test_edit_race_with_no_fields(client, admin_headers, test_races):
    response = client.patch(
        f"/races/{test_races[0].id}",
        headers=admin_headers,
        json={},
    )

    assert response.status_code == 400


def test_edit_race_not_found(client, admin_headers):
    response = client.patch("/races/999", headers=admin_headers, json={"speed": 25})

    assert response.status_code == 404


def test_edit_race_requires_admin(client, auth_headers, test_races):
    response = client.patch(
        f"/races/{test_races[0].id}",
        headers=auth_headers,
        json={"speed": 35},
    )

    assert response.status_code == 403


def test_admin_can_delete_unused_race(client, admin_headers, test_races):
    race_id = test_races[1].id

    assert client.delete(f"/races/{race_id}", headers=admin_headers).status_code == 204
    assert client.get(f"/races/{race_id}").status_code == 404


def test_delete_race_in_use(client, admin_headers, auth_headers, character_payload):
    assert (
        client.post(
            "/characters", headers=auth_headers, json=character_payload
        ).status_code
        == 201
    )

    response = client.delete(
        f"/races/{character_payload['race_id']}",
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Race is in use by a character"


def test_delete_race_not_found(client, admin_headers):
    assert client.delete("/races/999", headers=admin_headers).status_code == 404


def test_delete_race_requires_admin(client, auth_headers, test_races):
    response = client.delete(f"/races/{test_races[0].id}", headers=auth_headers)

    assert response.status_code == 403
