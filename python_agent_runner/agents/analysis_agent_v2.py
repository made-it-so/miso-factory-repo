import logging
import json
import ollama
import requests
import fitz  # PyMuPDF
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class AnalysisAgentV2:
    """
    An upgraded 'student' version of the AnalysisAgent that uses a long-context
    approach instead of chunking.
    """
    def __init__(self, model="llama3"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.logger.info("AnalysisAgentV2 (Student) initialized.")

    def _download_pdf(self, pdf_url: str, temp_path: str) -> bool:
        """Downloads a PDF from a URL to a temporary path."""
        try:
            self.logger.info(f"Downloading PDF from {pdf_url}...")
            response = requests.get(pdf_url, stream=True)
            response.raise_for_status()
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download PDF: {e}")
            return False

    def _extract_text(self, temp_path: str) -> str:
        """Extracts all text from a PDF file."""
        try:
            with fitz.open(temp_path) as doc:
                text = "".join(page.get_text() for page in doc)
            return text
        except Exception as e:
            self.logger.error(f"Failed to extract text from PDF: {e}")
            return ""

    def _create_synthesis_prompt(self, paper_title: str, full_text: str) -> str:
        """Creates the prompt to synthesize the full text into a report."""
        # Truncate full text to a manageable size to avoid overwhelming the model
        truncated_text = full_text[:15000]
        return f"""
        You are a Principal AI Architect at MISO. You have been given the FULL TEXT of a research paper.
        Your task is to synthesize this information into a single, structured, and actionable "Analysis Report."

        **Paper Title:** {paper_title}
        
        **Full Text (truncated):**
        {truncated_text}

        **Instructions:**
        Based on the full text, generate the final Analysis Report as a single JSON object with the following fields:
        - "key_takeaways": A bulleted list of the paper's most important contributions.
        - "extracted_techniques": A list of specific algorithms or methods.
        - "application_to_miso": A detailed hypothesis on how this research could improve a MISO agent.
        - "high_level_implementation_plan": A list of 3-5 high-level engineering steps.
        - "impact_score": An integer from 1-10 rating the potential impact.

        Respond with ONLY the JSON object.
        """

    def analyze_paper(self, paper: dict) -> dict:
        """The main method to perform a full analysis of a single paper."""
        pdf_url = paper.get("pdf_url")
        if not pdf_url: return {"error": "Missing PDF URL."}
        
        temp_pdf_path = f"temp_{paper.get('id', 'paper').split('/')[-1]}.pdf"
        
        if not self._download_pdf(pdf_url, temp_pdf_path):
            return {"error": "Failed to download PDF."}

        full_text = self._extract_text(temp_pdf_path)
        os.remove(temp_pdf_path)
        
        if not full_text: return {"error": "Failed to extract text from PDF."}

        self.logger.info("Performing direct long-context analysis...")
        try:
            synthesis_prompt = self._create_synthesis_prompt(paper.get('title'), full_text)
            final_response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': synthesis_prompt}], format='json')
            report_str = final_response['message']['content']
            report = json.loads(report_str)
            self.logger.info("Successfully generated final analysis report with long-context method.")
            return report
        except Exception as e:
            self.logger.error(f"Failed to synthesize final report: {e}")
            return {"error": "Failed to generate final report."}
