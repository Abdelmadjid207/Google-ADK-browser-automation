import os
os.environ["HTTPX_FORCE_IPV4"] = "1"

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams, StdioServerParameters

# -------------------------------------------------------------------
# Browser Agent (Execution Only)
# -------------------------------------------------------------------
browser_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="browser_agent",
    instruction=(
        "You are a low-level browser execution agent.\n"
        "You ONLY perform concrete browser actions using tools:\n"
        "- navigate to URLs\n"
        "- click elements\n"
        "- fill forms\n"
        "- take screenshots\n\n"
        "You do NOT decide what to do next.\n"
        "You strictly execute the steps given to you.\n"
        "After every action, confirm whether it succeeded."
    ),
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=["-y", "@playwright/mcp@latest"],
                ),
                timeout=30,
            ),
        )
    ],
)

# -------------------------------------------------------------------
# Navigation / Helper Agent (Planner)
# -------------------------------------------------------------------
navigation_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="navigation_helper_agent",
    instruction=(
        "You are a web navigation and reasoning assistant.\n"
        "Your job is to:\n"
        "- Understand the user's goal\n"
        "- Analyze the current web page (from screenshots / page info)\n"
        "- Decide the NEXT BEST browser action\n\n"
        "You do NOT use browser tools directly.\n"
        "You output clear, step-by-step instructions for the browser agent.\n"
        "Be extremely explicit (selectors, expected results, fallback steps).\n"
        "If the page is unclear, ask the browser agent for a screenshot."
    ),
)

# -------------------------------------------------------------------
# Root Orchestrator Agent
# -------------------------------------------------------------------
root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="root_orchestrator_agent",
    instruction=(
        "You are the orchestrator of a multi-agent web automation system.\n\n"
        "Workflow:\n"
        "1. Receive the user's request\n"
        "2. Delegate planning to `navigation_helper_agent`\n"
        "3. Send the resulting steps to `browser_agent` for execution\n"
        "4. Observe results and repeat until the task is complete\n\n"
        "Rules:\n"
        "- Navigation decisions ALWAYS come from navigation_helper_agent\n"
        "- Browser actions ALWAYS come from browser_agent\n"
        "- Never let the browser agent guess or improvise\n"
        "- Stop when the user's goal is satisfied"
    ),
    sub_agents=[
        navigation_agent,
        browser_agent,
    ],
)
