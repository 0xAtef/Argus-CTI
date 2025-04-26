# src/misp_client.py

from pymisp import PyMISP, MISPEvent
import logging

logger = logging.getLogger("argus_cti.misp_client")

class MISPClient:
    def __init__(self, url: str, api_key: str, ssl: bool = False):
        self.misp = PyMISP(url, api_key, ssl=ssl)

    def event_exists(self, info: str) -> bool:
        resp = self.misp.search(controller='events', value=info, python_return=True)
        return bool(resp)

    def create_event(self, entry: dict) -> None:
        info = entry["title"]
        if self.event_exists(info):
            logger.info(f"Event already exists for: {info}")
            return

        # 1) Build the MISPEvent
        event = MISPEvent()
        event.info = info
        event.date = entry.get("published", "")[:10] or None
        event.analysis = 1
        event.threat_level_id = 3
        event.distribution = 0

        # 2) Add the URL as an 'url' attribute
        event.add_attribute(
            'url',
            entry["link"],
            category="External analysis",
            to_ids=False
        )

        # 3) Add your inferred tags (sector, vendor, etc.)
        for tag_type, tags in entry.get("tags", {}).items():
            if isinstance(tags, list):
                for tag in tags:
                    event.add_attribute(
                        'text',
                        f"{tag_type}:{tag}",
                        category="Other",
                        to_ids=False
                    )

        # 4) Add RSS categories as text attributes
        for cat in entry.get("category", []):
            event.add_attribute(
                'text',
                f"category:{cat}",
                category="Other",
                to_ids=False
            )

        # 5) Push the event to MISP
        try:
            created = self.misp.add_event(event)  # you can use python_return=True if you need the JSON back
            event_id = created.get('Event', {}).get('id')
            logger.info(f"Created MISP event '{info}' (ID: {event_id})")
            
            # 6) Tag the event itself with each RSS category
            for cat in entry.get("category", []):
                try:
                    self.misp.tag(event_id, cat)
                    logger.debug(f"Tagged event {event_id} with '{cat}'")
                except Exception as e:
                    logger.warning(f"Failed tagging event {event_id} with '{cat}': {e}")

        except Exception as e:
            logger.error(f"Failed to create MISP event for '{info}': {e}")
