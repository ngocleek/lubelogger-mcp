from __future__ import annotations

from typing import Any, Sequence

from fastmcp import FastMCP

from lubelogger_mcp.client import LubeLoggerClient
from lubelogger_mcp.types import ExtraField

mcp = FastMCP("LubeLogger")


EXPECTED_TOOL_NAMES = [
    "vehicles_list",
    "vehicles_get_info",
    "odometer_list_records",
    "odometer_list_all_records",
    "odometer_get_latest",
    "odometer_get_adjusted",
    "odometer_add_record",
    "odometer_update_record",
    "odometer_delete_record",
    "plans_list_records",
    "plans_list_all_records",
    "plans_add_record",
    "plans_update_record",
    "plans_delete_record",
    "service_list_records",
    "service_list_all_records",
    "service_add_record",
    "service_update_record",
    "service_delete_record",
    "repair_list_records",
    "repair_list_all_records",
    "repair_add_record",
    "repair_update_record",
    "repair_delete_record",
    "upgrade_list_records",
    "upgrade_list_all_records",
    "upgrade_add_record",
    "upgrade_update_record",
    "upgrade_delete_record",
    "tax_list_records",
    "tax_list_all_records",
    "tax_add_record",
    "tax_update_record",
    "tax_delete_record",
    "gas_list_records",
    "gas_list_all_records",
    "gas_add_record",
    "gas_update_record",
    "gas_delete_record",
    "calendar_get",
    "documents_upload",
    "reminders_list",
    "reminders_list_all",
    "reminders_send_email",
    "admin_make_backup",
    "admin_cleanup",
]


def _client() -> LubeLoggerClient:
    return LubeLoggerClient()


def _record_query(
    *,
    vehicle_id: int | None = None,
    id: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    tags: Sequence[str] | None = None,
) -> list[tuple[str, Any]]:
    query: list[tuple[str, Any]] = []
    if vehicle_id is not None:
        query.append(("vehicleId", vehicle_id))
    if id is not None:
        query.append(("id", id))
    if start_date is not None:
        query.append(("startDate", start_date))
    if end_date is not None:
        query.append(("endDate", end_date))
    for tag in tags or []:
        query.append(("tags", tag))
    return query


def _form(**values: Any) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}


@mcp.tool
def vehicles_list() -> dict[str, Any]:
    """List vehicles."""

    return _client().get("/api/vehicles")


@mcp.tool
def vehicles_get_info(vehicle_id: int) -> dict[str, Any]:
    """Get details for a vehicle."""

    return _client().get("/api/vehicle/info", query={"vehicleId": vehicle_id})


