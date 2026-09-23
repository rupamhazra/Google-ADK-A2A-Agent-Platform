from vertexai.agent_engines.templates.a2a import A2aAgent
from research_agent.executor import ResearchAgentExecutor
from research_agent.agent import root_agent
from research_agent.agent_card import agent_card

app = A2aAgent(
    agent_card=agent_card,
    agent_executor_builder=lambda: ResearchAgentExecutor(root_agent),
)
