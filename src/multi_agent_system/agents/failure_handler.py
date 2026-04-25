from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class FailureDecision:
    should_retry: bool
    should_escalate: bool
    backoff_seconds: float
    use_fallback_specialist: bool


class FailureHandler:
    def __init__(
        self,
        retry_backoff_seconds: List[float],
        failure_threshold: int,
        use_fallback_specialist: bool,
    ) -> None:
        self.retry_backoff_seconds = retry_backoff_seconds
        self.failure_threshold = failure_threshold
        self.use_fallback_specialist = use_fallback_specialist
        self.failure_counts: Dict[str, int] = {}

    def record_failure(self, specialist_name: str) -> None:
        self.failure_counts[specialist_name] = self.failure_counts.get(specialist_name, 0) + 1

    def _is_circuit_open(self, specialist_name: str) -> bool:
        return self.failure_counts.get(specialist_name, 0) >= self.failure_threshold

    def decide(self, specialist_name: str, retry_index: int, max_retries: int) -> FailureDecision:
        circuit_open = self._is_circuit_open(specialist_name)
        should_retry = retry_index < max_retries and not circuit_open
        should_escalate = (retry_index >= max_retries) or circuit_open

        backoff = 0.0
        if should_retry:
            idx = min(retry_index, len(self.retry_backoff_seconds) - 1)
            jitter = random.uniform(0.0, 0.05)
            backoff = self.retry_backoff_seconds[idx] + jitter

        return FailureDecision(
            should_retry=should_retry,
            should_escalate=should_escalate,
            backoff_seconds=backoff,
            use_fallback_specialist=self.use_fallback_specialist and circuit_open,
        )

    @staticmethod
    def apply_backoff(seconds: float) -> None:
        if seconds > 0:
            time.sleep(seconds)
