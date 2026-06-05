import logging
import sys
from datetime import datetime, timedelta

from src.config import MAX_PAPERS_PER_WEEK
from src.fetchers.arxiv_fetcher import ArxivFetcher
from src.fetchers.semantic_scholar_fetcher import SemanticScholarFetcher
from src.filters.quality_scorer import QualityScorer
from src.analyzers.llm_analyzer import LLMAnalyzer
from src.reporters.markdown_reporter import MarkdownReporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def deduplicate(papers: list) -> list:
    seen = set()
    unique = []
    for paper in papers:
        key = paper.paper_id or paper.title.lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(paper)
    return unique


def main():
    logger.info("=== IC & EDA Weekly Paper Report Generator ===")
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    logger.info("Step 1: Fetching papers from sources...")
    all_papers = []

    try:
        arxiv_fetcher = ArxivFetcher()
        arxiv_papers = arxiv_fetcher.fetch(lookback_days=7)
        logger.info(f"ArXiv fetched: {len(arxiv_papers)} papers")
        all_papers.extend(arxiv_papers)
    except Exception as e:
        logger.error(f"ArXiv fetch failed: {e}")

    try:
        ss_fetcher = SemanticScholarFetcher()
        ss_papers = ss_fetcher.fetch(lookback_days=7)
        logger.info(f"Semantic Scholar fetched: {len(ss_papers)} papers")
        all_papers.extend(ss_papers)
    except Exception as e:
        logger.error(f"Semantic Scholar fetch failed: {e}")

    all_papers = deduplicate(all_papers)
    logger.info(f"Total papers after deduplication: {len(all_papers)}")

    if not all_papers:
        logger.warning("No papers fetched. Exiting.")
        return

    logger.info("Step 2: Filtering and scoring papers...")
    scorer = QualityScorer()
    top_papers = scorer.filter_and_rank(all_papers, top_n=MAX_PAPERS_PER_WEEK)
    logger.info(f"Top papers after scoring: {len(top_papers)}")

    if not top_papers:
        logger.warning("No papers passed the scoring threshold. Exiting.")
        return

    for i, p in enumerate(top_papers):
        logger.info(f"  {i + 1}. [{p.score:.3f}] {p.title[:80]}")

    logger.info("Step 3: Analyzing papers with LLM...")
    analyzer = LLMAnalyzer()
    analyses = analyzer.analyze_batch(top_papers)
    logger.info(f"Analysis complete for {len(analyses)} papers")

    logger.info("Step 4: Generating weekly report...")
    reporter = MarkdownReporter()
    report_path = reporter.generate(analyses, week_start)
    logger.info(f"Weekly report generated: {report_path}")

    logger.info("=== Done! ===")


if __name__ == "__main__":
    main()
