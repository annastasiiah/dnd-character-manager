"""Classes and backgrounds: the reference data behind the character form."""

import pytest

RESOURCES = [
    ("classes", "test_classes", "Wizard", "Class"),
    ("backgrounds", "test_backgrounds", "Sage", "Background"),
]


@pytest.fixture
def seeded(request, resource):
    """Load whichever conftest fixture seeds this resource."""
    _, fixture_name, _, _ = next(r for r in RESOURCES if r[0] == resource)

    return request.getfixturevalue(fixture_name)


@pytest.fixture(params=[r[0] for r in RESOURCES])
def resource(request):
    return request.param


@pytest.fixture
def first_name(resource):
    return next(r[2] for r in RESOURCES if r[0] == resource)


@pytest.fixture
def label(resource):
    return next(r[3] for r in RESOURCES if r[0] == resource)


def test_list_has_no_trailing_slash(client, resource, seeded, first_name):
    """A bare `/classes` must answer directly, not 307 to `/classes/`."""
    response = client.get(f"/{resource}", follow_redirects=False)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == first_name


def test_list_is_public(client, resource):
    assert client.get(f"/{resource}").status_code == 200


def test_get_one(client, resource, seeded, first_name):
    response = client.get(f"/{resource}/{seeded[0].id}")

    assert response.status_code == 200
    assert response.json()["name"] == first_name


def test_get_one_not_found(client, resource, label):
    response = client.get(f"/{resource}/999")

    assert response.status_code == 404
    assert response.json()["detail"] == f"{label} not found"


def test_admin_can_create(client, admin_headers, resource):
    response = client.post(
        f"/{resource}", headers=admin_headers, json={"name": "Homebrew"}
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Homebrew"

    assert "Homebrew" in [item["name"] for item in client.get(f"/{resource}").json()]


def test_create_duplicate(client, admin_headers, resource, seeded, first_name, label):
    response = client.post(
        f"/{resource}", headers=admin_headers, json={"name": first_name}
    )

    assert response.status_code == 409
    assert response.json()["detail"] == f"{label} already exists"


def test_create_requires_admin(client, auth_headers, resource):
    response = client.post(
        f"/{resource}", headers=auth_headers, json={"name": "Homebrew"}
    )

    assert response.status_code == 403


def test_create_requires_token(client, resource):
    assert client.post(f"/{resource}", json={"name": "Homebrew"}).status_code == 401


def test_create_validation(client, admin_headers, resource):
    assert (
        client.post(
            f"/{resource}", headers=admin_headers, json={"name": ""}
        ).status_code
        == 422
    )


def test_admin_can_edit(client, admin_headers, resource, seeded):
    response = client.patch(
        f"/{resource}/{seeded[0].id}",
        headers=admin_headers,
        json={"name": "Renamed"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Renamed"


def test_edit_with_taken_name(client, admin_headers, resource, seeded):
    response = client.patch(
        f"/{resource}/{seeded[0].id}",
        headers=admin_headers,
        json={"name": seeded[1].name},
    )

    assert response.status_code == 409


def test_edit_with_no_fields(client, admin_headers, resource, seeded):
    response = client.patch(
        f"/{resource}/{seeded[0].id}", headers=admin_headers, json={}
    )

    assert response.status_code == 400


def test_edit_not_found(client, admin_headers, resource):
    response = client.patch(
        f"/{resource}/999", headers=admin_headers, json={"name": "Renamed"}
    )

    assert response.status_code == 404


def test_edit_requires_admin(client, auth_headers, resource, seeded):
    response = client.patch(
        f"/{resource}/{seeded[0].id}", headers=auth_headers, json={"name": "Renamed"}
    )

    assert response.status_code == 403


def test_admin_can_delete_unused(client, admin_headers, resource, seeded):
    item_id = seeded[1].id

    assert (
        client.delete(f"/{resource}/{item_id}", headers=admin_headers).status_code
        == 204
    )
    assert client.get(f"/{resource}/{item_id}").status_code == 404


def test_delete_in_use(
    client, admin_headers, auth_headers, resource, character_payload, label
):
    assert (
        client.post(
            "/characters", headers=auth_headers, json=character_payload
        ).status_code
        == 201
    )

    key = "class_id" if resource == "classes" else "background_id"

    response = client.delete(
        f"/{resource}/{character_payload[key]}", headers=admin_headers
    )

    assert response.status_code == 409
    assert response.json()["detail"] == f"{label} is in use by a character"


def test_delete_not_found(client, admin_headers, resource):
    assert client.delete(f"/{resource}/999", headers=admin_headers).status_code == 404


def test_delete_requires_admin(client, auth_headers, resource, seeded):
    response = client.delete(f"/{resource}/{seeded[0].id}", headers=auth_headers)

    assert response.status_code == 403
