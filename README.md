

# OWASP ZAP — Install & Quickstart



> This README shows how to install OWASP ZAP on Ubuntu without Docker, configure Java, run ZAP in GUI and headless (daemon) modes, scan a local web target such as Juice Shop, run the Python scan scripts you already have, and troubleshoot common issues (e.g. `http://localhost:3000` not reachable). It also contains a short explanation of what the scanning project does and lists common attack types ZAP can detect.

---

## Table of contents

1. What this project does (short)
2. Attacks ZAP can detect (common list)
3. Requirements
4. Install Java (OpenJDK)
5. Download & install OWASP ZAP (standalone)
6. Run ZAP (GUI)
7. Run ZAP headless (daemon) and use API
8. Configure and run your Python ZAP scans
9. Example: Scan OWASP Juice Shop (local)
10. Troubleshooting (Juice Shop / Docker / localhost)
11. CI tips, report formats & exit codes
12. Security & best practices
13. Appendix: useful commands & quick examples

---

## 1. What this project will do (brief)

This project automates targeted ZAP active scanning of a web app (example: Juice Shop). It:

* Pre-hits common SPA paths to make ZAP discover AJAX endpoints.
* Optionally runs AJAX spider for dynamic endpoint discovery.
* Finds ZAP scanner plugin IDs that match keywords (e.g., `xss`, `sql`) and enables only those scanners — enabling focused, faster scans.
* Runs an active scan and waits for completion (or times out).
* Saves reports (HTML, XML if available, alerts JSON) in timestamped folders.
* Optionally fails CI when high-severity findings are present (useful for automated pipelines).

You provided two example Python scripts; they do the above with slightly different UIs. I improved robustness in the version I supplied earlier.

---

## 2. What attacks can ZAP detect (common list)

ZAP performs many automated checks. Typical attack categories ZAP can find (automatically or via plugin/policy) include:

* Cross-Site Scripting (XSS) — reflected, stored, DOM XSS
* SQL Injection (SQLi)
* Cross-Site Request Forgery (CSRF) detection (missing anti-CSRF tokens)
* Open Redirects
* Directory Traversal / Path Traversal
* Local File Inclusion / File Disclosure
* XML External Entities (XXE)
* Server-Side Request Forgery (SSRF)
* OS Command Injection (basic cases)
* Clickjacking (missing X-Frame-Options)
* Insecure cookie flags (missing `Secure`, `HttpOnly`, or `SameSite`)
* CORS misconfigurations
* Missing or misconfigured security headers (CSP, HSTS, X-Content-Type-Options, Referrer-Policy)
* TLS/SSL problems (weak ciphers, expired certs)
* Sensitive information disclosure (stack traces, credentials, API keys in responses)
* Various injection classes (LDAP, XPath, etc.) — depending on enabled scan rules
* Insecure direct object references and access control issues (to an extent — manual validation often needed)

> **Note:** Automated scanners are good at finding many low/medium issues. For some logical, business or complex auth flaws, you need manual testing or custom scripts.

---

## 3. Requirements

* Ubuntu 20.04 / 22.04 or similar
* Java (OpenJDK 17+ recommended for ZAP 2.16.x+; check release notes if using other ZAP versions)
* Internet connection to download ZAP
* `python3` (3.8+), `pip` for the Python ZAP client if you run the Python scripts
* (Optional) Docker if you want to run Juice Shop in a container

---

## 4. Install Java (OpenJDK) — simple steps

1. Update packages:

   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. Install OpenJDK 17 (recommended for modern ZAP):

   ```bash
   sudo apt install -y openjdk-17-jdk
   ```

3. Verify Java:

   ```bash
   java -version
   # Example output: openjdk version "17.0.x" ...
   ```

If you have other Java versions and want to set default:

```bash
sudo update-alternatives --config java
```

---

## 5. Download & install OWASP ZAP (standalone - Ubuntu)

1. Go to the ZAP downloads page (manually) or download via `wget`. (If you cannot browse, open a browser and go to: `https://www.zaproxy.org/download/`.)

2. Example using latest Linux cross-platform package (replace link with current version if newer):

   ```bash
   # create a directory
   mkdir -p ~/downloads/zap && cd ~/downloads/zap

   # Example — update the URL to the latest release .tar.gz or .sh from ZAP site
   wget https://github.com/zaproxy/zaproxy/releases/download/v2.16.1/ZAP_2_16_1_unix.tar.gz

   tar -xzf ZAP_2_16_1_unix.tar.gz
   cd ZAP_2_16_1
   ```

