from typing import List, Optional
from enum import Enum
from google.adk.agents import LlmAgent
from . import prompt
from pydantic import BaseModel, Field


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    RESOLVED = "resolved"


class SupportTicket(BaseModel):
    title: str = Field(description="A concise summary of the issue")
    description: str = Field(description="Detailed description of the problem")
    priority: Priority = Field(description="The ticket priority level")
    category: str = Field(
        description="The department this ticket belongs to, e.g., Technical, Billing, Account, Product"
    )
    steps_to_reproduce: Optional[List[str]] = Field(
        default=None,
        description="Steps to reproduce the issue (for technical problems)",
    )
    estimated_resolution_time: str = Field(
        description="Estimated time to resolve this issue, e.g., '2-4 hours', '1-2 days'"
    )
    customer_sentiment: Optional[str] = Field(
        default=None,
        description="Optional field indicating customer's emotional tone (e.g., frustrated, neutral, angry, appreciative)",
    )
    language: Optional[str] = Field(
        default=None,
        description="Detected language of the user’s message (e.g., 'en', 'es', 'fr', 'bn')",
    )
    status: TicketStatus = Field(
        default=TicketStatus.NEW, description="Current status of the ticket"
    )
    assigned_team: Optional[str] = Field(
        default=None, description="Team or individual assigned to resolve this ticket"
    )
    requires_followup: bool = Field(
        default=False,
        description="Whether the ticket requires follow-up from the support team",
    )


root_agent = LlmAgent(
    name="customer_support_agent",
    model="gemini-2.5-pro",
    description="Advanced support ticket generator with sentiment and category detection.",
    instruction=prompt.customer_support_instruction,
    output_schema=SupportTicket,
    output_key="support_ticket",
)
