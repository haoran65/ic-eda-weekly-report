import re

from src.config import load_keywords
from src.fetchers.base_fetcher import Paper


class KeywordFilter:
    def __init__(self):
        kw_config = load_keywords()
        self.ic_keywords: list[str] = kw_config.get("ic_keywords", [])
        self.eda_keywords: list[str] = kw_config.get("eda_keywords", [])
        self.exclude_keywords: list[str] = kw_config.get("exclude_keywords", [])
        self.all_keywords = self.ic_keywords + self.eda_keywords

    def match_score(self, paper: Paper) -> float:
        text = (paper.title + " " + paper.abstract).lower()
        matched_count = 0
        matched_keywords: list[str] = []

        for kw in self.all_keywords:
            pattern = re.compile(r"\b" + re.escape(kw.lower()) + r"\b")
            if pattern.search(text):
                matched_count += 1
                matched_keywords.append(kw)

        for kw in self.exclude_keywords:
            pattern = re.compile(r"\b" + re.escape(kw.lower()) + r"\b")
            if pattern.search(text):
                return 0.0

        if not self.all_keywords:
            return 0.0

        paper.keywords = matched_keywords
        return matched_count / len(self.all_keywords)

    def should_include(self, paper: Paper, min_score: float = 0.03) -> bool:
        score = self.match_score(paper)
        return score >= min_score
