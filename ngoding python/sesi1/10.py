#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import argparse
import datetime
import textwrap
import threading
import itertools
import time
import json
import sys
import os
import csv
import re
import xml.etree.ElementTree as ET
import subprocess
import concurrent.futures
from tqdm import tqdm
from git import Repo, GitCommandError, RemoteProgress
from google import genai
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader

VERSION = "0.13.0"

BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
ENDC = "\033[0m"

CVE_GITHUB_URL = "https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves"
EPSS_API_URL = "https://api.first.org/data/v1/epss?cve={cve_id}"
CISA_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
NUCLEI_URL = (
    "https://raw.githubusercontent.com/projectdiscovery/nuclei-templates/main/cves.json"
)
GITHUB_API_URL = "https://poc-in-github.motikan2010.net/api/v1/"
VULNCHECK_API_URL = "https://api.vulncheck.com/v3/index/vulncheck-kev"
EXPLOITDB_URL = "https://gitlab.com/exploit-database/exploitdb/-/raw/main/files_exploits.csv?ref_type=heads"
PACKETSTORM_URL = "https://packetstormsecurity.com/search/?q={cve_id}"
HACKERONE_URL = "https://hackerone.com/graphql"

CVSS_THRESHOLD = 6.0
EPSS_THRESHOLD = 0.2

PRIORITY_COLORS = {
    "A+": "\033[91m",
    "A": "\033[31m",
    "B": "\033[93m",
    "C": "\033[94m",
    "D": "\033[92m",
}


def get_cve_repo_dir():
    try:
        base_dir = config.get("local_database_dir",
                              os.path.expanduser("~/.sploitscan"))
    except NameError:
        base_dir = os.path.expanduser("~/.sploitscan")
    return os.path.join(base_dir, "cvelistV5")


def get_cve_local_dir():
    return os.path.join(get_cve_repo_dir(), "cves")


def parse_iso_date(date_string, date_format="%Y-%m-%d"):
    if not date_string:
        return ""
    try:
        return datetime.datetime.fromisoformat(date_string.rstrip("Z")).strftime(date_format)
    except ValueError:
        return date_string


class CloneProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        if max_count:
            percent = (cur_count / max_count) * 100
            print(f"🔄 Progress: {percent:.2f}% - {message}", end='\r')
        else:
            print(f"🔄 {message}", end='\r')


def clone_cvelistV5_repo():
    local_dir = get_cve_repo_dir()
    repo_url = 'https://github.com/CVEProject/cvelistV5.git'

    if not os.path.exists(os.path.join(local_dir, '.git')):
        try:
            print(f"📥 Cloning CVE List V5 into '{local_dir}'.")
            print(
                "⚠️ Warning: The repository is several GB in size and the download may take a while.")
            Repo.clone_from(repo_url, local_dir, progress=CloneProgress())
            print("\n✅ CVE List V5 cloned successfully.")
        except GitCommandError as e:
            print(f"❌ Error cloning cvelistV5: {e}")
            return None
    else:
        try:
            repo = Repo(local_dir)
            if repo.bare:
                print(
                    f"❌ Repository at '{local_dir}' is bare. Cannot pull updates.")
                return None
            print(f"📥 Pulling updates in '{local_dir}'...")
            repo.remotes.origin.pull()
            print("✅ Repository updated successfully.")
        except GitCommandError as e:
            print(f"❌ Error pulling updates: {e}")
            return None
    return local_dir


