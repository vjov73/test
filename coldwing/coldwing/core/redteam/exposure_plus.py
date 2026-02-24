from __future__ import annotations


def run(target: str, ports: list[int]) -> dict:
    suspicious = [p for p in ports if p in {21, 23, 3389}]
    return {"target": target, "high_risk_ports": suspicious}
