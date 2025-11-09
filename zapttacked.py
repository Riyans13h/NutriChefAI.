
import os, sys, time, json, logging
from datetime import datetime
from zapv2 import ZAPv2

# --------------------------
# Configuration via env vars
# --------------------------
ZAP_APIKEY = os.getenv("ZAP_APIKEY", "")
ZAP_HOST = os.getenv("ZAP_HOST", "127.0.0.1")
ZAP_PORT = int(os.getenv("ZAP_PORT", "8080"))
TARGET = os.getenv("ZAP_TARGET", "http://localhost:3000")
REPORT_DIR = os.getenv("ZAP_REPORT_DIR", "reports")
SPIDER_WAIT = float(os.getenv("ZAP_SPIDER_WAIT", "2"))
ACTIVE_POLL = float(os.getenv("ZAP_ACTIVE_POLL", "5"))
SPIDER_TIMEOUT = int(os.getenv("ZAP_SPIDER_TIMEOUT", "300"))
ACTIVE_TIMEOUT = int(os.getenv("ZAP_ACTIVE_TIMEOUT", "3600"))

# small list of SPA-friendly paths (customize if needed)
SPA_PATHS = [
    "/", "/#/","/#/search","/#/login","/#/product/1","/search","/login","/product/1","/rest/products"
]

# logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("zap_targeted_scan")

# --------------------------
# Helpers
# --------------------------
def exit_fail(msg, code=1):
    log.error(msg)
    sys.exit(code)

def ensure_env():
    if not ZAP_APIKEY:
        exit_fail("ZAP_APIKEY not set. Export it before running: export ZAP_APIKEY=...")
    if not TARGET.startswith(("http://","https://")):
        exit_fail("ZAP_TARGET must start with http:// or https://")

def connect_zap():
    proxy = f"http://{ZAP_HOST}:{ZAP_PORT}"
    log.info(f"Connecting to ZAP at {proxy}")
    try:
        zap = ZAPv2(apikey=ZAP_APIKEY, proxies={'http': proxy, 'https': proxy})
        _ = zap.core.version  # ensure connection
        log.info("Connected to ZAP (version %s)" % _)
        return zap
    except Exception as e:
        exit_fail(f"Failed to connect to ZAP API: {e}")

def find_scanner_ids(zap, keywords=("sql","xss")):
    """
    Return set of scanner ids whose 'name' contains any keyword (case-insensitive).
    Handles responses where zap.ascan.scanners() returns dict or list.
    """
    try:
        all_scanners = zap.ascan.scanners()
    except Exception as e:
        exit_fail(f"Failed to fetch scanners list from ZAP: {e}")

    scanners_list = []
    # support multiple return shapes
    if isinstance(all_scanners, dict):
        # possible key 'scanners' or similar
        if 'scanners' in all_scanners:
            scanners_list = all_scanners['scanners']
        else:
            # try flatten dict values
            for v in all_scanners.values():
                if isinstance(v, list):
                    scanners_list.extend(v)
    elif isinstance(all_scanners, list):
        scanners_list = all_scanners
    else:
        exit_fail("Unexpected scanner list type from zap.ascan.scanners()")

    matched = set()
    for s in scanners_list:
        # scanner entries sometimes come as dicts with 'id' and 'name' or strings
        sid = s.get('id') if isinstance(s, dict) else None
        name = s.get('name') if isinstance(s, dict) else str(s)
        if not sid or not name:
            continue
        lname = name.lower()
        for kw in keywords:
            if kw in lname:
                matched.add(str(sid))
    return matched

def disable_all_scanners(zap):
    # try to disable each scanner by reading the scanners list
    try:
        all_scanners = zap.ascan.scanners()
    except Exception as e:
        log.warning("Could not read scanners to disable: %s" % e)
        return
    scanners_list = all_scanners.get('scanners') if isinstance(all_scanners, dict) and 'scanners' in all_scanners else (all_scanners if isinstance(all_scanners, list) else [])
    for s in scanners_list:
        sid = s.get('id') if isinstance(s, dict) else None
        if not sid:
            continue
        try:
            zap.ascan.set_scanner_enabled(sid, 'false')
        except Exception:
            # some ZAP bindings require string "false" or boolean; ignore failures
            pass

