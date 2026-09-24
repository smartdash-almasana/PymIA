"""Run a minimal structured-output inference through PydanticAI and Vertex AI.

Requires Application Default Credentials and the non-secret environment variables
GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION.
"""

from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google_cloud import GoogleCloudProvider


class VertexSmokeResponse(BaseModel):
    status: Literal["ok"]
    message: str


def main() -> None:
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    location = os.environ["GOOGLE_CLOUD_LOCATION"]
    model_name = os.getenv("PYDANTIC_AI_VERTEX_MODEL", "gemini-2.5-flash")

    model = GoogleModel(
        model_name,
        provider=GoogleCloudProvider(project=project, location=location),
    )
    agent = Agent(
        model,
        output_type=VertexSmokeResponse,
        instructions=(
            "Return a structured response with status 'ok' and a short message confirming "
            "that Vertex AI structured output works."
        ),
    )
    result = agent.run_sync("Execute the smoke test.")
    print(result.output.model_dump_json())


if __name__ == "__main__":
    main()
