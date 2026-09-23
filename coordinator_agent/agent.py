import os

from coordinator_agent.auth import (
    CloneableAsyncClient,
    GoogleCloudAuth,
)

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
)


def required_env(name: str) -> str:
    """
    Return a required environment variable.
    """

    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            "Missing required environment variable: "
            f"{name}"
        )

    return value


authenticated_http_client = CloneableAsyncClient(
    auth=GoogleCloudAuth(),

    timeout=120.0,

    headers={
        "Content-Type": "application/json",
    },
)


remote_research_agent = RemoteA2aAgent(
    name="research_agent",

    description=(
        "Remote research specialist that gathers "
        "information and summarizes findings."
    ),

    agent_card=required_env(
        "RESEARCH_AGENT_CARD_URL"
    ),

    use_legacy=False,

    httpx_client=authenticated_http_client,
)


remote_analytics_agent = RemoteA2aAgent(
    name="analytics_agent",

    description=(
        "Remote mathematics and analytics specialist."
    ),

    agent_card=required_env(
        "ANALYTICS_AGENT_CARD_URL"
    ),

    use_legacy=False,

    httpx_client=authenticated_http_client,
)


root_agent = Agent(
    name="coordinator_agent",

    model="gemini-2.5-flash",

    description=(
        "Coordinator that delegates to remote "
        "A2A specialists."
    ),

    instruction="""
    You are the central corporate coordinator.

    Routing rules:

    1. Delegate research and information requests to
       research_agent.

    2. Delegate arithmetic, mathematics, calculations,
       and analytics requests to analytics_agent.

    3. For mixed research and calculation requests:
       a. Invoke research_agent first.
       b. Wait for the research result.
       c. Invoke analytics_agent with the required values.
       d. Wait for the analytics result.
       e. Combine both results.

    4. Do not perform specialist work yourself when a
       matching remote specialist exists.

    5. Return one complete final response.
    """,

    sub_agents=[
        remote_research_agent,
        remote_analytics_agent,
    ],
)