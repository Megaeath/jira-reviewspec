from atlassian import Confluence
from bs4 import BeautifulSoup
import re


class ConfluenceFetcher:
    def __init__(self, url, username, api_token):
        self.confluence = Confluence(
            url=url, username=username, password=api_token, cloud=True
        )

    def get_page_content(self, page_url):
        # Extract page ID or title from URL
        # URL format: https://domain.atlassian.net/wiki/spaces/SPACE/pages/12345/Title
        page_id_match = re.search(r"pages/(\d+)", page_url)
        if page_id_match:
            page_id = page_id_match.group(1)
            page = self.confluence.get_page_by_id(
                page_id, expand="body.storage,version,metadata.labels"
            )
        else:
            # Fallback to title search if URL is different
            # This is more complex, but for POC let's focus on page ID
            raise ValueError(
                "Could not extract page ID from URL. Please use a link containing '/pages/ID/'."
            )

        title = page.get("title", "Unknown Title")
        body_html = page.get("body", {}).get("storage", {}).get("value", "")
        version = page.get("version", {}).get("number", 1)

        # Clean HTML to text
        soup = BeautifulSoup(body_html, "html.parser")
        text_content = soup.get_text(separator="\n")

        return {
            "title": title,
            "text": text_content,
            "version": f"v{version}",
            "url": page_url,
        }
