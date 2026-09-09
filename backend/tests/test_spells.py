SPELL_PAYLOAD = {
    "name": "Fireball",
    "level": 3,
    "school": "Evocation",
    "casting_time": "1 action",
    "spell_range": "150 feet",
    "duration": "Instantaneous",
    "description": "A bright streak flashes to a point you choose.",
}


def test_get_spells(client, test_spells):
    response = client.get("/spells")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Magic Missile"
    assert data[0]["spell_range"] == "120 feet"


def test_get_spells_is_public(client):
    assert client.get("/spells").status_code == 200


def test_admin_can_create_spell(client, admin_headers):
    response = client.post("/spells", headers=admin_headers, json=SPELL_PAYLOAD)

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Fireball"
    assert data["level"] == 3
    assert data["id"] > 0

    assert "Fireball" in [s["name"] for s in client.get("/spells").json()]


def test_create_duplicate_spell(client, admin_headers, test_spells):
    response = client.post(
        "/spells",
        headers=admin_headers,
        json={**SPELL_PAYLOAD, "name": "Magic Missile"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Spell already exists"


def test_create_spell_requires_admin(client, auth_headers):
    response = client.post("/spells", headers=auth_headers, json=SPELL_PAYLOAD)

    assert response.status_code == 403


def test_create_spell_requires_token(client):
    assert client.post("/spells", json=SPELL_PAYLOAD).status_code == 401


def test_create_spell_validation(client, admin_headers):
    response = client.post(
        "/spells",
        headers=admin_headers,
        json={**SPELL_PAYLOAD, "level": -1},
    )

    assert response.status_code == 422
