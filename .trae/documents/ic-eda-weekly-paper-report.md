# IC & EDA 领域论文周报自动生成系统 - 实现计划

> **For agentic workers:** 按照本计划逐步实现，每步使用 checkbox (`- [ ]`) 语法跟踪进度。

**目标：** 构建一个自动化系统，每周从 ArXiv、Semantic Scholar 等学术平台获取 IC（集成电路）与 EDA（电子设计自动化）领域最新论文，通过关键词过滤和综合评分筛选 10-20 篇高价值论文，使用 OpenAI GPT-4 进行中文摘要分析，最终生成 Markdown 格式的周报。

**架构：** 采用模块化的 Python CLI 工具，分为 Fetcher（数据获取）、Filter（筛选排序）、Analyzer（LLM 分析）、Reporter（报告生成）四层，通过 GitHub Actions 定时（每周一 9:00 北京时间）自动运行。

**技术栈：** Python 3.11+、OpenAI API (GPT-4)、arxiv Python 库、Semantic Scholar API、PyYAML、GitHub Actions

---

## 需求汇总

| 维度 | 选择 |
|------|------|
| **论文来源** | ArXiv, Semantic Scholar（覆盖 IEEE TIP/TCE、ACM FPGA、FCCM、FPL 等） |
| **输出格式** | Markdown 文件（中文） |
| **运行方式** | GitHub Actions 定时任务（每周一早 9:00 北京时间） |
| **分析方式** | 规则过滤 + LLM (GPT-4) 混合分析 |
| **价值标准** | 综合评分（关键词匹配度 + 来源权威性 + 引用/影响力） |
| **论文数量** | 每周 10-20 篇 |
| **报告语言** | 中文 |

---

## 项目结构

```
report/
├── .github/
│   └── workflows/
│       └── weekly_report.yml          # GitHub Actions 定时工作流
├── src/
│   ├── __init__.py
│   ├── config.py                      # 配置管理（API Key、关键词、评分权重等）
│   ├── main.py                        # 主入口：编排整个流程
│   ├── fetchers/
│   │   ├── __init__.py
│   │   ├── base_fetcher.py            # 抽象基类
│   │   ├── arxiv_fetcher.py           # ArXiv API 论文获取
│   │   └── semantic_scholar_fetcher.py # Semantic Scholar API 论文获取
│   ├── filters/
│   │   ├── __init__.py
│   │   ├── keyword_filter.py          # IC/EDA 关键词匹配过滤
│   │   └── quality_scorer.py          # 综合评分与排序
│   ├── analyzers/
│   │   ├── __init__.py
│   │   └── llm_analyzer.py            # OpenAI GPT-4 论文分析与摘要
│   └── reporters/
│       ├── __init__.py
│       └── markdown_reporter.py       # Markdown 周报生成
├── config/
│   ├── keywords.yaml                  # IC/EDA 领域关键词配置
│   └── sources.yaml                   # 论文来源与搜索策略配置
├── output/                            # 周报输出目录（.gitkeep 保留）
│   └── .gitkeep
├── requirements.txt
└── .env.example                       # 环境变量模板
```

---

## 数据流

```
[GitHub Actions 定时触发]
        │
        ▼
[ArXiv API] ──→ arxiv_fetcher ──┐
                                 ├──→ [合并去重] ──→ keyword_filter ──→ quality_scorer
[Semantic Scholar API] ──→ ss_fetcher ──┘                        │
                                                                  ▼
                                              [Top 10-20 论文] ──→ llm_analyzer (GPT-4)
                                                                        │
                                                                        ▼
                                              markdown_reporter ──→ output/weekly_report_YYYY-MM-DD.md
```

---

## 任务分解

### Task 1: 项目初始化与配置文件

**文件：**
- 创建：`requirements.txt`
- 创建：`.env.example`
- 创建：`config/keywords.yaml`
- 创建：`config/sources.yaml`
- 创建：`output/.gitkeep`
- 创建：`src/__init__.py`
- 创建：`src/config.py`

- [ ] **Step 1: 创建 requirements.txt**

```txt
arxiv>=2.1.0
openai>=1.30.0
pyyaml>=6.0
python-dotenv>=1.0.0
requests>=2.31.0
semanticscholar>=0.6.0
```

- [ ] **Step 2: 创建 .env.example**

```
OPENAI_API_KEY=sk-your-key-here
SEMANTIC_SCHOLAR_API_KEY=your-key-here
```

- [ ] **Step 3: 创建 config/keywords.yaml**

