import json
import urllib.request
import urllib.error
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

    def add_assistant_message(self, message):
        self.messages.append({"role": "assistant", "content": message})

    def add_tool_message(self, message, id):
        self.messages.append({"role": "tool", "content": str(message), "tool_call_id": id})

    def to_list(self) -> List[Dict[str, str]]:
        """
        Convert to a list of messages.
        """
        return [self.system_message] + self.messages


# Classes to replicate the OpenAI SDK objects expected by main_loop.py
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
    An abstraction to prompt an LLM with standard library urllib requests.
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
        # Normalize endpoint URL
        base_url = self.config.llm_base_url.rstrip("/")
        if not base_url.endswith("/chat/completions"):
            url = f"{base_url}/chat/completions"
        else:
            url = base_url

        # Build payload according to OpenAI specification
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

        # Headers. Manually providing exactly one Authorization header prevents the
        # "Multiple authentication credentials received" error that sometimes occurs with 
        # newer Google Studio keys (such as keys starting with 'AQ.').
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
            print(f"\n[Error] API call failed with status {e.code}:")
            try:
                # Format JSON error messages for easier debugging
                print(json.dumps(json.loads(error_content), indent=2))
            except Exception:
                print(error_content)
            return f"Error: API call failed with status code {e.code}", []
        except Exception as e:
            print(f"\n[Error] Connection failed: {e}")
            return "Error: Connection failed.", []

        # Parse the JSON response
        choices = res_json.get("choices", [])
        if not choices:
            return "", []

        choice_message = choices[0].get("message", {})
        content = choice_message.get("content") or ""
        
        # Build structure-compatible tool call objects
        raw_tool_calls = choice_message.get("tool_calls") or []
        tool_calls = []
        for tc_dict in raw_tool_calls:
            func_dict = tc_dict.get("function", {})
            func_obj = ToolCallFunction(
                name=func_dict.get("name", ""),
                arguments=func_dict.get("arguments", "{}")
            )
            tool_calls.append(ToolCall(
                id=tc_dict.get("id", ""),
                function=func_obj,
                type=tc_dict.get("type", "function")
            ))

        return content, tool_calls