

from google import genai
from google.adk.tools.tool_context import ToolContext
from google.genai import types

client = genai.Client()


async def generate_images(tool_context: ToolContext):
    prompt_builder_output = tool_context.state.get("prompt_builder_output")
    optimized_prompts = prompt_builder_output.get("optimized_prompts")

    existing_artifacts = await tool_context.list_artifacts()

    generated_images = []

    for prompt in optimized_prompts:
        scene_id = prompt.get("scene_id")
        enhanced_prompt = prompt.get("enhanced_prompt")
        filename = f"scene_{scene_id}_image.jpeg"

        if filename in existing_artifacts:
            generated_images.append(
                {
                    "scene_id": scene_id,
                    "prompt": enhanced_prompt[:100],
                    "filename": filename,
                }
            )
            continue

        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[enhanced_prompt],
            # n=1,
            # quality="low",
            # moderation="low",
            # output_format="jpeg",
            # background="opaque",
            # size="1024x1536",
        )


        # image_bytes = base64.b64decode(image.data[0].b64_json)

        image = None
        if response.parts:
            for part in response.parts:
                if part.text is not None:
                    print(part.text)
                elif part.inline_data is not None:
                    image = part.as_image()
                    if image:
                        image.save(f"{filename}")

        if not image:
            raise ValueError("No image generated")

        artifact = types.Part(
            inline_data=types.Blob(
            mime_type="image/jpeg",
            data=image.image_bytes,
            )
        )

        await tool_context.save_artifact(
            filename=filename,
            artifact=artifact,
        )

        generated_images.append(
            {
                "scene_id": scene_id,
                "prompt": enhanced_prompt[:100],
                "filename": filename,
            }
        )

        return {
            "total_images": len(generated_images),
            "generated_images": generated_images,
            "status": "complete",
        }