def enable_scanners(zap, id_set):
    for sid in id_set:
        try:
            zap.ascan.set_scanner_enabled(sid, 'true')
            log.info(f"Enabled scanner id {sid}")
        except Exception as e:
            log.warning(f"Failed to enable scanner {sid}: {e}")

def sleep_poll(seconds):
    try:
        time.sleep(seconds)
    except KeyboardInterrupt:
        exit_fail("Interrupted by user", code=130)

def wait_for_status(get_status_func, id_, label, timeout):
    log.info(f"Waiting for {label} (timeout {timeout}s)...")
    start = time.time()
    while True:
        try:
            status = int(get_status_func(id_))
        except Exception:
            status = 100
        log.info(f"{label} status: {status}%")
        if status >= 100:
            return True
        if time.time() - start > timeout:
            log.warning(f"{label} timed out after {timeout}s (status {status}%)")
            return False
        sleep_poll(ACTIVE_POLL)

# --------------------------
# Main flow
# --------------------------
def main():
    ensure_env()
    zap = connect_zap()

    # open root target so ZAP knows the site
    try:
        log.info(f"Opening target: {TARGET}")
        zap.urlopen(TARGET)
        sleep_poll(1)
    except Exception as e:
        log.warning("zap.urlopen() raised: %s" % e)

    # perform light SPA crawl: request several common paths so ZAP records AJAX endpoints
    log.info("Performing lightweight SPA crawl (manual path hits)")
    for p in SPA_PATHS:
        url = TARGET.rstrip("/") + ("" if p.startswith("/") else "/") + p.lstrip("/")
        try:
            log.info("Visiting: %s" % url)
            zap.urlopen(url)
        except Exception as e:
            log.debug("Visit failed: %s" % e)
        sleep_poll(SPIDER_WAIT)

    # Find scanner IDs for SQLi and XSS
    log.info("Discovering scanner IDs for SQLi and XSS")
    sids = find_scanner_ids(zap, keywords=("sql","xss"))
    if not sids:
        log.warning("No scanner IDs found matching SQL/XSS keywords. Will run full active scan (no filter).")
    else:
        log.info(f"Found scanner IDs: {sids}")
        # disable all scanners then enable selected
        disable_all_scanners(zap)
        enable_scanners(zap, sids)

    # Start an active scan (uses enabled scanners)
    log.info("Starting active scan on target root")
    try:
        scan_id = zap.ascan.scan(TARGET)
    except Exception as e:
        exit_fail(f"Failed to start active scan: {e}")

    completed = wait_for_status(zap.ascan.status, scan_id, "Active Scan", ACTIVE_TIMEOUT)
    if not completed:
        log.warning("Active scan did not finish within timeout; continuing to fetch whatever results exist")

    # Save reports
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    base = os.path.join(REPORT_DIR, f"zap_targeted_{ts}")
    os.makedirs(base, exist_ok=True)
    try:
        html = zap.core.htmlreport()
        html_path = os.path.join(base, "zap_report.html")
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(html)
        log.info("Saved HTML report: %s" % html_path)
    except Exception as e:
        log.error("Failed to generate HTML report: %s" % e)
        html_path = None

    try:
        alerts = zap.core.alerts(baseurl=TARGET)
        json_path = os.path.join(base, "alerts.json")
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(alerts, fh, indent=2)
        log.info("Saved alerts JSON: %s" % json_path)
    except Exception as e:
        log.error("Failed to fetch/save alerts: %s" % e)
        alerts = []

    # Summarize
    counts = {"High":0,"Medium":0,"Low":0,"Other":0}
    for a in alerts:
        r = a.get("risk", "Other")
        if r not in counts:
            counts["Other"] += 1
        else:
            counts[r] += 1
    total = len(alerts)
    log.info("Scan summary: total=%d, High=%d, Medium=%d, Low=%d, Other=%d" %
             (total, counts["High"], counts["Medium"], counts["Low"], counts["Other"]))

    # Exit non-zero if high issues found (for CI)
    if counts["High"] > 0:
        log.warning("High severity issues found. Exiting with code 2.")
        sys.exit(2)

    log.info("Done. Reports in: %s" % base)
    sys.exit(0)

if __name__ == "__main__":
    main()
