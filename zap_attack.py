#!/usr/bin/env python3
"""
zap_category_scan.py
Run category-targeted ZAP active scans and save per-category alerts.

Usage examples:
  python zap_category_scan.py --apikey $ZAP_APIKEY --target http://localhost:3000 --category xss
  python zap_category_scan.py --apikey $ZAP_APIKEY --target https://staging.example.com --category xss,sqli
  python zap_category_scan.py --apikey $ZAP_APIKEY --target https://staging.example.com --category all
"""

import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime

try:
    from zapv2 import ZAPv2
except Exception:
    print("Install dependency: pip install python-owasp-zap-v2")
    raise

# Basic defaults
DEFAULT_HOST = os.getenv("ZAP_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("ZAP_PORT", "8080"))
DEFAULT_APIKEY = os.getenv("ZAP_APIKEY", "")#insert the key 
DEFAULT_TARGET = os.getenv("ZAP_TARGET", "http://localhost:3000")
REPORT_DIR = os.getenv("ZAP_REPORT_DIR", "reports")
SPIDER_WAIT = float(os.getenv("ZAP_SPIDER_WAIT", "1"))
ACTIVE_POLL = float(os.getenv("ZAP_ACTIVE_POLL", "5"))
ACTIVE_TIMEOUT = int(os.getenv("ZAP_ACTIVE_TIMEOUT", "3600"))
SPA_PATHS = [ "/", "/#/","/#/search","/#/login","/search","/login","/product/1","/rest/products" ]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("zap_category_scan")

CATEGORY_KEYWORDS = {
    # Key = category name used on CLI, Value = tuple of keywords to match scanner names
    "xss": ("xss", "cross site scripting", "cross-site scripting"),
    "sqli": ("sql injection", "sql-injection", "sql"),
    "csrf": ("csrf", "cross site request forgery"),
    "open_redirect": ("open redirect", "redirect"),
    "directory_traversal": ("directory traversal", "path traversal", "file disclosure"),
    "file_disclosure": ("file disclosure", "information disclosure", "sensitive"),
    "xxe": ("xxe", "xml external entity"),
    "ssrf": ("ssrf", "server side request forgery"),
    "command_injection": ("command injection", "os command"),
    "clickjacking": ("clickjacking", "x-frame-options"),
    "insecure_cookies": ("cookie", "secure flag", "httponly", "samesite"),
    "cors": ("cors", "cross origin resource sharing"),
    "security_headers": ("content security policy", "csp", "hsts", "x-content-type-options", "referrer-policy"),
    "tls": ("tls", "ssl", "cipher", "certificate"),
    "sensitive_info": ("information disclosure", "stack trace", "password", "secret"),
    "injection": ("injection", "command injection", "sql injection"),
    # add more categories/keywords as you wish
}

# helper wrappers
def parse_args():
    p = argparse.ArgumentParser(description="ZAP category targeted scanner")
    p.add_argument("--apikey", default=DEFAULT_APIKEY)
    p.add_argument("--host", default=DEFAULT_HOST)
    p.add_argument("--port", default=DEFAULT_PORT, type=int)
    p.add_argument("--target", default=DEFAULT_TARGET)
    p.add_argument("--report-dir", default=REPORT_DIR)
    p.add_argument("--category", default="all", help="Comma-separated categories or 'all'")
    p.add_argument("--keywords", default="", help="Extra keyword(s) to search scanner names")
    p.add_argument("--spider-wait", default=SPIDER_WAIT, type=float)
    p.add_argument("--active-poll", default=ACTIVE_POLL, type=float)
    p.add_argument("--active-timeout", default=ACTIVE_TIMEOUT, type=int)
    p.add_argument("--debug", action="store_true")
    return p.parse_args()

def connect_zap(apikey, host, port):
    proxy = f"http://{host}:{port}"
    log.info(f"Connecting to ZAP at {proxy}")
    zap = ZAPv2(apikey=apikey, proxies={'http': proxy, 'https': proxy})
    try:
        v = zap.core.version
    except Exception:
        v = zap.core.version()
    log.info("Connected to ZAP (version %s)" % v)
    return zap

def normalize_scanners(resp):
    scanners = []
    if not resp:
        return scanners
    if isinstance(resp, dict):
        if 'scanners' in resp and isinstance(resp['scanners'], list):
            scanners = resp['scanners']
        else:
            for v in resp.values():
                if isinstance(v, list):
                    scanners.extend(v)
    elif isinstance(resp, list):
        scanners = resp
    return scanners

def find_scanner_ids(zap, keywords):
    resp = None
    try:
        resp = zap.ascan.scanners()
    except Exception as e:
        log.warning("couldn't fetch scanners: %s", e)
        return set()
    scanners = normalize_scanners(resp)
    matched = set()
    kws = [k.lower() for k in keywords]
    for s in scanners:
        name = None
        sid = None
        if isinstance(s, dict):
            name = s.get("name") or s.get("description") or s.get("title")
            sid = s.get("id") or s.get("pluginId") or s.get("scanId")
        else:
            name = str(s)
        if not name or not sid:
            continue
        lname = name.lower()
        for kw in kws:
            if kw in lname:
                try:
                    matched.add(str(int(sid)))
                except Exception:
                    matched.add(str(sid))
    return matched

def disable_all_scanners(zap):
    try:
        resp = zap.ascan.scanners()
    except Exception as e:
        log.warning("could not read scanners to disable: %s", e)
        return
    for s in normalize_scanners(resp):
        sid = s.get("id") if isinstance(s, dict) else None
        if not sid:
            continue
        sid_s = str(sid)
        for val in ("false", False):
            try:
                zap.ascan.set_scanner_enabled(sid_s, val)
                break
            except Exception:
                pass

def enable_scanners(zap, sid_set):
    for sid in sid_set:
        sid_s = str(sid)
        ok = False
        for val in ("true", True):
            try:
                zap.ascan.set_scanner_enabled(sid_s, val)
                ok = True
                break
            except Exception as e:
                log.debug("enable try failed for %s: %s", sid_s, e)
        if ok:
            log.info("enabled scanner %s", sid_s)
        else:
            log.warning("failed to enable scanner %s", sid_s)

def wait_for_scan(zap, scan_id, timeout, poll_interval):
    start = time.time()
    while True:
        try:
            status = int(zap.ascan.status(scan_id))
        except Exception:
            status = 100
        log.info("scan status: %d%%", status)
        if status >= 100:
            return True
        if time.time() - start > timeout:
            log.warning("scan timeout (status %d%%)", status)
            return False
        time.sleep(poll_interval)

def save_alerts_json(alerts, outpath):
    with open(outpath, "w", encoding="utf-8") as fh:
        json.dump(alerts, fh, indent=2)
    log.info("Wrote alerts: %s", outpath)

def save_html_report(zap, outpath):
    try:
        html = zap.core.htmlreport()
        with open(outpath, "w", encoding="utf-8") as fh:
            fh.write(html)
        log.info("Wrote HTML report: %s", outpath)
    except Exception as e:
        log.debug("Could not produce HTML report: %s", e)

def run_category_scan(zap, target, category, extra_keywords, report_dir, spider_wait, poll, timeout):
    kws = list(CATEGORY_KEYWORDS.get(category, ())) + ([extra_keywords] if extra_keywords else [])
    kws = [k for k in kws if k]
    log.info("Scanning category '%s' using keywords: %s", category, kws)

    sids = find_scanner_ids(zap, kws)
    if not sids:
        log.warning("No scanner IDs matched for category '%s' (keywords: %s). Running full scan.", category, kws)
    else:
        log.info("Found scanner IDs for %s: %s", category, sids)
        disable_all_scanners(zap)
        enable_scanners(zap, sids)

    # start scan
    scan_id = zap.ascan.scan(target)
    scan_id = str(scan_id)
    log.info("Started active scan id=%s", scan_id)
    finished = wait_for_scan(zap, scan_id, timeout, poll)
    if not finished:
        log.warning("Scan did not finish within timeout for category %s", category)

    # fetch alerts and filter by category heuristics (name/description or plugin id)
    alerts = zap.core.alerts(baseurl=target)
    filtered = []
    for a in alerts:
        name = (a.get("name") or "").lower()
        desc = (a.get("description") or "").lower()
        risk = a.get("risk", "")
        matched = False
        for kw in kws:
            if kw.lower() in name or kw.lower() in desc:
                matched = True
                break
        # also include alerts whose pluginId in sids
        plugin_id = str(a.get("pluginId",""))
        if plugin_id in sids:
            matched = True
        if matched:
            filtered.append(a)

    # save outputs
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    outdir = os.path.join(report_dir, f"{category}_{ts}")
    os.makedirs(outdir, exist_ok=True)
    json_path = os.path.join(outdir, "alerts.json")
    save_alerts_json(filtered, json_path)
    save_html_report(zap, os.path.join(outdir, "report.html"))
    # summary counts
    counts = {"High":0,"Medium":0,"Low":0,"Other":0}
    for a in filtered:
        r = a.get("risk", "Other")
        if r not in counts:
            counts["Other"] += 1
        else:
            counts[r] += 1
    log.info("Category %s summary: total=%d High=%d Medium=%d Low=%d", category, len(filtered), counts["High"], counts["Medium"], counts["Low"])
    return filtered, outdir

def main():
    args = parse_args()
    if args.debug:
        log.setLevel(logging.DEBUG)

    if not args.apikey:
        log.error("ZAP API key required (--apikey or env ZAP_APIKEY)")
        sys.exit(1)
    if not args.target.startswith(("http://","https://")):
        log.error("Target must start with http:// or https://")
        sys.exit(1)

    zap = connect_zap(args.apikey, args.host, args.port)

    # pre-hit SPA paths
    try:
        zap.urlopen(args.target)
    except Exception as e:
        log.debug("open url failed: %s", e)
    for p in SPA_PATHS:
        url = args.target.rstrip("/") + (p if p.startswith("/") else "/" + p)
        try:
            zap.urlopen(url)
        except Exception:
            pass
        time.sleep(args.spider_wait)

    categories = []
    if args.category == "all":
        categories = list(CATEGORY_KEYWORDS.keys())
    else:
        categories = [c.strip() for c in args.category.split(",") if c.strip()]

    all_results = {}
    for cat in categories:
        filtered, outdir = run_category_scan(zap, args.target, cat, args.keywords, args.report_dir, args.spider_wait, args.active_poll, args.active_timeou*t if hasattr(args, "active_timeou*t") else args.active_timeout)  # fallback if attr name differs
        all_results[cat] = {"alerts": filtered, "dir": outdir}

    # Combined summary
    total_alerts = sum(len(all_results[c]["alerts"]) for c in all_results)
    log.info("Done. scanned categories: %s. Total matched alerts: %d. Reports: %s", ", ".join(all_results.keys()), total_alerts, args.report_dir)
    # exit code: non-zero if any High in any category
    for c in all_results:
        for a in all_results[c]["alerts"]:
            if a.get("risk") == "High":
                log.warning("High severity found in category %s: %s", c, a.get("name"))
                sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
