from vertexai.agent_engines.templates.a2a import A2aAgent
from analytics_agent.executor import AnalyticsAgentExecutor
from analytics_agent.agent import root_agent
from analytics_agent.agent_card import agent_card

app = A2aAgent(
    agent_card=agent_card,
    agent_executor_builder=lambda: AnalyticsAgentExecutor(root_agent),
)
