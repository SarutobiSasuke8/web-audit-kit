"""web-audit-kit: small, reusable SEO/AEO checks. Pure functions, no network unless asked."""
__version__ = "0.1.0"

from .jsonld import validate_jsonld
from .llms import lint_llms_txt
from .meta import check_meta

__all__ = ["__version__", "check_meta", "lint_llms_txt", "validate_jsonld"]
