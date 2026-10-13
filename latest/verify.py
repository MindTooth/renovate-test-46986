"""Verify actual Renovate PR bodies and updated files against the fixture matrix."""
import argparse
import base64
import json
from pathlib import Path
import re
import subprocess
import sys


def api(path):
    return json.loads(subprocess.check_output(["gh", "api", path], text=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="MindTooth/renovate-test-46986")
    parser.add_argument("--prefix", default="renovate/latest-46986/")
    parser.add_argument("--write", type=Path)
    parser.add_argument("--compare", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    expected = json.loads((root / "expectations.json").read_text())
    pulls = api("repos/" + args.repo + "/pulls?state=open&per_page=100")
    pulls = [p for p in pulls if p["head"]["ref"].startswith(args.prefix)]
    report = {"repository": args.repo, "prefix": args.prefix, "cases": [], "missing": []}
    remaining = set(expected)
    for pull in pulls:
        files = api("repos/" + args.repo + "/pulls/" + str(pull["number"]) + "/files")
        for file in files:
            name = file["filename"]
            if name not in expected:
                continue
            remaining.discard(name)
            exp = expected[name]
            body = pull["body"]
            summaries = re.findall(r"<summary>[^\n]*\(([^)]+)\)</summary>", body)
            actual_markers = {m: body.count(m) for m in exp.get("markers", {})}
            actual_summaries = {s: summaries.count(s) for s in exp.get("summaries", {})}
            contents = api("repos/" + args.repo + "/contents/" + name + "?ref=" + pull["head"]["sha"])
            text = base64.b64decode(contents["content"]).decode()
            versions = []
            for line in text.splitlines():
                if not line.strip():
                    continue
                if "@" in line:
                    versions.append(re.search(r"@([^\s]+)", line).group(1))
                else:
                    versions.append(line.split("=", 1)[1])
            normalized = [v.removeprefix("v") for v in versions]
            checks = {
                "markers": actual_markers == exp.get("markers", {}),
                "summaries": actual_summaries == exp.get("summaries", {}),
                "updates": normalized == exp["versions"],
            }
            report["cases"].append({
                "file": name, "pullRequest": pull["html_url"], "number": pull["number"],
                "branch": pull["head"]["ref"], "headSha": pull["head"]["sha"],
                "checks": checks, "pass": all(checks.values()),
                "expectedMarkers": exp.get("markers", {}), "actualMarkers": actual_markers,
                "expectedSummaries": exp.get("summaries", {}), "actualSummaries": actual_summaries,
                "expectedVersions": exp["versions"], "actualVersions": versions,
                "body": body,
            })
    report["cases"].sort(key=lambda c: c["file"])
    report["missing"] = sorted(remaining)
    report["pass"] = not remaining and all(c["pass"] for c in report["cases"])
    if args.compare:
        previous = json.loads(args.compare.read_text())
        def stable(value):
            return [{k: c[k] for k in ["file", "number", "branch", "headSha", "actualMarkers", "actualSummaries", "actualVersions", "body"]} for c in value["cases"]]
        report["retryStable"] = stable(previous) == stable(report)
    if args.write:
        args.write.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "pass": report["pass"], "missing": report["missing"],
        "cases": [{k: c[k] for k in ["file", "number", "checks", "pass", "actualMarkers", "actualSummaries", "actualVersions"]} for c in report["cases"]],
        **({"retryStable": report["retryStable"]} if "retryStable" in report else {}),
    }, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
