# Argus-CTI

**Argus-CTI** is an automated pipeline that ingests RSS threat feeds, filters for relevant intelligence (e.g., banking sector incidents, vendor advisories, new CVEs), and pushes structured events into MISP.

## 🔧 Prerequisites

- Python 3.8+
- A running MISP instance and API credentials
- Internet access to fetch RSS feeds

## 🚀 Installation

1. Clone the repository and navigate into it:

   ```bash
   git clone <repo_url> argus-cti
   cd argus-cti
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

### RSS Sources

Define your RSS feed URLs in **config/feeds.yml**:

```yaml
feeds:
  - https://example.com/threats/rss
  - https://another.source/apt/feed
```

These URLs are the “RSS sources” Argus-CTI will poll for threat intelligence.

### Filters

Edit **config/filters.yml** to specify which items to keep:

```yaml
filters:
  - type: sector
    equals: banking
  - type: vendor
    in: [fortinet, f5]
  - type: cve
    matches: '^CVE-20[0-9]{2}-'
```

## 📦 Usage

Run the CLI to fetch, filter, and push to MISP:

```bash
python -m argus_cti.cli   --feeds config/feeds.yml   --filters config/filters.yml   --misp-url https://misp.local   --misp-key YOUR_API_KEY
```

