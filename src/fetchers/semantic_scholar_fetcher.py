import logging
from datetime import datetime, timedelta, timezone

import requests

from src.config import load_sources, SEMANTIC_SCHOLAR_API_KEY
from src.fetchers.base_fetcher import BaseFetcher, Paper

logger = logging.getLogger(__name__)

BASE_URL = "https://api.semanticscholar.org/graph/v1"


class SemanticScholarFetcher(BaseFetcher):
    def __init__(self):
        sources = load_sources()
        ss_config = sources.get("semantic_scholar", {})
        self.search_queries = ss_config.get("search_queries", [])
        self.max_results = ss_config.get("max_results_per_query", 50)
        self.api_key = SEMANTIC_SCHOLAR_API_KEY or None

    @property
    def source_name(self) -> str:
        return "semantic_scholar"

    def _headers(self) -> dict:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def fetch(self, lookback_days: int = 7) -> list[Paper]:
        papers: list[Paper] = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=lookback_days)

        for query in self.search_queries:
            logger.info(f"Searching Semantic Scholar for: '{query}'")
            try:
                params = {
                    "query": query,
                    "limit": self.max_results,
                    "sort": "publicationDate:desc",
                    "fields": "paperId,title,authors,abstract,url,externalIds,publicationDate,venue,citationCount,year",
                }
                resp = requests.get(
                    f"{BASE_URL}/paper/search",
                    headers=self._headers(),
                    params=params,
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()

                for item in data.get("data", []):
                    pub_date_str = item.get("publicationDate")
                    if not pub_date_str:
                        continue
                    try:
                        pub_date = datetime.strptime(pub_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    except ValueError:
                        continue
                    if pub_date < cutoff_date:
                        continue

                    authors = [a.get("name", "") for a in item.get("authors", [])]
                    external_ids = item.get("externalIds", {})
                    doi = external_ids.get("DOI", "")
                    url = f"https://doi.org/{doi}" if doi else f"https://api.semanticscholar.org/paper/{item.get('paperId', '')}"

                    venues = item.get("venue", {}) or {}
                    venue_name = venues.get("name", "") if isinstance(venues, dict) else str(venues)

                    paper = Paper(
                        paper_id=item.get("paperId", ""),
                        title=item.get("title", ""),
                        authors=authors,
                        abstract=(item.get("abstract") or "").replace("\n", " "),
                        url=url,
                        pdf_url="",
                        published_date=pub_date,
                        source="semantic_scholar",
                        venue=venue_name,
                        citation_count=item.get("citationCount", 0) or 0,
                    )
                    papers.append(paper)

                logger.info(f"Found {len(papers)} papers from query '{query}' (total so far)")

            except Exception as e:
                logger.error(f"Failed to search Semantic Scholar for '{query}': {e}")

        return papers
