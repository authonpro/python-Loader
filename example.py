"""
Authon Python SDK - Complete Usage Example
============================================

Before running:
1. Create an account at https://authon.pro
2. Create an application in the dashboard
3. Copy your App ID and API Key
4. Replace the values below

Run:
    pip install requests
    python example.py

Need help? Join our Discord: https://discord.gg/jMZCTKPsmE
"""

import sys
from authon import Authon

# ╔══════════════════════════════════════════════════════════════╗
# ║  CONFIGURATION - Replace with your credentials             ║
# ║  Get these from: https://authon.pro/dashboard              ║
# ╚══════════════════════════════════════════════════════════════╝

APP_ID = "your-app-id"       # Dashboard → Apps → Your App → App ID
API_KEY = "your-api-key"     # Dashboard → Apps → Your App → Settings → API Key

# ══════════════════════════════════════════════════════════════
# STEP 1: Initialize
# ══════════════════════════════════════════════════════════════

auth = Authon(APP_ID, API_KEY)

print("═" * 50)
print("  Authon SDK Example - Python")
print("═" * 50)

print("\n[*] Connecting to Authon API...")

if not auth.init():
    print("[-] Failed to connect to Authon API")
    print("    → Check your APP_ID and API_KEY")
    print("    → Verify API status: https://api.authon.pro/health")
    print("    → Check service status: https://authon.pro/status")
    sys.exit(1)

print(f"[+] Connected: {auth.app_name} v{auth.app_version}")
print(f"    HWID Lock: {'Enabled' if auth.hwid_lock else 'Disabled'}")
print(f"    Your HWID: {auth.get_hwid()}")

# ══════════════════════════════════════════════════════════════
# STEP 2: Authenticate
# ══════════════════════════════════════════════════════════════

print("\n┌─────────────────────────────────────┐")
print("│  [1] Login (Username + Password)    │")
print("│  [2] License Key                    │")
print("│  [3] Register (New Account)         │")
print("└─────────────────────────────────────┘")

choice = input("\n> ").strip()

if choice == "1":
    username = input("  Username: ").strip()
    password = input("  Password: ").strip()
    print("\n[*] Logging in...")
    result = auth.login(username, password)

elif choice == "2":
    key = input("  License Key: ").strip()
    print("\n[*] Validating license...")
    result = auth.license(key)

elif choice == "3":
    username = input("  Username: ").strip()
    password = input("  Password: ").strip()
    license_key = input("  License Key: ").strip()
    print("\n[*] Registering...")
    result = auth.register(username, password, license_key)
    if result.get("success"):
        print("[+] Registration successful! Now logging in...")
        result = auth.login(username, password)
    else:
        print(f"[-] Registration failed: {result.get('message')}")
        sys.exit(1)
else:
    print("[-] Invalid choice")
    sys.exit(1)

# Check result
if not result.get("success"):
    print(f"\n[-] Authentication failed: {result.get('message')}")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════
# STEP 3: Authenticated! Show user info
# ══════════════════════════════════════════════════════════════

print(f"\n[+] ✓ Authenticated successfully!")
print(f"    ├─ Username:     {auth.username or 'N/A'}")
print(f"    ├─ Level:        {auth.level}")
print(f"    ├─ Subscription: {auth.subscription or 'None'}")
print(f"    ├─ Expires:      {auth.expires_at or 'Lifetime'}")
print(f"    └─ Session:      {auth.session_token[:16]}...")

# ══════════════════════════════════════════════════════════════
# STEP 4: Use features
# ══════════════════════════════════════════════════════════════

print("\n" + "─" * 50)
print("  FEATURES DEMO")
print("─" * 50)

# --- Variables ---
welcome = auth.get_var("welcome_message")
if welcome:
    print(f"\n[*] App Variable 'welcome_message': {welcome}")

# Set & get user variable
auth.set_var("last_os", f"Python {sys.version_info.major}.{sys.version_info.minor} on {sys.platform}")
saved = auth.get_user_var("last_os")
print(f"[*] User Variable 'last_os': {saved}")

# --- Files ---
files = auth.list_files()
if files:
    print(f"\n[*] Available Files ({len(files)}):")
    for i, f in enumerate(files):
        size_kb = f.get("size", 0) / 1024
        print(f"    [{i+1}] {f['name']} ({size_kb:.1f} KB) — Level {f.get('minLevel', 1)} required")

    # Download first file (commented out — uncomment to test)
    # data = auth.download_file(files[0]["id"])
    # if data:
    #     with open(files[0]["name"], "wb") as f:
    #         f.write(data)
    #     print(f"    → Downloaded {len(data)} bytes")

# --- Online Users ---
online = auth.fetch_online()
print(f"\n[*] Online Users: {online.get('count', 0)}")
for user in online.get("users", [])[:5]:
    print(f"    • {user.get('username')}")

# --- App Stats ---
stats = auth.fetch_stats()
if stats:
    print(f"\n[*] App Statistics:")
    print(f"    ├─ Total Users:  {stats.get('totalUsers', 0)}")
    print(f"    ├─ Online:       {stats.get('onlineUsers', 0)}")
    print(f"    └─ Total Keys:   {stats.get('totalKeys', 0)}")

# --- Activity Log ---
auth.log("Python SDK example executed successfully")
print("\n[*] Activity logged ✓")

# --- Session Check ---
if auth.check():
    print("[*] Session is valid ✓")

# ══════════════════════════════════════════════════════════════
# STEP 5: Cleanup
# ══════════════════════════════════════════════════════════════

print("\n" + "─" * 50)
input("Press Enter to logout and exit...")
auth.logout()
print("[+] Logged out. Goodbye!")
