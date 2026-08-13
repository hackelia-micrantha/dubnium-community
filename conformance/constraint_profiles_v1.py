"""Trusted capability-specific constraint profiles for Gateway v1alpha.

Profiles are runtime/conformance configuration. They are never selected by request
content and this module performs no dynamic loading or remote resolution.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .contract_primitives_v1 import (
    CAPABILITY_NAME,
    ContractError,
    _expect_fields,
    _expect_object,
    _require,
)
from .jcs_v1 import normalize_json

ConstraintKey = tuple[str, int]
RequestedConstraintNormalizer = Callable[[Any], dict[str, Any]]
GrantedConstraintNormalizer = Callable[[Any, Mapping[str, Any]], dict[str, Any]]


@dataclass(frozen=True, slots=True)
class ConstraintProfile:
    """Deterministic validators for one exact capability/schema identity."""

    normalize_requested: RequestedConstraintNormalizer
    normalize_granted: GrantedConstraintNormalizer

    def __post_init__(self) -> None:
        if not callable(self.normalize_requested) or not callable(self.normalize_granted):
            raise TypeError("constraint profile normalizers must be callable")


@dataclass(frozen=True, slots=True, init=False)
class ConstraintProfileRegistry:
    """Immutable trusted registry keyed by ``(capability_name, schema_version)``."""

    _profiles: Mapping[ConstraintKey, ConstraintProfile]

    def __init__(
        self,
        profiles: Mapping[ConstraintKey, ConstraintProfile] | None = None,
    ) -> None:
        normalized: dict[ConstraintKey, ConstraintProfile] = {}
        for key, profile in (profiles or {}).items():
            if (
                not isinstance(key, tuple)
                or len(key) != 2
                or not isinstance(key[0], str)
                or CAPABILITY_NAME.fullmatch(key[0]) is None
                or not isinstance(key[1], int)
                or isinstance(key[1], bool)
                or key[1] < 1
            ):
                raise ValueError("constraint profile key must be (capability_name, positive schema_version)")
            if not isinstance(profile, ConstraintProfile):
                raise TypeError("constraint profile registry values must be ConstraintProfile")
            normalized[(key[0], key[1])] = profile
        object.__setattr__(self, "_profiles", MappingProxyType(normalized))

    def get(self, capability_name: str, schema_version: int) -> ConstraintProfile | None:
        return self._profiles.get((capability_name, schema_version))

    def extend(
        self,
        profiles: Mapping[ConstraintKey, ConstraintProfile],
    ) -> "ConstraintProfileRegistry":
        combined = dict(self._profiles)
        for key, profile in profiles.items():
            if key in combined:
                if isinstance(key, tuple) and len(key) == 2:
                    label = f"{key[0]} v{key[1]}"
                else:
                    label = repr(key)
                raise ValueError(f"constraint profile already registered for {label}")
            combined[key] = profile
        return ConstraintProfileRegistry(combined)

    def __len__(self) -> int:
        return len(self._profiles)


def _profile_object(value: Any, field: str) -> dict[str, Any]:
    """Re-apply the restricted JSON profile to trusted validator output."""

    return _expect_object(normalize_json(value), field)


def _noop_requested(value: Any) -> dict[str, Any]:
    constraints = _expect_object(value, "requested_constraints")
    _expect_fields(constraints, {"max_result_bytes"}, "requested_constraints")
    maximum = _require(constraints, "max_result_bytes", "requested_constraints")
    if not isinstance(maximum, int) or isinstance(maximum, bool) or not 64 <= maximum <= 4096:
        raise ContractError(
            "constraint.max_result_bytes",
            "requested_constraints.max_result_bytes must be an integer from 64 through 4096",
        )
    return {"max_result_bytes": maximum}


def _noop_granted(value: Any, requested: Mapping[str, Any]) -> dict[str, Any]:
    granted = _expect_object(value, "granted_constraints")
    _expect_fields(granted, {"max_result_bytes"}, "granted_constraints")
    maximum = _require(granted, "max_result_bytes", "granted_constraints")
    if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 1:
        raise ContractError(
            "constraint.max_result_bytes",
            "granted max_result_bytes must be a positive integer",
        )
    requested_maximum = requested.get("max_result_bytes")
    if not isinstance(requested_maximum, int) or maximum > requested_maximum:
        raise ContractError(
            "manifest.constraint_widening",
            "granted constraints widen the normalized request",
        )
    return {"max_result_bytes": maximum}


DEFAULT_CONSTRAINT_PROFILES = ConstraintProfileRegistry(
    {
        ("example.noop", 1): ConstraintProfile(
            normalize_requested=_noop_requested,
            normalize_granted=_noop_granted,
        )
    }
)


def normalize_requested_constraints(
    value: Any,
    *,
    capability_name: str,
    schema_version: int,
    profiles: ConstraintProfileRegistry = DEFAULT_CONSTRAINT_PROFILES,
) -> dict[str, Any]:
    constraints = _expect_object(value, "requested_constraints")
    profile = profiles.get(capability_name, schema_version)
    if profile is None:
        if constraints:
            raise ContractError(
                "constraint.unsupported",
                "this capability does not define a requested constraint profile",
            )
        return {}
    return _profile_object(
        profile.normalize_requested(constraints),
        "requested_constraints",
    )


def normalize_granted_constraints(
    value: Any,
    *,
    capability_name: str,
    schema_version: int,
    requested: Mapping[str, Any],
    profiles: ConstraintProfileRegistry = DEFAULT_CONSTRAINT_PROFILES,
) -> dict[str, Any]:
    granted = _expect_object(value, "granted_constraints")
    profile = profiles.get(capability_name, schema_version)
    if profile is None:
        if granted:
            raise ContractError(
                "manifest.constraint_widening",
                "granted constraints are unsupported for this capability",
            )
        return {}
    return _profile_object(
        profile.normalize_granted(granted, requested),
        "granted_constraints",
    )
