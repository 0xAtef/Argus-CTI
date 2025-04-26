'''
inferer.py
Hugging Face inference module to classify or extract relevant CTI tags.
'''

import re
from typing import Dict, List
from transformers import pipeline

class HFInferer:
    """
    HFInferer uses a zero-shot classification model and regex to extract:
      - Sector tags (banking, healthcare, etc.)
      - Vendor tags (fortinet, f5, etc.)
      - CVE identifiers
    """
    def __init__(
        self,
        model_name: str = "facebook/bart-large-mnli",
        candidate_sectors: List[str] = None,
        candidate_vendors: List[str] = None,
        cve_pattern: str = r"CVE-\d{4}-\d{4,7}",
        threshold: float = 0.5,
    ):
        # Initialize zero-shot classifier
        self.classifier = pipeline("zero-shot-classification", model=model_name, device=0)
        # Default label sets
        self.candidate_sectors = candidate_sectors or ["banking", "healthcare", "energy", "government"]
        self.candidate_vendors = candidate_vendors or ["fortinet", "f5", "cisco", "palo alto"]
        # Regex for CVE extraction
        self.cve_regex = re.compile(cve_pattern, re.IGNORECASE)
        # Score threshold for label acceptance
        self.threshold = threshold

    def infer(self, entry: Dict) -> Dict[str, List[str]]:
        """
        Run inference on a feed entry, returning tags:
          {
            "sector": [...],
            "vendor": [...],
            "cve": [...]
          }
        """
        text = f"{entry.get('title', '')} {entry.get('summary', '')}"

        # Combine candidate labels for classification
        labels = self.candidate_sectors + self.candidate_vendors
        result = self.classifier(text, labels, multi_label=True)

        found_sectors: List[str] = []
        found_vendors: List[str] = []
        for label, score in zip(result["labels"], result["scores"]):
            if score >= self.threshold:
                label_lower = label.lower()
                if label_lower in [s.lower() for s in self.candidate_sectors]:
                    found_sectors.append(label)
                elif label_lower in [v.lower() for v in self.candidate_vendors]:
                    found_vendors.append(label)

        # Extract CVE identifiers
        found_cves = self.cve_regex.findall(text)

        return {
            "sector": list(set(found_sectors)),
            "vendor": list(set(found_vendors)),
            "cve": list(set(found_cves))
        }
