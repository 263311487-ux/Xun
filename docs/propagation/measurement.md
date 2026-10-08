# Measuring discovery without inventing readership

## Read-only snapshot

From the repository root:

```sh
python3 tools/research_metrics.py --repo 263311487-ux/Xun --output output/metrics/xun-20261008.json
python3 tools/research_metrics.py --owner 263311487-ux --output output/metrics/account-20261008.json
```

GitHub private traffic requires a token with the relevant repository access in the `GITHUB_TOKEN` environment variable. Supply it through your existing secret manager; never put it in a command, repository, issue or screenshot. Without authorization, endpoints are recorded as unavailable, not as zero. Public repository listing does not enumerate private projects. The tool uses current proxy configuration; use `--direct` only when the bridge is unavailable. Output files are local, excluded from Git, and cannot be overwritten. No recurring job or visitor tracker is enabled.

Record retrieval time, source response dates, daily-series range and endpoint availability. If a series ends before the retrieval date, report that lag explicitly. Keep the raw local snapshot and publish only necessary aggregate summaries.

## What each measure means

| Measure | Supports | Does not support |
|---|---|---|
| GitHub views / unique visitors | Visits to the repository over the returned rolling window | Pages visits, paper reading, lifetime audience or scientific impact |
| Clones / unique cloners | Repository retrieval activity | Human readership; bots, CI and our own checks can contribute |
| Referrers / popular paths | Partial routes visible to GitHub | A complete discovery funnel or bounce rate |
| Release asset downloads | Downloads of those specific assets | All PDF reads or Zenodo downloads |
| Zenodo all-version counts | Shared record-family aggregate | Sum of separate per-version totals; adding the same aggregate double-counts |
| Zenodo version counts | Counters for the specified version | Whether a visitor understood, endorsed or cited it |
| Citation aggregator | Citations within that source's coverage and update lag | All citations worldwide |

We have no Pages visitor/bounce analytics or measured search-impression baseline. A successful HTTP response, sitemap and scholarly metadata do not prove indexing in Google Scholar or any search engine.

## Compare changes honestly

1. Take one snapshot before a change or actual distribution action; log the precise change and timestamp.
2. Compare daily data on nonoverlapping available dates. Do not subtract overlapping 14-day totals and call the difference new readers. Unique visitors cannot be added across days/windows.
3. Record our verification traffic and CI/clone activity as possible contamination.
4. Link each actual public distribution to a permanent URL and date. A draft is not a post.
5. Track substantive review issues, reproducible attempts and corrections alongside access counts. A small sample cannot establish a cause of drop-off or the theory's quality.

## Decision rules

Before revising again, identify the missing observation: discovery (search/referrer), click (destination access), comprehension (specific feedback), or research use (replication/citation). Low counts alone cannot distinguish these. If no distribution has actually occurred, create a small, venue-appropriate contribution for review; repeated promotional posts are not a measurement strategy. Real experiments and methodological novelty remain independent of marketing.
