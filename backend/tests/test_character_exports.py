from uuid import uuid4

from celery.exceptions import OperationalError

from models.character_export import CharacterExport
from routers import characters as characters_router


def create_character(client, headers, payload):
    response = client.post("/characters", headers=headers, json=payload)
    assert response.status_code == 201
    return response.json()


def test_request_character_export(
    client, db, auth_headers, character_payload, monkeypatch
):
    character = create_character(client, auth_headers, character_payload)
    calls = []

    def fake_apply_async(*, kwargs, task_id):
        calls.append({"kwargs": kwargs, "task_id": task_id})

    monkeypatch.setattr(
        characters_router.export_character_pdf,
        "apply_async",
        fake_apply_async,
    )

    response = client.post(
        f"/characters/{character['id']}/export",
        headers=auth_headers,
    )

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "PENDING"
    assert calls == [
        {
            "kwargs": {
                "character_id": character["id"],
                "user_id": db.query(
                    CharacterExport
                ).filter_by(task_id=data["task_id"]).one().user_id,
            },
            "task_id": data["task_id"],
        }
    ]

    export = db.query(CharacterExport).filter_by(task_id=data["task_id"]).one()
    assert export.character_id == character["id"]
    assert export.status == "PENDING"


def test_request_export_for_missing_character(client, auth_headers):
    response = client.post("/characters/999/export", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Character not found"


def test_request_export_when_celery_is_unavailable(
    client, db, auth_headers, character_payload, monkeypatch
):
    character = create_character(client, auth_headers, character_payload)

    def fail_apply_async(*, kwargs, task_id):
        raise OperationalError("Celery unavailable")

    monkeypatch.setattr(
        characters_router.export_character_pdf,
        "apply_async",
        fail_apply_async,
    )

    response = client.post(
        f"/characters/{character['id']}/export",
        headers=auth_headers,
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Could not start PDF export"

    export = db.query(CharacterExport).order_by(CharacterExport.id.desc()).first()
    assert export is not None
    assert export.status == "FAILURE"
    assert export.error == "Failed to enqueue export task"

def test_get_export_status(
    client, db, auth_headers, test_user, character_payload
):
    character = create_character(client, auth_headers, character_payload)
    task_id = str(uuid4())

    db.add(
        CharacterExport(
            task_id=task_id,
            character_id=character["id"],
            user_id=test_user.id,
            status="PENDING",
        )
    )
    db.commit()

    response = client.get(
        f"/characters/exports/{task_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["task_id"] == task_id
    assert response.json()["status"] == "PENDING"
    db.commit()

    response = client.get(
        f"/characters/exports/{task_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["task_id"] == task_id
    assert response.json()["status"] == "PENDING"


def test_export_not_found_for_unknown_task(client, auth_headers):
    response = client.get(
        f"/characters/exports/{uuid4()}",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Export not found"


def test_export_cannot_be_downloaded_before_success(
    client, db, auth_headers, test_user, character_payload
):
    character = create_character(client, auth_headers, character_payload)
    task_id = str(uuid4())

    db.add(
        CharacterExport(
            task_id=task_id,
            character_id=character["id"],
            user_id=test_user.id,
            status="PENDING",
        )
    )
    db.commit()

    response = client.get(
        f"/characters/exports/{task_id}/download",
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Export is not ready for download"


def test_download_successful_export(
    client, db, auth_headers, test_user, character_payload, monkeypatch, tmp_path
):
    character = create_character(client, auth_headers, character_payload)
    task_id = str(uuid4())
    filename = "character_test.pdf"
    (tmp_path / filename).write_bytes(b"%PDF-1.4\nTest PDF\n")

    db.add(
        CharacterExport(
            task_id=task_id,
            character_id=character["id"],
            user_id=test_user.id,
            status="SUCCESS",
            filename=filename,
        )
    )
    db.commit()

    monkeypatch.setenv("EXPORTS_DIR", str(tmp_path))

    response = client.get(
        f"/characters/exports/{task_id}/download",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-1.4")


def test_export_cannot_be_downloaded_by_another_user(
    client, db, auth_headers, test_user, character_payload
):
    character = create_character(client, auth_headers, character_payload)
    task_id = str(uuid4())

    db.add(
        CharacterExport(
            task_id=task_id,
            character_id=character["id"],
            user_id=test_user.id,
            status="SUCCESS",
            filename="character_test.pdf",
        )
    )
    db.commit()

    registration = client.post(
        "/users/registration",
        json={
            "email": "other-export@example.com",
            "nickname": "otherexport",
            "password": "password123",
        },
    )
    assert registration.status_code == 201

    login = client.post(
        "/users/login",
        data={
            "username": "other-export@example.com",
            "password": "password123",
        },
    )
    assert login.status_code == 200
    other_headers = {
        "Authorization": f"Bearer {login.json()['access_token']}"
    }

    response = client.get(
        f"/characters/exports/{task_id}/download",
        headers=other_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Export not found"


def test_download_rejects_path_traversal(
    client, db, auth_headers, test_user, character_payload
):
    character = create_character(client, auth_headers, character_payload)
    task_id = str(uuid4())

    db.add(
        CharacterExport(
            task_id=task_id,
            character_id=character["id"],
            user_id=test_user.id,
            status="SUCCESS",
            filename="../secret.pdf",
        )
    )
    db.commit()

    response = client.get(
        f"/characters/exports/{task_id}/download",
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid export filename"


def test_download_returns_404_when_pdf_file_is_missing(
    client, db, auth_headers, test_user, character_payload, monkeypatch, tmp_path
):
    character = create_character(client, auth_headers, character_payload)
    task_id = str(uuid4())

    db.add(
        CharacterExport(
            task_id=task_id,
            character_id=character["id"],
            user_id=test_user.id,
            status="SUCCESS",
            filename="missing.pdf",
        )
    )
    db.commit()
    monkeypatch.setenv("EXPORTS_DIR", str(tmp_path))

    response = client.get(
        f"/characters/exports/{task_id}/download",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Export file not found"
