from a2a.types import AgentSkill
from vertexai.agent_engines.templates.a2a import create_agent_card

analytics_skill = AgentSkill(
    id="calculate_expression",
    name="Calculate an expression",
    description="Evaluates arithmetic expressions and explains results.",
    tags=["math", "calculation", "analytics"],
    examples=["Calculate (1250 * 18.5) / 100", "Evaluate (200 + 40) / 8"],
)

agent_card = create_agent_card(
    agent_name="Corporate Analytics Agent",
    description="A remote A2A mathematics and analytics specialist.",
    skills=[analytics_skill],
)
