import vertexai
from vertexai import agent_engines
from analytics_agent.a2a_app import app

PROJECT_ID = "project-c11bffff-09d9-480a-a53"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://analytics_agent_a2a_staging"

vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)
remote = agent_engines.create(
    agent_engine=app,
    display_name="Corporate-Analytics-Agent-A2A",
    description="Independent analytics specialist exposed through A2A.",
    requirements=f"analytics_agent/requirements.txt",
    extra_packages=["common", "analytics_agent"],
    env_vars={
        "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
        "OTEL_SEMCONV_STABILITY_OPT_IN": "gen_ai_latest_experimental",
    },
)
print(f"RESOURCE_NAME={remote.resource_name}")
