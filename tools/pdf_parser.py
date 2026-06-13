from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any


def _max_parse_pages() -> int:
    try:
        return max(1, int(os.getenv("FIN_AGENT_PDF_MAX_PAGES", "200")))
    except ValueError:
        return 200


def _extract_with_pdfplumber(path: Path, max_pages: int) -> tuple[str, int, int]:
    import pdfplumber

    text_parts: list[str] = []
    with pdfplumber.open(path) as pdf:
        total_pages = len(pdf.pages)
        pages = pdf.pages[:max_pages]
        for page in pages:
            text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts), total_pages, len(pages)


def _extract_with_pymupdf(path: Path, max_pages: int) -> tuple[str, int, int]:
    import fitz

    text_parts: list[str] = []
    with fitz.open(path) as doc:
        total_pages = doc.page_count
        pages_to_read = min(total_pages, max_pages)
        for page in doc[:pages_to_read]:
            text_parts.append(page.get_text())
    return "\n".join(text_parts), total_pages, pages_to_read


def _slice_section(text: str, keywords: list[str], max_chars: int = 1800) -> str:
    for keyword in keywords:
        idx = text.find(keyword)
        if idx >= 0:
            return text[idx : idx + max_chars]
    return ""


def parse_annual_report(pdf_path: str | Path | None) -> dict[str, Any]:
    if not pdf_path:
        return {"status": "skipped", "message": "未上传 PDF，已跳过年报文本增强分析。"}

    path = Path(pdf_path)
    if not path.exists():
        return {"status": "failed", "message": f"PDF 文件不存在：{path}"}

    max_pages = _max_parse_pages()
    try:
        text, total_pages, pages_parsed = _extract_with_pymupdf(path, max_pages)
    except Exception:
        try:
            text, total_pages, pages_parsed = _extract_with_pdfplumber(path, max_pages)
        except Exception as exc:
            return {"status": "failed", "message": f"PDF 解析失败：{exc}"}

    compact = re.sub(r"\s+", " ", text)
    company_match = re.search(r"([\u4e00-\u9fa5A-Za-z0-9（）()·]+股份有限公司)", compact)
    year_match = re.search(r"(20\d{2})\s*年(?:年度)?报告", compact)

    return {
        "status": "success",
        "company_name": company_match.group(1) if company_match else "未识别",
        "report_year": year_match.group(1) if year_match else "未识别",
        "management_discussion": _slice_section(text, ["管理层讨论与分析", "经营情况讨论与分析"]),
        "main_operations": _slice_section(text, ["主要经营情况", "主营业务分析"]),
        "risk_notes": _slice_section(text, ["风险提示", "可能面对的风险"]),
        "accounting_policy": _slice_section(text, ["重要会计政策", "会计估计"]),
        "text_preview": compact[:1200],
        "total_pages": total_pages,
        "pages_parsed": pages_parsed,
        "file_size_mb": round(path.stat().st_size / 1024 / 1024, 2),
        "message": f"PDF 解析完成：{path.stat().st_size / 1024 / 1024:.2f}MB，共{total_pages}页，已抽取前{pages_parsed}页。",
    }
