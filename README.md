


# Context

> Unlike chatbots that respond in a request-and-reply fashion, AI agents are systems that take high-level goals as the input, then autonomously reason, plan, and execute tasks to achieve those goals. A key enabler for this process is tool calling (a.k.a. function calling): instead of just replying with text, the agent can invoke external tools or APIs to actually carry out actions, determine their outcomes, and plan for the next steps.

# Workflow

1. The user issues a high-level instruction, such as changing directories, copying files, or inspecting document contents.
1. The LLM interprets the request, breaks it into concrete steps, and uses the Bash class when command execution is needed. Some tasks may require no execution at all, while others may span multiple commands. After each run, the model receives the output and decides the next step or when to stop.
1. Once the task is complete, whether successful or halted by an error, the agent returns the result to the user and waits for the next instruction.

# From
From <https://developer.nvidia.com/blog/create-your-own-bash-computer-use-agent-with-nvidia-nemotron-in-one-hour/>
and the accompanying <https://www.youtube.com/watch?v=F7f-eFou2-o> and <https://github.com/NVIDIA/GenerativeAIExamples/tree/be9acc9b9286a8b4ba3ef6d56dcb7ff989d5681a/nemotron/LLM/bash_computer_use_agent>


# Monitor API usage

<https://aistudio.google.com/usage>
