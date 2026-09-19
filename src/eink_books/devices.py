from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceProfile:
    name: str
    width: int
    height: int
    dpi: int = 167


DEVICES: dict[str, DeviceProfile] = {
    "kt4": DeviceProfile("kt4", 600, 800, 167),
    "kt": DeviceProfile("kt", 600, 800, 167),
    "k4": DeviceProfile("k4", 600, 800, 167),
    "pw1": DeviceProfile("pw1", 758, 1024, 212),
    "pw3": DeviceProfile("pw3", 1072, 1448, 300),
    "pw5": DeviceProfile("pw5", 1236, 1648, 300),
}


def resolve_device(
    name: str,
    width: int | None = None,
    height: int | None = None,
) -> DeviceProfile:
    key = name.lower().strip()
    if key not in DEVICES:
        known = ", ".join(sorted(DEVICES))
        raise ValueError(f"unknown device {name!r}; known: {known}")
    base = DEVICES[key]
    if width is None and height is None:
        return base
    return DeviceProfile(
        name=base.name,
        width=width or base.width,
        height=height or base.height,
        dpi=base.dpi,
    )
