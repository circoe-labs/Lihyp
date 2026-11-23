import pytest
from datetime import timezone
from decimal import Decimal
from simco2.domain.units import Quantity, Money, local_to_utc, dec
from simco2.domain.errors import DomainError


def test_conversions_and_roundtrip():
    a = Quantity(Decimal("1000"), "m")
    assert a.convert("km") == Quantity(Decimal("1"), "km")
    assert Quantity.from_json(a.to_json()) == a
    assert Money(dec("0.1")) + Money(dec("0.2")) == Money(dec("0.3"))


def test_incompatible_units_and_floats():
    with pytest.raises(DomainError):
        _ = Quantity(dec("1"), "L") + Quantity(dec("1"), "kWh")
    with pytest.raises(DomainError):
        Quantity(dec("1"), "L").convert("kWh")
    with pytest.raises(DomainError):
        dec(0.1)


def test_dst_nonexistent_and_ambiguous():
    with pytest.raises(DomainError, match="inexistante"):
        local_to_utc("2026-03-29T02:30:00", "Europe/Paris")
    with pytest.raises(DomainError, match="ambiguë"):
        local_to_utc("2026-10-25T02:30:00", "Europe/Paris")
    early = local_to_utc("2026-10-25T02:30:00", "Europe/Paris", fold=0)
    late = local_to_utc("2026-10-25T02:30:00", "Europe/Paris", fold=1)
    assert late - early == __import__("datetime").timedelta(hours=1)
    assert early.tzinfo == timezone.utc
