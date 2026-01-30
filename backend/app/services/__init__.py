# Import core services. Defer optional, heavy dependencies to avoid test-time failures.
from . import classifier, extractor, history  # noqa: F401

# preview depends on PIL/pdfplumber; import lazily
try:
    from . import preview
except Exception:
    preview = None

# email_collector imports imapclient which may not be present in test env
try:
    from . import email_collector
except Exception:
    email_collector = None

