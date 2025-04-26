# src/cli.py

import json
import logging
from pathlib import Path
import yaml
import click

from fetcher import RSSFetcher
from inferer import HFInferer
from filter_engine import FilterEngine
from misp_client import MISPClient
from utils import load_seen_ids, save_seen_ids

# Setup root logger
logger = logging.getLogger("argus_cti.cli")

def setup_logging(log_level):
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )

def load_yaml(path: str) -> dict:
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    return data or {}

@click.command(name="argus-cti")
@click.option("--feeds",     required=True, type=click.Path(exists=True), help="Path to RSS feeds YAML")
@click.option("--filters",   required=True, type=click.Path(exists=True), help="Path to filters YAML")
@click.option("--misp-url",  required=True, help="MISP instance URL")
@click.option("--misp-key",  required=True, help="MISP API key")
@click.option("--hours",     default=24,     help="Only include entries in last N hours")
@click.option("--log-level", default="INFO", help="Logging level: DEBUG/INFO/WARNING/ERROR")
def cli(feeds, filters, misp_url, misp_key, hours, log_level):
    """Argus-CTI Pipeline: fetch → infer → filter → MISP."""
    setup_logging(log_level)
    click.echo(f"Loading feeds from {feeds}", err=True)

    # Load configs
    feeds_cfg   = load_yaml(feeds)
    filters_cfg = load_yaml(filters)

    urls = feeds_cfg.get("feeds", [])
    if not urls:
        click.echo("ERROR: No RSS feeds defined.", err=True)
        raise click.Abort()

    rules = filters_cfg.get("filters", [])
    if not rules:
        logger.warning("No filters defined; passing all entries through.")

    # Fetch & filter
    fetcher = RSSFetcher(urls)
    entries = fetcher.fetch(recent_hours=hours)
    logger.info(f"Fetched {len(entries)} entries")

    inferer = HFInferer()
    for e in entries:
        e["tags"] = inferer.infer(e)
    logger.info("Completed inference tagging")

    engine = FilterEngine(rules)
    filtered = engine.filter(entries)
    logger.info(f"{len(filtered)} entries match filters")

    # Dedupe + MISP
    seen     = load_seen_ids()
    new_seen = set()
    misp     = MISPClient(misp_url, misp_key, ssl=False)

    for entry in filtered:
        eid = entry["id"]
        if eid in seen:
            logger.info(f"Skipping already-processed {eid}")
            continue
        misp.create_event(entry)
        new_seen.add(eid)

    # Persist
    save_seen_ids(seen | new_seen)
    click.echo(f"Processed {len(new_seen)} new entries", err=True)

if __name__ == "__main__":
    cli()
