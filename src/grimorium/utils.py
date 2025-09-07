import json
from typing import Optional

from google.adk.runners import Runner
from google.genai import types


async def call_agent_async(
    user_id: str,
    session_id: str,
    runner: Runner,
    query: str,
    image_bytes: Optional[bytes] = None,
    show_function_calls: bool = False,
    show_function_responses: bool = False,
    show_inline_data: bool = False,
    show_state_updates: bool = False,
    show_artifact_updates: bool = False,
    show_transfer_to_agent: bool = False,
    show_unknown_events: bool = False,
    show_final_responses: bool = True,
    center_width: int = 60,
) -> None:
    """Sends the query to the agent and calls on_message with each response."""
    print("\n")
    print(f" [User]>>>[QUERY]>>>[{runner.agent.name}] ".center(center_width, "="))
    print(query)
    print("=" * center_width)
    if image_bytes:
        content = types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=query),
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            ],
        )
    else:
        content = types.Content(role="user", parts=[types.Part.from_text(text=query)])
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        author = event.author

        if not event.content:
            if event.actions:
                try:
                    if event.actions.state_delta and show_state_updates:
                        print("\n")
                        print(
                            f" [{author}][STATE DELTA UPDATE] ".center(
                                center_width, "="
                            )
                        )
                        print(event.actions.state_delta)
                        print("=" * center_width)
                except Exception as e:
                    print(
                        f"Error while processing state delta in 'call_agent_async': {e}"
                    )

                try:
                    if event.actions.artifact_delta and show_artifact_updates:
                        print("\n")
                        print(
                            f" [{author}][ARTIFACT DELTA UPDATE] ".center(
                                center_width, "="
                            )
                        )
                        print(event.actions.artifact_delta)
                        print("=" * center_width)
                except Exception as e:
                    print(
                        f"Error while processing artifact delta in 'call_agent_async': {e}"
                    )

                try:
                    if event.actions.transfer_to_agent and show_transfer_to_agent:
                        print("\n")
                        print(
                            f" [{author}][TRANSFER TO AGENT] ".center(center_width, "=")
                        )
                        print(event.actions.transfer_to_agent)
                        print("=" * center_width)
                except Exception as e:
                    print(
                        f"Error while processing transfer to agent in 'call_agent_async': {e}"
                    )
            else:
                try:
                    if show_unknown_events:
                        print("\n")
                        print(f" [{author}][UNKNOWN EVENT] ".center(center_width, "="))
                        print(event)
                        print("=" * center_width)
                except Exception as e:
                    print(
                        f"Error while processing unknown event in 'call_agent_async': {e}"
                    )
            continue

        parts = event.content.parts

        for part in parts:
            if part.text:
                text = part.text
                try:
                    if event.is_final_response and show_final_responses:
                        final_response = text
                        print("\n")
                        print(
                            f" [User]<<<[FINAL RESPONSE]<<<[{author}] ".center(
                                center_width, "="
                            )
                        )
                        print(final_response)
                        print("=" * center_width)
                except Exception as e:
                    print(f"Error while processing text in 'call_agent_async': {e}")
            try:
                if part.function_call and show_function_calls:
                    func_call = part.function_call
                    print("\n")
                    print(f" [{author}][FUNCTION CALL] ".center(center_width, "="))
                    print(
                        f"{func_call.name}({', '.join(f'{k}={v}' for k, v in func_call.args.items())})"
                    )
                    print("=" * center_width)
            except Exception as e:
                print(
                    f"Error while processing function call in 'call_agent_async': {e}"
                )
            try:
                if part.function_response and show_function_responses:
                    func_response = part.function_response
                    print("\n")
                    print(f" [{author}][FUNCTION RESPONSE] ".center(center_width, "="))
                    print(func_response.response)
                    print("=" * center_width)
            except Exception as e:
                print(
                    f"Error while processing function response in 'call_agent_async': {e}"
                )
            try:
                if part.inline_data and show_inline_data:
                    inline_data = part.inline_data
                    print("\n")
                    print(f" [{author}][INLINE DATA] ".center(center_width, "="))
                    print(json.dumps(inline_data.data))
                    print("=" * center_width)
            except Exception as e:
                print(f"Error while processing inline data in 'call_agent_async': {e}")
