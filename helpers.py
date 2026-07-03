import json
import urllib.request
import urllib.error
import uuid
from typing import Any, Dict, List, Tuple

from configure_llm import Config

class Messages:
    """
    An abstraction for a list of system/user/assistant/tool messages.
    """

    def __init__(self, system_message: str = ""):
        self.system_message = None
        self.messages = []
        self.set_system_message(system_message)

    def set_system_message(self, message):
        self.system_message = {"role": "system", "content": message}

    def add_user_message(self, message):
        self.messages.append({"role": "user", "content": message})

    def add_assistant_message(self, message, tool_calls=None):
        payload = {"role": "assistant", "content": message or ""}
        if tool_calls:
            # Reconstruct the tool_calls list to match OpenAI specification
            payload["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in tool_calls
            ]
        self.messages.append(payload)

    def add_tool_message(self, message, id, name):
        # Convert output dicts (like stdout/stderr results) into standard JSON strings
        if isinstance(message, dict):
            content_str = json.dumps(message)
        else:
            content_str = str(message)

        # Gemini strictly requires the "name" field to match the original function name
        self.messages.append({
            "role": "tool",
            "content": content_str,
            "tool_call_id": id,
            "name": name
        })

    def to_list(self) -> List[Dict[str, str]]:
        """
        Convert to a list of messages.
        """
        return [self.system_message] + self.messages


# Simple classes to mimic the OpenAI tool call objects
class ToolCallFunction:
    def __init__(self, name: str, arguments: str):
        self.name = name
        self.arguments = arguments

class ToolCall:
    def __init__(self, id: str, function: ToolCallFunction, type: str = "function"):
        self.id = id
        self.function = function
        self.type = type


class LLM:
    """
    An abstraction to prompt an LLM using Python's standard library.
    """

    def __init__(self, config: Config):
        self.config = config
        print(f"Using model '{config.llm_model_name}' from '{config.llm_base_url}' (Standard Library Client)")

    def query(
        self,
        messages: Messages,
        tools: List[Dict[str, Any]],
        max_tokens=None,
    ) -> Tuple[str, List[ToolCall]]:
        base_url = self.config.llm_base_url.rstrip("/")
        if not base_url.endswith("/chat/completions"):
            url = f"{base_url}/chat/completions"
        else:
            url = base_url

        payload = {
            "model": self.config.llm_model_name,
            "messages": messages.to_list(),
            "temperature": self.config.llm_temperature,
            "top_p": self.config.llm_top_p,
        }
        
        if tools:
            payload["tools"] = tools
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.llm_api_key}"
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req) as response:
                res_data = response.read().decode("utf-8")
                res_json = json.loads(res_data)
        except urllib.error.HTTPError as e:
            error_content = e.read().decode("utf-8")
            print(f"\n[Error] API Request failed (HTTP {e.code}):")
            try:
                err_json = json.loads(error_content)
                print(json.dumps(err_json, indent=2))
            except Exception:
                print(error_content)
            return f"Error: API call failed with status code {e.code}", []
        except Exception as e:
            print(f"\n[Error] Connection failed: {e}")
            return f"Error: Failed to connect to the model provider.", []

        choices = res_json.get("choices", [])
        if not choices:
            return "", []

        message_data = choices[0].get("message", {})
        content = message_data.get("content") or ""
        
        raw_tool_calls = message_data.get("tool_calls") or []
        tool_calls = []
        for tc_dict in raw_tool_calls:
            func_dict = tc_dict.get("function", {})
            func_obj = ToolCallFunction(
                name=func_dict.get("name", ""),
                arguments=func_dict.get("arguments", "{}")
            )
            
            # Fallback UUID handles scenarios where Gemini leaves the tool call ID blank
            tc_id = tc_dict.get("id") or f"call_{uuid.uuid4().hex[:12]}"
            
            tool_calls.append(ToolCall(
                id=tc_id,
                function=func_obj,
                type=tc_dict.get("type", "function")
            ))

        return content, tool_calls