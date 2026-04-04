import string

PUNCTUATION_TABLE = str.maketrans('', '', string.punctuation)

def clean_text_for_search(title: str, content: str) -> str:
    """
    Apply Phase 1 indexing logic to produce searchable_text.
    1. Combine title and content
    2. Convert to lowercase
    3. Remove punctuation
    4. Normalize whitespace
    """
    if not title and not content:
        return ""
    combined = f"{title} {content}".lower()
    cleaned = combined.translate(PUNCTUATION_TABLE)
    cleaned = ' '.join(cleaned.split())
    return cleaned