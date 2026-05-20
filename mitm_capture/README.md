# Mitmproxy Browser Capture Setup Guide

This guide explains how to capture HTTP/HTTPS traffic from your browser to analyze the Betnacional authentication and API flow using `mitmproxy`.

---

## Prerequisites

1. Ensure the project virtual environment is active:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
2. Make sure dependencies are installed (`pip install -r requirements.txt`).

---

## Quick Start (Run Proxy)

We have created a helper script `run_capture.py` in the root of the project to launch `mitmweb` with our interceptor addon.

Run the launcher script:
```powershell
python run_capture.py
```

This will:
1. Start the proxy server on `127.0.0.1:8080`.
2. Start the Mitmweb Web UI interface on `http://127.0.0.1:8181` (usually opens automatically in your browser).
3. Load the custom interceptor addon `mitm_capture/addon.py`.

---

## Configuring Your Browser to Use the Proxy

You need to configure your web browser to direct traffic through the proxy:

### Option A: Using a Chrome/Edge Profile via CLI (Recommended)
This is the easiest way as it keeps your default browser profile clean and unaffected. Close all Chrome instances and run:
```powershell
# Open a clean Chrome window routed through the proxy
Start-Process "chrome.exe" -ArgumentList "--proxy-server=127.0.0.1:8080 --user-data-dir=$env:TEMP\chrome-mitm-profile"
```

### Option B: System-wide Proxy Settings (Windows)
1. Search for **Proxy Settings** in the Windows Start Menu.
2. Turn on **Use a proxy server**.
3. Set Address to `127.0.0.1` and Port to `8080`.
4. Click Save.
*Remember to disable it when you are done capturing.*

---

## Installing the Mitmproxy CA Certificate (CRITICAL for HTTPS)

Because Betnacional uses HTTPS, you will see SSL/TLS errors unless you trust the `mitmproxy` root certificate.

1. Keep the proxy running.
2. In the proxied browser window, navigate to: **[http://mitm.it](http://mitm.it)**.
3. You should see a download page with buttons for different operating systems.
4. Click on the **Windows** button to download the Certificate (usually `mitmproxy-ca-cert.p12` or `.crt`).
5. Double-click the downloaded certificate file to install it.
6. Choose **Current User** -> Place all certificates in the following store -> **Trusted Root Certification Authorities** -> Next -> Finish.
7. Restart your proxied browser.

---

## Capturing the Authentication Flow

1. Open your proxied browser and go to **[https://betnacional.com](https://betnacional.com)**.
2. Click on **Entrar** (Login).
3. Type in your CPF `09446024609` and password `!Senhas123` and click Login.
4. Browse around a bit (e.g. click on a sport, see some odds) to generate additional traffic logs.
5. In the command prompt running `run_capture.py`, you should see logs indicating intercepted requests.
6. The addon will automatically write the captured API requests/responses into the file **`mitm_capture/captured_flows.json`**.
7. Stop the proxy command by pressing `Ctrl + C` in the terminal.

---

## Next Steps

Once the flows are captured, we will read and parse `mitm_capture/captured_flows.json` to extract:
* The login API URL.
* The authentication payload format.
* Any required headers (such as `X-Xsrf-Token`, `User-Agent`, `Referer`).
* The response cookie names and values (session tokens).
