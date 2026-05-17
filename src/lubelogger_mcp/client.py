from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import httpx

from lubelogger_mcp.types import ExtraField, ToolResponse

QueryValue = str | int | float | bool | None
QueryParams = Mapping[str, QueryValue | Sequence[QueryValue]] | Sequence[tuple[str, QueryValue]]


class LubeLoggerConfigError(ValueError):
    """Raised when required LubeLogger environment configuration is missing."""


class LubeLoggerClient:
    """Small synchronous client for LubeLogger's HTTP API."""

    def __init__(
        self,
        *,
        transport: httpx.BaseTransport | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._transport = transport
        self._timeout = timeout

    def get(self, path: str, *, query: QueryParams | None = None) -> dict[str, Any]:
        return self.request("GET", path, query=query)

    def delete(self, path: str, *, query: QueryParams | None = None) -> dict[str, Any]:
        return self.request("DELETE", path, query=query)

    def form(
        self,
        method: str,
        path: str,
        *,
        query: QueryParams | None = None,
        form: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        files = [(key, (None, value)) for key, value in self._form_items(form or {})]
        return self.request(method, path, query=query, files=files)

    def multipart(
        self,
        method: str,
        path: str,
        *,
        query: QueryParams | None = None,
        file_paths: Sequence[str],
    ) -> dict[str, Any]:
        opened: list[Any] = []
        files: list[tuple[str, tuple[str, Any, str]]] = []
        try:
            for file_path in file_paths:
                path_obj = Path(file_path)
                handle = path_obj.open("rb")
                opened.append(handle)
                files.append(("documents", (path_obj.name, handle, "application/octet-stream")))
            return self.request(method, path, query=query, files=files)
        except OSError as exc:
            return self._error(f"Unable to read upload file: {exc}")
        finally:
            for handle in opened:
                handle.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        query: QueryParams | None = None,
        files: Any | None = None,
    ) -> dict[str, Any]:
        try:
            base_url, headers = self._load_config()
        except LubeLoggerConfigError as exc:
            return self._error(str(exc))

        try:
            with httpx.Client(
                base_url=base_url,
                headers=headers,
                timeout=self._timeout,
                transport=self._transport,
            ) as client:
                response = client.request(
                    method,
                    self._normalize_path(path),
                    params=self._query_items(query),
                    files=files,
                )
        except httpx.HTTPError as exc:
            return self._error(str(exc))

        return self._response(response)

    @staticmethod
    def _load_config() -> tuple[str, dict[str, str]]:
        base_url = os.getenv("LUBELOGGER_URL")
        api_key = os.getenv("LUBELOGGER_API_KEY")
        missing = [
            name
            for name, value in (
                ("LUBELOGGER_URL", base_url),
                ("LUBELOGGER_API_KEY", api_key),
            )
            if not value
        ]
        if missing:
            raise LubeLoggerConfigError(
                "Missing required environment variables: " + ", ".join(missing)
            )

        headers = {"x-api-key": api_key or ""}
        if os.getenv("LUBELOGGER_CULTURE_INVARIANT", "").lower() == "true":
            headers["culture-invariant"] = "true"
        return (base_url or "").rstrip("/"), headers

    @staticmethod
    def _normalize_path(path: str) -> str:
        return "/" + path.lstrip("/")

    @classmethod
    def _query_items(cls, query: QueryParams | None) -> list[tuple[str, str]]:
        if query is None:
            return []
        if isinstance(query, Mapping):
            items: Iterable[tuple[str, Any]] = query.items()
        else:
            items = query

        result: list[tuple[str, str]] = []
        for key, value in items:
            if value is None:
                continue
            if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
                for child in value:
                    if child is not None:
                        result.append((key, cls._stringify(child)))
            else:
                result.append((key, cls._stringify(value)))
        return result

    @classmethod
    def _form_items(cls, form: Mapping[str, Any]) -> list[tuple[str, str]]:
        result: list[tuple[str, str]] = []
        for key, value in form.items():
            if value is None:
                continue
            if key == "extra_fields":
                result.extend(cls._extra_field_items(value))
            else:
                result.append((key, cls._stringify(value)))
        return result

    @classmethod
    def _extra_field_items(cls, value: Any) -> list[tuple[str, str]]:
        result: list[tuple[str, str]] = []
        for index, item in enumerate(value or []):
            field = item if isinstance(item, ExtraField) else ExtraField.model_validate(item)
            result.append((f"extrafields[{index}][name]", field.name))
            result.append((f"extrafields[{index}][value]", field.value))
        return result

    @staticmethod
    def _stringify(value: Any) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    @staticmethod
    def _response(response: httpx.Response) -> dict[str, Any]:
        content_type = response.headers.get("content-type")
        media_type = content_type.split(";", 1)[0].strip() if content_type else None
        if media_type == "application/json":
            try:
                data: Any = response.json()
            except ValueError:
                data = response.text
        else:
            data = response.text

        error = None
        if response.is_error:
            error = data if isinstance(data, str) else response.reason_phrase

        return ToolResponse(
            ok=not response.is_error,
            status_code=response.status_code,
            content_type=content_type,
            data=data,
            error=error,
        ).model_dump()

    @staticmethod
    def _error(message: str) -> dict[str, Any]:
        return ToolResponse(
            ok=False,
            status_code=0,
            content_type=None,
            data=None,
            error=message,
        ).model_dump()
