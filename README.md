<p align="center">
  <img src="https://authon.pro/logo.png" alt="Authon" width="100" />
</p>

<h1 align="center">Authon Python SDK</h1>

<p align="center">
  <strong>Official Python SDK for <a href="https://authon.pro">Authon</a> — Software Licensing & Authentication Platform</strong>
</p>

<p align="center">
  <a href="https://authon.pro"><img src="https://img.shields.io/badge/Website-authon.pro-7c3aed?style=flat-square" alt="Website" /></a>
  <a href="https://discord.gg/MTY79JDFm6"><img src="https://img.shields.io/badge/Discord-Join-5865F2?style=flat-square&logo=discord&logoColor=white" alt="Discord" /></a>
  <a href="https://authon.pro/status"><img src="https://img.shields.io/badge/Status-Check-22c55e?style=flat-square" alt="Status" /></a>
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License" />
</p>

---

## 🚀 Quick Start

### 1. Install

```bash
pip install requests
```

### 2. Get Your Credentials

1. Create an account at [authon.pro](https://authon.pro)
2. Go to **Dashboard → Apps → Create Application**
3. Copy your **App ID** and **API Key** from App Settings

### 3. Use

```python
from authon import Authon

# Initialize with your credentials
auth = Authon("your-app-id", "your-api-key")
auth.init()

# Authenticate
result = auth.login("username", "password")
if result["success"]:
    print(f"Welcome {auth.username}! Level: {auth.level}")
    print(f"Expires: {auth.expires_at}")
else:
    print(f"Error: {result['message']}")

# Use features
value = auth.get_var("welcome_message")
files = auth.list_files()
auth.log("Application started")

# Logout when done
auth.logout()
```

---

## 📖 API Reference

### Initialization

| Method | Description |
|--------|-------------|
| `Authon(app_id, api_key)` | Create SDK instance |
| `init()` → `bool` | Connect to API, validate credentials |

### Authentication

| Method | Description |
|--------|-------------|
| `login(username, password, hwid?)` → `dict` | Login with credentials |
| `license(key, hwid?)` → `dict` | Authenticate with license key |
| `register(username, password, license_key, hwid?)` → `dict` | Create new account |
| `check()` → `bool` | Validate session (heartbeat) |
| `logout()` → `bool` | End session |

### Variables

| Method | Description |
|--------|-------------|
| `get_var(key)` → `str` | Get app-level variable |
| `set_var(key, value)` → `bool` | Set user-level variable |
| `get_user_var(key)` → `str` | Get user-level variable |

### Files

| Method | Description |
|--------|-------------|
| `list_files()` → `list` | List available files for user's level |
| `download_file(file_id)` → `bytes` | Download file content |

### Stats & Logging

| Method | Description |
|--------|-------------|
| `log(message)` → `bool` | Send activity log |
| `fetch_online()` → `dict` | Get online user count/list |
| `fetch_stats()` → `dict` | Get app statistics |

### Utility

| Method | Description |
|--------|-------------|
| `get_hwid()` → `str` | Generate hardware ID |
| `check_blacklist(ip?, hwid?)` → `dict` | Check ban status |
| `redeem_referral(code)` → `dict` | Redeem referral code |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `session_token` | `str` | Active session token |
| `username` | `str` | Authenticated username |
| `level` | `int` | User access level |
| `subscription` | `str` | Subscription plan name |
| `expires_at` | `str` | Subscription expiry date |
| `app_name` | `str` | Application name |
| `app_version` | `str` | Application version |
| `is_authenticated` | `bool` | Whether user has active session |

---

## 🔐 Authentication Methods

### Username + Password Login

```python
result = auth.login("username", "password")
if result["success"]:
    # auth.session_token, auth.username, auth.level are now set
    print(f"Level: {auth.level}")
```

### License Key Only

```python
result = auth.license("ABCDE-FGHIJ-KLMNO-PQRST")
if result["success"]:
    print(f"License valid! Level: {auth.level}")
```

### Register New Account

```python
result = auth.register("newuser", "password123", "LICENSE-KEY-HERE")
if result["success"]:
    print("Account created! Now login:")
    auth.login("newuser", "password123")
```

---

## 📁 File Downloads

```python
# List available files
files = auth.list_files()
for f in files:
    print(f"  {f['name']} ({f['size']} bytes) — Level {f['minLevel']}")

# Download a file
data = auth.download_file(files[0]["id"])
if data:
    with open(files[0]["name"], "wb") as f:
        f.write(data)
    print(f"Downloaded {len(data)} bytes")
```

---

## 🖥️ HWID (Hardware ID)

HWID is **automatically generated** from your system hardware. You don't need to handle it manually.

- **Windows**: Disk serial number + computer name
- **macOS**: Hardware UUID  
- **Linux**: /etc/machine-id

To override:
```python
result = auth.login("user", "pass", hwid="custom-hwid-value")
```

---

## ⚠️ Error Handling

```python
result = auth.login("user", "wrongpassword")
if not result["success"]:
    error = result["message"]
    # Possible error messages:
    # - "Invalid credentials"
    # - "Account banned"
    # - "Hardware ID mismatch"
    # - "Subscription expired"
    # - "Account is frozen. Contact admin to unfreeze."
    # - "VPN/Proxy connections are not allowed"
    # - "Application is paused"
    # - "IP address banned"
    print(f"Error: {error}")
```

---

## 🏗️ Project Structure

```
python-Loader/
├── authon.py           # SDK source (single file, copy to your project)
├── example.py          # Full usage example
├── requirements.txt    # Dependencies (just 'requests')
├── pyproject.toml      # Package metadata
└── README.md           # This file
```

---

## 🔗 Links

| Resource | URL |
|----------|-----|
| 🌐 Website | https://authon.pro |
| 📖 Documentation | https://authon.pro/docs |
| 💬 Discord Community | https://discord.gg/MTY79JDFm6 |
| 📊 Service Status | https://authon.pro/status |
| 🔗 API Health Check | https://api.authon.pro/health |
| 🐙 GitHub | https://github.com/authonpro |

---

## 📋 Requirements

- Python 3.8+
- `requests` library (`pip install requests`)

---

## 📄 License

MIT — Free to use in any project, commercial or personal.

---

<p align="center">
  <strong>Built with ❤️ by <a href="https://authon.pro">Authon</a></strong><br/>
  The #1 KeyAuth Alternative
</p>
