from zapv2 import ZAPv2
import time, os, json

# CONFIG - use environment variable ZAP_APIKEY for safety
API_KEY = os.getenv("ZAP_APIKEY", "")
if not API_KEY:
    raise SystemExit("Set ZAP_APIKEY environment variable before running.")

TARGET = 'http://localhost:3000/#/'   # change as needed
ZAP_PROXY = 'http://127.0.0.1:8080'

zap = ZAPv2(apikey=API_KEY, proxies={'http': ZAP_PROXY, 'https': ZAP_PROXY})

print("[*] ZAP version:", zap.core.version)
print("[*] Opening target:", TARGET)
zap.urlopen(TARGET)
time.sleep(2)

print("[*] Starting spider...")
spider_id = zap.spider.scan(TARGET)
while int(zap.spider.status(spider_id)) < 100:
    print("  Spider:", zap.spider.status(spider_id), "%")
    time.sleep(2)
print("[*] Spider finished.")

# wait for passive scan to finish
while int(zap.pscan.records_to_scan) > 0:
    print("  Passive records left:", zap.pscan.records_to_scan)
    time.sleep(1)
print("[*] Passive scan finished.")

print("[*] Starting active scan...")
scan_id = zap.ascan.scan(TARGET)
while int(zap.ascan.status(scan_id)) < 100:
    print("  Active scan:", zap.ascan.status(scan_id), "%")
    time.sleep(5)
print("[*] Active scan finished.")

alerts = zap.core.alerts(baseurl=TARGET)
print(f"[*] Found {len(alerts)} alerts")
for a in alerts:
    print(f"[{a.get('risk')}] {a.get('alert')} -> {a.get('url')}")

# save reports
os.makedirs("reports", exist_ok=True)
with open("reports/zap_report.html", "w", encoding="utf-8") as f:
    f.write(zap.core.htmlreport())
with open("reports/alerts.json", "w", encoding="utf-8") as f:
    json.dump(alerts, f, indent=2)
print("[*] Reports written to reports/")
