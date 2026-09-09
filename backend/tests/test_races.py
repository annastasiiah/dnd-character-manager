def test_get_races(client, test_races):
    response = client.get("/races")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Human"
    assert data[1]["name"] == "Elf"


def test_get_race(client, test_races):
    elf = test_races[1]

    response = client.get(f"/races/{elf.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == elf.id
    assert data["name"] == "Elf"
    assert data["speed"] == 30


def test_get_race_not_found(client, test_races):
    response = client.get("/races/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Race not found"


RACE_PAYLOAD = {
    "name": "Dwarf",
    "description": "Stout and hardy.",
    "speed": 25,
}


def test_get_races_when_empty(client):
    response = client.get("/races")

    assert response.status_code == 200
    assert response.json() == []


def test_admin_can_create_race(client, admin_headers):
    response = client.post("/race", headers=admin_headers, json=RACE_PAYLOAD)

    assert response.status_code == 200
    assert response.json()["name"] == "Dwarf"

    assert "Dwarf" in [r["name"] for r in client.get("/races").json()]


def test_create_duplicate_race(client, admin_headers, test_races):
    response = client.post(
        "/race",
        headers=admin_headers,
        json={**RACE_PAYLOAD, "name": "Human"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Race already exists"


def test_create_race_requires_admin(client, auth_headers):
    response = client.post("/race", headers=auth_headers, json=RACE_PAYLOAD)

    assert response.status_code == 403


def test_create_race_requires_token(client):
    assert client.post("/race", json=RACE_PAYLOAD).status_code == 401


def test_create_race_validation(client, admin_headers):
    response = client.post(
        "/race",
        headers=admin_headers,
        json={**RACE_PAYLOAD, "speed": 0},
    )

    assert response.status_code == 422
