from __future__ import annotations

from pydantic import BaseModel, Field


class ScanCreate(BaseModel):
    scope: dict
    profile: str = Field(default="snapshot")
    timeout_s: int = 120
    rate_limit: float = 5.0
    api_shodan: bool = False


class SubscriptionCreate(BaseModel):
    scope_path: str
    profile: str
    cron_expression: str
