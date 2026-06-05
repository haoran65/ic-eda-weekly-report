import logging
from datetime import datetime, timedelta, timezone

import arxiv

from src.config import load_sources
from src.fetchers.base_fetcher import BaseFetcher, Paper

logger = logging.getLogger(__name__)


class ArxivFetcher(BaseFetcher):
    def __init__(self):
        sources = load_sources()
        arxiv_config = sources.get("arxiv", {})
        self.categories = arxiv_config.get("categories", ["cs.AR", "cs.ET"])
        self.max_results = arxiv_config.get("max_results_per_category", 200)

    @property
    def source_name(self) -> str:
        return "arxiv"

    def fetch(self, lookback_days: int = 7) -> list[Paper]:
        papers: list[Paper] = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=lookback_days)

        for category in self.categories:
            logger.info(f"Fetching ArXiv papers from category: {category}")
            try:
                search = arxiv.Search(
                    query=f"cat:{category}",
                    max_results=self.max_results,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                )
                client = arxiv.Client()
                results = list(client.results(search))

                for result in results:
                    pub_date = result.published.replace(tzinfo=timezone.utc)
                    if pub_date < cutoff_date:
                        continue

                    paper = Paper(
                        paper_id=result.entry_id.split("/")[-1],
                        title=result.title,
                        authors=[str(a) for a in result.authors],
                        abstract=result.summary.replace("\n", " "),
                        url=result.entry_id,
                        pdf_url=result.pdf_url,
                        published_date=pub_date,
                        source="arxiv",
                        venue="ArXiv",
                    )
                    papers.append(paper)

                logger.info(f"Fetched {len(papers)} papers from category {category} (so far)")

            except Exception as e:
                logger.error(f"Failed to fetch ArXiv category {category}: {e}")

        return papers
