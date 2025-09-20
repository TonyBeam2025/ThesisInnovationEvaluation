import re
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, Optional


def _normalize_label(line: str) -> str:
    cleaned = line.strip()
    cleaned = re.sub(r'^[#\*\s]+', '', cleaned)
    cleaned = re.sub(r'[\*\s]+$', '', cleaned)
    return cleaned.strip()


def _match_date_value(text: str) -> Optional[date]:
    if not text:
        return None
    chunk = text.strip()
    if not chunk:
        return None
    parts = re.split(r'[：:]', chunk, maxsplit=1)
    if len(parts) == 2:
        chunk = parts[1]
    chunk = re.sub(r'（.*?）|\(.*?\)', '', chunk)
    translation = str.maketrans({
        '年': '-',
        '月': '-',
        '日': '',
        '/': '-',
        '.': '-',
        '．': '-',
    })
    chunk = chunk.translate(translation)
    chunk = re.sub(r'\s+', '', chunk)
    if not chunk:
        return None
    candidates = [chunk, chunk.replace('-', '')]
    formats = ('%Y-%m-%d', '%Y%m%d', '%Y-%m', '%Y%m')
    for candidate in candidates:
        for fmt in formats:
            try:
                dt = datetime.strptime(candidate, fmt)
                if fmt in ('%Y-%m', '%Y%m'):
                    dt = datetime(dt.year, dt.month, 1)
                return dt.date()
            except ValueError:
                continue
    match = re.search(r'(\d{4})(\d{1,2})(\d{1,2})', candidates[0])
    if match:
        year, month, day = map(int, match.groups())
        return date(year, month, day)
    return None


def _extract_date(md: str, labels: Iterable[str]) -> Optional[date]:
    lines = md.splitlines()
    label_lower = [lbl.lower() for lbl in labels]
    for idx, line in enumerate(lines):
        normalized = _normalize_label(line).lower()
        if any(lbl in normalized for lbl in label_lower):
            date_value = _match_date_value(line)
            if not date_value and idx + 1 < len(lines):
                date_value = _match_date_value(lines[idx + 1])
            if date_value:
                return date_value
    return None


def _first_heading(md: str) -> str:
    for line in md.splitlines():
        m = re.match(r"^\s{0,3}#\s+(.+)$", line.strip())
        if m:
            return m.group(1).strip()
    return ""


def _find_keywords(md: str, labels) -> str:
    for line in md.splitlines():
        if any(lbl.lower() in line.lower() for lbl in labels):
            m = re.search(r"(?:关键词|关键字|Keywords?)[:：]\s*(.+)", line, re.I)
            if m:
                return m.group(1).strip()
    return ""


def _extract_block(md: str, headers) -> str:
    # 提取“## 摘要 … 到下一个标题”
    pat_h = re.compile(
        r"^\s{0,3}#{1,6}\s*(" + "|".join(map(re.escape, headers)) + r")\b.*$",
        re.I | re.M,
    )
    m = pat_h.search(md)
    if m:
        start = m.end()
    else:
        pat_l = re.compile(
            r"^(?:" + "|".join(map(re.escape, headers)) + r")\s*[:：]?\s*$",
            re.I | re.M,
        )
        m = pat_l.search(md)
        if not m:
            return ""
        start = m.end()
    nxt = re.search(r"^\s{0,3}#{1,6}\s+\S+", md[start:], re.M)
    end = start + (nxt.start() if nxt else len(md) - start)
    return md[start:end].strip()


def _build_thesis_info_from_md(md_path: Path) -> Dict:
    md = md_path.read_text("utf-8", errors="ignore")
    h1 = _first_heading(md) or md_path.stem
    # 中文摘要/关键词
    abs_cn = _extract_block(md, ["中文摘要", "摘要"]) or ""
    kw_cn = _find_keywords(md, ["关键词", "关键字"]) or ""
    # 标题（若H1含中文）
    has_cn = bool(re.search(r"[\u4e00-\u9fa5]", h1))
    title_cn = h1 if has_cn else ""
    # 研究方法（可选）
    methods = _extract_block(md, ["研究方法", "方法"]) or ""

    defense_dt = _extract_date(md, ['论文答辩日期', '答辩日期', '答辩时间', '答辩'])
    completion_dt = _extract_date(md, ['论文完成日期', '完成日期', '完成时间'])
    submission_dt = _extract_date(md, ['论文提交日期', '提交日期', '提交时间'])
    search_cutoff = defense_dt or completion_dt or submission_dt

    # 同时填充多套命名，兼容内部用法
    info = {
        # cnki_client_pool 生成检索式用（中文简写）
        "title_ch": title_cn,
        "keywords_ch": kw_cn,
        "abstract_ch": abs_cn,
        # 常规字段（snake_case）
        "title_cn": title_cn,
        "keywords_cn": kw_cn,
        "abstract_cn": abs_cn,
        # 向量化/兼容用（驼峰）
        "ChineseTitle": title_cn,
        "ChineseKeywords": kw_cn,
        "ChineseAbstract": abs_cn,
        # 研究方法（可选）
        "research_methods": methods,
    }

    if defense_dt:
        info['defense_date'] = defense_dt.isoformat()
    if completion_dt:
        info['completion_date'] = completion_dt.isoformat()
    if submission_dt:
        info['submission_date'] = submission_dt.isoformat()
    if search_cutoff:
        info['search_cutoff_date'] = search_cutoff.strftime('%Y%m%d')

    return info


def main():
    from thesis_inno_eval.cnki_client_pool import cnki_auto_search

    input_dir = Path("data/input")
    md_files = sorted(input_dir.glob("*.md"))
    if not md_files:
        print("No .md files found in data/input")
        return

    print(f"Found {len(md_files)} .md files.")
    for md_file in md_files:
        print(f"\n=== Processing: {md_file.name} ===")
        thesis_info = _build_thesis_info_from_md(md_file)
        try:
            res = cnki_auto_search(
                file_path=str(md_file),
                languages=["Chinese"],  # 仅中文检索
                existing_thesis_info=thesis_info,  # 跳过章节/抽取，直接用.md要素
            )
            papers_by_lang = res.get("papers_by_lang", {}) if res else {}
            print(
                f"  Chinese: Top papers = {len(papers_by_lang.get('Chinese', []))}"
            )
        except Exception as e:
            print(f"  Failed: {e}")


if __name__ == "__main__":
    main()