def grep_local_db(keywords):
    local_dir = get_cve_local_dir()
    if not os.path.exists(local_dir):
        print("Local CVE database not found.")
        return None

    if isinstance(keywords, str):
        keywords = [keywords.lower()]
    else:
        keywords = [kw.lower() for kw in keywords]

    print(
        f"┌───[ 🕵️ Searching local database for keywords: {', '.join(keywords)} ]")

    json_files = []
    for root, _, files in os.walk(local_dir):
        for filename in files:
            if filename.endswith('.json'):
                json_files.append(os.path.join(root, filename))

    def process_file(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if all(kw in content for kw in keywords):
                    return os.path.splitext(os.path.basename(file_path))[0]
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
        return None

    matching_files = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for result in tqdm(executor.map(process_file, json_files),
                           total=len(json_files),
                           desc="Processing CVE files"):
            if result is not None:
                matching_files.append(result)

    return matching_files if matching_files else None


def search_cve_by_keywords(keywords):
    cve_ids = set()

    local_cve_ids = grep_local_db(keywords)
    if local_cve_ids:
        cve_ids.update(local_cve_ids)

    try:
        cisa_response = requests.get(CISA_URL)
        cisa_response.raise_for_status()
        cisa_data = cisa_response.json()
        for item in cisa_data.get("vulnerabilities", []):
            item_str = json.dumps(item).lower()
            if all(kw in item_str for kw in [k.lower() for k in keywords]):
                cve_ids.add(item["cveID"])
    except requests.RequestException as e:
        print(f"Error fetching data from CISA: {e}")

    try:
        nuclei_response = requests.get(NUCLEI_URL)
        nuclei_response.raise_for_status()
        for line in nuclei_response.text.splitlines():
            try:
                line_lower = line.lower()
                if all(kw in line_lower for kw in [k.lower() for k in keywords]):
                    template = json.loads(line)
                    cve_ids.add(template["ID"])
            except Exception:
                pass
    except requests.RequestException as e:
        print(f"Error fetching data from Nuclei Templates: {e}")

    if cve_ids:
        header = f" Found {len(cve_ids)} CVE(s) matching: {' '.join(keywords)} "
        line = "═" * len(header)
        print(f"\n╔{line}╗")
        print(f"║{header}║")
        print(f"╚{line}╝\n")
        print(", ".join(sorted(cve_ids)))
        print()
    else:
        print(f"No CVEs found for keywords '{' '.join(keywords)}'")

    return list(cve_ids)


def extract_cvss_info(cve_data):
    base_score, base_severity, vector = "N/A", "N/A", "N/A"
    if not cve_data or "containers" not in cve_data or "cna" not in cve_data["containers"]:
        return base_score, base_severity, vector

    cna = cve_data["containers"]["cna"]
    metrics = cna.get("metrics", [])

    for metric in metrics:
        cvss_data = (
            metric.get("cvssV4_0")
            or metric.get("cvssV3_1")
            or metric.get("cvssV3_0")
            or metric.get("cvssV3")
        )
        if cvss_data and cvss_data.get("baseScore"):
            base_score = cvss_data.get("baseScore", "N/A")
            base_severity = cvss_data.get("baseSeverity", "N/A")
            vector = cvss_data.get("vectorString", "N/A")
            break

    if base_score == "N/A":
        adp_entries = cve_data["containers"].get("adp", [])
        for adp_entry in adp_entries:
            for metric in adp_entry.get("metrics", []):
                cvss_data = (
                    metric.get("cvssV4_0")
                    or metric.get("cvssV3_1")
                    or metric.get("cvssV3_0")
                    or metric.get("cvssV3")
                )
                if cvss_data and cvss_data.get("baseScore"):
                    base_score = cvss_data.get("baseScore", "N/A")
                    base_severity = cvss_data.get("baseSeverity", "N/A")
                    vector = cvss_data.get("vectorString", "N/A")
                    break
            if base_score != "N/A":
                break

    return str(base_score), str(base_severity), str(vector)


def fetch_data(url, params=None, headers=None):
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        return f"❌ Error fetching data from {url}: {e}"


def fetch_json_data(url, params=None, headers=None):
    response = fetch_data(url, params=params, headers=headers)
    if isinstance(response, str):
        return None, response
    try:
        return response.json(), None
    except json.JSONDecodeError as e:
        return None, f"❌ Error parsing JSON data from {url}: {e}"


def fetch_github_cve_data(cve_id):
    cve_year = cve_id.split("-")[1]
    cve_num = int(cve_id.split("-")[2])
    url = f"{CVE_GITHUB_URL}/{cve_year}/{cve_num // 1000}xxx/{cve_id}.json"
    return fetch_json_data(url)


def fetch_epss_score(cve_id):
    return fetch_json_data(EPSS_API_URL.format(cve_id=cve_id))


def fetch_cisa_data():
    data, error = fetch_json_data(CISA_URL)
    if data and "vulnerabilities" in data:
        for vulnerability in data["vulnerabilities"]:
            vulnerability["cisa_status"] = "Yes"
            vulnerability["ransomware_use"] = vulnerability.get(
                "knownRansomwareCampaignUse", "Unknown"
            )
    return data, error


def fetch_nuclei_data(cve_id):
    response = fetch_data(NUCLEI_URL)
    if isinstance(response, str):
        return None, response
    try:
        for line in response.iter_lines():
            if line:
                template = json.loads(line.decode("utf-8"))
                if template["ID"] == cve_id:
                    return template, None
    except json.JSONDecodeError as e:
        return None, f"❌ Error parsing JSON data from {NUCLEI_URL}: {e}"
    return None, None


def fetch_vulncheck_data(cve_id):
    vulncheck_api_key = config.get("vulncheck_api_key")
    if not vulncheck_api_key:
        return None, "No VulnCheck API key is configured."

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {vulncheck_api_key}",
    }

    response = fetch_data(VULNCHECK_API_URL, params={
                          "cve": cve_id}, headers=headers)
    if isinstance(response, str):
        return None, response

    try:
        json_data = response.json()
        return json_data, None
    except json.JSONDecodeError as e:
        return None, f"Error parsing JSON data from VulnCheck: {e}"


def fetch_exploitdb_data(cve_id):
    response = fetch_data(EXPLOITDB_URL)
    if isinstance(response, str):
        return [], response
    try:
        decoded_content = response.content.decode("utf-8")
        csv_reader = csv.reader(decoded_content.splitlines(), delimiter=",")
        header = next(csv_reader)
        codes_index = header.index("codes")
        return [
            {"id": row[0], "date": row[3]}
            for row in csv_reader
            if cve_id in row[codes_index].split(";")
        ], None
    except csv.Error as e:
        return [], f"❌ Error parsing CSV data from {EXPLOITDB_URL}: {e}"


def fetch_packetstorm_data(cve_id):
    response = fetch_data(PACKETSTORM_URL.format(cve_id=cve_id))
    if isinstance(response, str):
        return {}, response
    return (
        {"packetstorm_url": PACKETSTORM_URL.format(cve_id=cve_id)}
        if "No Results Found" not in response.text
        else {}
    ), None


def fetch_hackerone_cve_details(cve_id):
    headers = {"content-type": "application/json"}
    payload = {
        "operationName": "CveDiscoveryDetailedViewCveEntry",
        "variables": {"cve_id": cve_id},
        "query": """
        query CveDiscoveryDetailedViewCveEntry($cve_id: String!) {
            cve_entry(cve_id: $cve_id) {
                rank
                reports_submitted_count
                severity_count_unknown
                severity_count_none
                severity_count_low
                severity_count_medium
                severity_count_high
                severity_count_critical
                __typename
            }
        }
        """,
    }

    response = requests.post(HACKERONE_URL, headers=headers, json=payload)
    if response.status_code == 200:
        try:
            data = response.json()
            if "data" in data and "cve_entry" in data["data"]:
                return data, None
            else:
                return None, "❌ No HackerOne data found for this CVE."
        except json.JSONDecodeError as e:
            return None, f"❌ Error parsing JSON data from HackerOne: {e}"
    else:
        return None, f"❌ Error fetching data from HackerOne: {response.status_code}: {response.text}"


def display_data(title, data, template, error=None):
    print(f"┌───[ {BLUE}{title}{ENDC} ]")
    if error:
        print("|")
        print(f"└ {error}\n")
        return
    if data:
        print("|")
        for line in template(data):
            print(line)
        print()
    else:
        print("|")
        print(f"└ ❌ No data found.\n")