```yaml
ic_keywords:
  - "integrated circuit"
  - "VLSI"
  - "ASIC"
  - "SoC"
  - "system-on-chip"
  - "semiconductor"
  - "transistor"
  - "CMOS"
  - "FinFET"
  - "nanometer"
  - "chip design"
  - "processor"
  - "microarchitecture"
  - "RTL"
  - "logic synthesis"
  - "physical design"
  - "place and route"
  - "clock tree"
  - "power analysis"
  - "timing analysis"
  - "DFT"
  - "design for test"
  - "verification"
  - "formal verification"
  - "analog circuit"
  - "mixed-signal"
  - "memory"
  - "SRAM"
  - "DRAM"
  - "NVM"
  - "non-volatile memory"
  - "interconnect"
  - "3D IC"
  - "chiplet"
  - "advanced packaging"
  - "silicon photonics"

eda_keywords:
  - "EDA"
  - "electronic design automation"
  - "CAD"
  - "computer-aided design"
  - "logic synthesis"
  - "high-level synthesis"
  - "HLS"
  - "physical design"
  - "floorplanning"
  - "placement"
  - "routing"
  - "clock tree synthesis"
  - "timing closure"
  - "power optimization"
  - "design space exploration"
  - "machine learning for EDA"
  - "ML for EDA"
  - "reinforcement learning"
  - "graph neural network"
  - "GNN"
  - "deep learning"
  - "circuit simulation"
  - "SPICE"
  - "static timing analysis"
  - "STA"
  - "formal verification"
  - "model checking"
  - "SAT solver"
  - "BDD"
  - "technology mapping"
  - "FPGA"
  - "field-programmable gate array"
  - "reconfigurable computing"
  - "FCCM"
  - "FPL"
  - "IP core"
  - "NoC"
  - "network-on-chip"
  - "thermal analysis"
  - "IR drop"
  - "electromigration"
  - "reliability"
  - "yield"

exclude_keywords:
  - "biomedical"
  - "biology"
  - "genetic"
  - "protein"
  - "drug"
  - "clinical"
  - "quantum computing"  # related but separate field
```

- [ ] **Step 4: 创建 config/sources.yaml**

```yaml
arxiv:
  categories:
    - "cs.AR"   # Hardware Architecture
    - "cs.ET"   # Emerging Technologies
    - "cs.LG"   # Machine Learning (filtered for EDA)
    - "cs.CV"   # Computer Vision (filtered for hardware acceleration)
  max_results_per_category: 200
  lookback_days: 7

semantic_scholar:
  search_queries:
    - "integrated circuit design"
    - "electronic design automation"
    - "VLSI design automation"
    - "FPGA architecture"
    - "EDA machine learning"
    - "physical design automation"
    - "logic synthesis optimization"
    - "hardware verification"
  venues:  # IEEE/ACM venues of interest
    - "IEEE Transactions on Image Processing"
    - "IEEE Transactions on Consumer Electronics"
    - "ACM Transactions on Reconfigurable Technology and Systems"
    - "FCCM"
    - "FPL"
  max_results_per_query: 50

scoring:
  keyword_weight: 0.50        # 关键词匹配度权重
  source_weight: 0.30         # 来源权威性权重
  recency_weight: 0.20        # 时效性权重
  min_score_threshold: 0.3    # 最低分数阈值

source_weights:
  "DAC": 1.0
  "ICCAD": 1.0
  "ISSCC": 1.0
  "IEEE TIP": 0.9
  "IEEE TCE": 0.8
  "ACM FPGA": 0.9
  "FCCM": 0.9
  "FPL": 0.9
  "ArXiv": 0.6
```

- [ ] **Step 5: 创建 output/.gitkeep**（空文件，确保 output 目录被 git 跟踪）

- [ ] **Step 6: 创建 src/__init__.py**（空文件）

- [ ] **Step 7: 创建 src/config.py**

```python
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
OUTPUT_DIR = PROJECT_ROOT / "output"


def load_keywords() -> dict:
    with open(CONFIG_DIR / "keywords.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_sources() -> dict:
    with open(CONFIG_DIR / "sources.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))

MAX_PAPERS_PER_WEEK = int(os.getenv("MAX_PAPERS_PER_WEEK", "20"))
```

- [ ] **Step 8: 初始化 git 仓库并提交**

```bash
cd d:\code\trae\report
git init
git add .
git commit -m "chore: initialize project structure and configuration"
```

---

### Task 2: 实现基础 Fetcher 抽象类

**文件：**
- 创建：`src/fetchers/__init__.py`
- 创建：`src/fetchers/base_fetcher.py`

