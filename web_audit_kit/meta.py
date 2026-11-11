"""Title and meta description presence and length checks (plus H1, canonical and lang)."""
from __future__ import annotations

from bs4 import BeautifulSoup

TITLE_RANGE = (30, 60)
DESCRIPTION_RANGE = (70, 160)


def _range_issue(kind: str, length: int, bounds: tuple[int, int]) -> str | None:
    lo, hi = bounds
    if length < lo:
        return f"{kind}-too-short ({length} < {lo} chars)"
    if length > hi:
        return f"{kind}-too-long ({length} > {hi} chars)"
    return None


def check_meta(html: str, title_range=TITLE_RANGE, description_range=DESCRIPTION_RANGE) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("title")
    title = tag.get_text(strip=True) if tag else None
    desc = None
    for m in soup.find_all("meta"):
        if (m.get("name") or "").strip().lower() == "description":
            desc = (m.get("content") or "").strip()
            break
    issues = []
    if not title:
        issues.append("title-missing")
    else:
        issue = _range_issue("title", len(title), title_range)
        if issue:
            issues.append(issue)
    if not desc:
        issues.append("meta-description-missing")
    else:
        issue = _range_issue("meta-description", len(desc), description_range)
        if issue:
            issues.append(issue)
    h1 = len(soup.find_all("h1"))
    if h1 == 0:
        issues.append("h1-missing")
    elif h1 > 1:
        issues.append(f"h1-multiple ({h1})")
    canonical = None
    for link in soup.find_all("link"):
        if "canonical" in [r.lower() for r in (link.get("rel") or [])] and link.get("href"):
            canonical = link["href"].strip()
            break
    if not canonical:
        issues.append("canonical-missing")
    lang = soup.html.get("lang") if soup.html else None
    if not lang:
        issues.append("html-lang-missing")
    return {"title": title, "title_len": len(title) if title else 0, "meta_description": desc,
            "meta_description_len": len(desc) if desc else 0, "h1_count": h1, "canonical": canonical,
            "html_lang": lang, "issues": issues, "ok": not issues}
