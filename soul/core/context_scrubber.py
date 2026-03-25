import re
from bs4 import BeautifulSoup

def scrub_web_content(html: str) -> str:
    """Removes noise (scripts, styles, boilerplate) to focus on relevant text."""
    if not html:
        return ""
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove junk tags
    for tag in soup(["script", "style", "svg", "path", "iframe", "footer", "nav"]):
        tag.decompose()
        
    # Get text and clean whitespace
    text = soup.get_text(separator='\n')
    text = re.sub(r'\n\s*\n', '\n', text) # Collapse multiple newlines
    
    # Truncate to save tokens (keep first 3000 chars)
    return text[:3000].strip()

def scrub_json_response(data: Dict) -> str:
    """Ensures JSON responses are clean and formatted."""
    import json
    return json.dumps(data, indent=2)[:2000]
