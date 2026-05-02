from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, List, Literal, Mapping, Set, Tuple

Operation = Literal[
    "add",
    "view",
    "edit",
    "delete",
    "export",
    "import",
    "approve",
    "reject",
]


@dataclass(frozen=True)
class CPPreset:
    key: str
    title: str
    description: str
    portals: FrozenSet[str]
    # perms: {module_name: {operations}}
    perms: Mapping[str, FrozenSet[Operation]]


OPERATIONS_ORDER: List[Operation] = [
    "add",
    "view",
    "edit",
    "delete",
    "export",
    "import",
    "approve",
    "reject",
]


def _ops(*ops: Operation) -> FrozenSet[Operation]:
    return frozenset(ops)


PRESETS: List[CPPreset] = [
    CPPreset(
        key="none",
        title="None (revoke all)",
        description="Revokes all portals and module permissions for the selected user(s).",
        portals=frozenset(),
        perms={},
    ),
    CPPreset(
        key="staff_standard",
        title="Staff (Standard)",
        description="Typical staff access: dashboards + core modules with view/edit where needed.",
        portals=frozenset({"staff"}),
        perms={
            "dashboard": _ops("view"),
            "customer": _ops("view", "edit"),
            "quotation": _ops("add", "view"),
            "inventory": _ops("view", "add", "edit"),
            "transactions": _ops("view", "add", "edit"),
            "firereport": _ops("view", "add"),
            "services": _ops("view", "add", "edit"),
            "barcode": _ops("view"),
        },
    ),
    CPPreset(
        key="vendor_standard",
        title="Vendor (Standard)",
        description="Vendor portal access with read-only access to vendor-related lists.",
        portals=frozenset({"vendor"}),
        perms={
            "transactions": _ops("view"),
            "inventory": _ops("view"),
            "barcode": _ops("view"),
        },
    ),
    CPPreset(
        key="customer_standard",
        title="Customer (Standard)",
        description="Customer portal access with complaint tracking and project viewing.",
        portals=frozenset({"customer"}),
        perms={
            "firereport": _ops("add", "view"),
            "barcode": _ops("view"),
        },
    ),
]


def preset_by_key(key: str) -> CPPreset:
    for p in PRESETS:
        if p.key == key:
            return p
    return PRESETS[0]


def preset_checkbox_state(preset: CPPreset) -> Tuple[Set[str], Set[Tuple[str, str]]]:
    """
    Returns:
      portals: {"staff", "vendor", ...}
      perms: {("customer","view"), ("inventory","add"), ...}
    """
    portals = set(preset.portals)
    perms: Set[Tuple[str, str]] = set()
    for module_name, ops in preset.perms.items():
        for op in ops:
            perms.add((module_name, op))
    return portals, perms

