from __future__ import annotations


def run(target: str, ports: list[int]) -> dict:
    open_ports = [p for p in ports if p in {80, 443, 22, 25, 8080}]
    return {"target": target, "checked_ports": ports, "open_ports": open_ports}
