"""
LLM agent loop for natural language queries.
Supports Claude (Anthropic) and Ollama backends, selected via LLM_BACKEND env var.
"""

import json
import os
from typing import Any

from tools import TOOL_DEFINITIONS, TOOL_DISPATCH

SYSTEM_PROMPT = """You are SniperStation, an assistant that monitors two succulent planters and the home environment in Orlando, FL.
You have access to real-time sensor data: exterior temperature, humidity, light, soil moisture (2 planters), water level, pump history, and indoor conditions for two bedrooms.
Answer in the same language the user writes in (Spanish or English). Be concise and friendly.
Use the tools to fetch real data before answering — never make up sensor values.
If no data is available yet (sensors not connected), say so clearly."""


def _dispatch_tool(name: str, inputs: dict) -> str:
    fn = TOOL_DISPATCH.get(name)
    if fn is None:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        result = fn(**inputs)
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


class ClaudeBackend:
    def __init__(self):
        import anthropic
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.model = "claude-haiku-4-5-20251001"  # fast + cheap for sensor queries

    def query(self, user_message: str) -> str:
        messages = [{"role": "user", "content": user_message}]

        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        return block.text
                return "(no response)"

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = _dispatch_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })
                messages.append({"role": "user", "content": tool_results})
                continue

            break

        return "(unexpected response)"


class OllamaBackend:
    def __init__(self):
        import httpx
        self.http = httpx.Client(timeout=60)
        self.url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        self.model = os.environ.get("OLLAMA_MODEL", "llama3.2")

    def query(self, user_message: str) -> str:
        # Build OpenAI-compatible tool definitions
        tools = [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["input_schema"],
                },
            }
            for t in TOOL_DEFINITIONS
        ]

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        while True:
            resp = self.http.post(
                f"{self.url}/v1/chat/completions",
                json={"model": self.model, "messages": messages, "tools": tools},
            )
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]
            msg = choice["message"]
            messages.append(msg)

            if choice["finish_reason"] == "tool_calls":
                for call in msg.get("tool_calls", []):
                    fn_name = call["function"]["name"]
                    fn_args = json.loads(call["function"]["arguments"])
                    result = _dispatch_tool(fn_name, fn_args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "content": result,
                    })
                continue

            return msg.get("content", "(no response)")


def get_backend() -> Any:
    backend = os.environ.get("LLM_BACKEND", "claude").lower()
    if backend == "ollama":
        return OllamaBackend()
    return ClaudeBackend()
