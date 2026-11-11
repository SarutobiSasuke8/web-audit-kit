"""llms.txt linter against the llmstxt.org shape: H1 title, > summary, ## sections, markdown links."""
from __future__ import annotations

import re

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)\s]+)[^)]*\)")


def lint_llms_txt(text: str | None, status: int | None = 200, content_type: str | None = "text/plain") -> dict:
    out = {"status": status, "content_type": content_type, "present": status == 200 and bool(text),
           "problems": [], "warnings": [], "h1": None, "has_summary": False, "h2_sections": 0,
           "links": 0, "bytes": len(text.encode()) if text else 0}
    if not out["present"]:
        out["problems"].append(f"not served (status {status})" if status != 200 else "empty file")
        return out
    if content_type and not re.search(r"text/(plain|markdown)", content_type, re.IGNORECASE):
        out["problems"].append(f"content-type is {content_type}, expected text/plain or text/markdown")
    if re.search(r"<html|<!doctype", text[:500], re.IGNORECASE):
        out["problems"].append("looks like HTML, not markdown")
    lines = [line for line in text.splitlines() if line.strip()]
    if lines and lines[0].startswith("# "):
        out["h1"] = lines[0][2:].strip()
    else:
        out["problems"].append("first non-empty line is not an H1 (# Title)")
    if sum(1 for line in lines if line.startswith("# ")) > 1:
        out["warnings"].append("more than one H1")
    out["has_summary"] = any(line.startswith(">") for line in lines[:6])
    if not out["has_summary"]:
        out["problems"].append("no > summary blockquote near the top")
    out["h2_sections"] = sum(1 for line in lines if line.startswith("## "))
    if out["h2_sections"] == 0:
        out["warnings"].append("no ## sections")
    links = LINK_RE.findall(text)
    out["links"] = len(links)
    if not links:
        out["problems"].append("no markdown links")
    relative = [u for u in links if not re.match(r"https?://", u)]
    if relative:
        out["warnings"].append(f"{len(relative)} relative link(s); absolute URLs are safer for AI fetchers")
    if out["bytes"] > 200_000:
        out["warnings"].append("larger than 200 KB; consider moving detail to llms-full.txt")
    out["ok"] = not out["problems"]
    return out
