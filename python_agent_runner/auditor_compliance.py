# auditor_compliance.py
# This file was missing from the application directory.

from typing import Dict, Any, List

class DataScientistAgentMock:
    """
    A mock dependency for testing purposes.
    """
    def get_semantic_similarity(self, text_a: str, text_b: str) -> float:
        """Mocks the calculation of semantic similarity."""
        if not text_b or not text_a:
            return 0.0
        similarity = 1.0 - (abs(len(text_a) - len(text_b)) / max(len(text_a), len(text_b)))
        return max(0.0, similarity)

    def get_concreteness_ratio(self, text: str, domain_keywords: List[str]) -> float:
        """Mocks the calculation of a concreteness ratio."""
        words = text.lower().split()
        if not words:
            return 0.0
        concrete_words = sum(1 for word in words if word in domain_keywords)
        return concrete_words / len(words)

class AuditorComplianceAgent:
    """
    Monitors network-level dynamics and cognitive fidelity.
    """
    def __init__(self, data_scientist_agent):
        self.WEIGHT_CONSISTENCY = 0.40
        self.WEIGHT_CONCRETENESS = 0.35
        self.WEIGHT_CONFIDENCE = 0.25
        self.data_scientist = data_scientist_agent

    def calculate_clarity_score(self, conversation_context: Dict[str, Any]) -> float:
        """
        Calculates a holistic Clarity Score from 0.0 to 1.0.
        """
        consistency_score = self.data_scientist.get_semantic_similarity(
            text_a=conversation_context["latest_user_utterance"],
            text_b=conversation_context["full_transcript"]
        )
        concreteness_score = self.data_scientist.get_concreteness_ratio(
            text=conversation_context["latest_user_utterance"],
            domain_keywords=conversation_context.get("project_domain_keywords", [])
        )
        interventions = conversation_context["inquisitor_interventions"]
        confidence_score = 0.95 ** interventions
        final_score = (
            (consistency_score * self.WEIGHT_CONSISTENCY) +
            (concreteness_score * self.WEIGHT_CONCRETENESS) +
            (confidence_score * self.WEIGHT_CONFIDENCE)
        )
        return min(final_score, 1.0)
