import pytest

ADMIN_ENDPOINTS = [
    ("get", "/admin/users"),
    ("get", "/admin/users/1"),
    ("patch", "/admin/users/1"),
    ("delete", "/admin/users/1"),
]


@pytest.mark.parametrize("method,path", ADMIN_ENDPOINTS)
def test_admin_endpoints_reject_anonymous(client, method, path):
    response = getattr(client, method)(path)

    assert response.status_code == 401


@pytest.mark.parametrize("method,path", ADMIN_ENDPOINTS)
def test_admin_endpoints_reject_regular_user(client, auth_headers, method, path):
    kwargs = {"headers": auth_headers}

    if method == "patch":
        kwargs["json"] = {"nickname": "whatever"}

    response = getattr(client, method)(path, **kwargs)

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_can_change_a_users_role(client, admin_headers, test_user):
    response = client.patch(
        f"/admin/users/{test_user.id}",
        headers=admin_headers,
        json={"role": "admin"},
    )

    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_admin_update_with_no_fields(client, admin_headers, test_user):
    response = client.patch(
        f"/admin/users/{test_user.id}",
        headers=admin_headers,
        json={},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "No fields to update"


def test_admin_update_rejects_unknown_role(client, admin_headers, test_user):
    response = client.patch(
        f"/admin/users/{test_user.id}",
        headers=admin_headers,
        json={"role": "superuser"},
    )

    assert response.status_code == 422


def test_deleting_a_user_removes_their_characters(
    client,
    admin_headers,
    auth_headers,
    character_payload,
    test_user,
    db,
):
    from models.character import Character

    create_response = client.post(
        "/characters",
        headers=auth_headers,
        json=character_payload,
    )

    assert create_response.status_code == 200

    character_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/admin/users/{test_user.id}",
        headers=admin_headers,
    )

    assert delete_response.status_code == 204

    assert db.query(Character).filter(Character.id == character_id).first() is None