def display_cve_data(cve_data, error=None):
    def template(data):
        if not data or "containers" not in data or "cna" not in data["containers"]:
            return ["└ ❌ No vulnerability data found."]

        cve_item = data["containers"]["cna"]
        published = data["cveMetadata"].get("datePublished", "")
        if published:
            published = parse_iso_date(published)
        description = (
            next(
                (
                    desc["value"]
                    for desc in cve_item.get("descriptions", [])
                    if desc["lang"] == "en"
                ),
                "No description available",
            )
            .replace("\n\n", " ")
            .replace("  ", " ")
        )
        wrapped_description = textwrap.fill(
            description, width=100, subsequent_indent=" " * 15
        )
        base_score, base_severity, vector_string = extract_cvss_info(data)

        return [
            f"├ Published:   {published}",
            f"├ Base Score:  {base_score} ({base_severity})",
            f"├ Vector:      {vector_string}",
            f"└ Description: {wrapped_description}",
        ]

    display_data("🔍 Vulnerability information", cve_data, template, error)


def display_epss_score(epss_data, error=None):
    def template(data):
        if not data or "data" not in data or not data["data"]:
            return ["└ ❌ No data found."]

        epss_score = data["data"][0].get("epss", "N/A")
        if epss_score != "N/A":
            percent = float(epss_score) * 100
            return [f"└ EPSS Score:  {percent:.2f}% Probability of exploitation."]
        return []

    display_data("♾️ Exploit Prediction Score (EPSS)",
                 epss_data, template, error)


def display_cisa_status(cve_id, cisa_data, error=None):
    def template(data):
        if not data or "vulnerabilities" not in data or not data["vulnerabilities"]:
            return ["└ ❌ No data found."]

        for vulnerability in data["vulnerabilities"]:
            if vulnerability["cveID"] == cve_id:
                cisa_status = vulnerability["cisa_status"]
                ransomware_use = vulnerability["ransomware_use"]
                return [
                    f"├ Listed:      {cisa_status}",
                    f"└ Ransomware:  {ransomware_use}",
                ]
        return ["└ ❌ No data found."]

    display_data("🛡️ CISA KEV Catalog", cisa_data, template, error)


def display_public_exploits(
    github_data, vulncheck_data, exploitdb_data, packetstorm_data, nuclei_data, vulncheck_error=None
):
    def template():
        total_exploits = 0
        entries = []

        if github_data and github_data.get("pocs"):
            entries.append("├ GitHub")
            sorted_pocs = sorted(
                github_data["pocs"], key=lambda x: x.get("created_at", ""), reverse=True
            )
            for poc in sorted_pocs:
                created_at = poc.get("created_at", "N/A")
                if created_at != "N/A":
                    created_at = parse_iso_date(created_at)
                entries.append(
                    f"│  ├ Date: {created_at} - {poc.get('html_url', 'N/A')}")
                total_exploits += 1
            if entries:
                entries[-1] = entries[-1].replace("├", "└")

        if vulncheck_data and isinstance(vulncheck_data, dict) and vulncheck_data.get("data"):
            entries.append("│")
            entries.append("├ VulnCheck")
            sorted_vulncheck = sorted(
                (
                    xdb
                    for item in vulncheck_data["data"]
                    for xdb in item.get("vulncheck_xdb", [])
                ),
                key=lambda x: x.get("date_added", ""),
                reverse=True,
            )
            for xdb in sorted_vulncheck:
                date_added = xdb.get("date_added", "N/A")
                if date_added != "N/A":
                    date_added = parse_iso_date(date_added)
                github_url = (
                    xdb.get("clone_ssh_url", "")
                    .replace("git@github.com:", "https://github.com/")
                    .replace(".git", "")
                )
                entries.append(f"│  ├ Date: {date_added} - {github_url}")
                total_exploits += 1
            if entries:
                entries[-1] = entries[-1].replace("├", "└")

        if vulncheck_error:
            entries.append("│")
            entries.append(f"└ ❌ VulnCheck Error: {vulncheck_error}")

        if exploitdb_data:
            entries.append("│")
            entries.append("├ Exploit-DB")
            sorted_exploitdb = sorted(
                exploitdb_data, key=lambda x: x["date"], reverse=True)
            for item in sorted_exploitdb:
                url = f"https://www.exploit-db.com/exploits/{item['id']}"
                entries.append(f"│  ├ Date: {item['date']} - {url}")
                total_exploits += 1
            if entries:
                entries[-1] = entries[-1].replace("├", "└")

        other_entries = []
        if packetstorm_data and packetstorm_data.get("packetstorm_url"):
            other_entries.append(
                f"PacketStorm: {packetstorm_data['packetstorm_url']}")
        if nuclei_data and nuclei_data.get("file_path"):
            base_url = "https://raw.githubusercontent.com/projectdiscovery/nuclei-templates/main/"
            file_path = nuclei_data["file_path"]
            full_url = f"{base_url}{file_path}"
            other_entries.append(f"Nuclei: {full_url}")

        if other_entries:
            entries.append("│")
            entries.append("└ Other")
            for index, entry in enumerate(other_entries[:-1]):
                entries.append(f"   ├ {entry}")
            entries.append(f"   └ {other_entries[-1]}")

        if not entries:
            return ["└ ❌ No data found."], total_exploits

        return entries, total_exploits

    exploits, total = template()
    print(f"┌───[ {BLUE}💣 Public Exploits (Total: {total}){ENDC} ]")
    if exploits:
        print("|")
        for line in exploits:
            print(line)
        print()
    else:
        print("|")
        print(f"└ ❌ No data found.\n")


def display_hackerone_data(hackerone_data, error=None):
    def template(data):
        if not data or "data" not in data or "cve_entry" not in data["data"]:
            return ["└ ❌ No data found."]

        cve_entry = data["data"]["cve_entry"]
        if not cve_entry:
            return ["└ ❌ No data found."]

        rank = cve_entry.get("rank", "N/A")
        reports_submitted_count = cve_entry.get(
            "reports_submitted_count", "N/A")
        severity_unknown = cve_entry.get("severity_count_unknown", 0)
        severity_none = cve_entry.get("severity_count_none", 0)
        severity_low = cve_entry.get("severity_count_low", 0)
        severity_medium = cve_entry.get("severity_count_medium", 0)
        severity_high = cve_entry.get("severity_count_high", 0)
        severity_critical = cve_entry.get("severity_count_critical", 0)

        severity_display = (
            f"Unknown: {severity_unknown} / None: {severity_none} / "
            f"Low: {severity_low} / Medium: {severity_medium} / "
            f"High: {severity_high} / Critical: {severity_critical}"
        )
        return [
            f"├ Rank:        {rank}",
            f"├ Reports:     {reports_submitted_count}",
            f"└ Severity:    {severity_display}",
        ]

    display_data("🕵️ HackerOne Hacktivity", hackerone_data, template, error)


