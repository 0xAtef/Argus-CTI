'''
fetcher.py
RSS ingestion module for Argus-CTI.
'''

import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger(__name__)

class RSSFetcher:
    """
    RSSFetcher pulls entries from given RSS feed URLs and normalizes them.
    """
    def __init__(self, urls: List[str]):
        self.urls = urls

    def fetch(self, recent_hours: int = 24) -> List[Dict]:
        """
        Fetch RSS feeds from configured URLs and return list of normalized entries,
        filtered to only include entries published within the last `recent_hours`.
        """
        all_entries: List[Dict] = []
        cutoff = datetime.utcnow() - timedelta(hours=recent_hours)

        for url in self.urls:
            try:
                feed = feedparser.parse(url)
                if feed.bozo:
                    logger.warning(f"Error parsing feed {url}: {feed.bozo_exception}")
                for entry in feed.entries:
                    published_iso = self._parse_published(entry)
                    try:
                        published_dt = datetime.fromisoformat(published_iso)
                    except Exception:
                        published_dt = None

                    if published_dt and published_dt < cutoff:
                        continue  # Skip older entries

                    # Collect all <category> tags into a list
                    categories = []
                    if hasattr(entry, "tags"):
                        categories = [tag.get("term", "").strip() for tag in entry.tags]

                    normalized = {
                        "id": getattr(entry, "id", entry.get("link", "")),
                        "title": entry.get("title", ""),
                        "summary": entry.get("summary", ""),
                        "link": entry.get("link", ""),
                        "published": published_iso,
                        "source": url,
                        # other fields (sector/vendor/etc.) come from the inferer
                        "category": categories,  
                    }
                    all_entries.append(normalized)
            except Exception as e:
                logger.error(f"Failed to fetch feed {url}: {e}")
        return all_entries


    def _parse_published(self, entry) -> str:
        """
        Attempt to parse published or updated date into ISO format, fallback to raw string.
        """
        raw_date = entry.get("published", "") or entry.get("updated", "")
        try:
            dt = datetime(*entry.published_parsed[:6])
            return dt.isoformat()
        except Exception:
            return raw_date
