import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation


def _parse_decimal(value):
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, AttributeError):
        return None


def _parse_date(value):
    if not value:
        return None
    value = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def parse_utility_csv(file_bytes):
    """Utility portal CSV: account, meter, billing period, kWh."""
    text = file_bytes.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return [], ["Empty file or no header row"]

    rows = []
    errors = []

    for i, raw in enumerate(reader, start=2):
        lower = {k.strip().lower(): v for k, v in raw.items()}

        account = lower.get("account") or lower.get("account_number") or ""
        meter = lower.get("meter_id") or lower.get("meter") or ""
        start = _parse_date(lower.get("period_start") or lower.get("billing_start"))
        end = _parse_date(lower.get("period_end") or lower.get("billing_end"))
        qty = _parse_decimal(lower.get("consumption") or lower.get("kwh"))
        unit = (lower.get("unit") or "kWh").strip().upper()
        ext = lower.get("external_id") or f"{account}-{meter}-{start}"

        suspicious = False
        reason = ""
        if qty is None or qty <= 0:
            suspicious = True
            reason = "Missing or zero consumption"
        if start and end and end < start:
            suspicious = True
            reason = "Billing period end before start"
        if start and end and (end - start).days > 95:
            suspicious = True
            reason = reason or "Billing period longer than 95 days"

        label = f"Meter {meter} {qty or '?'} {unit} ({start} to {end})"
        rows.append(
            {
                "label": label,
                "scope": "2",
                "activity_type": "electricity",
                "quantity": qty,
                "unit": unit,
                "normalized_quantity": qty,
                "normalized_unit": "KWH",
                "period_start": start,
                "period_end": end,
                "external_id": str(ext),
                "raw_data": dict(raw),
                "is_suspicious": suspicious,
                "suspicion_reason": reason,
            }
        )

    return rows, errors