def display_cve_references(cve_data, error=None):
    def template(data):
        if not data or "containers" not in data or "cna" not in data["containers"]:
            return ["└ ❌ No data found."]

        references = data["containers"]["cna"].get("references", [])
        if references:
            lines = [f"├ {ref['url']}" for ref in references[:-1]]
            lines.append(f"└ {references[-1]['url']}")
            return lines
        return ["└ ❌ No further references found."]

    display_data("📚 Further References", cve_data, template, error)


def calculate_priority(
    cve_id, cve_data, epss_data, github_data, cisa_data, vulncheck_data, exploitdb_data
):
    cvss_score, epss_score = 0, 0
    try:
        base_score, _, _ = extract_cvss_info(cve_data)
        cvss_score = float(base_score)
    except (ValueError, TypeError):
        pass

    try:
        epss_score = float(epss_data["data"][0]["epss"]
                           ) if epss_data and "data" in epss_data else 0
    except (KeyError, IndexError, TypeError, ValueError):
        pass

    in_cisa_kev = (
        any(vuln["cveID"] == cve_id for vuln in cisa_data.get(
            "vulnerabilities", []))
        if cisa_data
        else False
    )

    has_public_exploits = False
    if github_data:
        has_public_exploits = bool(github_data.get("pocs"))
    if not has_public_exploits and vulncheck_data:
        has_public_exploits = bool(vulncheck_data.get("data"))
    if not has_public_exploits and exploitdb_data:
        has_public_exploits = bool(exploitdb_data)

    if not (cvss_score or epss_score or in_cisa_kev or has_public_exploits):
        return None

    if in_cisa_kev or has_public_exploits:
        return "A+"
    if cvss_score >= CVSS_THRESHOLD and epss_score >= EPSS_THRESHOLD:
        return "A"
    if cvss_score >= CVSS_THRESHOLD:
        return "B"
    if epss_score >= EPSS_THRESHOLD:
        return "C"
    return "D"


def display_priority_rating(cve_id, priority):
    def template(data):
        if not data or "priority" not in data or not data["priority"]:
            return ["└ ❌ No data found."]

        priority_color = PRIORITY_COLORS.get(data["priority"], ENDC)
        return [f"└ Priority:     {priority_color}{data['priority']}{ENDC}"]

    if priority is None:
        display_data("⚠️ Patching Priority Rating", None, template)
    else:
        display_data("⚠️ Patching Priority Rating", {
                     "priority": priority}, template)


def load_config(config_path=None, debug=False):
    """
    Attempts to load a JSON config file in this order:
      1. The file path provided by `config_path`.
      2. The file path from the SPLOITSCAN_CONFIG_PATH environment variable.
      3. A list of standard config-file locations.
    Returns a dictionary of config data. If no file is found or parsing fails,
    returns the default config.
    """

    default_config = {
        "vulncheck_api_key": None,
        "openai_api_key": None
    }

    def debug_print(msg):
        if debug:
            print(msg)

    candidate_paths = []

    if config_path:
        candidate_paths.append(config_path)

    env_path = os.getenv("SPLOITSCAN_CONFIG_PATH")
    if env_path:
        candidate_paths.append(env_path)

    candidate_paths.extend([
        os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "config.json"),
        os.path.expanduser("~/.sploitscan/config.json"),
        os.path.expanduser("~/.config/sploitscan/config.json"),
        os.path.expanduser(
            "~/Library/Application Support/sploitscan/config.json"),
        os.path.join(os.getenv("APPDATA", ""), "sploitscan", "config.json"),
        "/etc/sploitscan/config.json"
    ])

    candidate_paths = [p for p in candidate_paths if p]

    for path in candidate_paths:
        if os.path.isfile(path):
            debug_print(f"Trying config file: {path}")
            try:
                with open(path, "r", encoding="utf-8") as file:
                    cfg = json.load(file)
                debug_print(f"Successfully loaded config file: {path}")
                return cfg
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing error in {path}: {e}")
            except Exception as e:
                print(f"⚠️ Unexpected error reading {path}: {e}")

    print("⚠️ Config file not found in any checked locations, using default settings.")
    return default_config


def get_openai_risk_assessment(prompt):
    openai_api_key = config.get("openai_api_key")
    if not openai_api_key:
        return "❌ OpenAI API key is not configured correctly."
    client = OpenAI(api_key=openai_api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a security analyst."},
                {"role": "user", "content": prompt}
            ],
            timeout=30
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error fetching data from OpenAI: {e}"


def get_google_risk_assessment(prompt):
    google_api_key = config.get("google_ai_api_key")
    if not google_api_key:
        return "❌ Google AI API key is not configured correctly."
    client = genai.Client(api_key=google_api_key)
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt]
            )
            if hasattr(response, "text"):
                return response.text.strip()
            else:
                return "Google AI: AI analysis failed."
        except Exception as e:
            if attempt < 2:
                print(
                    f"⚠️ Google AI Timeout (Attempt {attempt+1}/3), retrying...")
                time.sleep(5)
            else:
                return f"❌ Error fetching data from Google AI: {e}"


def get_grok_risk_assessment(prompt):
    grok_api_key = config.get("grok_api_key")
    if not grok_api_key:
        return "❌ Grok AI API key is not configured correctly."
    try:
        client = OpenAI(
            api_key=grok_api_key,
            base_url="https://api.x.ai/v1",
        )
        response = client.chat.completions.create(
            model="grok-2-latest",
            messages=[
                {"role": "system", "content": "You are a security analyst."},
                {"role": "user", "content": prompt}
            ],
            timeout=30
        )
        if response.choices and len(response.choices) > 0:
            message = response.choices[0].message
            if hasattr(message, "content"):
                return message.content.strip()
            else:
                return str(message)
        else:
            return "Grok AI: No response received."
    except Exception as e:
        return f"❌ Error fetching data from Grok AI: {e}"


