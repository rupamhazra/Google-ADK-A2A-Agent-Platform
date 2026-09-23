from google.adk.agents import LlmAgent
from analytics_agent.tools import calculator

root_agent = LlmAgent(
    name="analytics_agent",
    model="gemini-2.5-flash",
    description="Remote mathematics and analytics specialist.",
    instruction="""
You are an analytics specialist exposed as an independent A2A agent.
Use calculator for every arithmetic expression. Explain the expression,
result, and important assumptions. Return the completed result to the
calling coordinator through A2A.
""",
    tools=[calculator],
)
