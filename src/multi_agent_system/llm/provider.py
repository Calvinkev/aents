from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import json
import logging
import os
from typing import Any, Dict, List, Optional
import httpx

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    content: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    finish_reason: str = "stop"
    raw_response: Dict[str, Any] = field(default_factory=dict)


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, model: Optional[str] = None, temperature: float = 0.0, max_tokens: Optional[int] = None, response_format: Optional[Dict[str, Any]] = None) -> LLMResponse:
        pass


class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, default_model: Optional[str] = None):
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.base_url = (base_url or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.default_model = default_model or os.getenv("LLM_MODEL", "gpt-4o-mini")

    async def generate(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, model: Optional[str] = None, temperature: float = 0.0, max_tokens: Optional[int] = None, response_format: Optional[Dict[str, Any]] = None) -> LLMResponse:
        model_name = model or self.default_model
        if not self.api_key and "localhost" not in self.base_url:
            raise ValueError("LLM API key is missing.")

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        payload = {"model": model_name, "messages": messages, "temperature": temperature}
        if max_tokens: payload["max_tokens"] = max_tokens
        if response_format: payload["response_format"] = response_format
        if tools: payload["tools"] = tools

        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            choice = data["choices"][0]
            message = choice["message"]
            content = message.get("content") or ""
            usage = data.get("usage", {})
            p_tokens = usage.get("prompt_tokens", 0)
            c_tokens = usage.get("completion_tokens", 0)
            return LLMResponse(content=content, model=model_name, prompt_tokens=p_tokens, completion_tokens=c_tokens, total_tokens=p_tokens + c_tokens, estimated_cost=0.0001)


class MockLLMProvider(LLMProvider):
    def __init__(self, default_model: str = "mock-gpt"):
        self.default_model = default_model

    async def generate(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, model: Optional[str] = None, temperature: float = 0.0, max_tokens: Optional[int] = None, response_format: Optional[Dict[str, Any]] = None) -> LLMResponse:
        last_message = messages[-1]["content"] if messages else ""
        content = f"Mock LLM Response for: {last_message[:100]}"
        if response_format and response_format.get("type") == "json_object":
            content = json.dumps({"subtasks": [{"id": "s1", "title": "Analyze Request & Environment", "objective": "Inspect context.", "required_capabilities": ["research"], "dependencies": [], "acceptance_criteria": ["Context inspected"]}, {"id": "s2", "title": "Execute Solution & Fixes", "objective": "Perform core implementation.", "required_capabilities": ["coding"], "dependencies": ["s1"], "acceptance_criteria": ["Solution produced"]}]})
        p_tokens = len(str(messages)) // 4
        c_tokens = len(content) // 4
        return LLMResponse(content=content, model=model or self.default_model, prompt_tokens=p_tokens, completion_tokens=c_tokens, total_tokens=p_tokens + c_tokens, estimated_cost=0.0001)


def get_llm_provider(provider_type: Optional[str] = None, api_key: Optional[str] = None, base_url: Optional[str] = None) -> LLMProvider:
    provider_name = (provider_type or os.getenv("LLM_PROVIDER", "openai")).lower()
    if provider_name == "openai":
        key = api_key or os.getenv("LLM_API_KEY", "")
        if not key:
            return MockLLMProvider()
        return OpenAILLMProvider(api_key=key, base_url=base_url)
    return MockLLMProvider()
