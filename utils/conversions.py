# Unit conversions 
UNIT_FACTORS = {
    "nA": 1e-9,
    "μA": 1e-6,
    "mA": 1e-3,
    "A":  1.0,
}

def to_amperes(value: float, unit: str) -> float:
    factor = UNIT_FACTORS.get(unit, 1.0)
    return value * factor