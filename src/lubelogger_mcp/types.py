from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExtraField(BaseModel):
    """A LubeLogger custom extra field."""

    name: str = Field(description="Extra field name.")
    value: str = Field(description="Extra field value.")


class ToolResponse(BaseModel):
    """JSON-compatible MCP response envelope used by every tool."""

    ok: bool
    status_code: int
    content_type: str | None
    data: Any
    error: str | None = None
