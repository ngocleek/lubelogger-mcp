# LubeLogger MCP Server

A Python [FastMCP](https://gofastmcp.com/) stdio server for the
[LubeLogger](https://docs.lubelogger.com/Advanced/API/) API. It exposes
LubeLogger vehicle, maintenance, fuel, reminder, document, and admin endpoints
as MCP tools for local MCP clients.

This project targets FastMCP 3.3.1 and Python 3.10 or newer.

## Features

- FastMCP stdio server with `mcp.run()`
- API-key authentication with the `x-api-key` header
- Typed tool inputs for LubeLogger form and query parameters
- JSON-compatible response envelope for every tool
- Multipart upload support for LubeLogger documents
- MIT licensed for public reuse

## Requirements

Set these environment variables before running the server:

```powershell
$env:LUBELOGGER_URL = "https://your-lubelogger.example.com"
$env:LUBELOGGER_API_KEY = "your-api-key"
```

See `.env.example` for the full configuration surface.

Optional:

```powershell
$env:LUBELOGGER_CULTURE_INVARIANT = "true"
```

Your LubeLogger API key must have permission for the endpoints you call. Admin
tools such as backup and cleanup require admin-capable API access in LubeLogger.

## Installation

Recommended, from PyPI with pipx:

```powershell
pipx install lubelogger-mcp
```

Upgrade an existing install:

```powershell
pipx upgrade lubelogger-mcp
```

Install directly from GitHub if you want the latest source before a PyPI
release:

```powershell
pipx install git+https://github.com/ngocleek/lubelogger-mcp.git
```

From a local checkout:

```powershell
pip install -e .
```

For development:

```powershell
pip install -e ".[dev]"
pytest
```

## Running

```powershell
python -m lubelogger_mcp.server
```

or:

```powershell
fastmcp run src/lubelogger_mcp/server.py
```

Example MCP client config:

```json
{
  "mcpServers": {
    "lubelogger": {
      "command": "lubelogger-mcp",
      "env": {
        "LUBELOGGER_URL": "https://your-lubelogger.example.com",
        "LUBELOGGER_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Tools

The server exposes these tool groups:

- `vehicles_*`
- `odometer_*`
- `plans_*`
- `service_*`
- `repair_*`
- `upgrade_*`
- `tax_*`
- `gas_*`
- `calendar_get`
- `documents_upload`
- `reminders_*`
- `admin_*`

The LubeLogger `whoami` endpoint is intentionally not exposed.

## Response Format

Every tool returns:

```json
{
  "ok": true,
  "status_code": 200,
  "content_type": "application/json",
  "data": {},
  "error": null
}
```

For non-JSON responses, `data` contains the text response body.

## Example Calls

List vehicles:

```json
{}
```

Add an odometer record:

```json
{
  "vehicle_id": 1,
  "date": "08/26/2024",
  "odometer": 225000,
  "extra_fields": [
    {
      "name": "Trip Type",
      "value": "Leisure"
    }
  ]
}
```

Upload documents:

```json
{
  "file_paths": [
    "C:\\Users\\you\\Documents\\invoice.pdf"
  ]
}
```

## Limitations

- Response schemas are generic because the source Postman collection does not
  include response examples.
- Date formats are passed through to LubeLogger. Use the format expected by your
  LubeLogger instance.
- API-key authorization is enforced by LubeLogger, not this MCP server.

## License

MIT

## Publishing

This repository includes a GitHub Actions workflow for PyPI Trusted Publishing.
Before the first release, configure a PyPI pending trusted publisher with:

- Project name: `lubelogger-mcp`
- Owner: `ngocleek`
- Repository: `lubelogger-mcp`
- Workflow: `publish.yml`
- Environment: `pypi`

Release checklist:

1. Update the version in `pyproject.toml` and `src/lubelogger_mcp/__init__.py`.
2. Commit and push the release changes.
3. Create and push a matching tag, for example `v0.1.0`.
4. Create a GitHub Release from that tag.

When the GitHub Release is published, the workflow builds the package and
uploads it to PyPI without storing a PyPI token in GitHub secrets.
