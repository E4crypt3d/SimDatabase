import random
import base64
import re
import hashlib
import hmac


# Obfuscation Helpers
def _rot13(text: str) -> str:
    result = []
    for c in text:
        if "a" <= c <= "z":
            result.append(chr((ord(c) - ord("a") + 13) % 26 + ord("a")))
        elif "A" <= c <= "Z":
            result.append(chr((ord(c) - ord("A") + 13) % 26 + ord("A")))
        else:
            result.append(c)
    return "".join(result)


def _hex_encode(text: str) -> str:
    return text.encode("utf-8").hex()


def _hex_decode(hex_str: str) -> str:
    return bytes.fromhex(hex_str).decode("utf-8")


def _obfuscate_decode(encoded: str, method: str = "b64") -> str:
    if method == "b64":
        return base64.b64decode(encoded).decode()
    elif method == "hex":
        return _hex_decode(encoded)
    elif method == "rot13":
        return _rot13(encoded)
    elif method == "b64_hex":
        return base64.b64decode(encoded).decode()
    elif method == "hex_b64":
        decoded_b64 = base64.b64decode(encoded).decode()
        return _hex_decode(decoded_b64)
    return encoded


def _generate_key(seed: str) -> str:
    return hashlib.sha256(seed.encode()).digest()[:16]


def _xor_obfuscate(text: str, key: str) -> str:
    result = []
    for i, c in enumerate(text):
        result.append(chr(ord(c) ^ ord(key[i % len(key)])))
    return "".join(result)


def _xor_decode(encoded: str, key_seed: str = "simdb2024") -> str:
    key = _generate_key(key_seed)
    key_str = key.hex()[:16]
    result = []
    for i, c in enumerate(encoded):
        result.append(chr(ord(c) ^ ord(key_str[i % len(key_str)])))
    return "".join(result)


# Obfuscated Endpoints
def get_db():
    encoded = "aHR0cHM6Ly9wYWtzaW0uaW5mby9zaW0tZGF0YWJhc2UtZGF0YWJhc2Utb25saW5lLTIwMjItcmVzdWx0LnBocA=="
    return base64.b64decode(encoded).decode()


def get_alt_source_a_endpoint():
    encoded = (
        "aHR0cHM6Ly9zaW1zb3duZXJzZGV0YWlscy5jb20ucGsvd3AtYWRtaW4vYWRtaW4tYWpheC5waHA="
    )
    return base64.b64decode(encoded + "==").decode()


def get_alt_source_a_base_url():
    # Alternative source A base URL (HTML form)
    encoded = "aHR0cHM6Ly9zaW1zb3duZXJzZGV0YWlscy5jb20ucGsv"
    return base64.b64decode(encoded).decode()


def get_alt_source_a_referer():
    encoded = "aHR0cHM6Ly9zaW1zb3duZXJzZGV0YWlscy5jb20ucGsv"
    return base64.b64decode(encoded).decode()


def get_alt_source_b_endpoint():
    encoded = "aHR0cHM6Ly9mcmVzaHNpbXNkYXRhYmFzZXMuY29tL251bWJlckRldGFpbHMucGhw"
    return base64.b64decode(encoded).decode()


def get_alt_source_b_referer():
    encoded = "aHR0cHM6Ly9mcmVzaHNpbXNkYXRhYmFzZXMuY29tLw=="
    return base64.b64decode(encoded).decode()


# Advanced Headers
def _get_random_ip():
    return f"10.{random.randint(0,255)}.{random.randint(1,254)}.{random.randint(1,254)}"


def _get_accept_encoding():
    return random.choice(["gzip, deflate", "gzip, deflate, br", "deflate, gzip"])


def _get_accept_charset():
    return random.choice(["UTF-8", "ISO-8859-1", "windows-1252"])


# Headers
def get_headers(source: str = "primary"):
    user_agents_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/120.0.6099.144 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 Chrome/120.0.6099.144 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    ]

    fake_ip = _get_random_ip()

    if source == "alt_source_b":
        return {
            "User-Agent": random.choice(user_agents_list),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": get_alt_source_b_referer().rstrip("/"),
            "Referer": get_alt_source_b_referer(),
        }

    if source == "alt_source_a":
        return {
            "User-Agent": random.choice(user_agents_list),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": get_alt_source_a_referer().rstrip("/"),
            "Referer": get_alt_source_a_referer(),
        }

    ref_en = "aHR0cHM6Ly9wYWtzaW0uaW5mby9zZWFyY2gucGhw"
    ori_en = "aHR0cHM6Ly9wYWtzaW0uaW5mbw=="
    return {
        "User-Agent": random.choice(user_agents_list),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": base64.b64decode(ref_en).decode(),
        "Origin": base64.b64decode(ori_en).decode(),
    }


# Colors
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED, GREEN, YELLOW, BLUE, CYAN, WHITE = (
        "\033[31m",
        "\033[32m",
        "\033[33m",
        "\033[34m",
        "\033[36m",
        "\033[37m",
    )
    BRIGHT_CYAN = "\033[96m"


COLOR_MAP = {
    "red": Colors.RED,
    "green": Colors.GREEN,
    "yellow": Colors.YELLOW,
    "blue": Colors.BLUE,
    "cyan": Colors.CYAN,
    "white": Colors.WHITE,
    "bright_cyan": Colors.BRIGHT_CYAN,
}


def cs(text: str, color: str = "white") -> str:
    return f"{COLOR_MAP.get(color.lower(), Colors.WHITE)}{text}{Colors.RESET}"


def bold(text: str) -> str:
    return f"{Colors.BOLD}{text}{Colors.RESET}"


# CNIC analysis
PROVINCES = {
    "1": "Khyber Pakhtunkhwa",
    "3": "Punjab",
    "4": "Sindh",
    "5": "Balochistan",
    "6": "Islamabad",
}
DIVISIONS = {"35": "Lahore", "41": "Hyderabad", "42": "Karachi", "37": "Rawalpindi"}


def normalize_cnic(cnic: str) -> str | None:
    digits = re.sub(r"\D", "", cnic)
    return f"{digits[:5]}-{digits[5:12]}-{digits[12]}" if len(digits) == 13 else None


def analyze_cnic(cnic: str) -> dict:
    normalized = normalize_cnic(cnic)
    if not normalized:
        return {"error": "Invalid CNIC format"}
    area_code, family_code, gender_digit = normalized.split("-")
    return {
        "Input CNIC": cnic,
        "Normalized CNIC": normalized,
        "Province / Territory": PROVINCES.get(area_code[0], "Unknown"),
        "Division": DIVISIONS.get(area_code[:2], "Unknown"),
        "Gender": "Male" if int(gender_digit) % 2 != 0 else "Female",
    }