- [ ] **Step 1: 创建 src/fetchers/__init__.py**（空文件）

- [ ] **Step 2: 创建 src/fetchers/base_fetcher.py**

```python
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
    source: str = ""           # "arxiv", "semantic_scholar"
    venue: str = ""            # "DAC", "ICCAD", "ArXiv", etc.
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
```

- [ ] **Step 3: 提交**

```bash
git add src/fetchers/
git commit -m "feat: add base fetcher abstract class with Paper dataclass"
```

---

### Task 3: 实现 ArXiv Fetcher

**文件：**
- 创建：`src/fetchers/arxiv_fetcher.py`

- [ ] **Step 1: 创建 src/fetchers/arxiv_fetcher.py**

```python
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
```

- [ ] **Step 2: 提交**

```bash
git add src/fetchers/arxiv_fetcher.py
git commit -m "feat: add ArXiv paper fetcher"
```

---

### Task 4: 实现 Semantic Scholar Fetcher

**文件：**
- 创建：`src/fetchers/semantic_scholar_fetcher.py`

- [ ] **Step 1: 创建 src/fetchers/semantic_scholar_fetcher.py**

```python
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
```

- [ ] **Step 2: 提交**

```bash
git add src/fetchers/semantic_scholar_fetcher.py
git commit -m "feat: add Semantic Scholar paper fetcher"
```

---

### Task 5: 实现关键词过滤器

**文件：**
- 创建：`src/filters/__init__.py`
- 创建：`src/filters/keyword_filter.py`

- [ ] **Step 1: 创建 src/filters/__init__.py**（空文件）

- [ ] **Step 2: 创建 src/filters/keyword_filter.py**

```python
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
```

- [ ] **Step 3: 提交**

```bash
git add src/filters/
git commit -m "feat: add keyword-based paper filter"
```

---

### Task 6: 实现综合评分器

**文件：**
- 创建：`src/filters/quality_scorer.py`

- [ ] **Step 1: 创建 src/filters/quality_scorer.py**

```python
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
```

- [ ] **Step 2: 提交**

```bash
git add src/filters/quality_scorer.py
git commit -m "feat: add comprehensive quality scorer with multi-factor ranking"
```

---

### Task 7: 实现 LLM 论文分析器

**文件：**
- 创建：`src/analyzers/__init__.py`
- 创建：`src/analyzers/llm_analyzer.py`

- [ ] **Step 1: 创建 src/analyzers/__init__.py**（空文件）

- [ ] **Step 2: 创建 src/analyzers/llm_analyzer.py**

```python
import json
import logging
import time

from openai import OpenAI

from src.config import OPENAI_API_KEY, LLM_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE
from src.fetchers.base_fetcher import Paper

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一位 IC（集成电路）与 EDA（电子设计自动化）领域的资深研究员。请对用户提供的英文学术论文进行专业分析，输出 JSON 格式。"""

USER_PROMPT_TEMPLATE = """请分析以下论文，生成中文摘要和评价。返回严格 JSON 格式（不要包含 markdown 代码块标记）：

{
  "chinese_title": "论文中文译名",
  "summary": "200-300字的中文摘要，涵盖：研究问题、核心方法、主要创新点和实验结果",
  "contribution": "该论文对 IC/EDA 领域的主要贡献（1-2句话）",
  "relevance_score": 1-5（该论文对 IC/EDA 领域的相关度和重要性评分，5为最高）,
  "tags": ["标签1", "标签2", "标签3"]
}

论文标题：{title}
作者：{authors}
摘要：{abstract}
发布日期：{date}
来源：{source}
"""


class LLMAnalyzer:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set. Please set it in .env file.")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = LLM_MODEL
        self.max_tokens = LLM_MAX_TOKENS
        self.temperature = LLM_TEMPERATURE

    def analyze(self, paper: Paper) -> dict:
        prompt = USER_PROMPT_TEMPLATE.format(
            title=paper.title,
            authors=", ".join(paper.authors[:5]),
            abstract=paper.abstract[:3000],
            date=paper.published_date.strftime("%Y-%m-%d") if paper.published_date else "N/A",
            source=f"{paper.source} ({paper.venue})" if paper.venue else paper.source,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)

        except Exception as e:
            logger.error(f"LLM analysis failed for paper '{paper.title[:50]}...': {e}")
            return {
                "chinese_title": paper.title,
                "summary": f"[分析失败: {str(e)}]",
                "contribution": "",
                "relevance_score": 0,
                "tags": [],
            }

    def analyze_batch(self, papers: list[Paper]) -> list[dict]:
        results = []
        for i, paper in enumerate(papers):
            logger.info(f"Analyzing paper {i + 1}/{len(papers)}: {paper.title[:60]}...")
            result = self.analyze(paper)
            result["paper_id"] = paper.paper_id
            result["url"] = paper.url
            result["original_title"] = paper.title
            result["authors"] = paper.authors
            result["venue"] = paper.venue
            result["source"] = paper.source
            result["citation_count"] = paper.citation_count
            result["score"] = paper.score
            result["published_date"] = (
                paper.published_date.strftime("%Y-%m-%d") if paper.published_date else "N/A"
            )
            results.append(result)
            time.sleep(0.5)
        return results
```

