from google.adk.agents import LlmAgent
from research_agent.tools import search_topic

root_agent = LlmAgent(
    name="research_agent",
    model="gemini-2.5-flash",
    description="Remote research specialist for topic research and summaries.",
    instruction="""
You are a research specialist exposed as an independent A2A agent.
Always call search_topic before answering a research request.
Summarize the returned evidence and include source URLs when present.
Return the completed result to the calling coordinator. Do not try to
transfer to coordinator_agent because the A2A protocol returns the result.
""",
    tools=[search_topic],
)
