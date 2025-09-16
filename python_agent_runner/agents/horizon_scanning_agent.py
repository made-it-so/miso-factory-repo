import logging
import arxiv
from datetime import datetime, timedelta, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class HorizonScanningAgent:
    """Scans arXiv for recent research papers in specified categories."""
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("HorizonScanningAgent initialized.")

    def scan_for_research(self, categories=['cs.AI', 'cs.LG', 'cs.SE', 'cs.HC'], max_results=25):
        """
        Scans for new papers in the last 7 days.
        Returns a list of dictionaries, each representing a paper.
        """
        self.logger.info(f"Scanning arXiv for new research in categories: {categories}")
        try:
            search = arxiv.Search(
                query=" OR ".join(f"cat:{cat}" for cat in categories),
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            client = arxiv.Client()
            results_generator = client.results(search)
            
            recent_papers = []
            one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)

            for result in results_generator:
                if result.published >= one_week_ago:
                    recent_papers.append({
                        "id": result.entry_id,
                        "title": result.title,
                        "summary": result.summary.replace('\n', ' '),
                        "authors": [author.name for author in result.authors],
                        "published_date": result.published.isoformat(),
                        "pdf_url": result.pdf_url
                    })
            
            self.logger.info(f"Found {len(recent_papers)} new papers in the last week.")
            return recent_papers

        except Exception as e:
            self.logger.error(f"An error occurred while scanning arXiv: {e}")
            return []
