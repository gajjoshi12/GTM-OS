"""
The LLM layer every agent reasons through.

Provider-agnostic by design (spec section 8): one internal interface, several
provider adapters, switched with `LLM_PROVIDER` in .env.

    LLM_PROVIDER=groq        (default) -> GROQ_API_KEY,      GROQ_MODEL,      GROQ_WORKER_MODEL
    LLM_PROVIDER=anthropic             -> ANTHROPIC_API_KEY, ANTHROPIC_MODEL, ANTHROPIC_WORKER_MODEL
    LLM_PROVIDER=openai                -> OPENAI_API_KEY,    OPENAI_MODEL,    OPENAI_WORKER_MODEL

Two models per provider:
  * `model`        the reasoning model — AI CMO, ICP derivation, strategy, decisions
  * `worker_model` the cheap/fast model — bulk personalisation, reply classification

When the active provider's key is blank, `live` is False and every agent falls back
to the deterministic simulations in `apps/agents/simulations.py`, so the whole
closed loop stays demoable with zero credentials.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

from django.conf import settings

log = logging.getLogger(__name__)

# Reasoning models (DeepSeek-R1 distills, Qwen3, ...) emit a <think> block before
# the answer. Strip it everywhere rather than relying on a per-model parameter.
_THINK_RE = re.compile(r"<think>.*?</think>\s*", re.S | re.I)


def strip_reasoning(text: str) -> str:
    return _THINK_RE.sub("", text or "").strip()


# --------------------------------------------------------------------------- providers
class BaseProvider:
    """One LLM vendor behind the interface the agents call."""

    name = ""

    def __init__(self, api_key: str, model: str, worker_model: str):
        self.api_key = api_key
        self.model = model
        self.worker_model = worker_model
        self._client = None

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def complete(self, system: str, user: str, *, model: str, max_tokens: int, json_mode: bool, effort: str | None) -> str:
        raise NotImplementedError

    def ping(self) -> dict:
        raise NotImplementedError


class GroqProvider(BaseProvider):
    """Groq — OpenAI-compatible chat completions on their LPU inference stack."""

    name = "groq"

    @property
    def available(self) -> bool:
        try:
            import groq  # noqa: F401
        except Exception:
            return False
        return bool(self.api_key)

    @property
    def client(self):
        if self._client is None:
            import groq

            kwargs: dict[str, Any] = {
                "api_key": self.api_key,
                # Groq's free tier has tight RPM/TPM limits; the SDK backs off for us.
                "max_retries": settings.GROQ_MAX_RETRIES,
                "timeout": settings.GROQ_TIMEOUT,
                # ALWAYS pass an explicit base_url. The SDK falls back to the
                # GROQ_BASE_URL env var and only guards with `is None`, so the
                # empty string python-dotenv exports for a blank key would be
                # taken as the base URL and every request would fail with
                # "Request URL is missing an 'http://' or 'https://' protocol".
                "base_url": settings.GROQ_BASE_URL or "https://api.groq.com",
            }
            self._client = groq.Groq(**kwargs)
        return self._client

    def complete(self, system, user, *, model, max_tokens, json_mode, effort):
        import groq

        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        base: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": settings.GROQ_TEMPERATURE,
            "max_completion_tokens": max_tokens,
        }
        if json_mode:
            # Groq's JSON mode needs the word "JSON" in the prompt — complete_json guarantees it.
            base["response_format"] = {"type": "json_object"}
        if effort and settings.GROQ_SEND_REASONING_EFFORT:
            base["reasoning_effort"] = effort

        # Graceful degradation: not every model on Groq accepts every parameter.
        attempts: list[dict[str, Any]] = [base]
        if json_mode:
            attempts.append({k: v for k, v in base.items() if k != "response_format"})
        attempts.append({k: v for k, v in attempts[-1].items() if k != "reasoning_effort"})
        legacy = {k: v for k, v in attempts[-1].items() if k != "max_completion_tokens"}
        legacy["max_tokens"] = max_tokens
        attempts.append(legacy)

        last_error: Exception | None = None
        for i, kwargs in enumerate(attempts):
            try:
                response = self.client.chat.completions.create(**kwargs)
                break
            except groq.BadRequestError as exc:
                last_error = exc
                log.warning("groq rejected params (attempt %s/%s): %s", i + 1, len(attempts), exc)
        else:
            raise RuntimeError(f"Groq rejected the request: {last_error}")

        choice = response.choices[0]
        if choice.finish_reason == "length":
            log.warning("groq response hit the token ceiling (%s) - output may be truncated", max_tokens)
        return strip_reasoning(choice.message.content or "")

    def ping(self) -> dict:
        models = [m.id for m in self.client.models.list().data]
        return {"models_available": len(models), "sample": sorted(models)[:8]}


class AnthropicProvider(BaseProvider):
    """Anthropic Claude — optional alternative."""

    name = "anthropic"

    @property
    def available(self) -> bool:
        try:
            import anthropic  # noqa: F401
        except Exception:
            return False
        return bool(self.api_key)

    @property
    def client(self):
        if self._client is None:
            import anthropic

            self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    def complete(self, system, user, *, model, max_tokens, json_mode, effort):
        kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "system": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            "messages": [{"role": "user", "content": user}],
            "thinking": {"type": "adaptive"},
        }
        if effort:
            kwargs["output_config"] = {"effort": effort}
        response = self.client.messages.create(**kwargs)
        if getattr(response, "stop_reason", None) == "refusal":
            details = getattr(response, "stop_details", None)
            raise RuntimeError(f"Model refused: {getattr(details, 'explanation', '') or 'safety refusal'}")
        return "".join(b.text for b in response.content if getattr(b, "type", "") == "text")

    def ping(self) -> dict:
        return {"models_available": len(list(self.client.models.list(limit=5).data))}


class OpenAIProvider(BaseProvider):
    """OpenAI — optional alternative (also covers OpenAI-compatible gateways)."""

    name = "openai"

    @property
    def available(self) -> bool:
        try:
            import openai  # noqa: F401
        except Exception:
            return False
        return bool(self.api_key)

    @property
    def client(self):
        if self._client is None:
            import openai

            # Same empty-string-from-dotenv trap as Groq: pass an explicit URL.
            kwargs: dict[str, Any] = {
                "api_key": self.api_key,
                "base_url": settings.OPENAI_BASE_URL or "https://api.openai.com/v1",
            }
            self._client = openai.OpenAI(**kwargs)
        return self._client

    def complete(self, system, user, *, model, max_tokens, json_mode, effort):
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_completion_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = self.client.chat.completions.create(**kwargs)
        return strip_reasoning(response.choices[0].message.content or "")

    def ping(self) -> dict:
        return {"models_available": len(list(self.client.models.list().data))}


PROVIDERS = {"groq": GroqProvider, "anthropic": AnthropicProvider, "openai": OpenAIProvider}


def _build_provider(name: str) -> BaseProvider:
    name = (name or "groq").strip().lower()
    cls = PROVIDERS.get(name, GroqProvider)
    creds = {
        "groq": (settings.GROQ_API_KEY, settings.GROQ_MODEL, settings.GROQ_WORKER_MODEL),
        "anthropic": (settings.ANTHROPIC_API_KEY, settings.ANTHROPIC_MODEL, settings.ANTHROPIC_WORKER_MODEL),
        "openai": (settings.OPENAI_API_KEY, settings.OPENAI_MODEL, settings.OPENAI_WORKER_MODEL),
    }[cls.name]
    return cls(*creds)


# --------------------------------------------------------------------------- facade
class LLM:
    """What every agent talks to. Stable across providers."""

    def __init__(self) -> None:
        self.provider = _build_provider(settings.LLM_PROVIDER)

    # -- introspection used by the health endpoint and the run log -----------
    @property
    def provider_name(self) -> str:
        return self.provider.name

    @property
    def model(self) -> str:
        return self.provider.model

    @property
    def worker_model(self) -> str:
        return self.provider.worker_model

    @property
    def live(self) -> bool:
        return self.provider.available

    @property
    def key_env_var(self) -> str:
        return f"{self.provider.name.upper()}_API_KEY"

    def status(self) -> dict:
        return {
            "provider": self.provider_name,
            "model": self.model,
            "worker_model": self.worker_model,
            "live": self.live,
            "key_env_var": self.key_env_var,
        }

    # -- the two calls the agents make ---------------------------------------
    def complete(self, system: str, user: str, *, max_tokens: int = 8000, worker: bool = False,
                 effort: str | None = None, json_mode: bool = False) -> str:
        if not self.live:
            raise RuntimeError(f"LLM not configured ({self.key_env_var} missing)")
        model = self.worker_model if worker else self.model
        return self.provider.complete(
            system, user, model=model, max_tokens=max_tokens, json_mode=json_mode, effort=effort
        )

    def complete_json(self, system: str, user: str, **kw) -> Any:
        """Ask for JSON and parse it robustly (strips reasoning blocks and code fences)."""
        # The literal word "JSON" here is required by Groq/OpenAI JSON mode.
        text = self.complete(
            system + "\n\nRespond with valid JSON only. No prose, no markdown fences.",
            user, json_mode=True, **kw,
        )
        return parse_json(text)


def parse_json(text: str) -> Any:
    text = strip_reasoning(text)
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # salvage the first {...} or [...] block
        m = re.search(r"(\{.*\}|\[.*\])", text, re.S)
        if m:
            return json.loads(m.group(1))
        raise


llm = LLM()
