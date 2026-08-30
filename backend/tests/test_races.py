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