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
        lines.append("# IC & EDA 领域论文周报")
        lines.append("")
        lines.append(f"**报告周期：** {week_start.strftime('%Y年%m月%d日')} - {week_end.strftime('%Y年%m月%d日')}")
        lines.append(f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**论文数量：** {len(analyses)} 篇")
        lines.append("")
        lines.append("---")
        lines.append("")

        papers_by_relevance = sorted(analyses, key=lambda a: a.get("relevance_score", 0), reverse=True)

        lines.append("## 总体概览")
        lines.append("")
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

        lines.append("## 论文详情")
        lines.append("")

        for i, analysis in enumerate(papers_by_relevance, 1):
            title = analysis.get("chinese_title", analysis.get("original_title", "N/A"))
            org_title = analysis.get("original_title", "")
            relevance = analysis.get("relevance_score", 0)
            stars = "⭐" * relevance

            lines.append(f"### {i}. {title}")
            lines.append("")
            lines.append(f"> **原文标题：** {org_title}")
            lines.append("")
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

            lines.append("")

            summary = analysis.get("summary", "暂无摘要")
            lines.append(f"**中文摘要：** {summary}")
            lines.append("")

            contribution = analysis.get("contribution", "")
            if contribution:
                lines.append(f"**核心贡献：** {contribution}")
                lines.append("")

            tags = analysis.get("tags", [])
            if tags:
                tag_str = "、".join(tags)
                lines.append(f"**标签：** {tag_str}")
                lines.append("")

            lines.append("---")
            lines.append("")

        content = "\n".join(lines)
        filepath.write_text(content, encoding="utf-8")
        return filepath
