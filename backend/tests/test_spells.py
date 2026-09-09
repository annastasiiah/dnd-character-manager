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

    assert data["total"] == 2
    assert data["limit"] == 50
    assert data["offset"] == 0

    items = data["items"]

    assert len(items) == 2
    assert items[0]["name"] == "Magic Missile"
    assert items[0]["spell_range"] == "120 feet"


def test_get_spells_is_public(client):
    assert client.get("/spells").status_code == 200


def test_get_spells_pagination(client, test_spells):
    first = client.get("/spells", params={"limit": 1, "offset": 0}).json()

    assert first["total"] == 2
    assert [s["name"] for s in first["items"]] == ["Magic Missile"]

    second = client.get("/spells", params={"limit": 1, "offset": 1}).json()

    assert second["total"] == 2
    assert [s["name"] for s in second["items"]] == ["Shield"]


def test_get_spells_filter_by_school(client, test_spells):
    data = client.get("/spells", params={"school": "abjuration"}).json()

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Shield"


def test_get_spells_filter_by_level(client, test_spells):
    assert client.get("/spells", params={"level": 1}).json()["total"] == 2
    assert client.get("/spells", params={"level": 5}).json()["total"] == 0


def test_get_spells_search_by_name(client, test_spells):
    data = client.get("/spells", params={"search": "missile"}).json()

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Magic Missile"


def test_get_spells_rejects_a_silly_limit(client):
    assert client.get("/spells", params={"limit": 0}).status_code == 422
    assert client.get("/spells", params={"limit": 5000}).status_code == 422
    assert client.get("/spells", params={"offset": -1}).status_code == 422


def test_get_spell(client, test_spells):
    spell = test_spells[0]

    response = client.get(f"/spells/{spell.id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Magic Missile"


def test_get_spell_not_found(client):
    assert client.get("/spells/999").status_code == 404


def test_admin_can_create_spell(client, admin_headers):
    response = client.post("/spells", headers=admin_headers, json=SPELL_PAYLOAD)

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Fireball"
    assert data["level"] == 3
    assert data["id"] > 0

    listed = client.get("/spells").json()["items"]

    assert "Fireball" in [s["name"] for s in listed]


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


def test_admin_can_edit_spell(client, admin_headers, test_spells):
    spell = test_spells[0]

    response = client.patch(
        f"/spells/{spell.id}",
        headers=admin_headers,
        json={"level": 2},
    )

    assert response.status_code == 200
    assert response.json()["level"] == 2
    assert response.json()["name"] == "Magic Missile"


def test_edit_spell_with_taken_name(client, admin_headers, test_spells):
    response = client.patch(
        f"/spells/{test_spells[0].id}",
        headers=admin_headers,
        json={"name": "Shield"},
    )

    assert response.status_code == 409


def test_edit_spell_with_no_fields(client, admin_headers, test_spells):
    response = client.patch(
        f"/spells/{test_spells[0].id}",
        headers=admin_headers,
        json={},
    )

    assert response.status_code == 400


def test_edit_spell_not_found(client, admin_headers):
    response = client.patch("/spells/999", headers=admin_headers, json={"level": 2})

    assert response.status_code == 404


def test_edit_spell_requires_admin(client, auth_headers, test_spells):
    response = client.patch(
        f"/spells/{test_spells[0].id}",
        headers=auth_headers,
        json={"level": 2},
    )

    assert response.status_code == 403


def test_admin_can_delete_unknown_spell(client, admin_headers, test_spells):
    spell_id = test_spells[0].id

    assert (
        client.delete(f"/spells/{spell_id}", headers=admin_headers).status_code == 204
    )
    assert client.get(f"/spells/{spell_id}").status_code == 404


def test_delete_spell_known_by_a_character(
    client,
    admin_headers,
    auth_headers,
    character_payload,
    test_spells,
):
    character_id = client.post(
        "/characters", headers=auth_headers, json=character_payload
    ).json()["id"]

    spell_id = test_spells[0].id

    client.post(
        f"/characters/{character_id}/spells",
        headers=auth_headers,
        json={"spell_id": spell_id},
    )

    response = client.delete(f"/spells/{spell_id}", headers=admin_headers)

    assert response.status_code == 409
    assert response.json()["detail"] == "Spell is known by a character"


def test_delete_spell_not_found(client, admin_headers):
    assert client.delete("/spells/999", headers=admin_headers).status_code == 404


def test_delete_spell_requires_admin(client, auth_headers, test_spells):
    response = client.delete(f"/spells/{test_spells[0].id}", headers=auth_headers)

    assert response.status_code == 403
