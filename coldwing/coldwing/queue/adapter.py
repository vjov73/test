from __future__ import annotations

from abc import ABC, abstractmethod


class QueueAdapter(ABC):
    @abstractmethod
    def enqueue(self, job_spec: dict) -> str:
        raise NotImplementedError

    @abstractmethod
    def status(self, job_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def result(self, job_id: str) -> dict | None:
        raise NotImplementedError
