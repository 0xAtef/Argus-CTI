'''
filter_engine.py
Rule-based filtering engine for Argus-CTI.
'''

import re
import logging
from typing import List, Dict, Any

class FilterEngine:
    def __init__(self, filters: List[Dict[str, Any]]):
        self.filters = filters

    def filter(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filtered_entries = []
        for entry in entries:
            if self._matches_filters(entry):
                filtered_entries.append(entry)
        return filtered_entries

    def _matches_filters(self, entry: Dict[str, Any]) -> bool:
        """
        OR-across-rules: return True if any one rule dict matches.
        """
        for rule in self.filters:
            if all(self._match(entry, key, criteria) for key, criteria in rule.items()):
                return True
        return False

    def _match(self, entry: Dict[str, Any], key: str, criteria: Dict[str, Any]) -> bool:
        """
        Match a single entry field against one criteria dict.
        """
        logger = logging.getLogger("argus_cti.filter_engine")

        # Special fallback for category: if no categories, look in title
        if key == "category":
            cats = entry.get("category") or []
            if not cats:
                title = entry.get("title", "")
                allowed = criteria.get("in", [])
                for term in allowed:
                    if term.lower() in title.lower():
                        return True
                logger.debug(f"Entry {entry.get('id')} failed category/title fallback for {allowed}")
                return False
            # otherwise, fall through to normal “in” check

        # Field missing? auto-fail (unless it’s category, which we handled above)
        if key not in entry:
            logger.debug(f"Skipping entry {entry.get('id','<no-id>')} - Missing '{key}'")
            return False

        value = entry[key]

        # equals
        if "equals" in criteria:
            if value != criteria["equals"]:
                logger.debug(f"{value!r} != {criteria['equals']!r} for key '{key}'")
                return False
            return True

        # in
        if "in" in criteria:
            allowed = criteria["in"]
            if isinstance(value, list):
                if not any(item in allowed for item in value):
                    logger.debug(f"No overlap between {value!r} and {allowed!r} for key '{key}'")
                    return False
            else:
                if value not in allowed:
                    logger.debug(f"{value!r} not in {allowed!r} for key '{key}'")
                    return False
            return True

        # regex
        if "matches" in criteria:
            pattern = criteria["matches"]
            if not re.search(pattern, str(value)):
                logger.debug(f"'{value}' !~ /{pattern}/ for key '{key}'")
                return False
            return True

        # contains
        if "contains" in criteria:
            substr = criteria["contains"].lower()
            if substr not in str(value).lower():
                logger.debug(f"'{substr}' not in '{value}' for key '{key}'")
                return False
            return True

        return False
