"""JSON-LD validator: parse every ld+json block, list types, flag missing required properties.

The required-property table is a deliberately small subset of Google's rich-result
minimums. It is a lint, not a full schema.org validator.
"""
from __future__ import annotations

import json
import re

from bs4 import BeautifulSoup

REQUIRED_PROPS = {
    "Organization": ["name", "url"],
    "WebSite": ["name", "url"],
    "Article": ["headline", "author", "datePublished"],
    "FAQPage": ["mainEntity"],
    "Question": ["name", "acceptedAnswer"],
    "BreadcrumbList": ["itemListElement"],
    "LocalBusiness": ["name", "address"],
    "Service": ["name", "provider"],
    "Product": ["name"],
    "SoftwareApplication": ["name"],
    "Event": ["name", "startDate", "location"],
}
SUBTYPES = {
    "BlogPosting": "Article", "NewsArticle": "Article", "TechArticle": "Article",
    "Corporation": "Organization", "OnlineBusiness": "Organization", "NGO": "Organization",
    "ProfessionalService": "LocalBusiness", "LegalService": "LocalBusiness",
    "FinancialService": "LocalBusiness", "Store": "LocalBusiness", "Restaurant": "LocalBusiness",
    "WebApplication": "SoftwareApplication", "MobileApplication": "SoftwareApplication",
    "VideoGame": "SoftwareApplication",
}


def _types(node) -> list[str]:
    t = node.get("@type") if isinstance(node, dict) else None
    if t is None:
        return []
    return [str(x) for x in (t if isinstance(t, list) else [t])]


def _walk(data):
    """Every dict carrying @type, including @graph members and nested values."""
    if isinstance(data, list):
        for item in data:
            yield from _walk(item)
    elif isinstance(data, dict):
        if "@type" in data:
            yield data
        for key, value in data.items():
            if key != "@context" and isinstance(value, (list, dict)):
                yield from _walk(value)


def _top(data):
    """Top-level entities only (direct, list items, @graph members): where required props apply."""
    if isinstance(data, list):
        for item in data:
            yield from _top(item)
    elif isinstance(data, dict):
        if isinstance(data.get("@graph"), list):
            yield from _top(data["@graph"])
        if "@type" in data:
            yield data


def _empty(value) -> bool:
    return value is None or value == "" or value == [] or value == {}


def validate_jsonld(html: str) -> dict:
    """Return {blocks, types, parse_errors, missing_required, ok} for one HTML document."""
    soup = BeautifulSoup(html, "html.parser")
    blocks, errors, types, missing = 0, [], set(), []
    for i, tag in enumerate(soup.find_all("script", attrs={"type": re.compile(r"ld\+json", re.IGNORECASE)})):
        blocks += 1
        raw = tag.string if tag.string is not None else tag.get_text()
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError) as exc:
            errors.append(f"block {i}: {exc.__class__.__name__}: {str(exc)[:120]}")
            continue
        for node in _walk(data):
            types.update(_types(node))
            for t in _types(node):
                if SUBTYPES.get(t, t) == "Question":
                    for prop in REQUIRED_PROPS["Question"]:
                        if _empty(node.get(prop)):
                            missing.append(f"{t}.{prop}")
        for node in _top(data):
            for t in _types(node):
                base = SUBTYPES.get(t, t)
                if base == "Question":
                    continue
                for prop in REQUIRED_PROPS.get(base, []):
                    if _empty(node.get(prop)):
                        missing.append(f"{t}.{prop}")
    missing = sorted(set(missing))
    return {"blocks": blocks, "types": sorted(types), "parse_errors": errors,
            "missing_required": missing, "ok": blocks > 0 and not errors and not missing}
