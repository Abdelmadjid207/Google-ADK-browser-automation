import os
os.environ["HTTPX_FORCE_IPV4"] = "1"

from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams, StdioServerParameters


browser_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="browser_agent",
    instruction=(
        "You are a browser execution agent.\n"
        "You ONLY execute explicit browser actions using tools.\n\n"
        "Rules:\n"
        "- Do not plan\n"
        "- Do not guess\n"
        "- Execute exactly ONE instruction per turn\n"
        "- Report results clearly (success, failure, observations)\n"
    ),
    tools=[MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@playwright/mcp@latest"],
            ),
            timeout=30,
        )
    )],
)

navigation_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="navigation_helper_agent",
    instruction=(
        "You are a navigation planning agent.\n\n"
        "Input:\n"
        "- User goal\n"
        "- Latest browser feedback\n\n"
        "Your task:\n"
        "- Decide the NEXT SINGLE browser action\n"
        "- Output it clearly for execution\n"
        "- If information is missing, request it (e.g., screenshot)\n\n"
        "Never output multiple steps at once."
    ),
)


loop_agent = LoopAgent(
    name="browser_control_loop",
    sub_agents=[
        navigation_agent,
        browser_agent,
    ],
    max_iterations=7,   # safety guard (important)
)

root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="root_agent",
    instruction=(
        "You are the entry point agent.\n"
        "Forward the user's request to the browser_control_loop\n"
        "and return the final answer."
    ),
    sub_agents=[loop_agent],
)

