import json
from decimal import Decimal


# Tiny stub: airport pair -> km when API/CSV has no distance
AIRPORT_KM = {
    ("DEL", "BOM"): 1150,
    ("BOM", "DEL"): 1150,
    ("LHR", "JFK"): 5540,
    ("JFK", "LHR"): 5540,
}


def parse_travel_json(file_bytes):
    """
    JSON shaped like a trimmed Concur expense export (list or {expenses: [...]}).
    """
    try:
        payload = json.loads(file_bytes.decode("utf-8"))
    except json.JSONDecodeError as exc:
        return [], [f"Invalid JSON: {exc}"]

    if isinstance(payload, dict):
        items = payload.get("expenses") or payload.get("data") or []
    elif isinstance(payload, list):
        items = payload
    else:
        return [], ["JSON must be a list or object with 'expenses'"]

    rows = []
    errors = []

    for i, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            errors.append(f"Row {i}: not an object")
            continue

        ext = str(item.get("id") or item.get("expenseId") or f"travel-{i}")
        category = (item.get("expenseType") or item.get("category") or "unknown").lower()
        origin = (item.get("origin") or item.get("from") or "").upper()
        dest = (item.get("destination") or item.get("to") or "").upper()
        distance = item.get("distanceKm") or item.get("distance_km")

        if category in ("air", "airfare", "flight"):
            activity = "flight"
        elif category in ("hotel", "lodging"):
            activity = "hotel"
        else:
            activity = "ground"

        qty = None
        unit = "KM"
        if distance is not None:
            try:
                qty = Decimal(str(distance))
            except Exception:
                qty = None

        if qty is None and origin and dest:
            qty = Decimal(str(AIRPORT_KM.get((origin, dest), 800)))
            suspicious = True
            reason = f"Distance estimated from {origin}-{dest}"
        elif qty is None:
            qty = Decimal("1")
            unit = "TRIP"
            suspicious = True
            reason = "No distance — used trip fallback"
        else:
            suspicious = False
            reason = ""

        label = f"{activity.title()} {origin}-{dest}".strip(" -")
        if activity == "hotel":
            label = f"Hotel {item.get('city') or dest or 'unknown'}"

        rows.append(
            {
                "label": label,
                "scope": "3",
                "activity_type": activity,
                "quantity": qty,
                "unit": unit,
                "normalized_quantity": qty,
                "normalized_unit": unit,
                "period_start": None,
                "period_end": None,
                "external_id": ext,
                "raw_data": item,
                "is_suspicious": suspicious,
                "suspicion_reason": reason,
            }
        )

    return rows, errors
