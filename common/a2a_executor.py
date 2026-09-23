from __future__ import annotations

import os
from a2a import types as a2a_types
from a2a.server.agent_execution.agent_executor import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import Part
from google.adk import Runner
from google.adk.agents import LlmAgent
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types as genai_types


class AdkA2aExecutor(AgentExecutor):
    """Bridges an incoming A2A task to an ADK LlmAgent."""

    def __init__(self, agent: LlmAgent):
        self.agent = agent
        self.runner = None

    def _init_runner(self) -> None:
        if self.runner is None:
            # This example uses an in-memory session service to keep the code
            # easy to understand. For production, use the managed session
            # service appropriate for the deployed Agent Runtime.
            self.runner = Runner(
                app_name=self.agent.name,
                agent=self.agent,
                artifact_service=InMemoryArtifactService(),
                session_service=InMemorySessionService(),
                memory_service=InMemoryMemoryService(),
            )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        updater = TaskUpdater(
            event_queue=event_queue,
            task_id=context.task_id or "",
            context_id=context.context_id or "",
        )
        await updater.cancel()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        self._init_runner()
        if not context.message:
            return

        metadata = context.message.metadata or {}
        user_id = metadata.get("user_id", "a2a_user")
        task_id = context.task_id or ""
        context_id = context.context_id or task_id
        updater = TaskUpdater(event_queue, task_id, context_id)

        task = a2a_types.Task(
            id=task_id,
            context_id=context_id,
            status=a2a_types.TaskStatus(
                state=a2a_types.TaskState.TASK_STATE_SUBMITTED
            ),
            history=[context.message],
        )
        await event_queue.enqueue_event(task)
        await updater.start_work()

        query = context.get_user_input()
        content = genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)],
        )

        try:
            session = await self.runner.session_service.get_session(
                app_name=self.runner.app_name,
                user_id=user_id,
                session_id=context_id,
            )
            if session is None:
                session = await self.runner.session_service.create_session(
                    app_name=self.runner.app_name,
                    user_id=user_id,
                    session_id=context_id,
                )

            final_event = None
            async for event in self.runner.run_async(
                session_id=session.id,
                user_id=user_id,
                new_message=content,
            ):
                if event.is_final_response():
                    final_event = event

            if final_event and final_event.content and final_event.content.parts:
                response_text = "".join(
                    part.text
                    for part in final_event.content.parts
                    if getattr(part, "text", None)
                )
                if response_text:
                    await updater.add_artifact(
                        [Part(text=response_text)],
                        name="result",
                        last_chunk=True,
                    )
                    await updater.complete()
                    return

            await updater.update_status(
                a2a_types.TaskState.TASK_STATE_FAILED,
                message=updater.new_agent_message(
                    [Part(text="The specialist produced no final text response.")]
                ),
            )
        except Exception as exc:
            await updater.update_status(
                a2a_types.TaskState.TASK_STATE_FAILED,
                message=updater.new_agent_message(
                    [Part(text=f"Specialist execution failed: {exc}")]
                ),
            )
