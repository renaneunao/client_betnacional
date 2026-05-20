import os
import sys
import subprocess

def main():
    # Detect the path of mitmweb executable
    if os.name == 'nt':
        mitmweb_path = os.path.join("venv", "Scripts", "mitmweb.exe")
    else:
        mitmweb_path = os.path.join("venv", "bin", "mitmweb")

    if not os.path.exists(mitmweb_path):
        # Check standard path or look in system PATH
        mitmweb_path = "mitmweb"

    addon_script = os.path.join("mitm_capture", "addon.py")
    
    print("=" * 60)
    print("Starting mitmproxy interceptor for Betnacional...")
    print(f"Using addon: {addon_script}")
    print("Open http://127.0.0.1:8181 in your browser to view live flows.")
    print("Set your browser proxy to 127.0.0.1:8080")
    print("Press Ctrl+C to stop.")
    print("=" * 60)

    try:
        # Run mitmweb with the custom addon
        subprocess.run([mitmweb_path, "-s", addon_script], check=True)
    except FileNotFoundError:
        print(f"Error: Could not find '{mitmweb_path}'. Make sure your virtual environment is activated and dependencies are installed.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProxy stopped. Intercepted flows saved in mitm_capture/captured_flows.json")

if __name__ == "__main__":
    main()
