import math
from datetime import datetime, timezone

from src.config import load_sources
from src.fetchers.base_fetcher import Paper
from src.filters.keyword_filter import KeywordFilter


class QualityScorer:
    def __init__(self):
        sources = load_sources()
        scoring_config = sources.get("scoring", {})
        self.keyword_weight = scoring_config.get("keyword_weight", 0.50)
        self.source_weight = scoring_config.get("source_weight", 0.30)
        self.recency_weight = scoring_config.get("recency_weight", 0.20)
        self.min_score_threshold = scoring_config.get("min_score_threshold", 0.3)
        self.source_weights = sources.get("source_weights", {})
        self.keyword_filter = KeywordFilter()

    def _source_score(self, paper: Paper) -> float:
        venue = paper.venue or ""
        for known_venue, weight in self.source_weights.items():
            if known_venue.lower() in venue.lower():
                return weight
        return 0.5

    def _recency_score(self, paper: Paper) -> float:
        if not paper.published_date:
            return 0.5
        now = datetime.now(timezone.utc)
        delta_days = (now - paper.published_date).days
        if delta_days <= 1:
            return 1.0
        elif delta_days <= 3:
            return 0.9
        elif delta_days <= 7:
            return 0.7
        elif delta_days <= 14:
            return 0.5
        else:
            return 0.2

    def _citation_score(self, paper: Paper) -> float:
        citations = paper.citation_count
        if citations <= 0:
            return 0.3
        log_score = math.log(citations + 1) / math.log(100)
        return min(log_score, 1.0)

    def score(self, paper: Paper) -> float:
        kw_score = self.keyword_filter.match_score(paper)
        src_score = self._source_score(paper)
        rec_score = self._recency_score(paper)
        cit_score = self._citation_score(paper)

        total = (
            self.keyword_weight * kw_score
            + self.source_weight * src_score
            + self.recency_weight * (0.5 * rec_score + 0.5 * cit_score)
        )
        paper.score = round(total, 4)
        return paper.score

    def filter_and_rank(self, papers: list[Paper], top_n: int = 20) -> list[Paper]:
        scored = []
        for paper in papers:
            s = self.score(paper)
            if s >= self.min_score_threshold:
                scored.append(paper)

        scored.sort(key=lambda p: p.score, reverse=True)
        return scored[:top_n]
