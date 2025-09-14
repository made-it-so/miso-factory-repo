import logging
import json
import ollama
import requests
import fitz  # PyMuPDF
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class AnalysisAgent:
    """Downloads, reads, and performs deep analysis on a research paper."""
    def __init__(self, model="llama3"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=7000, chunk_overlap=200)
        self.logger.info("AnalysisAgent initialized.")

    def _download_pdf(self, pdf_url: str, temp_path: str) -> bool:
        try:
            self.logger.info(f"Downloading PDF from {pdf_url}...")
            response = requests.get(pdf_url, stream=True)
            response.raise_for_status()
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192): f.write(chunk)
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download PDF: {e}")
            return False

    def _extract_text(self, temp_path: str) -> str:
        try:
            with fitz.open(temp_path) as doc:
                text = "".join(page.get_text() for page in doc)
            return text
        except Exception as e:
            self.logger.error(f"Failed to extract text from PDF: {e}")
            return ""

    def _create_synthesis_prompt(self, paper_title: str, chunk_summaries: list) -> str:
        combined_summaries = "\n\n".join(chunk_summaries)
        return f"""
        You are a Principal AI Architect at MISO. You have been given chunk-by-chunk summaries of a research paper.
        Your task is to synthesize this information into a single, structured, and actionable "Analysis Report."
        **Paper Title:** {paper_title}
        **Summaries of Paper Sections:**
        {combined_summaries}
        **Instructions:**
        Based on ALL the information provided, generate the final Analysis Report as a single JSON object.
        Respond with ONLY the JSON object.
        """

    def analyze_paper(self, paper: dict) -> dict:
        pdf_url = paper.get("pdf_url")
        if not pdf_url: return {"error": "Missing PDF URL."}
        
        temp_pdf_path = f"temp_{paper.get('id', 'paper').split('/')[-1]}.pdf"
        
        if not self._download_pdf(pdf_url, temp_pdf_path): return {"error": "Failed to download PDF."}
        full_text = self._extract_text(temp_pdf_path)
        os.remove(temp_pdf_path)
        
        if not full_text: return {"error": "Failed to extract text from PDF."}

        chunks = self.text_splitter.split_text(full_text)
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            self.logger.info(f"Analyzing chunk {i + 1}/{len(chunks)}...")
            try:
                prompt = f"Summarize the key findings, techniques, and potential applications from the following section of a research paper:\n\n{chunk}"
                response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}])
                chunk_summaries.append(response['message']['content'])
            except Exception as e:
                self.logger.error(f"Failed to analyze chunk {i+1}: {e}")
        
        self.logger.info("Synthesizing final analysis report...")
        try:
            synthesis_prompt = self._create_synthesis_prompt(paper.get('title'), chunk_summaries)
            final_response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': synthesis_prompt}], format='json')
            report = json.loads(final_response['message']['content'])
            
            # THE FIX: Add the paper's title to the final report
            report['paper_title'] = paper.get('title', 'Unknown Title')
            
            self.logger.info("Successfully generated final analysis report.")
            return report
        except Exception as e:
            self.logger.error(f"Failed to synthesize final report: {e}")
            return {"error": "Failed to generate final report from summaries."}
