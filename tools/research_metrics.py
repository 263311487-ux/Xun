#!/usr/bin/env python3
"""Read-only aggregate snapshots; unavailable metrics never become zero."""
import argparse
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat()


def fetch_json(url, token=None, opener=None):
    headers = {"Accept": "application/json", "User-Agent": "RRC-ACT-research-metrics/1.0"}
    if token and urllib.parse.urlparse(url).hostname == "api.github.com":
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers)
    result = {"source": url, "retrieved_at": now()}
    try:
        with (opener or urllib.request.urlopen)(request, timeout=25) as response:
            result.update(status="ok", http_status=response.status,
                          server_date=response.headers.get("Date"), data=json.load(response))
    except urllib.error.HTTPError as error:
        result.update(status="unavailable" if error.code in (401, 403, 404, 429) else "error",
                      http_status=error.code)
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        # Do not serialize exception messages, headers or authentication details.
        result.update(status="error", error="network_or_invalid_json")
    return result


def traffic_summary(result, series):
    summary = {"status": result["status"]}
    if result["status"] != "ok":
        return summary
    data = result["data"]
    dates = sorted(row["timestamp"][:10] for row in data.get(series, []) if row.get("timestamp"))
    summary.update(count=data.get("count"), uniques=data.get("uniques"),
                   first_day=dates[0] if dates else None, last_day=dates[-1] if dates else None)
    return summary


def zenodo_summary(result):
    summary = {"status": result["status"]}
    if result["status"] != "ok":
        return summary
    data = result["data"]
    stats = data.get("stats", {})
    fields = ("views", "unique_views", "downloads", "unique_downloads")
    summary.update(record_id=data.get("id"), version=data.get("metadata", {}).get("version"),
                   all_versions={key: stats.get(key) for key in fields},
                   this_version={key: stats.get("version_" + key) for key in fields})
    return summary


def github_snapshot(repo, token, opener):
    base = "https://api.github.com/repos/" + repo
    sources = {name: fetch_json(base + path, token, opener) for name, path in (
        ("repository", ""), ("views", "/traffic/views"), ("clones", "/traffic/clones"),
        ("referrers", "/traffic/popular/referrers"), ("paths", "/traffic/popular/paths"))}
    return {"repository": repo, "views": traffic_summary(sources["views"], "views"),
            "clones": traffic_summary(sources["clones"], "clones"), "sources": sources}


def public_repositories(owner, token, opener):
    names, sources = [], []
    page = 1
    while True:
        result = fetch_json("https://api.github.com/users/" + owner
                            + "/repos?type=owner&per_page=100&page=" + str(page), token, opener)
        sources.append(result)
        if result["status"] != "ok":
            break
        names.extend(row["full_name"] for row in result["data"] if not row.get("private"))
        if len(result["data"]) < 100:
            break
        page += 1
    return names, sources


def github_complete(snapshot):
    return bool(snapshot["sources"]) and all(
        result["status"] == "ok" for result in snapshot["sources"].values()
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", action="append", help="owner/name; repeatable")
    parser.add_argument("--owner", help="also collect all PUBLIC repositories of this owner")
    parser.add_argument("--zenodo-record", default="23146271", help="one version record; never sum versions")
    parser.add_argument("--output", required=True, type=Path, help="new local JSON file (never overwritten)")
    parser.add_argument("--direct", action="store_true", help="bypass environment proxies if unavailable")
    args = parser.parse_args()
    repos = args.repo or ([] if args.owner else ["263311487-ux/Xun"])
    if any(not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) for repo in repos):
        parser.error("invalid repository name")
    if args.owner and not re.fullmatch(r"[A-Za-z0-9-]+", args.owner):
        parser.error("invalid owner")
    if not args.zenodo_record.isdigit():
        parser.error("Zenodo record must be numeric")
    if args.output.exists():
        parser.error("output exists; use a new filename")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({})).open if args.direct else None
    token = os.environ.get("GITHUB_TOKEN")
    listing = []
    if args.owner:
        names, listing = public_repositories(args.owner, token, opener)
        repos += names
    repos = sorted(set(repos))
    with ThreadPoolExecutor(max_workers=4) as pool:
        github = list(pool.map(lambda repo: github_snapshot(repo, token, opener), repos))
    zenodo = fetch_json("https://zenodo.org/api/records/" + args.zenodo_record, opener=opener)
    snapshot = {"schema_version": 1, "captured_at": now(), "github": github,
                "public_repository_listing": listing, "zenodo": zenodo,
                "zenodo_summary": zenodo_summary(zenodo),
                "limits": ["GitHub traffic is a rolling window, not lifetime or Pages readership.",
                           "Returned dates may lag capture time. Clones can include automation.",
                           "No authentication or unavailable source means unknown, not zero.",
                           "Zenodo all-version totals must not be summed across versions.",
                           "Referrers are partial; none reported does not prove no external readers."]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(snapshot, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    coverage = sum(row["views"]["status"] == "ok" for row in github)
    print("Snapshot:", args.output)
    print("GitHub views available:", str(coverage) + "/" + str(len(github)))
    print("GitHub repositories with complete endpoint coverage:",
          str(sum(github_complete(row) for row in github)) + "/" + str(len(github)))
    print("Zenodo:", zenodo["status"])
    return 0 if all(github_complete(row) for row in github) and zenodo["status"] == "ok" and (
        not args.owner or listing and all(row["status"] == "ok" for row in listing)) else 2


if __name__ == "__main__":
    raise SystemExit(main())
