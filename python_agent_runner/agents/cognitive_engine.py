# cognitive_engine.py (v2 - Corrected)
import networkx as nx
import ollama
import logging
import json

class CognitiveReasoningEngine:
    """
    Houses the Cognitive Reasoning Engine, including the Abstraction Engine
    responsible for generating metaphors.
    """
    def __init__(self, model_name="miso-local-model"):
        self.model = model_name

    def generate_metaphor(self, conversation_context: dict) -> str:
        """
        Analyzes conversation context to generate a project metaphor.
        This version uses a simple heuristic based on keywords.
        """
        # A simple, rule-based mapping for generating metaphors.
        metaphor_map = {
            "database": "a digital library for storing information",
            "api": "a universal translator between different software",
            "user": "a customer visiting a digital storefront",
            "payment": "a secure cash register",
            "server": "the engine room of the application",
            "frontend": "the storefront and display windows",
            "backend": "the warehouse and inventory system"
        }
        
        keywords = conversation_context.get("project_domain_keywords", [])
        
        components = []
        for keyword in keywords:
            if keyword in metaphor_map:
                components.append(metaphor_map[keyword])

        if not components:
            return "A blank canvas."

        if len(components) == 1:
             return f"This project is like {components[0]}."
        else:
            joined_components = ", ".join(components[:-1]) + f", and {components[-1]}"
            return f"Think of this project as a system with several parts: it has {joined_components}."
