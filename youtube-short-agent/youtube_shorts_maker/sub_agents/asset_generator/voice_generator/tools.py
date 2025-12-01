from typing import Any, Dict, List

from google import genai
from google.adk.tools.tool_context import ToolContext
from google.genai import types

client = genai.Client()


async def generate_narrations(
    tool_context: ToolContext, voice: str, voice_instructions: List[Dict[str, Any]]
):
    """
    Generate narration audio for each scene using Gemini TTS API

    Args:
        tool_context: Tool context to access artifacts and save files
        voice: Selected voice for TTS (Puck, Charon, Kore, Fenrir, Aoede)
        voice_instructions: List of dictionaries containing narration instructions for each scene

    Returns:
        Information about all generated audio files
    """

    existing_artifacts = await tool_context.list_artifacts()

    generated_narrations = []

    for instruction in voice_instructions:
        text_input = instruction.get("input")
        instructions = instruction.get("instructions")
        scene_id = instruction.get("scene_id")
        filename = f"scene_{scene_id}_narration.mp3"

        if filename in existing_artifacts:
            generated_narrations.append(
                {
                    "scene_id": scene_id,
                    "filename": filename,
                    "input": text_input,
                    "instructions": instructions[:50] if instructions else None,
                }
            )
            continue

        # Combine text_input with instructions for a better prompt
        full_prompt = f"{instructions}\n\n{text_input}" if instructions else text_input

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice
                        )
                    )
                )
            ),
        )

        # Extract audio data from response
        audio_data = None
        if response and response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if (
                        hasattr(part, "inline_data")
                        and part.inline_data
                        and hasattr(part.inline_data, "mime_type")
                        and part.inline_data.mime_type
                        and part.inline_data.mime_type.startswith("audio/")
                    ):
                        audio_data = part.inline_data.data
                        break

        if not audio_data:
            raise ValueError(
                f"No audio generated for scene {scene_id}. Response: {response}"
            )

        artifact = types.Part(
            inline_data=types.Blob(mime_type="audio/mpeg", data=audio_data)
        )

        await tool_context.save_artifact(filename=filename, artifact=artifact)

        generated_narrations.append(
            {
                "scene_id": scene_id,
                "filename": filename,
                "input": text_input,
                "instructions": instructions[:50] if instructions else None,
            }
        )

    return {
        "success": True,
        "narrations": generated_narrations,
        "total_narrations": len(generated_narrations),
    }
