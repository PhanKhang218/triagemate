"""Headless demo of the TriageMate pipeline. Run: uv run python demo.py
(requires GEMINI_API_KEY in .env)."""

from __future__ import annotations

import asyncio

from dotenv import load_dotenv

load_dotenv()  # must run before importing the agent

from google.adk.runners import InMemoryRunner  # noqa: E402
from google.genai import types  # noqa: E402

from triage_agent import root_agent  # noqa: E402

APP_NAME = "triagemate"
USER_ID = "nurse_demo"

SAMPLE_PRESENTATION = (
    "58-year-old man, crushing chest pressure radiating to the left arm for 20 "
    "minutes, sweaty and nauseous. HR 110, SpO2 95%."
)


async def main() -> None:
    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )

    message = types.Content(role="user", parts=[types.Part(text=SAMPLE_PRESENTATION)])

    print(f"NURSE INPUT:\n  {SAMPLE_PRESENTATION}\n")
    print("=" * 72)

    async for event in runner.run_async(
        user_id=USER_ID, session_id=session.id, new_message=message
    ):
        author = event.author
        if not (event.content and event.content.parts):
            continue
        for part in event.content.parts:
            if getattr(part, "function_call", None):
                fc = part.function_call
                print(f"\n[{author}] -> MCP tool call: {fc.name}({dict(fc.args)})")
            elif getattr(part, "function_response", None):
                print(f"[{author}] <- tool result received")
            elif getattr(part, "text", None):
                print(f"\n[{author}]\n{part.text}")

    final = await runner.session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session.id
    )
    print("\n" + "=" * 72)
    print("FINAL TriageResult (validated, stored in session state):")
    print(final.state.get("triage_result"))


if __name__ == "__main__":
    asyncio.run(main())
