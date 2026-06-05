import json
import logging
import time

from openai import OpenAI

from src.config import OPENAI_API_KEY, LLM_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE
from src.fetchers.base_fetcher import Paper

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "你是一位 IC（集成电路）与 EDA（电子设计自动化）领域的资深研究员。请对用户提供的英文学术论文进行专业分析，输出 JSON 格式。"

USER_PROMPT_TEMPLATE = """请分析以下论文，生成中文摘要和评价。返回严格 JSON 格式（不要包含 markdown 代码块标记）：

{{
  "chinese_title": "论文中文译名",
  "summary": "200-300字的中文摘要，涵盖：研究问题、核心方法、主要创新点和实验结果",
  "contribution": "该论文对 IC/EDA 领域的主要贡献（1-2句话）",
  "relevance_score": 1-5（该论文对 IC/EDA 领域的相关度和重要性评分，5为最高）,
  "tags": ["标签1", "标签2", "标签3"]
}}

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
