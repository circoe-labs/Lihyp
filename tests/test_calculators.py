from decimal import Decimal
import pytest
from simco2.domain.calculators import (
    energy_fixed, cost_breakdown, emissions, allocate_by_service_hours, safe_ratio)
from simco2.domain.errors import DomainError, MissingReference


VEHICLE = {"maintenance_eur_per_km": "0", "labor_eur_per_h": "15",
           "purchase_eur": "100000", "residual_eur": "10000",
           "life_years": 10, "insurance_eur_year": "365"}


def test_energy_cost_emission_synthetic_reference():
    # Valeurs illustratives du handoff, jamais de referentiel national.
    one = energy_fixed(100000, 7200, "0.2", "0")
    assert one == Decimal("20")
    cost = cost_breakdown(energy_quantity=one * 2, price_per_unit="2",
                          distance_m=Decimal(200000), duration_s=Decimal(14400),
                          vehicle_count=2, days=1, vehicle=VEHICLE, scope="variable")
    assert cost["total_eur"] == Decimal("80")
    assert emissions(energy_quantity=one*2, factors={"direct": "2.7", "well_to_wheel": "3.3"},
                     perimeter="direct") == Decimal("108")
    assert emissions(energy_quantity=one*2, factors={"direct": "2.7", "well_to_wheel": "3.3"},
                     perimeter="well_to_wheel") == Decimal("132")


def test_fixed_allocation_no_double_count_and_safe_zero():
    shares = allocate_by_service_hours(Decimal("101.1"),
                                      {"A": Decimal("10"), "B": Decimal("20")})
    assert sum(shares.values()) == Decimal("101.1")
    assert safe_ratio(Decimal(25), Decimal(0)) is None
    complete = cost_breakdown(energy_quantity=Decimal(0), price_per_unit="0",
                              distance_m=Decimal(0), duration_s=Decimal(3600),
                              vehicle_count=1, days=1, vehicle=VEHICLE, scope="complete",
                              infrastructure_daily_eur="3")
    assert complete["labor_eur"] == Decimal("15")
    assert complete["infrastructure_eur"] == Decimal("3")
    assert complete["vehicle_fixed_eur"] > 0


def test_error_on_missing_scope_factor_or_negative():
    with pytest.raises(MissingReference):
        emissions(energy_quantity=Decimal(1), factors={}, perimeter="direct")
    with pytest.raises(DomainError):
        emissions(energy_quantity=Decimal(1), factors={"lifecycle": "1"}, perimeter="lifecycle")
    with pytest.raises(DomainError):
        energy_fixed(-1, 1, "0.1", "0")
    with pytest.raises(DomainError):
        allocate_by_service_hours(Decimal(1), {"A": Decimal(0)})
