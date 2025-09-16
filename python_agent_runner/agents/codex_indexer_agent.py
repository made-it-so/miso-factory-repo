import logging
import json
import os
import numpy as np
import ollama
from langchain.text_splitter import PythonCodeTextSplitter
from sklearn.cluster import DBSCAN

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class CodexIndexerAgent:
    """
    Analyzes a completed project and builds a hierarchical knowledge tree using a RAPTOR-like methodology.
    """
    def __init__(self, model="llama3"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.text_splitter = PythonCodeTextSplitter(chunk_size=1024, chunk_overlap=100)
        self.logger.info("CodexIndexerAgent initialized.")

    def _load_and_chunk_project(self, project_path: str) -> list:
        """Loads all .py files from a project and splits them into chunks."""
        all_chunks = []
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    chunks = self.text_splitter.create_documents([code])
                    all_chunks.extend([{'text': chunk.page_content, 'source': file_path} for chunk in chunks])
        self.logger.info(f"Loaded and split project into {len(all_chunks)} code chunks.")
        return all_chunks

    def _get_embeddings(self, texts: list) -> np.ndarray:
        """Generates embeddings for a list of texts."""
        self.logger.info(f"Generating embeddings for {len(texts)} text(s)...")
        embeddings = [ollama.embeddings(model='mxbai-embed-large', prompt=text)['embedding'] for text in texts]
        return np.array(embeddings)

    def _summarize_text(self, text: str, level: int) -> str:
        """Uses an LLM to summarize a piece of text."""
        self.logger.info(f"Summarizing text at level {level}...")
        prompt = f"You are a code analysis AI. Summarize the following code snippet(s) into a high-level concept. Focus on the 'what' and 'why', not the 'how'.\n\nCODE:\n{text}"
        response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']

    def _cluster_chunks(self, embeddings: np.ndarray) -> list:
        """Clusters embeddings and returns a list of cluster labels."""
        self.logger.info(f"Clustering {len(embeddings)} embeddings...")
        clustering = DBSCAN(eps=0.5, min_samples=2, metric='cosine').fit(embeddings)
        return clustering.labels_

    def index_project(self, project_path: str) -> dict:
        """Main method to perform RAPTOR indexing on a project directory."""
        self.logger.info(f"Starting RAPTOR indexing for project: {project_path}")
        
        leaf_chunks = self._load_and_chunk_project(project_path)
        if not leaf_chunks:
            return {"error": "No Python files found to index."}

        # Level 0: Initial summarization of raw code chunks
        self.logger.info("--- Building Level 0 of the knowledge tree ---")
        summaries = [self._summarize_text(chunk['text'], 0) for chunk in leaf_chunks]
        
        tree = {
            "level_0": [{"summary": s, "source_chunk": c['text']} for s, c in zip(summaries, leaf_chunks)]
        }
        
        current_level = 0
        current_summaries = summaries

        while len(current_summaries) > 1:
            current_level += 1
            self.logger.info(f"--- Building Level {current_level} of the knowledge tree ---")
            
            embeddings = self._get_embeddings(current_summaries)
            labels = self._cluster_chunks(embeddings)
            
            next_level_summaries = []
            level_nodes = []
            
            # Group summaries by cluster label
            clusters = {}
            for i, label in enumerate(labels):
                if label not in clusters: clusters[label] = []
                clusters[label].append(current_summaries[i])

            for label, items in clusters.items():
                if label == -1: # Noise points become their own nodes
                    for item in items:
                        next_level_summaries.append(item)
                        level_nodes.append({"summary": item, "children": [item]})
                else: # Cluster items get summarized
                    combined_text = "\n\n---\n\n".join(items)
                    new_summary = self._summarize_text(combined_text, current_level)
                    next_level_summaries.append(new_summary)
                    level_nodes.append({"summary": new_summary, "children": items})

            tree[f"level_{current_level}"] = level_nodes
            current_summaries = next_level_summaries
            if len(tree[f"level_{current_level-1}"]) == len(current_summaries):
                self.logger.warning("Clustering did not reduce nodes. Halting to prevent infinite loop.")
                break
        
        tree["root"] = current_summaries[0]
        self.logger.info("Successfully built RAPTOR knowledge tree.")
        return tree
