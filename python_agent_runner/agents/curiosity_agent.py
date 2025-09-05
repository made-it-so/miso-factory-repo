import arxiv
import fitz  # PyMuPDF
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class CuriosityAgent:
    def __init__(self):
        self.analysis_model = "gpt-4o"
        print(f"Curiosity Agent initialized with model: {self.analysis_model}")

    def search_arxiv(self, query="agentic AI", max_results=1):
        """Searches arXiv for relevant papers."""
        print(f"Curiosity Agent: Searching arXiv for '{query}'...")
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        paper = next(search.results(), None)
        return paper

    def download_and_parse_pdf(self, paper):
        """Downloads a paper's PDF and extracts its text content."""
        if not paper:
            return None
        
        pdf_path = paper.download_pdf(dirpath="./temp_research")
        print(f"Curiosity Agent: Downloaded '{paper.title}' to {pdf_path}")

        try:
            with fitz.open(pdf_path) as doc:
                text = "".join(page.get_text() for page in doc)
            print("Curiosity Agent: Successfully parsed PDF content.")
            return text
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return None
        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)


    def generate_project_proposal(self, paper, paper_content):
        """Analyzes paper content and generates a project proposal."""
        if not paper or not paper_content:
            return {"error": "Missing paper or content for analysis."}

        print("Curiosity Agent: Analyzing research to generate a project proposal...")
        
        system_prompt = """You are MISO, an advanced AI architect. You have been given the title and abstract of a new research paper, along with its full text.
        Your task is to analyze this research and determine if it offers a viable improvement to your own architecture.
        If it does, create a formal 'Project Proposal' in a structured format. If it's not relevant, state that.
        The proposal must include a hypothesis, a specific and actionable Colosseum challenge for another agent, and measurable success metrics."""

        user_prompt = f"""**Paper Title:** {paper.title}
        **Paper Abstract:** {paper.summary}

        **Your Goal:** Determine if the concepts in this paper can improve the MISO system and, if so, generate a Project Proposal.

        **Full Paper Text for Context:**
        {paper_content[:10000]}...
        """ # Truncate for context window

        response = openai.chat.completions.create(
            model=self.analysis_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content

    def run_research_cycle(self):
        """Runs one full cycle of research, analysis, and proposal."""
        latest_paper = self.search_arxiv()
        if latest_paper:
            paper_content = self.download_and_parse_pdf(latest_paper)
            proposal = self.generate_project_proposal(latest_paper, paper_content)
            return proposal
        return "No new research found."