- [ ] **Step 3: 提交**

```bash
git add src/analyzers/
git commit -m "feat: add LLM-based paper analyzer using OpenAI GPT-4"
```

---

### Task 8: 实现 Markdown 周报生成器

**文件：**
- 创建：`src/reporters/__init__.py`
- 创建：`src/reporters/markdown_reporter.py`

- [ ] **Step 1: 创建 src/reporters/__init__.py**（空文件）

- [ ] **Step 2: 创建 src/reporters/markdown_reporter.py**

```python
from datetime import datetime, timedelta
from pathlib import Path

from src.config import OUTPUT_DIR


class MarkdownReporter:
    def __init__(self):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def generate(self, analyses: list[dict], week_start: datetime) -> Path:
        week_end = week_start + timedelta(days=6)
        filename = f"weekly_report_{week_start.strftime('%Y-%m-%d')}.md"
        filepath = OUTPUT_DIR / filename

        lines = []
        lines.append(f"# IC & EDA 领域论文周报")
        lines.append(f"")
        lines.append(f"**报告周期：** {week_start.strftime('%Y年%m月%d日')} - {week_end.strftime('%Y年%m月%d日')}")
        lines.append(f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**论文数量：** {len(analyses)} 篇")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

        papers_by_relevance = sorted(analyses, key=lambda a: a.get("relevance_score", 0), reverse=True)

        lines.append(f"## 总体概览")
        lines.append(f"")
        top_tags = {}
        for a in papers_by_relevance:
            for tag in a.get("tags", []):
                top_tags[tag] = top_tags.get(tag, 0) + 1
        sorted_tags = sorted(top_tags.items(), key=lambda x: x[1], reverse=True)[:10]

        if sorted_tags:
            lines.append("**本周热门研究主题：**")
            lines.append("")
            for tag, count in sorted_tags:
                lines.append(f"- {tag}（{count}篇）")
            lines.append("")

        lines.append(f"## 论文详情")
        lines.append(f"")

        for i, analysis in enumerate(papers_by_relevance, 1):
            title = analysis.get("chinese_title", analysis.get("original_title", "N/A"))
            org_title = analysis.get("original_title", "")
            relevance = analysis.get("relevance_score", 0)
            stars = "⭐" * relevance

            lines.append(f"### {i}. {title}")
            lines.append(f"")
            lines.append(f"> **原文标题：** {org_title}")
            lines.append(f"")
            lines.append(f"**相关性评分：** {stars} ({relevance}/5)  ")
            lines.append(f"**来源：** {analysis.get('source', 'N/A')} ({analysis.get('venue', 'N/A')})  ")
            lines.append(f"**作者：** {', '.join(analysis.get('authors', [])[:5])}  ")

            pub_date = analysis.get("published_date", "N/A")
            lines.append(f"**发布日期：** {pub_date}  ")

            citations = analysis.get("citation_count", 0)
            if citations:
                lines.append(f"**引用数：** {citations}  ")

            url = analysis.get("url", "")
            if url:
                lines.append(f"**论文链接：** [{url}]({url})  ")

            lines.append(f"")

            summary = analysis.get("summary", "暂无摘要")
            lines.append(f"**中文摘要：** {summary}")
            lines.append(f"")

            contribution = analysis.get("contribution", "")
            if contribution:
                lines.append(f"**核心贡献：** {contribution}")
                lines.append(f"")

            tags = analysis.get("tags", [])
            if tags:
                tag_str = "、".join(tags)
                lines.append(f"**标签：** {tag_str}")
                lines.append(f"")

            lines.append(f"---")
            lines.append(f"")

        content = "\n".join(lines)
        filepath.write_text(content, encoding="utf-8")
        return filepath
```

- [ ] **Step 3: 提交**

```bash
git add src/reporters/
git commit -m "feat: add Markdown weekly report generator"
```

---

### Task 9: 实现主入口 main.py

