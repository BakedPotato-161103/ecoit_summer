import re
import unicodedata

def clean_text(text):
    """
    Remove all hyperlinks from the input text, keeping only the visible text.
    Supports formats like <a href="...">text</a> and raw URLs.
    """
    # Remove HTML anchor tags but keep the text inside
    text = re.sub(r'<a [^>]*>(.*?)</a>', r'\1', text, flags=re.IGNORECASE)
    # Remove raw URLs (http, https, www)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = unicodedata.normalize("NFKD", text)
    return text.strip()

