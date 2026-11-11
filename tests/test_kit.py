from pathlib import Path

from web_audit_kit import check_meta, lint_llms_txt, validate_jsonld
from web_audit_kit.cli import main

F = Path(__file__).parent / "fixtures"


def test_jsonld_good():
    r = validate_jsonld((F / "page_good.html").read_text())
    assert r["ok"] and r["blocks"] == 1 and not r["missing_required"]
    assert {"Organization", "WebSite", "FAQPage", "Question", "Answer"} <= set(r["types"])


def test_jsonld_bad():
    r = validate_jsonld((F / "page_bad.html").read_text())
    assert not r["ok"] and r["blocks"] == 3 and len(r["parse_errors"]) == 1
    assert "Organization.url" in r["missing_required"]
    assert "BlogPosting.author" in r["missing_required"] and "BlogPosting.datePublished" in r["missing_required"]


def test_jsonld_question_missing_answer():
    html = '<script type="application/ld+json">{"@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Q"}]}</script>'
    assert "Question.acceptedAnswer" in validate_jsonld(html)["missing_required"]


def test_jsonld_none():
    r = validate_jsonld("<html></html>")
    assert r["blocks"] == 0 and not r["ok"]


def test_meta_good_and_bad():
    good = check_meta((F / "page_good.html").read_text())
    assert good["ok"], good["issues"]
    bad = check_meta((F / "page_bad.html").read_text())
    assert any(i.startswith("title-too-short") for i in bad["issues"])
    assert "meta-description-missing" in bad["issues"] and "canonical-missing" in bad["issues"]
    assert "html-lang-missing" in bad["issues"] and any(i.startswith("h1-multiple") for i in bad["issues"])


def test_llms_good():
    r = lint_llms_txt((F / "llms_good.txt").read_text())
    assert r["ok"] and r["h1"] == "Example Studio" and r["h2_sections"] == 1 and r["links"] == 2


def test_llms_bad():
    r = lint_llms_txt("<!doctype html><html>nope</html>", 200, "text/html")
    assert not r["ok"] and len(r["problems"]) >= 3
    assert not lint_llms_txt(None, 404, None)["present"]
    rel = lint_llms_txt("# T\n\n> s\n\n## A\n- [x](/x)\n")
    assert rel["ok"] and rel["warnings"]


def test_cli(capsys):
    assert main(["all", str(F / "page_good.html")]) == 0
    assert main(["llms", str(F / "llms_good.txt")]) == 0
    assert main(["meta", str(F / "page_bad.html")]) == 1
