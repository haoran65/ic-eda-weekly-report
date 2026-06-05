from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Paper:
    paper_id: str
    title: str
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    url: str = ""
    pdf_url: str = ""
    published_date: Optional[datetime] = None
    source: str = ""
    venue: str = ""
    citation_count: int = 0
    keywords: list[str] = field(default_factory=list)
    score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "url": self.url,
            "pdf_url": self.pdf_url,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "source": self.source,
            "venue": self.venue,
            "citation_count": self.citation_count,
            "keywords": self.keywords,
            "score": self.score,
        }


class BaseFetcher(ABC):
    @abstractmethod
    def fetch(self, lookback_days: int = 7) -> list[Paper]:
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        pass
