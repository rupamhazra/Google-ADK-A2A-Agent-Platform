import os
import vertexai
from vertexai import agent_engines
from vertexai.agent_engines import AdkApp

PROJECT_ID = "project-c11bffff-09d9-480a-a53"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://coordinator_agent_a2a_staging"
COORDINATOR_SERVICE_ACCOUNT = "corporate-a2a-coordinator@project-c11bffff-09d9-480a-a53.iam.gserviceaccount.com"

# Set these in Cloud Shell before running this deployment script.
card_env = {
    "RESEARCH_AGENT_CARD_URL": "https://us-central1-aiplatform.googleapis.com/v1beta1/projects/509933330289/locations/us-central1/reasoningEngines/3789132023839326208/a2a/v1/card",
    "ANALYTICS_AGENT_CARD_URL": "https://us-central1-aiplatform.googleapis.com/v1beta1/projects/509933330289/locations/us-central1/reasoningEngines/3562016902005915648/a2a/v1/card",
    "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
    "OTEL_SEMCONV_STABILITY_OPT_IN": "gen_ai_latest_experimental",
}

# Make these values available to agent.py during local import.
os.environ.update(card_env)

# Import only after card URL environment variables are present locally.
from coordinator_agent.agent import root_agent

vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)
app = AdkApp(agent=root_agent)
remote = agent_engines.create(
    agent_engine=app,
    display_name="Corporate-A2A-Coordinator",
    description="Coordinator that invokes three remote A2A specialist agents.",
    requirements="coordinator_agent/requirements.txt",
    extra_packages=["coordinator_agent"],
    env_vars=card_env,
    service_account=COORDINATOR_SERVICE_ACCOUNT,
)
print(f"RESOURCE_NAME={remote.resource_name}")