def get_deepseek_risk_assessment(prompt):
    deepseek_api_key = config.get("deepseek_api_key")
    if not deepseek_api_key:
        return "❌ DeepSeek API key is not configured correctly."
    try:
        client = OpenAI(api_key=deepseek_api_key,
                        base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a security analyst."},
                {"role": "user", "content": prompt}
            ],
            timeout=30,
            stream=False
        )
        if response.choices and len(response.choices) > 0:
            message = response.choices[0].message
            if hasattr(message, "content"):
                return message.content.strip()
            else:
                return str(message)
        else:
            return "DeepSeek: No response received."
    except Exception as e:
        return f"❌ Error fetching data from DeepSeek: {e}"


def generate_ai_prompt(cve_details, cve_data):
    prompt = f"""
You are a security analyst. Provide exactly four sections of output, labeled with numeric headers:
1. Risk Assessment
Provide a detailed risk assessment including the nature of the vulnerability & its business impact.
Describe the likelihood and ease of exploitation, and potential impacts on confidentiality, integrity, and availability.

2. Potential Attack Scenarios
Describe at least one potential attack scenario that leverages this vulnerability. Include a detailed description of the attack vector, process, and potential outcomes.

3. Mitigation Recommendations
Provide specific, actionable mitigation recommendations. Include immediate actions such as patching, and provide links to relevant resources where applicable.

4. Executive Summary
Summarize the vulnerability, potential impacts, and importance of taking action in language understandable by non-technical stakeholders.

IMPORTANT:
- Output only plain text with no bullet points, dashes, or Markdown formatting.
- Each heading must be on its own line.
- If text spans multiple paragraphs, separate them by a blank line.
- No other decorative characters or lists.

CVE DETAILS:
{cve_details}

FULL CVE DATA:
{json.dumps(cve_data, indent=4)}
"""
    return prompt


def get_risk_assessment(ai_provider, cve_details, cve_data):
    prompt = generate_ai_prompt(cve_details, cve_data)
    if ai_provider == "openai":
        return get_openai_risk_assessment(prompt)
    elif ai_provider == "google":
        return get_google_risk_assessment(prompt)
    elif ai_provider == "grok":
        return get_grok_risk_assessment(prompt)
    elif ai_provider == "deepseek":
        return get_deepseek_risk_assessment(prompt)
    else:
        return "❌ Unknown AI provider selected."


def display_ai_risk_assessment(cve_details, cve_data, ai_provider):
    def spinner_animation(message):
        spinner = itertools.cycle(["|", "/", "-", "\\"])
        while not stop_spinner:
            sys.stdout.write(f"\r{message} {next(spinner)}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")
        sys.stdout.flush()

    def get_risk_assessment_thread():
        nonlocal assessment
        try:
            assessment = get_risk_assessment(
                ai_provider, cve_details, cve_data)
        except Exception as e:
            assessment = f"❌ Error fetching AI response: {e}"
        global stop_spinner
        stop_spinner = True

    global stop_spinner
    stop_spinner = False
    assessment = None

    print("┌───[ 🤖 AI-Powered Risk Assessment ]")
    print("|")
    spinner_thread = threading.Thread(
        target=spinner_animation,
        args=(f"| Loading {ai_provider} risk assessment...",)
    )
    spinner_thread.start()
    assessment_thread = threading.Thread(target=get_risk_assessment_thread)
    assessment_thread.start()
    assessment_thread.join()
    spinner_thread.join()

    print("|")
    if assessment:
        sections = assessment.split("\n\n")
        for section in sections:
            section = section.strip()
            if section:
                if section.startswith(("1. ", "2. ", "3. ", "4. ")):
                    header = section.split("\n")[0].strip()
                    print(f"| {header}")
                    print("| " + "-" * (len(header) + 1))
                    content = "\n".join(section.split("\n")[1:]).strip()
                    wrapped_content = textwrap.fill(
                        content, width=100, initial_indent="| ", subsequent_indent="| "
                    )
                    print(wrapped_content)
                else:
                    wrapped_content = textwrap.fill(
                        section, width=100, initial_indent="| ", subsequent_indent="| "
                    )
                    print(wrapped_content)
                print("|")
    else:
        print("| ❌ No AI Risk Assessment could be retrieved.")
        print("|")

    print("└────────────────────────────────────────\n")


def import_vulnerability_data(file_path, file_type=None):
    if not os.path.exists(file_path):
        print(f"❌ Error: The file '{file_path}' does not exist.")
        return []

    if not file_type:
        if is_plaintext_cve_list(file_path):
            return import_file(file_path, parse_plaintext_cve_list)
        else:
            print(
                f"❌ Error: The file '{
                    file_path}' does not appear to be a valid list of CVEs. "
                "Please specify the correct file type using the --type option."
            )
            return []

    if file_type == "nessus":
        return import_file(file_path, parse_nessus_file)
    if file_type == "nexpose":
        return import_file(file_path, parse_nexpose_file)
    if file_type == "openvas":
        return import_file(file_path, parse_openvas_file)
    if file_type == "docker":
        return import_file(file_path, parse_docker_file)

    print(f"❌ Unsupported file type: {file_type}")
    return []


def is_plaintext_cve_list(file_path):
    try:
        with open(file_path, "r") as file:
            for _ in range(10):
                line = file.readline().strip()
                if line and not is_valid_cve_id(line.upper()):
                    return False
        return True
    except Exception as e:
        print(f"❌ Error reading file '{file_path}': {e}")
        return False


def parse_plaintext_cve_list(file):
    return [line.strip().upper() for line in file if is_valid_cve_id(line.strip().upper())]


def parse_nessus_file(file):
    tree = ET.parse(file)
    root = tree.getroot()
    return [
        cve.text.strip().upper()
        for report_item in root.findall(".//ReportItem")
        for cve in report_item.findall("cve")
        if is_valid_cve_id(cve.text.strip().upper())
    ]


def parse_nexpose_file(file):
    tree = ET.parse(file)
    root = tree.getroot()
    return [
        link.get("LinkTitle").upper()
        for link in root.findall(".//URLLink")
        if link.get("LinkTitle", "").startswith("CVE-")
    ]