3. Run ZAP (GUI):

   ```bash
   ./zap.sh
   ```

   If you get `permission denied`:

   ```bash
   chmod +x zap.sh
   ./zap.sh
   ```

4. Optionally, create a desktop shortcut or add ZAP to your PATH.

---

## 6. Run ZAP (GUI) & first-time steps

* On first launch, ZAP will ask about persisting session and might create an API key. You can create an API key now or set one later.
* GUI is full-featured: you can use quick scan, active scan, spider, and many add-ons via the Marketplace.

---

## 7. Run ZAP headless (daemon) + API

Many CI setups run ZAP in daemon mode (no GUI) and call the ZAP REST API.

Example (start ZAP daemon with GUI disabled, set API key, listen only on localhost):

```bash
# from ZAP directory
./zap.sh -daemon -host 127.0.0.1 -port 8080 -config api.key=YOUR_API_KEY
```

* `-daemon` starts without GUI.
* `-config api.key=...` sets the API key.
* Ensure the `host`/`port` match what your scripts expect.

To check ZAP is up:

```bash
curl "http://127.0.0.1:8080/JSON/core/view/version/"
```

> If you get an API error, verify the API key (if required) and that the daemon binds to the expected host/port.

---

## 8. Configure and run your Python ZAP scans

### Python requirements

Install the python ZAP client:

```bash
python3 -m pip install --user python-owasp-zap-v2
```

### Environment variables (example)

```bash
export ZAP_APIKEY="your_api_key_here"
export ZAP_HOST="127.0.0.1"
export ZAP_PORT="8080"
export ZAP_TARGET="http://localhost:3000"
export ZAP_REPORT_DIR="reports"
```

### Running the improved targeted scan script

If you saved the improved script as `zapprobe.py`:

```bash
python3 zapprobe.py --apikey $ZAP_APIKEY --target http://localhost:3000 --ajax-spider
```

### Running the category-targeted script

If you saved the second script as `zap_category_scan.py` (updated version provided), run:

```bash
python3 zap_category_scan.py --apikey $ZAP_APIKEY --target http://localhost:3000 --category xss,sqli
```

Or to run all categories:

```bash
python3 zap_category_scan.py --apikey $ZAP_APIKEY --target http://localhost:3000 --category all
```

**Notes:**

* The scripts automatically pre-hit SPA paths to help find JS/AJAX endpoints.
* If your target needs authentication, you must either:

  * Configure ZAP context and authentication (preferred), or
  * Inject a session cookie or token via the script before scanning.
* Reports will be saved under `ZAP_REPORT_DIR` in timestamped folders (HTML and alerts JSON).

---

## 9. Example: scanning OWASP Juice Shop locally

### Start Juice Shop via Docker (recommended for quick testing):

```bash
# If container exists, remove or rename the existing container before starting
sudo docker rm -f juice-shop || true

# Start new container
sudo docker run -d --name juice-shop -p 3000:3000 bkimminich/juice-shop
```

If Docker reports the container name in use:

```bash
sudo docker ps -a          # show all containers and IDs
sudo docker rm -f juice-shop
# then re-run the docker run command
```

Wait a few seconds and then test:

```bash
# From the host
curl -I http://localhost:3000/
# or open in browser: http://localhost:3000/#/
```

If it says `Server listening on port 3000` in the container logs but browser shows “unable to connect”, see Troubleshooting below.

Once Juice Shop is reachable from your host:

```bash
# Start ZAP daemon
./zap.sh -daemon -host 127.0.0.1 -port 8080 -config api.key=YOUR_API_KEY

# Run targeted scan
python3 zapprobe.py --apikey $ZAP_APIKEY --target http://localhost:3000 --ajax-spider
```

---

## 10. Troubleshooting — Juice Shop / Docker / localhost

**Problem:** `http://localhost:3000/#/` shows "Unable to connect" though container logs say `Server listening on port 3000`.

**Checks & fixes:**

1. Is the container actually running?

   ```bash
   sudo docker ps
   ```

2. Check container logs:

   ```bash
   sudo docker logs juice-shop --tail 200
   ```

3. If Docker says container name already in use, remove the old container:

   ```bash
   sudo docker rm -f juice-shop
   ```

4. Re-run with `-p 3000:3000` and check host port:

   ```bash
   sudo docker run -d --name juice-shop -p 3000:3000 bkimminich/juice-shop
   ```

