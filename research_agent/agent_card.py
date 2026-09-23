from a2a.types import AgentSkill
from vertexai.agent_engines.templates.a2a import create_agent_card

research_skill = AgentSkill(
    id="research_topic",
    name="Research a topic",
    description="Searches for external information and summarizes findings.",
    tags=["research", "search", "summary"],
    examples=["Research Amazon Alexa", "Summarize serverless computing"],
)

agent_card = create_agent_card(
    agent_name="Corporate Research Agent",
    description="A remote A2A research specialist.",
    skills=[research_skill],
)
