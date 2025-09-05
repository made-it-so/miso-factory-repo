# data_contracts.py
# Owner: MISO
# Manifest Version: v31.0
# Purpose: Defines the formal, standardized data structures (contracts) for
# communication between agents in the MISO Agentic AI Mesh.

from dataclasses import dataclass, field
from typing import List

@dataclass
class ConversationContext:
    """
    A standardized data packet representing the state of the user-facing
    discovery interview at any given moment.
    """
    full_transcript: str
    latest_user_utterance: str
    inquisitor_interventions: int
    project_domain_keywords: List[str] = field(default_factory=list)
    clarity_score: float = 0.0
    project_metaphor: str = ""

# Example of how this might be used:
if __name__ == '__main__':
    print("--- MISO Data Contracts: Standalone Test ---")

    # The discovery-interview agent would create this object
    context = ConversationContext(
        full_transcript="User wants a new app for tracking books.",
        latest_user_utterance="It needs a database for the books.",
        inquisitor_interventions=1,
        project_domain_keywords=["app", "database", "books"]
    )

    print("Created ConversationContext object:")
    print(context)

    # Another agent could then update a field
    context.clarity_score = 0.75
    print("\nUpdated clarity_score:")
    print(context)
