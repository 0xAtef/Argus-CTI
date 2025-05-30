# Argus-CTI

**Argus-CTI** is an automated pipeline that ingests RSS threat feeds, applies machine learning inference to extract or classify relevant cyber threat intelligence (CTI) tags, filters the entries based on user-defined rules (e.g., banking sector incidents, vendor advisories, new CVEs), and pushes structured events into MISP (Malware Information Sharing Platform).

---

**🛡️ Why "Argus"?**
In Greek mythology, Argus was a figure described variously as the son of Inachus, Agenor, or Arestor — or as an aboriginal hero (autochthon).
His byname comes from having a hundred eyes across his head or body, symbolizing vigilance and constant watchfulness — much like how Argus-CTI monitors cyber threat intelligence feeds.

---

It uses a **Hugging Face inference module** to enhance raw feed entries by tagging them with CTI-relevant labels, improving filtering and threat visibility.

## 🔧 Prerequisites

- Python 3.8+
- A running MISP instance and API credentials
- Internet access to fetch RSS feeds

## 🚀 Installation

1. Clone the repository and navigate into it:

   ```bash
   git clone https://github.com/0xAtef/Argus-CTI.git
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
  - https://feeds.feedburner.com/TheHackersNews
  - https://krebsonsecurity.com/feed/
  - https://www.bleepingcomputer.com/feed/
  - https://www.cisa.gov/news.xml
  - https://www.cert.ssi.gouv.fr/feed/
```

These URLs are the “RSS sources” Argus-CTI will poll for threat intelligence.

### Filters

Edit **config/filters.yml** to specify which items to keep:

```yaml
filters:
  - sector:
      equals: Banking
  - vendor:
      in: ["Fortinet", "F5"]
  - cve:
      matches: "CVE-202[3-5]-\\d{4,}"
  - attack_type:
      equals: "APT"
  - severity:
      equals: "Critical"
  - summary:
      contains: "vulnerability"
  - category:
      in: ["Malware", "Crypto", "Microsoft"]
```

## 📦 Usage

Run the CLI to fetch, filter, and push to MISP:

```bash
python src\cli.py   --feeds config/feeds.yml   --filters config/filters.yml   --misp-url https://misp.local   --misp-key YOUR_API_KEY
```
