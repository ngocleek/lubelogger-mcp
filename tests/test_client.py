from pathlib import Path

import httpx
import pytest

from lubelogger_mcp.client import LubeLoggerClient
from lubelogger_mcp.types import ExtraField


def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LUBELOGGER_URL", raising=False)
    monkeypatch.delenv("LUBELOGGER_API_KEY", raising=False)
    monkeypatch.delenv("LUBELOGGER_CULTURE_INVARIANT", raising=False)


def _set_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUBELOGGER_URL", "https://demo.lubelogger.com/")
    monkeypatch.setenv("LUBELOGGER_API_KEY", "secret-key")
    monkeypatch.delenv("LUBELOGGER_CULTURE_INVARIANT", raising=False)


def test_missing_environment_returns_typed_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)

    result = LubeLoggerClient().get("/api/vehicles")

    assert result == {
        "ok": False,
        "status_code": 0,
        "content_type": None,
        "data": None,
        "error": "Missing required environment variables: LUBELOGGER_URL, LUBELOGGER_API_KEY",
    }


def test_api_key_header_and_url_join(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["api_key"] = request.headers.get("x-api-key")
        return httpx.Response(200, json={"vehicles": []})

    client = LubeLoggerClient(transport=httpx.MockTransport(handler))
    result = client.get("/api/vehicles")

    assert seen == {
        "url": "https://demo.lubelogger.com/api/vehicles",
        "api_key": "secret-key",
    }
    assert result["ok"] is True
    assert result["data"] == {"vehicles": []}


def test_optional_culture_invariant_header(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    monkeypatch.setenv("LUBELOGGER_CULTURE_INVARIANT", "true")
    seen: dict[str, str | None] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["culture"] = request.headers.get("culture-invariant")
        return httpx.Response(200, json={"ok": True})

    LubeLoggerClient(transport=httpx.MockTransport(handler)).get("/api/calendar")

    assert seen["culture"] == "true"


def test_query_filters_and_repeated_params(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    seen: dict[str, list[str]] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["urgencies"] = request.url.params.get_list("urgencies")
        seen["tags"] = request.url.params.get_list("tags")
        seen["startDate"] = [request.url.params["startDate"]]
        return httpx.Response(204, text="")

    client = LubeLoggerClient(transport=httpx.MockTransport(handler))
    result = client.get(
        "/api/vehicle/reminders/send",
        query=[
            ("urgencies", "NotUrgent"),
            ("urgencies", "Urgent"),
            ("tags", "inspection"),
            ("tags", "oil"),
            ("startDate", "2026-01-01"),
        ],
    )

    assert seen == {
        "urgencies": ["NotUrgent", "Urgent"],
        "tags": ["inspection", "oil"],
        "startDate": ["2026-01-01"],
    }
    assert result["ok"] is True
    assert result["status_code"] == 204


def test_delete_request_formats_query(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["url"] = str(request.url)
        return httpx.Response(200, json={"deleted": True})

    result = LubeLoggerClient(transport=httpx.MockTransport(handler)).delete(
        "/api/vehicle/gasrecords/delete",
        query={"id": 7},
    )

    assert seen["method"] == "DELETE"
    assert seen["url"] == "https://demo.lubelogger.com/api/vehicle/gasrecords/delete?id=7"
    assert result["data"] == {"deleted": True}


def test_form_data_serializes_extra_fields_and_bools(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)
    seen: dict[str, bytes | str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        body = request.read()
        seen["content_type"] = request.headers["content-type"]
        seen["body"] = body
        return httpx.Response(201, json={"id": 123})

    client = LubeLoggerClient(transport=httpx.MockTransport(handler))
    result = client.form(
        "POST",
        "/api/vehicle/odometerrecords/add",
        query={"vehicleId": 1},
        form={
            "date": "08/26/2024",
            "odometer": 225000,
            "isfilltofull": True,
            "extra_fields": [ExtraField(name="Trip Type", value="Leisure")],
        },
    )

    body = seen["body"]
    assert isinstance(body, bytes)
    assert seen["content_type"].startswith("multipart/form-data; boundary=")
    assert b'name="date"' in body
    assert b"08/26/2024" in body
    assert b'name="odometer"' in body
    assert b"225000" in body
    assert b'name="isfilltofull"' in body
    assert b"true" in body
    assert b'name="extrafields[0][name]"' in body
    assert b"Trip Type" in body
    assert b'name="extrafields[0][value]"' in body
    assert b"Leisure" in body
    assert result["status_code"] == 201


def test_multipart_upload_sends_repeated_documents(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _set_env(monkeypatch)
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("alpha", encoding="utf-8")
    second.write_text("beta", encoding="utf-8")
    seen: dict[str, bytes | str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["content_type"] = request.headers["content-type"]
        seen["body"] = request.read()
        return httpx.Response(200, json={"uploaded": 2})

    result = LubeLoggerClient(transport=httpx.MockTransport(handler)).multipart(
        "POST",
        "/api/documents/upload",
        file_paths=[str(first), str(second)],
    )

    body = seen["body"]
    assert isinstance(body, bytes)
    assert seen["content_type"].startswith("multipart/form-data; boundary=")
    assert body.count(b'name="documents"') == 2
    assert b'filename="first.txt"' in body
    assert b"alpha" in body
    assert b'filename="second.txt"' in body
    assert b"beta" in body
    assert result["data"] == {"uploaded": 2}


def test_non_json_response_uses_text_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_env(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="backup created", headers={"content-type": "text/plain"})

    result = LubeLoggerClient(transport=httpx.MockTransport(handler)).get("/api/makebackup")

    assert result == {
        "ok": True,
        "status_code": 200,
        "content_type": "text/plain",
        "data": "backup created",
        "error": None,
    }
