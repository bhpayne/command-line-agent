

from typing import Any, Dict, List
import re
import subprocess
from config_llm import Config


class Bash:
    """
    An implementation of a tool that executes Bash commands
    """
 
    def __init__(self, cwd: str, allowed_commands: List[str]):
        self.cwd = cwd  # The current working directory
        self._allowed_commands = allowed_commands  # Allowed commands
 
    def exec_bash_command(self, cmd: str) -> Dict[str, str]:
        """
        Execute the bash command after getting confirmation from the user
        """
        if cmd:
            # Check the allowlist
            allowed = True
 
            for cmd_part in self._extract_commands(cmd):
                if cmd_part not in self._allowed_commands:
                    allowed = False
                    break
 
            if not allowed:
                return {"error": "Parts of this command were not in the allowlist."}
 
            return self._run_bash_command(cmd)
        return {"error": "No command was provided"}
 
    def to_json_schema(self) -> Dict[str, Any]:
        """
        Convert the function signature to a JSON schema for LLM tool calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "exec_bash_command",
                "description": "Execute a bash command and return stdout/stderr and the working directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cmd": {
                            "type": "string",
                            "description": "The bash command to execute"
                        }
                    },
                    "required": ["cmd"],
   },
            },
        }
 
    def _run_bash_command(self, cmd: str) -> Dict[str, str]:
        """
        Runs the bash command and catches exceptions (if any).
        """
        stdout = ""
        stderr = ""
        new_cwd = self.cwd
 
        try:
            # Wrap the command so we can keep track of the working directory.
            wrapped = f"{cmd};echo __END__;pwd"
            result = subprocess.run(
                wrapped, shell=True, cwd=self.cwd,
                capture_output=True, text=True,
                executable="/bin/bash"
            )
            stderr = result.stderr
            # Find the separator marker
            split = result.stdout.split("__END__")
            stdout = split[0].strip()
 
            # If no output/error at all, inform that the call was successful.
            if not stdout and not stderr:
                stdout = "Command executed successfully, without any output."
 
            # Get the new working directory, and change it
            new_cwd = split[-1].strip()
            self.cwd = new_cwd
        except Exception as e:
            stdout = ""
            stderr = str(e)
 
        return {"stdout": stdout, "stderr": stderr, "cwd": new_cwd}

