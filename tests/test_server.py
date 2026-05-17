import asyncio

import pytest
from fastmcp.client import Client

from lubelogger_mcp.server import EXPECTED_TOOL_NAMES, mcp


def test_expected_tools_are_registered_and_whoami_is_absent() -> None:
    async def run() -> set[str]:
        async with Client(mcp) as client:
            tools = await client.list_tools()
        return {tool.name for tool in tools}

    names = asyncio.run(run())

    assert names == set(EXPECTED_TOOL_NAMES)
    assert "auth_who_am_i" not in names
    assert "whoami" not in names


def test_tool_call_returns_typed_config_error_when_env_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LUBELOGGER_URL", raising=False)
    monkeypatch.delenv("LUBELOGGER_API_KEY", raising=False)

    async def run() -> dict[str, object] | None:
        async with Client(mcp) as client:
            result = await client.call_tool("vehicles_list", {})
        return result.data

    assert asyncio.run(run()) == {
        "ok": False,
        "status_code": 0,
        "content_type": None,
        "data": None,
        "error": "Missing required environment variables: LUBELOGGER_URL, LUBELOGGER_API_KEY",
    }