**文件：**
- 创建：`src/main.py`

- [ ] **Step 1: 创建 src/main.py**

```python
import logging
import sys
from datetime import datetime, timedelta

from src.config import MAX_PAPERS_PER_WEEK
from src.fetchers.arxiv_fetcher import ArxivFetcher
from src.fetchers.semantic_scholar_fetcher import SemanticScholarFetcher
from src.filters.keyword_filter import KeywordFilter
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
```

- [ ] **Step 2: 提交**

```bash
git add src/main.py
git commit -m "feat: add main entry point orchestrating the full pipeline"
```

---

### Task 10: 配置 GitHub Actions 定时工作流

**文件：**
- 创建：`.github/workflows/weekly_report.yml`

- [ ] **Step 1: 创建 .github/workflows/weekly_report.yml**

```yaml
name: Weekly IC & EDA Paper Report

on:
  schedule:
    - cron: "0 1 * * 1"   # 每周一 UTC+8 9:00 = UTC 1:00
  workflow_dispatch:       # 允许手动触发

jobs:
  generate-report:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Generate weekly report
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          SEMANTIC_SCHOLAR_API_KEY: ${{ secrets.SEMANTIC_SCHOLAR_API_KEY }}
        run: python -m src.main

      - name: Commit and push report
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add output/
          git diff --cached --quiet || git commit -m "docs: add weekly report $(date +'%Y-%m-%d')"
          git push
```

- [ ] **Step 2: 提交**

```bash
git add .github/workflows/weekly_report.yml
git commit -m "feat: add GitHub Actions weekly scheduled workflow"
```

---

### Task 11: 本地运行验证

**文件：** 无新文件

- [ ] **Step 1: 创建 .env 文件并填入真实的 API Key**

在项目根目录创建 `.env` 文件：
```
OPENAI_API_KEY=sk-your-real-key
SEMANTIC_SCHOLAR_API_KEY=your-real-key  # 可选
```

- [ ] **Step 2: 安装依赖**

```bash
cd d:\code\trae\report
pip install -r requirements.txt
```

- [ ] **Step 3: 本地运行完整流程**

```bash
python -m src.main
```

- [ ] **Step 4: 验证输出**

检查 `output/` 目录下是否生成了 `weekly_report_YYYY-MM-DD.md` 文件，确认内容包括：
- 报告标题和周期
- 总体概览（热门主题标签）
- 10-20 篇论文的详细分析（中文标题、摘要、核心贡献、标签）
- 论文原文链接

- [ ] **Step 5: 提交 .gitignore（如果需要）**

创建 `.gitignore`：
```
.env
__pycache__/
*.pyc
.venv/
venv/
```

---

## 假设与决策

| 决策点 | 选择与理由 |
|--------|-----------|
| **论文来源策略** | 使用 ArXiv API（免费）+ Semantic Scholar API（免费层）为主。IEEE Xplore 和 ACM DL 直接 API 需要机构订阅，改用 Semantic Scholar 间接获取这些期刊/会议的论文元数据。 |
| **不下载 PDF** | 由于版权和付费墙限制，系统仅获取论文元数据和摘要，不做 PDF 全文下载。LLM 基于摘要进行分析。 |
| **语言** | 所有代码注释、报告内容均为中文。配置文件中的关键词保留英文以保持匹配准确性。 |
| **去重逻辑** | 按 paper_id（优先）和 title（备选）进行去重。 |
| **评分公式** | `0.50 × 关键词匹配 + 0.30 × 来源权威度 + 0.20 × 时效性/引用度` |
| **LLM 调用** | 每篇论文间隔 0.5 秒，避免触发 OpenAI rate limit。使用 GPT-4o 模型，设定 `response_format={"type": "json_object"}` 保证结构化输出。 |
| **GitHub Actions** | 使用 `ubuntu-latest` runner，Python 3.11，每周一 UTC 1:00（北京时间 9:00）触发。 |
| **API Key 管理** | 通过 GitHub Secrets 管理 `OPENAI_API_KEY` 和 `SEMANTIC_SCHOLAR_API_KEY`。 |

---

## 验证方法

1. **单元测试**（可选后续扩展）：对各模块编写 pytest 测试
2. **本地运行**：执行 `python -m src.main`，确认完整流程无报错
3. **输出检查**：确认生成的 Markdown 文件格式正确、内容完整
4. **GitHub Actions 手动触发**：push 到 GitHub 后在 Actions 页面手动触发 `workflow_dispatch`，验证云端运行
5. **定时任务验证**：首次运行后等待下一周，确认自动触发是否正常
