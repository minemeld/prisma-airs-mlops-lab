"""Inference client for LLM serving via Vertex AI.

Supports multiple inference backends:
- vertex_ai: Vertex AI Endpoint with vLLM (OpenAI-compatible API)
- local: Local transformers model for development
"""

import os
import httpx
from typing import Any
from pydantic import BaseModel


class InferenceConfig(BaseModel):
    """Configuration for inference backend."""

    backend: str = os.getenv("INFERENCE_BACKEND", "vertex_ai")

    # Vertex AI Endpoint (vLLM with OpenAI-compatible API)
    vertex_endpoint_id: str = os.getenv("VERTEX_ENDPOINT_ID", "")
    vertex_project: str = os.getenv("VERTEX_PROJECT", "jlimon-prod")
    vertex_location: str = os.getenv("VERTEX_LOCATION", "us-central1")

    # Local model path (for development)
    local_model_path: str = os.getenv("MODEL_PATH", "")

    # System prompt for the security advisor
    system_prompt: str = os.getenv(
        "SYSTEM_PROMPT",
        "You are a Cloud Security Advisor trained on NIST cybersecurity frameworks. "
        "Provide specific, actionable security guidance for cloud infrastructure. "
        "Reference relevant NIST controls and best practices in your responses.",
    )


class ChatMessage(BaseModel):
    """A single chat message."""
    role: str  # "system", "user", "assistant"
    content: str


class InferenceClient:
    """Unified client for LLM inference across backends."""

    def __init__(self, config: InferenceConfig | None = None):
        self.config = config or InferenceConfig()
        self._local_pipeline = None
        self._local_tokenizer = None

    async def chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """Send a chat message and get a response.

        Args:
            message: User message text.
            history: Optional list of previous messages [{"role": "user/assistant", "content": "..."}].
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.

        Returns:
            Assistant response text.
        """
        if self.config.backend == "vertex_ai":
            return await self._chat_vertex_ai(message, history, max_tokens, temperature)
        elif self.config.backend == "local":
            return await self._chat_local(message, history, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown backend: {self.config.backend}")

    async def _chat_vertex_ai(
        self,
        message: str,
        history: list[dict[str, str]] | None,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Call Vertex AI endpoint with vLLM completions API.

        The Vertex AI vLLM container exposes /v1/completions (not /v1/chat/completions),
        so we format messages into a Qwen2 chat template prompt.
        """
        if not self.config.vertex_endpoint_id:
            raise ValueError("VERTEX_ENDPOINT_ID not configured")

        # Build prompt using Qwen2 chat template format
        prompt_parts = []
        prompt_parts.append(f"<|im_start|>system\n{self.config.system_prompt}<|im_end|>")
        if history:
            for msg in history:
                prompt_parts.append(f"<|im_start|>{msg['role']}\n{msg['content']}<|im_end|>")
        prompt_parts.append(f"<|im_start|>user\n{message}<|im_end|>")
        prompt_parts.append("<|im_start|>assistant\n")
        prompt = "\n".join(prompt_parts)

        # Vertex AI rawPredict URL
        url = (
            f"https://{self.config.vertex_location}-aiplatform.googleapis.com/v1/"
            f"projects/{self.config.vertex_project}/locations/{self.config.vertex_location}/"
            f"endpoints/{self.config.vertex_endpoint_id}:rawPredict"
        )

        payload = {
            "model": "openapi",  # Vertex AI vLLM launcher overrides served-model-name to 'openapi'
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stop": ["<|im_end|>"],
        }

        # Get access token for GCP auth
        import google.auth
        import google.auth.transport.requests

        credentials, _ = google.auth.default()
        auth_request = google.auth.transport.requests.Request()
        credentials.refresh(auth_request)
        access_token = credentials.token

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        # Extract response from completions format
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("text", "").strip()
        return "I'm sorry, I couldn't generate a response."

    async def _chat_local(
        self,
        message: str,
        history: list[dict[str, str]] | None,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Run inference locally with transformers (for development)."""
        if self._local_pipeline is None:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch

            model_path = self.config.local_model_path
            if not model_path:
                raise ValueError("MODEL_PATH not configured for local backend")

            self._local_tokenizer = AutoTokenizer.from_pretrained(model_path)
            self._local_pipeline = AutoModelForCausalLM.from_pretrained(
                model_path, torch_dtype=torch.bfloat16, device_map="auto"
            )

        # Build chat messages
        messages = [{"role": "system", "content": self.config.system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        # Apply chat template
        text = self._local_tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self._local_tokenizer(text, return_tensors="pt").to(
            self._local_pipeline.device
        )

        outputs = self._local_pipeline.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
        )

        # Decode only the generated tokens (skip input)
        generated = outputs[0][inputs["input_ids"].shape[1]:]
        return self._local_tokenizer.decode(generated, skip_special_tokens=True)

    async def health_check(self) -> dict[str, Any]:
        """Check health of inference backend."""
        if self.config.backend == "vertex_ai":
            return {
                "status": "healthy",
                "backend": "vertex_ai",
                "endpoint": self.config.vertex_endpoint_id,
                "project": self.config.vertex_project,
            }
        elif self.config.backend == "local":
            return {
                "status": "healthy",
                "backend": "local",
                "model": self.config.local_model_path,
            }
        return {"status": "unknown", "backend": self.config.backend}


# Global client instance
_inference_client: InferenceClient | None = None


def get_inference_client() -> InferenceClient:
    """Get or create the global inference client."""
    global _inference_client
    if _inference_client is None:
        _inference_client = InferenceClient()
    return _inference_client
