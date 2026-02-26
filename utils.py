import random
import os
import base64


def get_db():
    encoded = (
        "aHR0cHM6Ly9wYWtzaW0uaW5mby9zaW0tZGF0YWJhc2Utb25saW5lLTIwMjItcmVzdWx0LnBocA=="
    )

    decoded = base64.b64decode(encoded).decode()
    return decoded


def get_headers():

    user_agents_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.48",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.257",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (Linux; Android 10; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
    ]
    user_agent = random.choice(user_agents_list)

    ref_en = "aHR0cHM6Ly9wYWtzaW0uaW5mby9zZWFyY2gucGhw"
    ori_en = "aHR0cHM6Ly9wYWtzaW0uaW5mbw=="
    ref_de = base64.b64decode(ref_en).decode()
    ori_de = base64.b64decode(ori_en).decode()

    headers = {
        "User-Agent": user_agent,
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": ref_de,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Origin": ori_de,
        "Cache-Control": "max-age=0",
    }

    return headers


# ANSI Color Codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    # Standard colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


COLOR_MAP = {
    "black": Colors.BLACK,
    "red": Colors.RED,
    "green": Colors.GREEN,
    "yellow": Colors.YELLOW,
    "blue": Colors.BLUE,
    "magenta": Colors.MAGENTA,
    "cyan": Colors.CYAN,
    "white": Colors.WHITE,
    "bright_black": Colors.BRIGHT_BLACK,
    "bright_red": Colors.BRIGHT_RED,
    "bright_green": Colors.BRIGHT_GREEN,
    "bright_yellow": Colors.BRIGHT_YELLOW,
    "bright_blue": Colors.BRIGHT_BLUE,
    "bright_magenta": Colors.BRIGHT_MAGENTA,
    "bright_cyan": Colors.BRIGHT_CYAN,
    "bright_white": Colors.BRIGHT_WHITE,
}


def cs(text: str, color: str = "white") -> str:
    """Colorize text with the specified color."""
    color_code = COLOR_MAP.get(color.lower(), Colors.WHITE)
    return f"{color_code}{text}{Colors.RESET}"


def bold(text: str) -> str:
    """Make text bold."""
    return f"{Colors.BOLD}{text}{Colors.RESET}"


import re

PROVINCES = {
    "1": "Khyber Pakhtunkhwa",
    "2": "Ex-FATA (Merged into Khyber Pakhtunkhwa)",
    "3": "Punjab",
    "4": "Sindh",
    "5": "Balochistan",
    "6": "Islamabad Capital Territory",
    "7": "Gilgit-Baltistan",
    "8": "Azad Kashmir",
}

DIVISIONS = {
    "11": "Bannu Division",
    "12": "Dera Ismail Khan Division",
    "13": "Hazara Division",
    "14": "Kohat Division",
    "15": "Malakand Division",
    "16": "Mardan Division",
    "17": "Peshawar Division",
    "31": "Bahawalpur Division",
    "32": "Dera Ghazi Khan Division",
    "33": "Faisalabad Division",
    "34": "Gujranwala / Gujrat Division",
    "35": "Lahore Division",
    "36": "Multan / Sahiwal Division",
    "37": "Rawalpindi Division",
    "38": "Sargodha / Mianwali Division",
    "41": "Hyderabad Division",
    "42": "Karachi Division",
    "43": "Larkana Division",
    "44": "Mirpur Khas Division",
    "45": "Sukkur / Shaheed Benazirabad Division",
    "51": "Kalat / Rakhshan Division",
    "52": "Makran Division",
    "53": "Nasirabad Division",
    "54": "Quetta Division",
    "55": "Sibi Division",
    "56": "Zhob / Loralai Division",
    "61": "Islamabad Capital Territory",
    "71": "Gilgit-Baltistan (All Divisions)",
    "81": "Mirpur Division",
    "82": "Poonch / Muzaffarabad Division",
}


def normalize_cnic(cnic: str) -> str | None:
    digits = re.sub(r"\D", "", cnic)

    if len(digits) != 13:
        return None

    return f"{digits[:5]}-{digits[5:12]}-{digits[12]}"


def analyze_cnic(cnic: str) -> dict:
    normalized = normalize_cnic(cnic)

    if not normalized:
        return {"error": "Invalid CNIC number"}

    area_code, family_code, gender_digit = normalized.split("-")

    province_code = area_code[0]
    division_code = area_code[:2]

    province = PROVINCES.get(province_code, "Unknown")
    division = DIVISIONS.get(division_code, "Unknown")
    gender = "Male" if int(gender_digit) % 2 != 0 else "Female"

    return {
        "Input CNIC": cnic,
        "Normalized CNIC": normalized,
        "Province / Territory": province,
        "Division": division,
        "Family Number": family_code,
        "Gender": gender,
    }