def parse_openvas_file(file):
    tree = ET.parse(file)
    root = tree.getroot()
    return [
        ref.attrib.get("id").upper()
        for ref in root.findall(".//ref[@type='cve']")
        if is_valid_cve_id(ref.attrib.get("id").upper())
    ]


def parse_docker_file(file):
    data = json.load(file)
    return [
        rule.get("id", "").upper()
        for run in data.get("runs", [])
        for rule in run.get("tool", {}).get("driver", {}).get("rules", [])
        if rule.get("id", "").startswith("CVE-")
    ]


def import_file(file_path, parse_function):
    try:
        with open(file_path, "r") as file:
            cve_ids = parse_function(file)
        unique_cve_ids = list(set(cve_ids))
        print(
            YELLOW +
            f"📥 Successfully imported {len(unique_cve_ids)} CVE(s) from '{
                file_path}'.\n"
        )
        return unique_cve_ids
    except ET.ParseError as e:
        print(f"❌ Error parsing the file '{file_path}': {e}")
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing the JSON file '{file_path}': {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred while processing '{
              file_path}': {e}")
    return []


def is_valid_cve_id(cve_id):
    return re.match(r"CVE-\d{4}-\d{4,7}$", cve_id) is not None


def generate_filename(cve_ids, extension):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    cve_part = "_".join(cve_ids[:3]) + \
        ("_and_more" if len(cve_ids) > 3 else "")
    return f"{timestamp}_{cve_part}_export.{extension}"


def datetimeformat(value, format="%Y-%m-%d"):
    return parse_iso_date(value, format)


def export_to_html(all_results, cve_ids):
    def template(data):
        base_path = os.path.dirname(os.path.abspath(__file__))
        template_paths = [
            os.path.join(base_path, "templates"),
            os.path.expanduser("~/.sploitscan/templates"),
            os.path.expanduser("~/.config/sploitscan/templates"),
            "/etc/sploitscan/templates",
        ]

        for path in template_paths:
            if os.path.exists(os.path.join(path, "report_template.html")):
                env = Environment(loader=FileSystemLoader(path))
                break
        else:
            print(
                "❌ HTML template 'report_template.html' not found in any checked locations.")
            return ["❌ Error exporting to HTML: template not found"]

        env.filters["datetimeformat"] = datetimeformat
        tmpl = env.get_template("report_template.html")
        filename = generate_filename(cve_ids, "html")
        output = tmpl.render(cve_data=handle_cvss(data))

        with open(filename, "w", encoding="utf-8") as file:
            file.write(output)

        return [f"└ Data exported to file: {filename}"]

    def handle_cvss(data):
        for result in data:
            result["Public Exploits Total"] = sum(
                [
                    len(result.get("GitHub Data", {}).get("pocs", []))
                    if result.get("GitHub Data")
                    else 0,
                    sum(
                        len(item.get("vulncheck_xdb", []))
                        for item in result.get("VulnCheck Data", {}).get("data", [])
                    )
                    if result.get("VulnCheck Data")
                    else 0,
                    len(result.get("ExploitDB Data", [])) if result.get(
                        "ExploitDB Data") else 0,
                ]
            )

            if result.get("GitHub Data") and result["GitHub Data"].get("pocs"):
                result["GitHub Data"]["pocs"] = sorted(
                    result["GitHub Data"]["pocs"], key=lambda x: x.get("created_at", ""), reverse=True
                )

            if result.get("VulnCheck Data") and result["VulnCheck Data"].get("data"):
                for item in result["VulnCheck Data"]["data"]:
                    if item.get("vulncheck_xdb"):
                        item["vulncheck_xdb"] = sorted(
                            item["vulncheck_xdb"], key=lambda x: x.get("date_added", ""), reverse=True
                        )

            if result.get("ExploitDB Data"):
                result["ExploitDB Data"] = sorted(
                    result["ExploitDB Data"], key=lambda x: x.get("date", ""), reverse=True
                )

            if result.get("EPSS Data") and result["EPSS Data"].get("data") and len(result["EPSS Data"]["data"]) > 0:
                try:
                    epss_value = float(
                        result["EPSS Data"]["data"][0].get("epss", 0))
                except ValueError:
                    epss_value = 0.0
                result["EPSS Data"]["data"][0]["epss"] = epss_value

            # Fix CVSS data to ensure they are float/strings in the HTML
            if "CVE Data" in result and result["CVE Data"] and "containers" in result["CVE Data"]:
                base_score, base_severity, vector_string = extract_cvss_info(
                    result["CVE Data"])
                # Convert base_score to float if possible
                try:
                    base_score_float = float(base_score)
                except (ValueError, TypeError):
                    base_score_float = 0.0

                result["CVE Data"]["cvss_info"] = {
                    "baseScore": base_score_float,
                    "baseSeverity": base_severity,
                    "vectorString": vector_string,
                }
        return data

    display_data("📁 HTML Export", all_results, template)


def export_to_json(all_results, cve_ids):
    def template(data):
        filename = generate_filename(cve_ids, "json")
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        return [f"└ Data exported to file: {filename}"]

    display_data("📁 JSON Export", all_results, template)


def export_to_csv(all_results, cve_ids):
    def template(data):
        filename = generate_filename(cve_ids, "csv")
        keys = list(data[0].keys()) + ["Risk Assessment"]
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            for item in data:
                item["Risk Assessment"] = item.get("Risk Assessment", "N/A")
                writer.writerow(item)
        return [f"└ Data exported to CSV: {filename}"]

    display_data("📁 CSV Export", all_results, template)


def display_banner():
    banner = f"""
███████╗██████╗ ██╗      ██████╗ ██╗████████╗███████╗ ██████╗ █████╗ ███╗   ██╗
██╔════╝██╔══██╗██║     ██╔═══██╗██║╚══██╔══╝██╔════╝██╔════╝██╔══██╗████╗  ██║
███████╗██████╔╝██║     ██║   ██║██║   ██║   ███████╗██║     ███████║██╔██╗ ██║
╚════██║██╔═══╝ ██║     ██║   ██║██║   ██║   ╚════██║██║     ██╔══██║██║╚██╗██║
███████║██║     ███████╗╚██████╔╝██║   ██║   ███████║╚██████╗██║  ██║██║ ╚████║
╚══════╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝
v{VERSION} / Alexander Hagenah / @xaitax / ah@primepage.de
"""
    print(BLUE + banner + ENDC)


