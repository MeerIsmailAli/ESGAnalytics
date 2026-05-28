import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation


def _parse_decimal(value):
    if value is None or str(value).strip() == "":
        return None
    try:
        return Decimal(str(value).replace(",", ".").strip())
    except InvalidOperation:
        return None


def _parse_date(value):
    if not value:
        return None
    value = str(value).strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _normalize_header(h):
    return h.strip().lower().replace(" ", "_")


def parse_sap_file(file_bytes):
    """
    SAP-style semicolon flat file. Supports German or English headers.
    Returns list of dicts ready for Entry creation.
    """
    text = file_bytes.decode("utf-8-sig", errors="replace")
    delimiter = ";" if ";" in text.splitlines()[0] else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    if not reader.fieldnames:
        return [], ["Empty file or no header row"]

    header_map = {_normalize_header(h): h for h in reader.fieldnames}
    rows = []
    errors = []

    def col(*names):
        for name in names:
            key = _normalize_header(name)
            if key in header_map:
                return header_map[key]
        return None

    date_col = col("budat", "posting_date", "date")
    plant_col = col("werk", "plant")
    qty_col = col("menge", "quantity")
    unit_col = col("meins", "unit")
    mat_col = col("matnr", "material", "material_description")
    type_col = col("materialart", "material_type", "type")
    ext_col = col("external_id", "belnr", "document")

    for i, raw in enumerate(reader, start=2):
        qty = _parse_decimal(raw.get(qty_col)) if qty_col else None
        unit = (raw.get(unit_col) or "").strip().upper() if unit_col else ""
        mat_type = (raw.get(type_col) or "").strip().upper() if type_col else ""
        plant = (raw.get(plant_col) or "").strip() if plant_col else ""
        mat = (raw.get(mat_col) or "SAP line").strip() if mat_col else "SAP line"
        ext = (raw.get(ext_col) or f"sap-row-{i}").strip() if ext_col else f"sap-row-{i}"
        posting = _parse_date(raw.get(date_col)) if date_col else None

        if mat_type in ("ROH", "PROCUREMENT", "PURCHASE") or "PROC" in mat_type:
            scope = "3"
            activity = "procurement"
        else:
            scope = "1"
            activity = "fuel"

        label = f"{plant} {mat} {qty or '?'} {unit}".strip()
        suspicious = False
        reason = ""

        if qty is None or qty <= 0:
            suspicious = True
            reason = "Missing or zero quantity"
        if unit not in ("L", "KG", "KWH", ""):
            suspicious = True
            reason = reason or f"Unusual unit: {unit}"

        rows.append(
            {
                "label": label,
                "scope": scope,
                "activity_type": activity,
                "quantity": qty,
                "unit": unit,
                "normalized_quantity": qty,
                "normalized_unit": unit or "KG",
                "period_start": posting,
                "period_end": posting,
                "external_id": ext,
                "raw_data": dict(raw),
                "is_suspicious": suspicious,
                "suspicion_reason": reason,
            }
        )

    return rows, errors
