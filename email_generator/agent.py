from google.adk.agents import Agent
from . import prompt
from pydantic import BaseModel, Field


class EmailContent(BaseModel):
    """Schema for email content with subject and body."""

    subject: str = Field(
        description="The subject line of the email. Should be concise and descriptive."
    )
    body: str = Field(
        description="The main content of the email. Should be well-formatted with proper greeting, paragraphs, and signature."
    )


root_agent = Agent(
    name="professional_email_agent",
    model="gemini-2.5-pro",
    description="A professional email generator assistant that creates structured, polished business emails based on user input.",
    instruction=prompt.email_generate_prompt,
    output_schema=EmailContent,
    output_key="generated_email",
)
