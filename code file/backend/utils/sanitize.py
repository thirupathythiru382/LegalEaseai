import re
import unicodedata


def sanitize_text(text: str) -> str:
    """
    Clean AI-generated text so that it can safely
    be displayed and exported.
    """

    if not text:
        return ""

    text = text.replace("\u2018", "'")
    text = text.replace("\u2019", "'")

    text = text.replace("\u201c", '"')
    text = text.replace("\u201d", '"')

    text = text.replace("\u2013", "-")
    text = text.replace("\u2014", "-")

    text = text.replace("\u00a0", " ")

    text = unicodedata.normalize("NFKC", text)

    # Remove dangerous control characters.
    text = re.sub(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]",
        "",
        text,
    )

    # Prevent excessive blank lines.
    text = re.sub(
        r"\n{4,}",
        "\n\n\n",
        text,
    )

    return text.strip()


def split_terms(terms: str) -> list[str]:
    """
    Convert semicolon-separated terms into a list.
    """

    if not terms:
        return []

    return [
        item.strip()
        for item in terms.split(";")
        if item.strip()
    ]