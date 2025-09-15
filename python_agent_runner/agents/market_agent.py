import logging
import json
import ollama
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class MarketAgent:
    """
    Analyzes developer and entrepreneur communities to identify trending project ideas.
    """
    def __init__(self, model="llama3"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.hn_api_base = "https://hacker-news.firebaseio.com/v0"
        self.reddit_sources = ["smallbusiness", "Entrepreneur", "sideproject"]
        self.logger.info("MarketAgent v2 initialized.")

    def _gather_market_data(self, limit_per_source=15) -> list:
        """Gathers headlines from multiple sources (HN, Reddit) to get a broad view."""
        all_headlines = []
        
        # Hacker News (for developer perspective)
        try:
            self.logger.info("Fetching top story IDs from Hacker News...")
            top_stories_url = f"{self.hn_api_base}/topstories.json"
            story_ids = requests.get(top_stories_url).json()
            for story_id in story_ids[:limit_per_source]:
                story_url = f"{self.hn_api_base}/item/{story_id}.json"
                story_data = requests.get(story_url).json()
                if story_data and "title" in story_data:
                    all_headlines.append(f"[HN] {story_data['title']}")
            self.logger.info(f"Fetched {limit_per_source} titles from Hacker News.")
        except Exception as e:
            self.logger.warning(f"Could not fetch from Hacker News: {e}")

        # Reddit (for broader, non-technical user perspective)
        try:
            self.logger.info(f"Fetching top posts from Reddit sources: {self.reddit_sources}")
            for subreddit in self.reddit_sources:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit_per_source}"
                headers = {'User-Agent': 'MISO Market Research Agent v2.0'}
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                for post in response.json()['data']['children']:
                    all_headlines.append(f"[r/{subreddit}] {post['data']['title']}")
            self.logger.info(f"Fetched titles from Reddit.")
        except Exception as e:
            self.logger.warning(f"Could not fetch from Reddit: {e}")

        return all_headlines

    def _create_analysis_prompt(self, headlines: list) -> str:
        """Creates the prompt for the LLM to analyze the headlines for a broad audience."""
        headlines_str = "\n".join(f"- {h}" for h in headlines)
        return f"""
        You are a market research analyst. Your goal is to identify common problems and software needs for a broad audience, including **developers, entrepreneurs, small business owners, and creators.**
        Analyze the following list of headlines from Hacker News and Reddit.
        Identify and categorize discussions about common pain points, popular new business ideas, or frequently requested "starter" application types.

        **Headlines:**
        {headlines_str}

        **Instructions:**
        1.  Read all the headlines to understand the current zeitgeist.
        2.  Identify recurring themes or project ideas (e.g., "AI-powered scheduling tool", "inventory management app", "social media content generator").
        3.  Generate a ranked list of the top 5 most common or valuable project categories you identified.
        4.  For each category, provide a brief "opportunity analysis" explaining why it's a valuable area for MISO to target for "anyone".
        5.  You MUST respond with ONLY a single, valid JSON object.

        **JSON Output Format:**
        {{
          "trends": [
            {{ "rank": <int>, "project_category": "<string>", "opportunity_analysis": "<string>" }}
          ]
        }}
        """

    def analyze_market_trends(self) -> dict:
        """Performs the full market analysis workflow."""
        headlines = self._gather_market_data()
        if not headlines:
            return {"error": "Could not retrieve any headlines for analysis."}

        prompt = self._create_analysis_prompt(headlines)
        self.logger.info("Sending headlines to LLM for trend analysis...")

        try:
            response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}], format='json')
            report = json.loads(response['message']['content'])
            self.logger.info("Successfully generated market trends report.")
            return report
        except Exception as e:
            self.logger.error(f"Failed to generate market trends report: {e}")
            return {"error": "Failed to get analysis from LLM."}
