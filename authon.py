"""
Authon Python SDK v1.0.0
Official SDK for Authon — Software Licensing & Authentication Platform

Website: https://authon.pro
API:     https://api.authon.pro/v1
Docs:    https://authon.pro/docs
Discord: https://discord.gg/jMZCTKPsmE
Status:  https://authon.pro/status

Usage:
    from authon import Authon

    auth = Authon("your-app-id", "your-api-key")
    auth.init()
    result = auth.login("username", "password")

Requirements:
    pip install requests

License: MIT
"""

import requests
import hashlib
import platform
import subprocess
import sys
import os

__version__ = "1.0.0"
__api_version__ = "v1"

class AuthonError(Exception):
    """Custom exception for Authon SDK errors"""
    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class Authon:
    """
    Authon SDK Client

    Provides full authentication, licensing, and file management
    for applications protected by Authon (https://authon.pro).

    Args:
        app_id (str): Your Application ID (from Authon Dashboard → Apps)
        api_key (str): Your API Key (from Authon Dashboard → Apps → Settings)
        api_url (str): API endpoint URL (default: https://api.authon.pro/v1)

    Example:
        auth = Authon("your-app-id", "your-api-key")
        if auth.init():
            result = auth.login("user", "pass")
            if result["success"]:
                print(f"Welcome! Level: {auth.level}")
    """

    API_URL = "https://api.authon.pro/v1"

    def __init__(self, app_id: str, api_key: str, api_url: str = None):
        if not app_id or not api_key:
            raise AuthonError("app_id and api_key are required")

        self.app_id = app_id
        self.api_key = api_key
        self.api_url = api_url or self.API_URL

        # Session state
        self.session_token: str = None
        self.username: str = None
        self.level: int = 0
        self.subscription: str = None
        self.expires_at: str = None

        # App info (populated after init())
        self.app_name: str = None
        self.app_version: str = None
        self.hwid_lock: bool = False
        self.hash_check: bool = False

        # Internal
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": f"Authon-Python-SDK/{__version__}"
        })
        self._initialized = False

    @property
    def is_authenticated(self) -> bool:
        """Check if user has an active session"""
        return self.session_token is not None

    @staticmethod
    def get_hwid() -> str:
        """
        Generate a unique Hardware ID from the current machine.
        
        Windows: Uses disk serial number + computer name
        Linux/Mac: Uses hostname + machine + processor info
        
        Returns:
            str: MD5 hash of system identifiers
        """
        try:
            if sys.platform == "win32":
                # Windows: disk serial + computer name
                output = subprocess.check_output(
                    "wmic diskdrive get serialnumber",
                    shell=True, stderr=subprocess.DEVNULL, timeout=5
                )
                serial = output.decode(errors="ignore").split("\n")[1].strip()
                raw = serial + platform.node()
            elif sys.platform == "darwin":
                # macOS: hardware UUID
                output = subprocess.check_output(
                    ["system_profiler", "SPHardwareDataType"],
                    stderr=subprocess.DEVNULL, timeout=5
                )
                for line in output.decode().split("\n"):
                    if "UUID" in line:
                        raw = line.split(":")[1].strip()
                        break
                else:
                    raw = platform.node() + platform.machine()
            else:
                # Linux: machine-id
                if os.path.exists("/etc/machine-id"):
                    with open("/etc/machine-id") as f:
                        raw = f.read().strip()
                else:
                    raw = platform.node() + platform.machine() + platform.processor()
        except Exception:
            raw = platform.node() + platform.machine()

        return hashlib.md5(raw.encode()).hexdigest()

    def _request(self, data: dict) -> dict:
        """
        Send a POST request to the Authon API.

        All requests go to: POST {api_url}
        Body always includes: appId, apiKey, type

        Args:
            data: Request payload (type + params)

        Returns:
            dict: API response with 'success', 'message', 'data' fields
        """
        data["appId"] = self.app_id
        data["apiKey"] = self.api_key

        try:
            response = self._session.post(self.api_url, json=data, timeout=15)
            
            # Handle binary response (file downloads)
            content_type = response.headers.get("Content-Type", "")
            if "octet-stream" in content_type:
                return {"success": True, "binary": response.content}

            return response.json()
        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "Connection failed. Check your internet or API status at https://authon.pro/status"}
        except requests.exceptions.Timeout:
            return {"success": False, "message": "Request timed out (15s). API may be overloaded."}
        except requests.exceptions.JSONDecodeError:
            return {"success": False, "message": "Invalid response from server"}
        except Exception as e:
            return {"success": False, "message": f"Unexpected error: {str(e)}"}

    # ═══════════════════════════════════════════════════════════
    # INITIALIZATION
    # ═══════════════════════════════════════════════════════════

    def init(self) -> bool:
        """
        Initialize connection to the Authon API.
        Must be called before any other method.

        Validates your app_id and api_key, retrieves app info.

        Returns:
            bool: True if connection successful

        Raises:
            AuthonError: If app is paused or credentials are invalid

        Example:
            auth = Authon("app-id", "api-key")
            if not auth.init():
                print("Failed to connect")
                sys.exit(1)
            print(f"Connected to {auth.app_name} v{auth.app_version}")
        """
        result = self._request({"type": "init"})
        if result.get("success"):
            data = result.get("data", {})
            self.app_name = data.get("name")
            self.app_version = data.get("version")
            self.hwid_lock = data.get("hwidLock", False)
            self.hash_check = data.get("hashCheck", False)
            self._initialized = True
            return True
        return False

    # ═══════════════════════════════════════════════════════════
    # AUTHENTICATION
    # ═══════════════════════════════════════════════════════════

    def login(self, username: str, password: str, hwid: str = None) -> dict:
        """
        Authenticate with username and password.

        Args:
            username: User's username
            password: User's password  
            hwid: Hardware ID (auto-generated if not provided)

        Returns:
            dict: {"success": bool, "message": str, "data": {...}}
            On success, data contains: sessionToken, username, level, subscription, expiresAt

        Example:
            result = auth.login("john", "mypassword123")
            if result["success"]:
                print(f"Welcome {auth.username}! Level: {auth.level}")
                print(f"Subscription: {auth.subscription}")
                print(f"Expires: {auth.expires_at}")
            else:
                print(f"Login failed: {result['message']}")
                # Possible errors:
                # - "Invalid credentials"
                # - "Account banned"
                # - "Hardware ID mismatch" 
                # - "Subscription expired"
                # - "Account is frozen"
                # - "VPN/Proxy connections are not allowed"
        """
        if not username or not password:
            return {"success": False, "message": "Username and password are required"}

        result = self._request({
            "type": "login",
            "username": username,
            "password": password,
            "hwid": hwid or self.get_hwid()
        })

        if result.get("success"):
            data = result.get("data", {})
            self.session_token = data.get("sessionToken")
            self.username = data.get("username")
            self.level = data.get("level", 0)
            self.subscription = data.get("subscription")
            self.expires_at = data.get("expiresAt")

        return result

    def license(self, key: str, hwid: str = None) -> dict:
        """
        Authenticate with a license key only (no username/password).

        First use activates the license. Subsequent uses validate it.

        Args:
            key: License key (format: XXXXX-XXXXX-XXXXX-XXXXX)
            hwid: Hardware ID (auto-generated if not provided)

        Returns:
            dict: {"success": bool, "message": str, "data": {...}}

        Example:
            result = auth.license("A1B2C-D3E4F-G5H6I-J7K8L")
            if result["success"]:
                print(f"License valid! Level: {auth.level}")
        """
        if not key:
            return {"success": False, "message": "License key is required"}

        result = self._request({
            "type": "license",
            "licenseKey": key,
            "hwid": hwid or self.get_hwid()
        })

        if result.get("success"):
            data = result.get("data", {})
            self.session_token = data.get("sessionToken")
            self.level = data.get("level", 0)
            self.subscription = data.get("subscription")
            self.expires_at = data.get("expiresAt")

        return result

    def register(self, username: str, password: str, license_key: str, hwid: str = None) -> dict:
        """
        Register a new account using a license key.

        Args:
            username: Desired username
            password: Desired password (min 6 chars recommended)
            license_key: Valid unused license key
            hwid: Hardware ID (auto-generated if not provided)

        Returns:
            dict: {"success": bool, "message": str, "data": {...}}

        Example:
            result = auth.register("newuser", "securepass123", "XXXXX-XXXXX-XXXXX-XXXXX")
            if result["success"]:
                print("Account created! You can now login.")
            else:
                print(f"Registration failed: {result['message']}")
                # Possible: "Username already exists", "Invalid or already used license key"
        """
        if not username or not password or not license_key:
            return {"success": False, "message": "username, password, and license_key are required"}

        return self._request({
            "type": "register",
            "username": username,
            "password": password,
            "licenseKey": license_key,
            "hwid": hwid or self.get_hwid()
        })

    # ═══════════════════════════════════════════════════════════
    # SESSION MANAGEMENT
    # ═══════════════════════════════════════════════════════════

    def check(self) -> bool:
        """
        Validate current session (heartbeat).
        
        Call periodically to keep session alive and verify it hasn't expired.

        Returns:
            bool: True if session is still valid
        """
        if not self.session_token:
            return False
        result = self._request({"type": "check", "sessionToken": self.session_token})
        return result.get("success", False)

    def logout(self) -> bool:
        """
        End the current session.

        Returns:
            bool: True if logout successful
        """
        if not self.session_token:
            return False
        result = self._request({"type": "logout", "sessionToken": self.session_token})
        if result.get("success"):
            self.session_token = None
            self.username = None
            self.level = 0
        return result.get("success", False)

    # ═══════════════════════════════════════════════════════════
    # VARIABLES
    # ═══════════════════════════════════════════════════════════

    def get_var(self, key: str) -> str:
        """
        Get an application-level variable.
        
        App variables are set by the seller in the dashboard and are
        shared across all users (e.g., download URLs, announcements).

        Args:
            key: Variable name

        Returns:
            str: Variable value, or None if not found
        """
        result = self._request({
            "type": "var",
            "key": key,
            "sessionToken": self.session_token
        })
        if result.get("success"):
            return result.get("data", {}).get("value")
        return None

    def set_var(self, key: str, value: str) -> bool:
        """
        Set a user-level variable (stored per-user).

        Args:
            key: Variable name
            value: Variable value

        Returns:
            bool: True if saved successfully
        """
        result = self._request({
            "type": "setvar",
            "key": key,
            "value": str(value),
            "sessionToken": self.session_token
        })
        return result.get("success", False)

    def get_user_var(self, key: str) -> str:
        """
        Get a user-level variable.

        Args:
            key: Variable name

        Returns:
            str: Variable value, or None if not found
        """
        result = self._request({
            "type": "getvar",
            "key": key,
            "sessionToken": self.session_token
        })
        if result.get("success"):
            return result.get("data", {}).get("value")
        return None

    # ═══════════════════════════════════════════════════════════
    # FILES
    # ═══════════════════════════════════════════════════════════

    def list_files(self) -> list:
        """
        List files available for the current user's level.

        Returns:
            list: Array of file objects with id, name, size, minLevel

        Example:
            files = auth.list_files()
            for f in files:
                print(f"{f['name']} ({f['size']} bytes) - Level {f['minLevel']} required")
        """
        result = self._request({
            "type": "list_files",
            "sessionToken": self.session_token
        })
        if result.get("success"):
            return result.get("data", [])
        return []

    def download_file(self, file_id: str) -> bytes:
        """
        Download a file by its ID (returns raw bytes).

        The file must be accessible for the user's level.
        Use list_files() to get available file IDs.

        Args:
            file_id: File ID from list_files()

        Returns:
            bytes: Raw file content, or None on failure

        Example:
            data = auth.download_file("abc123")
            if data:
                with open("output.exe", "wb") as f:
                    f.write(data)
                print(f"Downloaded {len(data)} bytes")
        """
        if not self.session_token or not file_id:
            return None

        # File download uses the same POST endpoint
        result = self._request({
            "type": "file",
            "fileId": file_id,
            "sessionToken": self.session_token
        })

        # If binary data returned directly
        if result.get("binary"):
            return result["binary"]

        # Fallback: try GET endpoint
        try:
            url = self.api_url.replace("/v1", "") + f"/v1/files/download/{file_id}"
            response = self._session.get(
                url,
                headers={"X-Session-Token": self.session_token},
                timeout=60
            )
            if response.headers.get("Content-Type", "").startswith("application/octet-stream"):
                return response.content
        except Exception:
            pass

        return None

    # ═══════════════════════════════════════════════════════════
    # LOGGING & STATS
    # ═══════════════════════════════════════════════════════════

    def log(self, message: str) -> bool:
        """
        Send an activity log entry visible in the seller dashboard.

        Args:
            message: Log message (max 500 chars)

        Returns:
            bool: True if logged successfully
        """
        result = self._request({
            "type": "log",
            "message": message[:500],
            "sessionToken": self.session_token
        })
        return result.get("success", False)

    def fetch_online(self) -> dict:
        """
        Get list of currently online users.

        Returns:
            dict: {"count": int, "users": [{"username": str, "lastActive": str}]}
        """
        result = self._request({
            "type": "fetch_online",
            "sessionToken": self.session_token
        })
        if result.get("success"):
            return result.get("data", {})
        return {"count": 0, "users": []}

    def fetch_stats(self) -> dict:
        """
        Get application statistics.

        Returns:
            dict: {"totalUsers": int, "onlineUsers": int, "totalKeys": int, "appVersion": str}
        """
        result = self._request({
            "type": "fetch_stats",
            "sessionToken": self.session_token
        })
        if result.get("success"):
            return result.get("data", {})
        return {}

    # ═══════════════════════════════════════════════════════════
    # UTILITY
    # ═══════════════════════════════════════════════════════════

    def check_blacklist(self, ip: str = None, hwid: str = None) -> dict:
        """
        Check if an IP address or HWID is blacklisted.

        Args:
            ip: IP address to check (optional)
            hwid: Hardware ID to check (optional)

        Returns:
            dict: {"blacklisted": bool, "reason": str or None}
        """
        data = {"type": "check_blacklist"}
        if ip:
            data["ip"] = ip
        if hwid:
            data["hwid"] = hwid
        result = self._request(data)
        if result.get("success"):
            return result.get("data", {})
        return {"blacklisted": False, "reason": None}

    def redeem_referral(self, code: str) -> dict:
        """
        Redeem a referral code for bonus subscription days.

        Args:
            code: Referral code

        Returns:
            dict: {"success": bool, "message": str, "data": {"expiresAt": str, "rewardDays": int}}
        """
        return self._request({
            "type": "redeem_referral",
            "code": code,
            "sessionToken": self.session_token
        })
