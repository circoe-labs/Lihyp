"""DTO métier stable pour adaptateurs et calculs; sans dépendance framework."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Protocol


class SolveStatus(StrEnum):
    OPTIMAL = "optimal"
    FEASIBLE_NOT_PROVEN = "feasible_not_proven"
    INFEASIBLE_PROVEN = "infeasible_proven"
    TIMEOUT_WITH_INCUMBENT = "timeout_with_incumbent"
    TIMEOUT_NO_SOLUTION = "timeout_no_solution"
    INVALID_INPUT = "invalid_input"
    PROVIDER_ERROR = "provider_error"


@dataclass(frozen=True)
class RouteResult:
    distance_m: Decimal
    duration_s: Decimal
    profile: str
    provider: str
    provider_version: str
    valid_at: str
    geometry: dict | None = None
    restrictions: tuple[str, ...] = ()


class RoutingProvider(Protocol):
    def route(self, origin: tuple[float, float], destination: tuple[float, float],
              profile: str, departure_time: datetime | None = None) -> RouteResult: ...


@dataclass(frozen=True)
class SolveResult:
    status: SolveStatus
    result: dict
    warnings: tuple[str, ...] = ()
    violations: tuple[str, ...] = ()
    optimality_gap: Decimal | None = None
    lower_bound: Decimal | None = None


class SimulationEngine(Protocol):
    def solve(self, snapshot: dict) -> SolveResult: ...
