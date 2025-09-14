import logging
import json
import ollama
import requests
import fitz
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class AnalysisAgent:
    """Downloads, reads, and performs deep analysis on a research paper."""
    def __init__(self, model="llama3"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=7000, chunk_overlap=200)

    def _download_pdf(self, pdf_url: str, temp_path: str) -> bool:
        # (Implementation is unchanged)
        try:
            r = requests.get(pdf_url, stream=True); r.raise_for_status()
            with open(temp_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
            return True
        except Exception as e:
            self.logger.error(f"Failed to download PDF: {e}"); return False

    def _extract_text(self, temp_path: str) -> str:
        # (Implementation is unchanged)
        try:
            with fitz.open(temp_path) as doc: text = "".join(page.get_text() for page in doc)
            return text
        except Exception as e:
            self.logger.error(f"Failed to extract text: {e}"); return ""
    
    def _create_synthesis_prompt(self, paper_title: str, chunk_summaries: list) -> str:
        # (Implementation is unchanged)
        combined = "\n\n".join(chunk_summaries)
        return f'You are a Principal AI Architect... Analyze these summaries for the paper "{paper_title}":\n{combined}\n\nRespond with ONLY the JSON Analysis Report.'

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
            try:
                prompt = f"Summarize key findings from this section:\n\n{chunk}"
                response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}])
                chunk_summaries.append(response['message']['content'])
            except Exception as e:
                self.logger.error(f"Failed to analyze chunk {i+1}: {e}")
        
        try:
            synthesis_prompt = self._create_synthesis_prompt(paper.get('title'), chunk_summaries)
            final_response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': synthesis_prompt}], format='json')
            report = json.loads(final_response['message']['content'])
            
            report['paper_title'] = paper.get('title', 'Unknown Title')
            # THE FIX: Embed the original paper data needed for the Gauntlet
            report['original_paper_data'] = paper
            
            self.logger.info("Successfully generated final analysis report.")
            return report
        except Exception as e:
            self.logger.error(f"Failed to synthesize final report: {e}")
            return {"error": "Failed to generate final report from summaries."}
