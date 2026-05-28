from decimal import Decimal

# Rough prototype factors (kg CO2e per unit) — not for real audit
FACTORS = {
    "L": Decimal("2.68"),  # diesel-ish
    "KG": Decimal("1.5"),  # generic procurement placeholder
    "KWH": Decimal("0.42"),  # grid electricity
    "KM": Decimal("0.15"),  # air travel per km
    "TRIP": Decimal("250"),  # fallback when no distance
}


def compute_emissions(quantity, normalized_unit):
    if quantity is None:
        return None
    unit = (normalized_unit or "").upper()
    factor = FACTORS.get(unit)
    if not factor:
        return None
    return (Decimal(str(quantity)) * factor).quantize(Decimal("0.01"))