def print_cve_header(cve_id):
    header = f" CVE ID: {cve_id} "
    line = "═" * len(header)
    print(f"{GREEN}╔{line}╗{ENDC}")
    print(f"{GREEN}║{header}║{ENDC}")
    print(f"{GREEN}╚{line}╝{ENDC}\n")


def fetch_and_display_cve_data(cve_id):
    cve_data, cve_error = fetch_github_cve_data(cve_id)
    display_cve_data(cve_data, cve_error)
    return cve_data


def fetch_and_display_epss_score(cve_id):
    epss_data, epss_error = fetch_epss_score(cve_id)
    display_epss_score(epss_data, epss_error)
    return epss_data


def fetch_and_display_cisa_status(cve_id):
    cisa_data, cisa_error = fetch_cisa_data()
    display_cisa_status(cve_id, cisa_data, cisa_error)
    relevant_cisa_data = next(
        (item for item in cisa_data.get(
            "vulnerabilities", []) if item["cveID"] == cve_id),
        None,
    )
    return relevant_cisa_data if relevant_cisa_data else {"cisa_status": "N/A", "ransomware_use": "N/A"}


def fetch_and_display_public_exploits(cve_id):
    github_data, github_error = fetch_json_data(
        GITHUB_API_URL, params={"cve_id": cve_id})
    vulncheck_data, vulncheck_error = fetch_vulncheck_data(cve_id)
    exploitdb_data, exploitdb_error = fetch_exploitdb_data(cve_id)
    packetstorm_data, packetstorm_error = fetch_packetstorm_data(cve_id)
    nuclei_data, nuclei_error = fetch_nuclei_data(cve_id)

    display_public_exploits(
        github_data,
        vulncheck_data,
        exploitdb_data,
        packetstorm_data,
        nuclei_data,
        vulncheck_error,
    )
    return {
        "github_data": github_data,
        "vulncheck_data": vulncheck_data if isinstance(vulncheck_data, dict) else {},
        "exploitdb_data": exploitdb_data,
        "packetstorm_data": packetstorm_data,
        "nuclei_data": nuclei_data,
    }


def fetch_and_display_hackerone_data(cve_id):
    hackerone_data, hackerone_error = fetch_hackerone_cve_details(cve_id)
    display_hackerone_data(hackerone_data, hackerone_error)
    return hackerone_data


def compile_cve_details(cve_id, cve_data, epss_data, relevant_cisa_data, public_exploits):
    published = cve_data["cveMetadata"].get(
        "datePublished", "N/A") if cve_data else "N/A"
    published_formatted = parse_iso_date(
        published) if published != "N/A" else "N/A"
    description = (
        next(
            (
                desc["value"]
                for desc in cve_data["containers"]["cna"].get("descriptions", [])
                if desc["lang"] == "en"
            ),
            "No description available",
        )
        .replace("\n\n", " ")
        .replace("  ", " ")
        if cve_data
        else "No description available"
    )

    base_score, base_severity, vector_string = extract_cvss_info(cve_data)

    epss_score = (
        epss_data["data"][0].get("epss", "N/A")
        if epss_data and "data" in epss_data and epss_data["data"]
        else "N/A"
    )

    cisa_status = relevant_cisa_data["cisa_status"] if relevant_cisa_data else "N/A"
    ransomware_use = relevant_cisa_data["ransomware_use"] if relevant_cisa_data else "N/A"

    github_exploits = (
        "\n".join(
            [
                f"{poc['created_at']}: {poc['html_url']}"
                for poc in public_exploits["github_data"].get("pocs", [])
            ]
        )
        if public_exploits["github_data"]
        else "N/A"
    )

    vulncheck_exploits = (
        "\n".join(
            [
                f"{xdb['date_added']}: "
                f"{xdb['clone_ssh_url'].replace(
                    'git@github.com:', 'https://github.com/').replace('.git', '')}"
                for item in public_exploits["vulncheck_data"].get("data", [])
                for xdb in item.get("vulncheck_xdb", [])
            ]
        )
        if public_exploits["vulncheck_data"]
        else "N/A"
    )

    packetstorm_url = public_exploits["packetstorm_data"].get(
        "packetstorm_url", "N/A")

    nuclei_url = (
        f"https://raw.githubusercontent.com/projectdiscovery/nuclei-templates/main/{
            public_exploits['nuclei_data']['file_path']}"
        if public_exploits["nuclei_data"] and "file_path" in public_exploits["nuclei_data"]
        else "N/A"
    )

    references_list = (
        cve_data["containers"]["cna"].get("references", [])
        if cve_data and "containers" in cve_data and "cna" in cve_data["containers"]
        else []
    )
    references = "\n".join(
        [ref["url"] for ref in references_list]) if references_list else "N/A"

    return f"""
    Published: {published_formatted}
    Base Score: {base_score} ({base_severity})
    Vector: {vector_string}
    Description: {description}
    EPSS Score: {epss_score}
    CISA Status: {cisa_status}
    Ransomware Use: {ransomware_use}
    GitHub Exploits: {github_exploits}
    VulnCheck Exploits: {vulncheck_exploits}
    PacketStorm URL: {packetstorm_url}
    Nuclei Template: {nuclei_url}
    Further References: {references}
    """


