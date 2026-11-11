"""web-audit-kit CLI. Reads a local file, stdin (-) or, with --url, fetches one URL (GET, no crawl)."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

from . import __version__
from .jsonld import validate_jsonld
from .llms import lint_llms_txt
from .meta import check_meta

USER_AGENT = f"web-audit-kit/{__version__} (+https://github.com/SarutobiSasuke8/web-audit-kit)"


def _read(source: str, is_url: bool):
    if is_url:
        req = urllib.request.Request(source, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.read().decode("utf-8", "replace"), resp.status, resp.headers.get("content-type")
        except urllib.error.HTTPError as exc:
            return "", exc.code, exc.headers.get("content-type")
    if source == "-":
        return sys.stdin.read(), 200, "text/plain"
    with open(source, encoding="utf-8") as fh:
        return fh.read(), 200, "text/plain"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="web-audit-kit", description=__doc__)
    ap.add_argument("check", choices=["jsonld", "llms", "meta", "all"])
    ap.add_argument("source", help="file path, - for stdin, or a URL with --url")
    ap.add_argument("--url", action="store_true", help="treat SOURCE as a URL and fetch it once")
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)
    text, status, ctype = _read(a.source, a.url)
    out = {}
    if a.check in ("jsonld", "all"):
        out["jsonld"] = validate_jsonld(text)
    if a.check in ("meta", "all"):
        out["meta"] = check_meta(text)
    if a.check == "llms":
        out["llms"] = lint_llms_txt(text, status, ctype)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if all(v.get("ok") for v in out.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