@mcp.tool
def odometer_list_records(
    vehicle_id: int,
    id: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """List odometer records for a vehicle."""

    return _client().get(
        "/api/vehicle/odometerrecords",
        query=_record_query(
            vehicle_id=vehicle_id,
            id=id,
            start_date=start_date,
            end_date=end_date,
            tags=tags,
        ),
    )


@mcp.tool
def odometer_list_all_records() -> dict[str, Any]:
    """List all odometer records."""

    return _client().get("/api/vehicle/odometerrecords/all")


@mcp.tool
def odometer_get_latest(vehicle_id: int) -> dict[str, Any]:
    """Get the latest odometer record for a vehicle."""

    return _client().get("/api/vehicle/odometerrecords/latest", query={"vehicleId": vehicle_id})


@mcp.tool
def odometer_get_adjusted(vehicle_id: int, odometer: int) -> dict[str, Any]:
    """Get adjusted odometer value for a vehicle."""

    return _client().get(
        "/api/vehicle/adjustedodometer",
        query={"vehicleId": vehicle_id, "odometer": odometer},
    )


@mcp.tool
def odometer_add_record(
    vehicle_id: int,
    date: str,
    odometer: int,
    extra_fields: list[ExtraField] | None = None,
) -> dict[str, Any]:
    """Add an odometer record."""

    return _client().form(
        "POST",
        "/api/vehicle/odometerrecords/add",
        query={"vehicleId": vehicle_id},
        form=_form(date=date, odometer=odometer, extra_fields=extra_fields),
    )


@mcp.tool
def odometer_update_record(
    id: int,
    date: str,
    initial_odometer: int,
    odometer: int,
    notes: str | None = None,
    extra_fields: list[ExtraField] | None = None,
) -> dict[str, Any]:
    """Update an odometer record."""

    return _client().form(
        "PUT",
        "/api/vehicle/odometerrecords/update",
        form=_form(
            id=id,
            date=date,
            initialOdometer=initial_odometer,
            odometer=odometer,
            notes=notes,
            extra_fields=extra_fields,
        ),
    )


@mcp.tool
def odometer_delete_record(id: int) -> dict[str, Any]:
    """Delete an odometer record."""

    return _client().delete("/api/vehicle/odometerrecords/delete", query={"id": id})


def _register_plan_tools() -> None:
    @mcp.tool
    def plans_list_records(
        vehicle_id: int,
        id: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """List plan records for a vehicle."""

        return _client().get(
            "/api/vehicle/planrecords",
            query=_record_query(vehicle_id=vehicle_id, id=id, start_date=start_date, end_date=end_date, tags=tags),
        )

    @mcp.tool
    def plans_list_all_records() -> dict[str, Any]:
        """List all plan records."""

        return _client().get("/api/vehicle/planrecords/all")

    @mcp.tool
    def plans_add_record(
        vehicle_id: int,
        date: str,
        description: str,
        cost: float,
        type: str,
        priority: str,
        progress: str,
    ) -> dict[str, Any]:
        """Add a plan record."""

        return _client().form(
            "POST",
            "/api/vehicle/planrecords/add",
            query={"vehicleId": vehicle_id},
            form=_form(
                date=date,
                description=description,
                cost=cost,
                type=type,
                priority=priority,
                progress=progress,
            ),
        )

    @mcp.tool
    def plans_update_record(
        id: int,
        date: str,
        description: str,
        cost: float,
        type: str,
        priority: str,
        progress: str,
    ) -> dict[str, Any]:
        """Update a plan record."""

        return _client().form(
            "PUT",
            "/api/vehicle/planrecords/update",
            form=_form(id=id, date=date, description=description, cost=cost, type=type, priority=priority, progress=progress),
        )

    @mcp.tool
    def plans_delete_record(id: int) -> dict[str, Any]:
        """Delete a plan record."""

        return _client().delete("/api/vehicle/planrecords/delete", query={"id": id})


def _register_standard_record_tools(prefix: str, path_part: str) -> None:
    def list_records(
        vehicle_id: int,
        id: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        return _client().get(
            f"/api/vehicle/{path_part}",
            query=_record_query(vehicle_id=vehicle_id, id=id, start_date=start_date, end_date=end_date, tags=tags),
        )

    def list_all_records() -> dict[str, Any]:
        return _client().get(f"/api/vehicle/{path_part}/all")

    def add_record(vehicle_id: int, date: str, odometer: int, description: str, cost: float) -> dict[str, Any]:
        return _client().form(
            "POST",
            f"/api/vehicle/{path_part}/add",
            query={"vehicleId": vehicle_id},
            form=_form(date=date, odometer=odometer, description=description, cost=cost),
        )

    def update_record(id: int, date: str, odometer: int, description: str, cost: float) -> dict[str, Any]:
        return _client().form(
            "PUT",
            f"/api/vehicle/{path_part}/update",
            form=_form(id=id, date=date, odometer=odometer, description=description, cost=cost),
        )

    def delete_record(id: int) -> dict[str, Any]:
        return _client().delete(f"/api/vehicle/{path_part}/delete", query={"id": id})

    mcp.tool(name=f"{prefix}_list_records", description=f"List {prefix} records for a vehicle.")(list_records)
    mcp.tool(name=f"{prefix}_list_all_records", description=f"List all {prefix} records.")(list_all_records)
    mcp.tool(name=f"{prefix}_add_record", description=f"Add a {prefix} record.")(add_record)
    mcp.tool(name=f"{prefix}_update_record", description=f"Update a {prefix} record.")(update_record)
    mcp.tool(name=f"{prefix}_delete_record", description=f"Delete a {prefix} record.")(delete_record)


def _register_cost_only_record_tools(prefix: str, path_part: str) -> None:
    def list_records(
        vehicle_id: int,
        id: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        return _client().get(
            f"/api/vehicle/{path_part}",
            query=_record_query(vehicle_id=vehicle_id, id=id, start_date=start_date, end_date=end_date, tags=tags),
        )

    def list_all_records() -> dict[str, Any]:
        return _client().get(f"/api/vehicle/{path_part}/all")

    def add_record(vehicle_id: int, date: str, description: str, cost: float) -> dict[str, Any]:
        return _client().form(
            "POST",
            f"/api/vehicle/{path_part}/add",
            query={"vehicleId": vehicle_id},
            form=_form(date=date, description=description, cost=cost),
        )

    def update_record(id: int, date: str, description: str, cost: float) -> dict[str, Any]:
        return _client().form(
            "PUT",
            f"/api/vehicle/{path_part}/update",
            form=_form(id=id, date=date, description=description, cost=cost),
        )

    def delete_record(id: int) -> dict[str, Any]:
        return _client().delete(f"/api/vehicle/{path_part}/delete", query={"id": id})

    mcp.tool(name=f"{prefix}_list_records", description=f"List {prefix} records for a vehicle.")(list_records)
    mcp.tool(name=f"{prefix}_list_all_records", description=f"List all {prefix} records.")(list_all_records)
    mcp.tool(name=f"{prefix}_add_record", description=f"Add a {prefix} record.")(add_record)
    mcp.tool(name=f"{prefix}_update_record", description=f"Update a {prefix} record.")(update_record)
    mcp.tool(name=f"{prefix}_delete_record", description=f"Delete a {prefix} record.")(delete_record)


_register_plan_tools()
for _prefix, _path_part in (
    ("service", "servicerecords"),
    ("repair", "repairrecords"),
    ("upgrade", "upgraderecords"),
):
    _register_standard_record_tools(_prefix, _path_part)
for _prefix, _path_part in (
    ("tax", "taxrecords"),
):
    _register_cost_only_record_tools(_prefix, _path_part)


@mcp.tool
def gas_list_records(
    vehicle_id: int,
    id: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """List gas records for a vehicle."""

    return _client().get(
        "/api/vehicle/gasrecords",
        query=_record_query(vehicle_id=vehicle_id, id=id, start_date=start_date, end_date=end_date, tags=tags),
    )


@mcp.tool
def gas_list_all_records() -> dict[str, Any]:
    """List all gas records."""

    return _client().get("/api/vehicle/gasrecords/all")


@mcp.tool
def gas_add_record(
    vehicle_id: int,
    date: str,
    odometer: int,
    fuel_consumed: float,
    is_fill_to_full: bool,
    missed_fuel_up: bool,
    cost: float,
) -> dict[str, Any]:
    """Add a gas record."""

    return _client().form(
        "POST",
        "/api/vehicle/gasrecords/add",
        query={"vehicleId": vehicle_id},
        form=_form(
            date=date,
            odometer=odometer,
            fuelconsumed=fuel_consumed,
            isfilltofull=is_fill_to_full,
            missedfuelup=missed_fuel_up,
            cost=cost,
        ),
    )


@mcp.tool
def gas_update_record(
    id: int,
    date: str,
    odometer: int,
    fuel_consumed: float,
    is_fill_to_full: bool,
    missed_fuel_up: bool,
    cost: float,
    notes: str | None = None,
) -> dict[str, Any]:
    """Update a gas record."""

    return _client().form(
        "PUT",
        "/api/vehicle/gasrecords/update",
        form=_form(
            id=id,
            date=date,
            odometer=odometer,
            fuelconsumed=fuel_consumed,
            isfilltofull=is_fill_to_full,
            missedfuelup=missed_fuel_up,
            cost=cost,
            notes=notes,
        ),
    )


@mcp.tool
def gas_delete_record(id: int) -> dict[str, Any]:
    """Delete a gas record."""

    return _client().delete("/api/vehicle/gasrecords/delete", query={"id": id})


@mcp.tool
def calendar_get() -> dict[str, Any]:
    """Get calendar data."""

    return _client().get("/api/calendar")


@mcp.tool
def documents_upload(file_paths: list[str]) -> dict[str, Any]:
    """Upload one or more document files."""

    return _client().multipart("POST", "/api/documents/upload", file_paths=file_paths)


@mcp.tool
def reminders_list(vehicle_id: int) -> dict[str, Any]:
    """List reminders for a vehicle."""

    return _client().get("/api/vehicle/reminders", query={"vehicleId": vehicle_id})


@mcp.tool
def reminders_list_all() -> dict[str, Any]:
    """List all reminders."""

    return _client().get("/api/vehicle/reminders/all")


@mcp.tool
def reminders_send_email(urgencies: list[str] | None = None) -> dict[str, Any]:
    """Send reminder emails for urgency levels."""

    values = urgencies or ["NotUrgent", "Urgent", "VeryUrgent", "PastDue"]
    return _client().get(
        "/api/vehicle/reminders/send",
        query=[("urgencies", urgency) for urgency in values],
    )


@mcp.tool
def admin_make_backup() -> dict[str, Any]:
    """Request a LubeLogger backup."""

    return _client().get("/api/makebackup")


@mcp.tool
def admin_cleanup(deep_clean: bool = True) -> dict[str, Any]:
    """Run LubeLogger cleanup."""

    return _client().get("/api/cleanup", query={"deepClean": deep_clean})


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