def main(cve_ids, export_format=None, import_file=None, import_type=None, ai_provider=None,
         config_path=None, methods=None, debug=False, fast_mode=False):
    global config
    config = load_config(config_path=config_path,
                         debug=debug) if config_path else load_config(debug=debug)

    all_results = []
    if export_format:
        export_format = export_format.lower()

    if import_file:
        cve_ids = import_vulnerability_data(import_file, import_type)
        if not cve_ids:
            print("❌ No valid CVE IDs found in the provided file.")
            return

    if not cve_ids:
        print("❌ No CVE IDs provided. Please provide CVE IDs or an import file.")
        return

    default_methods = ["cisa", "epss", "hackerone", "ai", "prio", "references"]
    selected_methods = methods.split(",") if methods else default_methods

    for cve_id in cve_ids:
        cve_id = cve_id.upper()
        if not is_valid_cve_id(cve_id):
            print(
                f"❌ Invalid CVE ID format: {cve_id}. Please use the format CVE-YYYY-NNNNN.")
            continue

        print_cve_header(cve_id)

        if fast_mode:
            parts = cve_id.split('-')
            year = parts[1]
            hundreds = parts[2][:-3] + "xxx"
            cve_path = os.path.join(
                get_cve_local_dir(), year, hundreds, f"{cve_id}.json")
            if os.path.exists(cve_path):
                try:
                    with open(cve_path, "r", encoding="utf-8") as file:
                        cve_data = json.load(file)
                    display_cve_data(cve_data)
                except Exception as e:
                    print(f"Error reading local CVE file {cve_path}: {e}")
                    continue
            else:
                cve_data = fetch_and_display_cve_data(cve_id)
        else:
            cve_data = fetch_and_display_cve_data(cve_id)
            if not cve_data:
                continue

            public_exploits = fetch_and_display_public_exploits(cve_id)
            epss_data = fetch_and_display_epss_score(
                cve_id) if "epss" in selected_methods else None
            relevant_cisa_data = fetch_and_display_cisa_status(
                cve_id) if "cisa" in selected_methods else None
            hackerone_data = fetch_and_display_hackerone_data(
                cve_id) if "hackerone" in selected_methods else None

            risk_assessment = None
            if "ai" in selected_methods:
                cve_details = compile_cve_details(
                    cve_id, cve_data, epss_data, relevant_cisa_data, public_exploits)
                risk_assessment = get_risk_assessment(
                    ai_provider, cve_details, cve_data)
                display_ai_risk_assessment(cve_details, cve_data, ai_provider)

            priority = None
            if "prio" in selected_methods:
                priority = calculate_priority(
                    cve_id,
                    cve_data,
                    epss_data,
                    public_exploits.get("github_data"),
                    relevant_cisa_data,
                    public_exploits.get("vulncheck_data"),
                    public_exploits.get("exploitdb_data"),
                )
                display_priority_rating(cve_id, priority)

            if "references" in selected_methods:
                display_cve_references(cve_data)

        cve_result = {
            "CVE Data": cve_data,
            "EPSS Data": None if fast_mode else epss_data,
            "CISA Data": {"cisa_status": "N/A", "ransomware_use": "N/A"} if fast_mode
            else (relevant_cisa_data or {"cisa_status": "N/A", "ransomware_use": "N/A"}),
            "Nuclei Data": None if fast_mode else public_exploits.get("nuclei_data"),
            "GitHub Data": None if fast_mode else public_exploits.get("github_data"),
            "VulnCheck Data": None if fast_mode else public_exploits.get("vulncheck_data"),
            "ExploitDB Data": None if fast_mode else public_exploits.get("exploitdb_data"),
            "PacketStorm Data": None if fast_mode else public_exploits.get("packetstorm_data"),
            "HackerOne Data": None if fast_mode else hackerone_data,
            "Priority": {"Priority": 0} if fast_mode else {"Priority": priority},
            "Risk Assessment": None if fast_mode else risk_assessment,
        }
        all_results.append(cve_result)

    if export_format == "json":
        export_to_json(all_results, cve_ids)
    elif export_format == "csv":
        export_to_csv(all_results, cve_ids)
    elif export_format == "html":
        export_to_html(all_results, cve_ids)


def cli():
    display_banner()
    parser = argparse.ArgumentParser(
        description="SploitScan: Retrieve and display vulnerability and exploit data for specified CVE ID(s)."
    )
    parser.add_argument("cve_ids", type=str, nargs="*", default=[],
                        help="Enter one or more CVE IDs (e.g., CVE-YYYY-NNNNN). This is optional if an import file is provided via -i.")
    parser.add_argument("-e", "--export", choices=["json", "csv", "html"],
                        help="Export the results in the specified format ('json', 'csv', or 'html').")
    parser.add_argument("-t", "--type", choices=["nessus", "nexpose", "openvas", "docker"],
                        help="Specify the type of the import file ('nessus', 'nexpose', 'openvas', or 'docker').")
    parser.add_argument("--ai", type=str, choices=["openai", "google", "grok", "deepseek"],
                        help="Select the AI provider for risk assessment (e.g., 'openai', 'google', 'grok', or 'deepseek').")
    parser.add_argument("-k", "--keywords", type=str, nargs='+',
                        help="Search for CVEs related to specific keywords (e.g., product name).")
    parser.add_argument("-local", "--local-database", dest='local_database', action='store_true',
                        help="Download the cvelistV5 repository into the local directory. Use the local database over online research if available.")
    parser.add_argument("-f", "--fast-mode", dest='fast_mode', action='store_true',
                        help="Enable fast mode: only display basic CVE information without fetching additional exploits or data.")
    parser.add_argument("-m", "--methods", type=str,
                        help="Specify which methods to run, separated by commas (e.g., 'cisa,epss,hackerone,ai,prio,references').")
    parser.add_argument("-i", "--import-file", type=str,
                        help="Path to an import file. When provided, positional CVE IDs can be omitted. The file should be a plain text list with one CVE per line.")
    parser.add_argument("-c", "--config", type=str,
                        help="Path to a custom configuration file.")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug output.")

    args = parser.parse_args()

    if args.local_database:
        clone_cvelistV5_repo()

    if args.keywords:
        cve_ids = search_cve_by_keywords(args.keywords)
        if not cve_ids:
            sys.exit("No valid CVE IDs found for the provided keywords.")
    else:
        cve_ids = args.cve_ids

    main(cve_ids,
         export_format=args.export,
         import_file=args.import_file,
         import_type=args.type,
         ai_provider=args.ai,
         config_path=args.config,
         methods=args.methods,
         debug=args.debug,
         fast_mode=args.fast_mode)


if __name__ == "__main__":
    cli()