5. Check local host port binding:

   ```bash
   ss -ltnp | grep 3000
   # or
   sudo lsof -i :3000
   ```

6. Firewall or WSL issue:

   * If you run Ubuntu under WSL2, `localhost` in the WSL environment may differ from `localhost` on your Windows host. For WSL2, ensure ports are exposed correctly or access via the WSL IP.
   * Uncomplicated Firewall (ufw): `sudo ufw status` — allow port 3000 if needed:

     ```bash
     sudo ufw allow 3000/tcp
     ```

7. Browser caching / proxy:

   * Ensure your browser/OS network is not using a proxy; try `curl` from terminal:

     ```bash
     curl -v http://localhost:3000/
     ```

8. Docker bind to all interfaces (if needed):

   * If `-p 3000:3000` didn't bind to 127.0.0.1 for any reason, you can explicitly bind:

     ```bash
     sudo docker run -d --name juice-shop -p 127.0.0.1:3000:3000 bkimminich/juice-shop
     ```

9. Verify container started correctly:

   ```bash
   docker inspect --format='{{.State.Running}}' juice-shop
   ```

---

## 11. CI tips, report formats & exit codes

* Reports produced: HTML (human readable), XML (if supported), alerts JSON (machine readable).
* Exit codes: your script can exit `2` when High severity alerts exist — useful in CI to fail the job.
* In CI (GitHub Actions / GitLab), run ZAP in the job (as service or container), run your Python script, then upload the produced reports as artifacts.

---

## 12. Security & best practices

* Keep ZAP API key secret. Do not print it into logs or commit to VCS.
* Use ZAP against only targets you own or have authorization to test.
* Limit scan scope and rate so you don’t unintentionally DoS the target.
* For authenticated scans, use ZAP contexts and session handling rather than simply disabling auth.
* Keep ZAP updated and review Marketplace add-ons for latest rules.

---

## 13. Appendix — Useful commands & examples

### Basic ZAP daemon start:

```bash
./zap.sh -daemon -host 127.0.0.1 -port 8080 -config api.key=YOUR_API_KEY
```

### Quick test with curl to ensure API is reachable:

```bash
curl "http://127.0.0.1:8080/JSON/core/view/version/?apikey=YOUR_API_KEY"
```

### Example: run the improved `zapprobe.py`

```bash
python3 zapprobe.py --apikey $ZAP_APIKEY --target http://localhost:3000 --ajax-spider --debug
```

### Example: run the category script (updated)

```bash
python3 zap_category_scan.py --apikey $ZAP_APIKEY --target http://localhost:3000 --category xss,sqli --debug
```

---

## A note on your earlier `zap_category_scan.py` and errors

* I saw a broken expression in your submitted script (a stray `*` in `args.active_timeou*t`) and some attribute name fallbacks. I revised that code earlier and provided a corrected, more robust script (`zapprobe.py`) — use the cleaned versions I gave in the previous message and the CLI examples above.
* If alerts JSON is empty (you reported "Summary of Alerts ... all zeros"), possible reasons:

  * The scanner didn't find issues (could be true for a hardened site).
  * The scan didn't run correctly or timed out early.
  * ZAP did not reach the target (network issue).
  * The scan used only a small subset of scanners (e.g., only SQL/XSS) and site has none of those issues.
* When you get blank results: check ZAP logs, verify the `scan_id` progress, and fetch `zap.core.alerts(baseurl=TARGET)` manually from a Python REPL or `curl` to make sure the ZAP API returns alert objects.

---

## Final checklist to get started (quick)

1. Install Java: `sudo apt install -y openjdk-17-jdk`
2. Download & extract ZAP, run `./zap.sh`
3. Start ZAP daemon: `./zap.sh -daemon -host 127.0.0.1 -port 8080 -config api.key=MYKEY`
4. Start Juice Shop (remove old container first):

   ```bash
   sudo docker rm -f juice-shop || true
   sudo docker run -d --name juice-shop -p 3000:3000 bkimminich/juice-shop
   ```
5. Verify Juice Shop reachable: `curl http://localhost:3000/`
6. Export env vars:

   ```bash
   export ZAP_APIKEY="MYKEY"
   export ZAP_TARGET="http://localhost:3000"
   ```
7. Run the improved scan:

   ```bash
   python3 zapprobe.py --apikey $ZAP_APIKEY --target $ZAP_TARGET --ajax-spider
   ```

---
