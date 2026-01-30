from app.services.advanced_classifier import classify_email as advanced_classify


def classify_email(text: str, attachments: list[dict] | None = None, remetente: str | None = None) -> dict:
    """Wrapper to keep backward compatibility. Calls the advanced classifier which returns
    {'tipo','subtipo','confidence'}. For backwards compatibility with older callers that expect
    only tipo/confidence, we still provide these keys.
    """
    res = advanced_classify(text, attachments or [], remetente)
    return res

