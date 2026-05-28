from analysis.models import AuditLog, Entry, Source
from analysis.parsers import parse_sap_file, parse_travel_json, parse_utility_csv
from analysis.parsers.emissions import compute_emissions

PARSERS = {
    Source.SourceType.SAP: parse_sap_file,
    Source.SourceType.UTILITY: parse_utility_csv,
    Source.SourceType.TRAVEL: parse_travel_json,
}


def ingest_file(source_type, file_bytes, source_name, client_name, user, filename=""):
    parser = PARSERS.get(source_type)
    if not parser:
        return None, {"detail": f"Unknown source type: {source_type}"}

    parsed_rows, parse_errors = parser(file_bytes)
    if not parsed_rows and parse_errors:
        return None, {"detail": "Parse failed", "errors": parse_errors}

    source = Source.objects.create(
        name=source_name,
        source_type=source_type,
        client_name=client_name,
        filename=filename,
        created_by=user,
    )

    created = 0
    for row in parsed_rows:
        emissions = compute_emissions(
            row.get("normalized_quantity"), row.get("normalized_unit")
        )
        entry = Entry.objects.create(
            source=source,
            label=row["label"],
            scope=row.get("scope", "3"),
            activity_type=row.get("activity_type", ""),
            quantity=row.get("quantity"),
            unit=row.get("unit", ""),
            normalized_quantity=row.get("normalized_quantity"),
            normalized_unit=row.get("normalized_unit", ""),
            emissions_kg_co2e=emissions,
            period_start=row.get("period_start"),
            period_end=row.get("period_end"),
            external_id=row.get("external_id", ""),
            raw_data=row.get("raw_data", {}),
            is_suspicious=row.get("is_suspicious", False),
            suspicion_reason=row.get("suspicion_reason", ""),
            created_by=user,
            status=Entry.Status.FLAGGED if row.get("is_suspicious") else Entry.Status.NEW,
        )
        AuditLog.objects.create(
            entry=entry,
            user=user,
            action=AuditLog.Action.INGESTED,
            note=f"From {filename or source_type}",
        )
        created += 1

    return {
        "source_id": source.id,
        "created": created,
        "errors": parse_errors,
    }, None
