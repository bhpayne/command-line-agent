
# Use

There are two different modes supported: constrained (read-only) and isolated (read, write, edit, delete allowed). The specific set of commands for each mode are in the `allowed_commands` function in `configure_llm.py`.

Both modes default to relying on Internet access for calls to the LLM. 

## constrained to read-only

This mode is intended to be safe to run on a bare-metal environment as the commands the agent has access to are constrained and run as user (not root).

In your shell set the Gemini API key
```
export GEMINI_API_KEY="xxxxxxxxxxxxxxxxxxxxxxx"
```
The files in `src/` can run with just `python3` since there are no third-party dependencies. Launch the agent using
```
cd src/
python3 main_loop.py 
```
The initial response should be
```
Using model 'gemini-2.5-flash' from 'https://generativelanguage.googleapis.com/v1beta/openai' (Standard Library Client)
[INFO] Type 'quit' at any time to exit the agent loop.

['/path/to/command-line-agent/src/' 🙂]
```

## containerized Use -- isolated environment

In this mode a container (e.g., Docker, Podman, Apptainer) or a Virtual Machine can isolate the agent and the agent has access to potentially destructive commands.

To use the agent on a virtual machine,
```
cd src/
python3 main_loop.py --isolated
```

If the isolation is a container, then build and launch a Docker container using
```
make container_build
make container_live_as_root
```
which puts you inside the container where you can then run
```
[root@30009b4ce9d2 opt]# python3 /agent/main_loop.py --isolated --dir /opt
Using model 'gemini-2.5-flash' from 'https://generativelanguage.googleapis.com/v1beta/openai'
[INFO] Type 'quit' at any time to exit the agent loop.

['/opt' 🙂] clone the repo git@github.com:yourusername/yourproject.git
```
The `container_live_as_root` targetr only has local storage (no mount to host).

# Example capabilities

- inspect this directory tree and find the 5 largest files
- based on logs in `/var/log/dmesg`, what caused the most recent system crash?

# Context

> Unlike chatbots that respond in a request-and-reply fashion, AI agents are systems that take high-level goals as the input, then autonomously reason, plan, and execute tasks to achieve those goals. A key enabler for this process is tool calling (a.k.a. function calling): instead of just replying with text, the agent can invoke external tools or APIs to actually carry out actions, determine their outcomes, and plan for the next steps.

[source](https://developer.nvidia.com/blog/create-your-own-bash-computer-use-agent-with-nvidia-nemotron-in-one-hour/)

# Workflow

In `main_loop.py`
1. The user issues a high-level instruction, such as changing directories, copying files, or inspecting document contents.
1. The LLM interprets the request, breaks it into concrete steps, and uses the Bash class when command execution is needed. Some tasks may require no execution at all, while others may span multiple commands. After each run, the model receives the output and decides the next step or when to stop.
1. Once the task is complete, whether successful or halted by an error, the agent returns the result to the user and waits for the next instruction.

# From

From <https://developer.nvidia.com/blog/create-your-own-bash-computer-use-agent-with-nvidia-nemotron-in-one-hour/>
and the accompanying <https://www.youtube.com/watch?v=F7f-eFou2-o> and <https://github.com/NVIDIA/GenerativeAIExamples/tree/be9acc9b9286a8b4ba3ef6d56dcb7ff989d5681a/nemotron/LLM/bash_computer_use_agent>


# Monitor API usage for Gemini

<https://aistudio.google.com/usage>
