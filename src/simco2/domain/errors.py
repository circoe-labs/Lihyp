"""Erreurs de domaine sérialisables sans couplage à HTTP."""
from __future__ import annotations


class DomainError(Exception):
    def __init__(self, code: str, message: str, *, details: dict | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def as_dict(self) -> dict:
        return {"code": self.code, "message": self.message, "details": self.details}


class MissingReference(DomainError):
    def __init__(self, message: str):
        super().__init__("missing_reference", message)


class UnsupportedMode(DomainError):
    def __init__(self, message: str):
        super().__init__("unsupported_mode", message)


class RoutingFailure(DomainError):
    def __init__(self, code: str, message: str):
        super().__init__(code, message)
