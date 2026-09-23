import asyncio
import json

import agentplatform

from a2a.client import ClientCallContext
from a2a.helpers import new_text_message
from a2a.types import Role
from a2a.types import SendMessageRequest


PROJECT_ID = "project-c11bffff-09d9-480a-a53"
LOCATION = "us-central1"

RESEARCH_RESOURCE_ID = "8663152720561045504"

RESOURCE_NAME = (
    f"projects/{PROJECT_ID}/"
    f"locations/{LOCATION}/"
    f"reasoningEngines/{RESEARCH_RESOURCE_ID}"
)


def to_json_compatible(value):
    """
    Convert an SDK response to JSON-compatible data.
    """

    if hasattr(value, "model_dump"):
        return value.model_dump(
            mode="json",
            exclude_none=True,
        )

    if hasattr(value, "to_json"):
        return json.loads(
            value.to_json()
        )

    if isinstance(value, dict):
        return value

    return {
        "value": str(value),
    }


async def main():
    print("Resource name:")
    print(RESOURCE_NAME)

    client = agentplatform.Client(
        project=PROJECT_ID,
        location=LOCATION,
        http_options={
            "api_version": "v1beta1",
            "timeout": 120000,
        },
    )

    remote_agent = client.runtimes.get(
        name=RESOURCE_NAME
    )

    print("\nRuntime type:")
    print(type(remote_agent))

    print("\nHas on_message_send:")
    print(
        hasattr(
            remote_agent,
            "on_message_send",
        )
    )

    # Create a typed A2A Message.
    message = new_text_message(
        (
            "Research Amazon Alexa and identify "
            "the original release year."
        ),
        role=Role.ROLE_USER,
    )

    # Wrap the Message in the typed A2A request.
    request = SendMessageRequest(
        message=message
    )

    # Create the typed A2A client context.
    context = ClientCallContext()

    print("\nRequest type:")
    print(type(request))

    print("\nMessage type:")
    print(type(message))

    print("\nContext type:")
    print(type(context))

    print("\nSending A2A message...")

    response = await remote_agent.on_message_send(
        request=request,
        context=context,
    )

    print("\nRaw response:")
    print(response)

    response_data = to_json_compatible(
        response
    )

    print("\nFormatted response:")

    print(
        json.dumps(
            response_data,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())