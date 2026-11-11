# web-audit-kit

Small, reusable SEO and AEO (answer-engine) checks as pure Python functions plus a tiny CLI.
No crawling, no accounts, no data collection: give it HTML or an `llms.txt` and it tells you what is wrong.

| Check | Function | What it flags |
|---|---|---|
| JSON-LD | `validate_jsonld(html)` | unparseable `ld+json` blocks; missing required properties for common schema.org types (Organization, WebSite, Article, FAQPage/Question, BreadcrumbList, LocalBusiness, Service, Product, SoftwareApplication, Event) |
| llms.txt | `lint_llms_txt(text, status, content_type)` | not served, HTML instead of markdown, wrong content type, no `# Title`, no `>` summary, no links; warns on relative links, missing `##` sections, files over 200 KB |
| Meta | `check_meta(html)` | title outside 30 to 60 characters, description outside 70 to 160, missing or multiple H1, missing canonical, missing `html lang` |

The required-property table is a small lint subset of Google's rich-result minimums, not a full
schema.org validator. Length ranges are common guidance, not hard rules; pass your own ranges to `check_meta`.

## Use

```
pip install git+https://github.com/SarutobiSasuke8/web-audit-kit
web-audit-kit all page.html                          # JSON-LD + meta for a saved page
web-audit-kit llms --url https://example.com/llms.txt  # one GET, no crawl
curl -s https://example.com/ | web-audit-kit jsonld -
```

Exit code is 0 when every requested check passes, 1 otherwise. Output is JSON.

```python
from web_audit_kit import validate_jsonld, lint_llms_txt, check_meta
```

## Contributing

One check or fix per change, with a fixture and a test. Fixtures use `example.com` only:
never commit real client pages, findings or private data. `pip install -e ".[dev]" && ruff check . && pytest -q`.

Licence: [MIT](LICENSE).
